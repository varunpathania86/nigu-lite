#!/usr/bin/env python3
"""Ensure GitHub Pages publishes the gh-pages branch."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request


def request(repository: str, token: str, method: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    request_object = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/pages",
        method=method,
        data=body,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request_object) as response:  # noqa: S310  # GitHub API URL is fixed
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404 and method == "GET":
            return {}
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    payload = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
    existing = request(args.repository, token, "GET")
    method = "PUT" if existing else "POST"
    request(args.repository, token, method, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
