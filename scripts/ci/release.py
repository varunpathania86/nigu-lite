#!/usr/bin/env python3
"""Create a GitHub Release from trusted publish artifacts."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def request(path: str, token: str, method: str = "GET", body: bytes | None = None) -> Any:
    payload = urllib.request.Request(
        f"https://api.github.com{path}",
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(payload) as response:  # noqa: S310  # URL prefix is fixed to api.github.com
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def create_release(repository: str, tag: str, token: str, publish_dir: Path) -> dict[str, Any]:
    existing = request(f"/repos/{repository}/releases/tags/{tag}", token)
    if existing is None:
        existing = request(
            f"/repos/{repository}/releases",
            token,
            method="POST",
            body=json.dumps(
                {
                    "tag_name": tag,
                    "name": tag,
                    "generate_release_notes": True,
                    "draft": False,
                    "prerelease": False,
                }
            ).encode(),
        )
    uploaded: list[str] = []
    upload_url = str(existing["upload_url"]).split("{", 1)[0]
    current_names = {asset["name"] for asset in existing.get("assets", [])}
    for path in sorted(publish_dir.glob("**/*")):
        if not path.is_file() or path.name in {"published.json"} or path.name.endswith(".key"):
            continue
        if path.name in current_names:
            continue
        query = urllib.parse.urlencode({"name": path.name})
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        asset_request = urllib.request.Request(  # noqa: S310  # upload URL is returned by api.github.com
            f"{upload_url}?{query}",
            data=path.read_bytes(),
            method="POST",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "Content-Type": content_type,
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(asset_request):  # noqa: S310  # upload URL is returned by api.github.com
            uploaded.append(path.name)
    return {"release": existing["html_url"], "uploaded": uploaded}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish-dir", type=Path, required=True)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--tag", default=os.environ.get("GITHUB_REF_NAME", ""))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token or not args.repository or not args.tag.startswith("v"):
        raise SystemExit("release requires GITHUB_TOKEN, repository and a v* tag")
    result = create_release(args.repository, args.tag, token, args.publish_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
