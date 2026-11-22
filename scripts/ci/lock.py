#!/usr/bin/env python3
"""Build immutable VPS lock documents from image and package metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def build_lock(host: str, source_commit: str, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    required = {"kind", "name", "digest", "signature", "sbom"}
    for artifact in artifacts:
        missing = required - artifact.keys()
        if missing:
            raise ValueError(f"artifact {artifact.get('name', 'unknown')} lacks: {', '.join(sorted(missing))}")
        if not artifact["signature"]["verified"]:
            raise ValueError(f"signature is not verified for {artifact['name']}")
    return {
        "schema_version": 1,
        "host": host,
        "source_commit": source_commit,
        "artifacts": sorted(artifacts, key=lambda item: (item["kind"], item["name"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifacts = json.loads(args.artifacts.read_text(encoding="utf-8"))
    if isinstance(artifacts, dict):
        artifacts = artifacts.get("artifacts", [])
    lock = build_lock(args.host, args.source_commit, artifacts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(lock, sort_keys=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
