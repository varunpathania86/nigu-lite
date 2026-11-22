#!/usr/bin/env python3
"""Merge CI report fragments into machine, Markdown and self-contained HTML formats."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def load_fragments(directory: Path) -> list[dict[str, Any]]:
    fragments: list[dict[str, Any]] = []
    for path in sorted(directory.rglob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(document, dict) and "job" in document:
            fragments.append(document)
    return fragments


def final_status(fragments: list[dict[str, Any]]) -> str:
    return "failure" if any(item.get("status") == "failure" for item in fragments) else "success"


def markdown_report(workflow: str, fragments: list[dict[str, Any]], needs: dict[str, Any] | None = None) -> str:
    status = final_status(fragments)
    lines = [
        f"# {workflow} report",
        "",
        f"**Final status:** {status}",
        "",
        "| Job | Status | Duration | Details |",
        "|---|---|---:|---|",
    ]
    for fragment in fragments:
        details = fragment.get("summary", "No summary")
        lines.append(
            f"| {fragment.get('job', 'unknown')} | {fragment.get('status', 'unknown')} | "
            f"{fragment.get('duration_seconds', 0)}s | {str(details).replace('|', '\\|')} |"
        )
    if needs:
        lines.extend(["", "## Workflow jobs", "", f"```json\n{json.dumps(needs, indent=2, sort_keys=True)}\n```"])
    lines.extend(["", "## Evidence", ""])
    if fragments:
        lines.extend(
            f"- {fragment.get('job', 'unknown')}: {fragment.get('status', 'unknown')}" for fragment in fragments
        )
    else:
        lines.append("- No job fragments were produced.")
    return "\n".join(lines) + "\n"


def html_report(title: str, markdown: str) -> str:
    escaped = html.escape(markdown)
    return f"""<!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <style>
        body {{ font: 16px/1.5 sans-serif; max-width: 72rem; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
        pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #f5f5f5; padding: 1rem; }}
    </style>
    </head>
    <body><h1>{html.escape(title)}</h1><pre>{escaped}</pre></body>
    </html>
    """


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--parts", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("report"))
    parser.add_argument("--needs-json", default="{}")
    parser.add_argument("--needs-file", type=Path)
    args = parser.parse_args()
    fragments = load_fragments(args.parts)
    try:
        needs_text = args.needs_file.read_text(encoding="utf-8") if args.needs_file else args.needs_json
        needs = json.loads(needs_text)
    except json.JSONDecodeError:
        needs = {"raw": needs_text}
    markdown = markdown_report(args.workflow, fragments, needs)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.md").write_text(markdown, encoding="utf-8")
    (args.output / "report.html").write_text(html_report(f"{args.workflow} report", markdown), encoding="utf-8")
    combined = {
        "schema_version": 1,
        "workflow": args.workflow,
        "status": final_status(fragments),
        "fragments": fragments,
        "needs": needs,
    }
    (args.output / "report.json").write_text(json.dumps(combined, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
