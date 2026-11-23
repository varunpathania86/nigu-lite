#!/usr/bin/env python3
"""Publish a stable pull request summary for Reviewdog SARIF inputs."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

MARKER = "<!-- nigu-reviewdog-summary -->"
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def findings(path: Path) -> Counter[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    levels: Counter[str] = Counter()
    for run in document.get("runs", []):
        for result in run.get("results", []):
            levels[str(result.get("level", "warning"))] += 1
    return levels


def markdown(trivy: Counter[str], ruff: Counter[str], run_url: str) -> str:
    rows = []
    for name, levels in (("Trivy", trivy), ("Ruff", ruff)):
        total = sum(levels.values())
        status = "No findings" if total == 0 else f"{total} finding(s)"
        details = ", ".join(f"{level}: {count}" for level, count in sorted(levels.items())) or "Clean"
        rows.append(f"| {name} | {status} | {details} |")
    return (
        f"{MARKER}\n"
        "## Reviewdog quality report\n\n"
        "| Tool | Status | Details |\n"
        "|---|---|---|\n"
        f"{chr(10).join(rows)}\n\n"
        f"Review the annotations and inline findings in the [GitHub Actions checks]({run_url}).\n"
        "Only findings on added or modified lines are reported inline.\n"
    )


def api_request(url: str, token: str, method: str = "GET", body: dict[str, str] | None = None) -> Any:
    request = urllib.request.Request(  # noqa: S310  # callers use the fixed GitHub API host
        url,
        data=None if body is None else json.dumps(body).encode(),
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request) as response:  # noqa: S310
        return json.load(response)


def publish(repository: str, pull_request: int, token: str, body: str) -> str:
    if not REPOSITORY_PATTERN.fullmatch(repository):
        raise ValueError("repository must be in owner/name format")
    if pull_request <= 0:
        raise ValueError("pull_request must be positive")
    endpoint = f"https://api.github.com/repos/{repository}/issues/{pull_request}/comments"
    page = 1
    existing = None
    while True:
        query = urllib.parse.urlencode({"per_page": 100, "page": page})
        comments = api_request(f"{endpoint}?{query}", token)
        for comment in comments:
            if MARKER in comment.get("body", ""):
                existing = comment
                break
        if existing is not None or len(comments) < 100:
            break
        page += 1
    if existing is None:
        created = api_request(endpoint, token, method="POST", body={"body": body})
        return str(created["html_url"])
    updated = api_request(
        existing["url"],
        token,
        method="PATCH",
        body={"body": body},
    )
    return str(updated["html_url"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trivy", type=Path, required=True)
    parser.add_argument("--ruff", type=Path, required=True)
    parser.add_argument("--pull-request", type=int, required=True)
    parser.add_argument("--run-url", required=True)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repository:
        raise SystemExit("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
    url = publish(
        repository,
        args.pull_request,
        token,
        markdown(findings(args.trivy), findings(args.ruff), args.run_url),
    )
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
