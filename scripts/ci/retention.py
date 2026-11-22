#!/usr/bin/env python3
"""Produce a retention plan for immutable local/registry publication metadata."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def retention_plan(metadata: list[dict[str, Any]], keep: int) -> dict[str, Any]:
    ordered = sorted(
        metadata,
        key=lambda item: (
            item.get("package", ""),
            item.get("created_at", ""),
            item.get("digest", ""),
        ),
        reverse=True,
    )
    retain_digests: set[str] = set()
    for package in sorted({str(item.get("package", "")) for item in ordered}):
        versions = [item for item in ordered if str(item.get("package", "")) == package]
        retain = versions[:keep]
        retain_digests.update(
            str(item.get("digest"))
            for item in versions
            if item.get("referenced")
            or item in retain
            or any(not str(tag).startswith("sha-") for tag in item.get("tags", []))
        )
    return {
        "schema_version": 1,
        "keep": keep,
        "dry_run": True,
        "retain": [item for item in ordered if item.get("digest") in retain_digests],
        "candidates": [item for item in ordered if item.get("digest") not in retain_digests],
    }


def github_api(path: str, token: str, method: str = "GET") -> Any:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request) as response:  # noqa: S310  # URL prefix is fixed to api.github.com
        if response.status == 204:
            return None
        return json.load(response)


def package_metadata(owner: str, token: str) -> list[dict[str, Any]]:
    try:
        packages = github_api(f"/orgs/{owner}/packages?package_type=container&per_page=100", token)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        packages = github_api(f"/users/{owner}/packages?package_type=container&per_page=100", token)
    namespace = "orgs"
    try:
        github_api(f"/orgs/{owner}", token)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            namespace = "users"
    result: list[dict[str, Any]] = []
    for package in packages:
        name = urllib.parse.quote(package["name"], safe="")
        versions = github_api(f"/{namespace}/{owner}/packages/container/{name}/versions?per_page=100", token)
        for version in versions:
            tags = version.get("metadata", {}).get("container", {}).get("tags", [])
            if not any(str(tag).startswith("sha-") for tag in tags):
                continue
            result.append(
                {
                    "package": package["name"],
                    "id": version["id"],
                    "digest": version.get("name", ""),
                    "tags": tags,
                    "created_at": version.get("created_at", ""),
                    "referenced": False,
                }
            )
    return result


def delete_versions(owner: str, token: str, candidates: list[dict[str, Any]]) -> list[str]:
    namespace = "orgs"
    try:
        github_api(f"/orgs/{owner}", token)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            namespace = "users"
    deleted: list[str] = []
    for candidate in candidates:
        package = urllib.parse.quote(str(candidate["package"]), safe="")
        path = f"/{namespace}/{owner}/packages/container/{package}/versions/{candidate['id']}"
        github_api(path, token, method="DELETE")
        deleted.append(str(candidate.get("digest", "")))
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--keep", type=int, default=30)
    parser.add_argument("--owner", default=os.environ.get("GITHUB_REPOSITORY_OWNER", ""))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    metadata = (
        json.loads(args.metadata.read_text(encoding="utf-8"))
        if args.metadata
        else package_metadata(args.owner, token)
        if args.owner and token
        else {"versions": []}
    )
    result = retention_plan(metadata if isinstance(metadata, list) else metadata.get("versions", []), args.keep)
    result["dry_run"] = not args.apply
    if args.apply:
        if not args.owner or not token:
            raise SystemExit("OWNER and GITHUB_TOKEN are required for retention deletion")
        result["deleted"] = delete_versions(args.owner, token, result["candidates"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
