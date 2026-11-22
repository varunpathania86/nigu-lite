#!/usr/bin/env python3
"""Render validated synthetic configuration inputs for advisory IaC scanning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from scripts.manifests.validator import has_secret_key, validate


def render(root: Path, output: Path) -> list[Path]:
    findings = validate(root)
    if findings:
        raise ValueError("cannot render invalid repository manifests")
    output.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for path in sorted(root.glob("deployments/*.yml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if has_secret_key(document):
            raise ValueError(f"secret-like key in deployment manifest: {path}")
        target = output / f"{path.stem}.json"
        target.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        files.append(target)
    for product in ("erp", "edu"):
        for path in sorted(root.glob(f"tests/tenants/{product}/*/tenant.yml")):
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
            if has_secret_key(document):
                raise ValueError(f"secret-like key in tenant manifest: {path}")
            target = output / f"tenant-{product}-{path.parent.name}.json"
            target.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            files.append(target)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("report/rendered"))
    args = parser.parse_args()
    files = render(args.root.resolve(), args.output)
    print(json.dumps({"files": [str(path) for path in files]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
