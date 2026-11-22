#!/usr/bin/env python3
"""Execute one catalog module inside a Build Container."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.ci.package import package_tenant

DOCKER = shutil.which("docker") or "docker"
TRIVY = shutil.which("trivy") or "trivy"


def find_module(catalog: dict[str, object], module_id: str) -> dict[str, object]:
    for module in catalog.get("modules", []):
        if module.get("id") == module_id:
            return module
    raise ValueError(f"unknown module id: {module_id}")


def run(module: dict[str, object], root: Path, output: Path) -> dict[str, object]:
    path = root / str(module["path"])
    result: dict[str, object] = {
        "job": f"module-{module['id']}",
        "status": "success",
        "duration_seconds": 0,
        "module": module["id"],
        "type": module["type"],
        "summary": f"Built module {module['id']}",
    }
    if module["type"] == "tenant":
        result.update(package_tenant(path, output / f"{module['id']}.tar.gz"))
        return result
    if module["type"] == "image":
        context = path
        filename = "Containerfile" if (context / "Containerfile").is_file() else "Dockerfile"
        tag = f"local-nigu/{module['id']}:{os.environ.get('SOURCE_TREE', 'unknown')[:12]}"
        subprocess.run(  # noqa: S603  # catalog-validated module path and fixed Docker executable
            [DOCKER, "build", "--file", str(context / filename), "--tag", tag, str(context)], check=True
        )
        subprocess.run(  # noqa: S603  # catalog-validated module reference and fixed Trivy executable
            [
                TRIVY,
                "image",
                "--skip-db-update",
                "--skip-check-update",
                "--exit-code",
                "1",
                "--severity",
                "HIGH,CRITICAL",
                "--ignore-unfixed",
                tag,
            ],
            check=True,
        )
        result.update({"reference": tag})
        return result
    if module["type"] in {"vps", "role"}:
        result["status"] = "validated"
        return result
    raise ValueError(f"unsupported module type: {module['type']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    result = run(find_module(catalog, args.id), args.root.resolve(), args.output)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / f"{args.id}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
