#!/usr/bin/env python3
"""Build deterministic, allow-listed tenant package archives."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path
from typing import Any

import yaml

ALLOWED_FILES = {"tenant.yml", "README.md"}
ALLOWED_DIRS = {"assets", "migrations"}
MAX_PACKAGE_BYTES = 10 * 1024 * 1024
SECRET_KEYS = ("vault", "password", "secret", "token", "key")


def _allowed(path: Path, directory: Path) -> bool:
    relative = path.relative_to(directory)
    return relative.as_posix() in ALLOWED_FILES or (relative.parts and relative.parts[0] in ALLOWED_DIRS)


def inspect_tenant(directory: Path) -> list[str]:
    errors: list[str] = []
    tenant_path = directory / "tenant.yml"
    if not tenant_path.is_file():
        return ["missing tenant.yml"]
    document = yaml.safe_load(tenant_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        return ["tenant.yml must contain an object"]
    for key, value in document.items():
        if any(word in str(key).lower() for word in SECRET_KEYS):
            errors.append(f"secret-like key in tenant.yml: {key}")
        if isinstance(value, str) and value.startswith("$ANSIBLE_VAULT"):
            errors.append(f"Vault data in tenant.yml at {key}")
    for path in sorted(directory.rglob("*")):
        if path.is_file() and not _allowed(path, directory):
            errors.append(f"file is outside package allow-list: {path.relative_to(directory).as_posix()}")
    return errors


def package_tenant(directory: Path, output: Path) -> dict[str, Any]:
    errors = inspect_tenant(directory)
    if errors:
        raise ValueError("; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    files = [path for path in sorted(directory.rglob("*")) if path.is_file() and _allowed(path, directory)]
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for path in files:
                    data = path.read_bytes()
                    relative = path.relative_to(directory).as_posix()
                    info = tarfile.TarInfo(relative)
                    info.size = len(data)
                    info.mode = 0o644
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    archive.addfile(info, io.BytesIO(data))
    size = output.stat().st_size
    if size > MAX_PACKAGE_BYTES:
        output.unlink()
        raise ValueError(f"package is {size} bytes; maximum is {MAX_PACKAGE_BYTES}")
    tenant = yaml.safe_load((directory / "tenant.yml").read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "product": tenant["product"],
        "tenant": tenant["id"],
        "archive": str(output),
        "files": [path.relative_to(directory).as_posix() for path in files],
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "size_bytes": size,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = package_tenant(args.tenant, args.output)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
