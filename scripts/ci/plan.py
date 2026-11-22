#!/usr/bin/env python3
"""Map changed paths to CI modules."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

GIT = shutil.which("git")
if GIT is None:
    raise RuntimeError("git executable is required")


def changed_paths(root: Path, base: str, head: str = "HEAD") -> list[str]:
    merge_base = subprocess.run(  # noqa: S603  # fixed Git executable and revision arguments
        [GIT, "merge-base", base, head],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    result = subprocess.run(  # noqa: S603  # fixed Git executable and revision arguments
        [GIT, "diff", "--name-only", "--diff-filter=ACMR", f"{merge_base}...{head}"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(line for line in result.stdout.splitlines() if line)


def _matches(path: str, prefix: str) -> bool:
    candidate = PurePosixPath(path)
    target = PurePosixPath(prefix)
    return candidate == target or target in candidate.parents


def plan(catalog: dict[str, Any], paths: list[str], modules: str = "") -> dict[str, Any]:
    selected: dict[str, dict[str, Any]] = {}
    reasons: dict[str, list[str]] = {}
    requested = {item.strip() for item in modules.split(",") if item.strip()}
    for module in catalog.get("modules", []):
        module_id = module["id"]
        matches: list[str] = []
        if requested and ("all" in requested or module_id in requested):
            matches = ["manual module selection"]
        else:
            for changed in paths:
                if any(_matches(changed, item) for item in module.get("inputs", [])):
                    matches.append(changed)
            if changed_global(module, paths):
                matches.extend(changed_global(module, paths))
        if matches:
            selected[module_id] = module
            reasons[module_id] = sorted(set(matches))
    ordered = [selected[key] for key in sorted(selected)]
    return {
        "schema_version": 1,
        "job": "plan",
        "status": "success",
        "duration_seconds": 0,
        "summary": f"{len(ordered)} modules affected",
        "changed_paths": sorted(paths),
        "modules": ordered,
        "any": bool(ordered),
        "reasons": reasons,
        "skip_reason": "" if ordered else "No build modules are affected by the selected source changes.",
    }


def changed_global(module: dict[str, Any], paths: list[str]) -> list[str]:
    changed = set()
    for item in paths:
        if item.startswith("versions.yml") or item.startswith("scripts/ci/"):
            if module["type"] in {"image", "tenant", "vps"}:
                changed.add(item)
        if item.startswith(f"{module.get('product')}/ansible/") and module["type"] in {"image", "tenant"}:
            changed.add(item)
        if item.startswith("core/ansible/") and module["type"] in {"image", "tenant", "vps"}:
            changed.add(item)
    return sorted(changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--paths-file", type=Path)
    parser.add_argument("--modules", default="")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    paths = (
        [line for line in args.paths_file.read_text(encoding="utf-8").splitlines() if line]
        if args.paths_file
        else changed_paths(args.catalog.resolve().parents[1], args.base, args.head)
    )
    result = plan(catalog, paths, args.modules)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as stream:
            stream.write(f"any={'true' if result['any'] else 'false'}\n")
            stream.write(f"modules={json.dumps(result['modules'], separators=(',', ':'))}\n")
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
