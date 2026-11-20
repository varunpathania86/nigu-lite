#!/usr/bin/env python3
"""Check AI-instruction and documentation rules (master-plan.md §11).

- Every `.github/instructions/*.instructions.md` is indexed in AGENTS.md and vice versa.
- AGENTS.md has at most 60 lines; each instruction file 20-30 lines with a `description`.
- Required templates exist.
- Mermaid blocks in Markdown files are closed and start with a known diagram type.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AGENTS_MAX_LINES = 60
INSTRUCTION_LINES = (20, 30)
REQUIRED_TEMPLATES = (
    "ADR.template.md",
    "LLD.template.md",
    "SDD.template.md",
    "README.template.md",
    "DEV.template.md",
    "tenant/README.template.md",
    "tenant/tenant.template.yml",
    "vps-manifest.template.yml",
)
MERMAID_TYPES = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "pie",
    "timeline",
    "mindmap",
    "C4Context",
)
SKIP_DIRS = {".git", ".venv", "node_modules", ".cache"}

_INDEX_RE = re.compile(r"`(?:\.github/instructions/)?([a-z0-9-]+\.instructions\.md)`")
_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


def check_agents_index(root: Path) -> list[str]:
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return ["AGENTS.md is missing"]
    text = agents.read_text(encoding="utf-8")
    errors = []
    if len(text.splitlines()) > AGENTS_MAX_LINES:
        errors.append(f"AGENTS.md has more than {AGENTS_MAX_LINES} lines")
    indexed = set(_INDEX_RE.findall(text))
    present = {p.name for p in (root / ".github/instructions").glob("*.instructions.md")}
    errors += [f"AGENTS.md indexes missing file {n}" for n in sorted(indexed - present)]
    errors += [f"{n} is not indexed in AGENTS.md" for n in sorted(present - indexed)]
    return errors


def check_instruction_files(root: Path) -> list[str]:
    errors = []
    low, high = INSTRUCTION_LINES
    for path in sorted((root / ".github/instructions").glob("*.instructions.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        rel = path.relative_to(root)
        if not low <= len(lines) <= high:
            errors.append(f"{rel} has {len(lines)} lines; expected {low}-{high} (split or merge)")
        front = _front_matter(lines)
        if front is None:
            errors.append(f"{rel} lacks YAML front matter")
        elif not any(line.startswith("description:") for line in front):
            errors.append(f"{rel} front matter lacks 'description:'")
    return errors


def check_templates(root: Path) -> list[str]:
    base = root / "docs/templates"
    return [f"Missing template docs/templates/{t}" for t in REQUIRED_TEMPLATES if not (base / t).is_file()]


def check_mermaid(path: Path, root: Path) -> list[str]:
    errors = []
    fence: tuple[str, int, bool] | None = None  # (marker, start line, is mermaid)
    expect_type = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = _FENCE_RE.match(line)
        if fence is None:
            if match:
                info = match.group(3).strip()
                fence = (match.group(2), number, info == "mermaid")
                expect_type = fence[2]
            continue
        marker, start, is_mermaid = fence
        if (
            match
            and match.group(2).startswith(marker[0])
            and len(match.group(2)) >= len(marker)
            and not match.group(3).strip()
        ):
            if expect_type:
                errors.append(f"{path.relative_to(root)}:{start}: empty mermaid block")
            fence = None
            continue
        if is_mermaid and expect_type and line.strip() and not line.strip().startswith("%%"):
            if line.split()[0] not in MERMAID_TYPES:
                errors.append(f"{path.relative_to(root)}:{number}: unknown mermaid diagram type '{line.split()[0]}'")
            expect_type = False
    if fence is not None:
        errors.append(f"{path.relative_to(root)}:{fence[1]}: code block is never closed")
    return errors


def markdown_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(root).parts))


def _front_matter(lines: list[str]) -> list[str] | None:
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return lines[1:index]
    return None


def run(root: Path) -> list[str]:
    errors = check_agents_index(root) + check_instruction_files(root) + check_templates(root)
    for path in markdown_files(root):
        errors += check_mermaid(path, root)
    return errors


def main() -> int:
    errors = run(Path(__file__).resolve().parents[1])
    for error in errors:
        print(f"check-docs: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
