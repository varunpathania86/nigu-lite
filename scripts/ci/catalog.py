#!/usr/bin/env python3
"""Build the repository module catalog used by CI and local Act runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.manifests.validator import validate


def build_catalog(root: Path) -> dict[str, Any]:
    modules: list[dict[str, Any]] = []
    if (root / "local" / "Containerfile").is_file():
        modules.append(
            {
                "id": "image-local-vps",
                "type": "image",
                "path": "local",
                "product": "local",
                "inputs": ["local/Containerfile", "local/entrypoint.sh", "local/scripts"],
                "dependencies": [],
            }
        )
    if (root / "local" / "operations" / "Containerfile").is_file():
        modules.append(
            {
                "id": "image-local-operations",
                "type": "image",
                "path": "local/operations",
                "product": "local",
                "inputs": ["local/operations", "local/ansible"],
                "dependencies": [],
            }
        )
    image_roots = (
        root / "core" / "images",
        root / "erp" / "images",
        root / "edu" / "images",
        root / "tests" / "fixtures" / "images",
    )
    for image_root in image_roots:
        if not image_root.is_dir():
            continue
        for path in sorted(image_root.iterdir()):
            if (path / "Containerfile").is_file() or (path / "Dockerfile").is_file():
                modules.append(
                    {
                        "id": f"image-{path.relative_to(root).as_posix().replace('/', '-')}",
                        "type": "image",
                        "path": path.relative_to(root).as_posix(),
                        "product": path.relative_to(root).parts[0],
                        "inputs": [path.relative_to(root).as_posix()],
                        "dependencies": [],
                    }
                )
    for product in ("erp", "edu"):
        for base in (root / product / "tenants", root / "tests" / "tenants" / product):
            if not base.is_dir():
                continue
            for tenant in sorted(base.glob("*/tenant.yml")):
                tenant_path = tenant.parent.relative_to(root).as_posix()
                modules.append(
                    {
                        "id": f"tenant-{product}-{tenant.parent.name}",
                        "type": "tenant",
                        "path": tenant_path,
                        "product": product,
                        "inputs": [tenant_path, "versions.yml"],
                        "dependencies": [],
                    }
                )

    deployments = root / "deployments"
    for manifest in sorted(deployments.glob("*.yml")):
        if manifest.name.endswith(".lock.yml"):
            continue
        modules.append(
            {
                "id": f"vps-{manifest.stem}",
                "type": "vps",
                "path": manifest.relative_to(root).as_posix(),
                "product": "core",
                "inputs": [manifest.relative_to(root).as_posix(), "versions.yml"],
                "dependencies": [],
            }
        )

    for product in ("core", "erp", "edu"):
        roles = root / product / "ansible" / "roles"
        if not roles.is_dir():
            continue
        for role in sorted(path for path in roles.iterdir() if path.is_dir()):
            role_path = role.relative_to(root).as_posix()
            modules.append(
                {
                    "id": f"role-{product}-{role.name}",
                    "type": "role",
                    "path": role_path,
                    "product": product,
                    "inputs": [role_path],
                    "dependencies": [],
                }
            )
    modules.sort(key=lambda item: item["id"])
    return {"schema_version": 1, "modules": modules}


def catalog(root: Path) -> dict[str, Any]:
    findings = validate(root)
    modules = build_catalog(root)
    return {
        **modules,
        "job": "catalog",
        "status": "success" if not findings else "failure",
        "duration_seconds": 0,
        "summary": f"{len(modules['modules'])} modules inventoried",
        "valid": not findings,
        "findings": [finding.to_dict() for finding in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = catalog(args.root.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 1 if not result["valid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
