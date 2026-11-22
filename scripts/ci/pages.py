#!/usr/bin/env python3
"""Create report routing and the GitHub Pages landing page."""

from __future__ import annotations

import argparse
import html
import re
import shutil
from pathlib import Path


def sanitize_ref(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")
    if not value or value in {".", ".."}:
        raise ValueError(f"unsafe report reference: {name!r}")
    return value


def report_directory(git_ref: str, ref_name: str) -> str:
    if git_ref == "refs/heads/main":
        return "main"
    if git_ref.startswith("refs/tags/"):
        return f"tags/{sanitize_ref(ref_name)}"
    raise ValueError(f"Pages publication is restricted to main and tags: {git_ref}")


def write_index(public: Path) -> None:
    sections = []
    for path, label in (
        ("allure/", "Test Results (Allure)"),
        ("security/", "Security Findings (Trivy)"),
        ("sbom/", "Package & License Inventory (CycloneDX)"),
    ):
        sections.append(f'<li><a href="{html.escape(path)}">{html.escape(label)}</a></li>')
    public.mkdir(parents=True, exist_ok=True)
    (public / "index.html").write_text(
        """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>nigu-lite CI reports</title>
<style>
    body { font: 16px/1.5 sans-serif; max-width: 60rem; margin: 3rem auto; padding: 0 1rem; }
    li { margin: .75rem 0; }
</style>
</head>
<body>
<h1>nigu-lite CI reports</h1>
<ul>
"""
        + "\n".join(sections)
        + """
</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def restore_history(source: Path, destination: Path) -> None:
    if not source.is_dir():
        return
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        target = destination / path.name
        if path.is_dir():
            shutil.copytree(path, target, dirs_exist_ok=True)
        else:
            shutil.copy2(path, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    destination = subparsers.add_parser("destination")
    destination.add_argument("--git-ref", required=True)
    destination.add_argument("--ref-name", required=True)
    destination.add_argument("--github-output", type=Path)
    landing = subparsers.add_parser("landing")
    landing.add_argument("--public", type=Path, required=True)
    history = subparsers.add_parser("history")
    history.add_argument("--source", type=Path, required=True)
    history.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "destination":
        value = report_directory(args.git_ref, args.ref_name)
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as stream:
                stream.write(f"report_dir={value}\n")
        else:
            print(value)
    elif args.command == "landing":
        write_index(args.public)
    else:
        restore_history(args.source, args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
