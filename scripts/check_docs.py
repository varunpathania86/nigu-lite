#!/usr/bin/env python3
"""Check AI-instruction and documentation rules (master-plan.md §11).

- Every `.github/instructions/*.instructions.md` is indexed in AGENTS.md and vice versa.
- AGENTS.md has at most 60 lines; each instruction file 20-30 lines with a `description`.
- Required templates exist.
- Mermaid blocks in Markdown files are closed and start with a known diagram type.
- Mermaid classes come only from `docs/diagram-style.md` (master-plan.md §11.6), with exact styles.
- `[+]` nodes keep their component class plus the green border (or `new` when untyped).
- `[-]` nodes are `removed`; decisions and sequence diagrams stay uncoloured.
- Subgraphs use the standard `style`; `linkStyle` only marks added (solid) or removed (dotted) links.

`--fix` first rewrites `classDef` and subgraph `style` lines in every flowchart from the style source.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

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
STYLE_FILE = "docs/diagram-style.md"
# Change-diagram classes need a text marker, so meaning is not carried by colour alone.
CHANGE_MARKERS = {"new": "[+]", "removed": "[-]"}
FLOWCHART_TYPES = ("flowchart", "graph")

_INDEX_RE = re.compile(r"`(?:\.github/instructions/)?([a-z0-9-]+\.instructions\.md)`")
_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
_CLASSDEF_RE = re.compile(r"^\s*classDef\s+(\S+)\s+(.+?);?\s*$")
_CLASS_LINE_RE = re.compile(r"^\s*class\s+(\S+)\s+([\w-]+);?\s*$")
_INLINE_CLASS_RE = re.compile(r":::([\w-]+)")
_STYLE_RE = re.compile(r"^\s*style\s+(\S+)\s+(.+?);?\s*$")
_LINK_STYLE_RE = re.compile(r"^\s*linkStyle\s+(\S+)\s+(.+?);?\s*$")
_SUBGRAPH_RE = re.compile(r"^\s*subgraph\s+([\w-]+)")
# Arrow operators (quoted strings and |edge labels| blanked first): `-- text -->`, `-. text .->`, `-->`, `-.->`, `==>`
_LINK_OP_RE = re.compile(r"--\s[^-]*?\s-->|-\.\s.*?\s\.->|<?-\.+->?|<?-{2,}[>xo]?|<?={2,}>?|~~~")
_NOT_EDGE_RE = re.compile(r"^\s*(class|classDef|style|linkStyle|subgraph|end|direction|click)\b")
# A node id followed by its shape opener; `{` alone (not `{{`) is a decision diamond.
_NODE_RE = re.compile(r"(?<![\w-])([A-Za-z_][\w-]*)(\(\[|\[\[|\[\(|\(\(|\{\{|\[|\(|\{)\s*(\"?)")


class Style(NamedTuple):
    palette: dict[str, str]
    subgraph: str  # `style` of every subgraph
    added_node: str  # `style` of an added node that keeps its component class
    added_link: str
    removed_link: str


def load_style(path: Path) -> Style:
    """Read the styles from the first mermaid block in `path` (docs/diagram-style.md)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "```mermaid") + 1
    end = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("```"))
    block = lines[start:end]
    subgraphs = _subgraph_ids(block)
    palette: dict[str, str] = {}
    found: dict[str, str] = {}
    for line in block:
        if m := _CLASSDEF_RE.match(line):
            palette[m.group(1)] = m.group(2)
        elif m := _STYLE_RE.match(line):
            found["subgraph" if m.group(1) in subgraphs else "added_node"] = m.group(2)
        elif m := _LINK_STYLE_RE.match(line):
            found["removed_link" if "dasharray" in m.group(2) else "added_link"] = m.group(2)
    names = ("subgraph", "added_node", "added_link", "removed_link")
    if not palette or any(n not in found for n in names):
        raise ValueError(f"{path}: needs classDef, subgraph/node style and added/removed linkStyle lines")
    return Style(palette, *(found[n] for n in names))


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
    rel = path.relative_to(root)
    fence: tuple[str, int, bool] | None = None  # (marker, start line, is mermaid)
    block: list[tuple[int, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = _FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = (match.group(2), number, match.group(3).strip() == "mermaid")
                block = []
            continue
        marker, start, is_mermaid = fence
        if (
            match
            and match.group(2).startswith(marker[0])
            and len(match.group(2)) >= len(marker)
            and not match.group(3).strip()
        ):
            if is_mermaid:
                errors += _check_block(block, f"{rel}:{start}", str(rel))
            fence = None
            continue
        block.append((number, line))
    if fence is not None:
        errors.append(f"{rel}:{fence[1]}: code block is never closed")
    return errors


def _check_block(block: list[tuple[int, str]], where: str, rel: str) -> list[str]:
    body = [(n, line) for n, line in block if line.strip() and not line.strip().startswith("%%")]
    if not body:
        return [f"{where}: empty mermaid block"]
    first_number, first = body[0]
    kind = first.split()[0]
    if kind not in MERMAID_TYPES:
        return [f"{rel}:{first_number}: unknown mermaid diagram type '{kind}'"]
    if kind == "sequenceDiagram":
        return [
            f"{rel}:{n}: sequence diagrams stay uncoloured; remove 'rect' (master-plan.md §11.6)"
            for n, line in body[1:]
            if line.split()[0] == "rect"
        ]
    errors: list[str] = []
    defined: set[str] = set()
    links = _links([line for _, line in body[1:]]) if kind in FLOWCHART_TYPES else []
    nodes = _node_info([line for _, line in body[1:]])
    subgraphs = _subgraph_ids([line for _, line in body])
    styled: dict[str, tuple[int, str]] = {}
    for number, line in body[1:]:
        at = f"{rel}:{number}"
        if classdef := _CLASSDEF_RE.match(line):
            errors += _check_classdef(*classdef.groups(), at)
            defined.add(classdef.group(1))
        elif style := _STYLE_RE.match(line):
            styled[style.group(1)] = (number, style.group(2))
        elif link_style := _LINK_STYLE_RE.match(line):
            errors += _check_link_style(link_style.group(1), link_style.group(2), links, at)
        else:
            classes = [m.group(2)] if (m := _CLASS_LINE_RE.match(line)) else _INLINE_CLASS_RE.findall(line)
            errors += _unknown_classes(set(classes), at)
    used = set().union(*(info["classes"] for info in nodes.values())) if nodes else set()
    errors += [
        f"{where}: mermaid class '{n}' is used but has no classDef" for n in sorted((used & PALETTE.keys()) - defined)
    ]
    for node, info in sorted(nodes.items()):
        errors += _check_node(node, info, node in styled, where)
    for node, (number, value) in sorted(styled.items()):
        if node in subgraphs:
            if not _same_style(value, STYLE.subgraph):
                errors.append(f"{rel}:{number}: subgraph style must be '{STYLE.subgraph}' (master-plan.md §11.6)")
        elif not _same_style(value, STYLE.added_node) or not nodes.get(node, {}).get("label", "").startswith("[+]"):
            errors.append(
                f"{rel}:{number}: 'style' is only for subgraphs and added '[+]' nodes "
                f"('{STYLE.added_node}'); run make fix-docs"
            )
    errors += [
        f"{where}: subgraph '{n}' needs 'style {n} {STYLE.subgraph}'; run make fix-docs"
        for n in sorted(subgraphs - styled.keys())
    ]
    return errors


def _check_node(node: str, info: dict, has_style: bool, where: str) -> list[str]:
    classes, label = info["classes"], info["label"]
    components = classes & COMPONENT_CLASSES
    if info["shape"] == "{" and classes:
        return [f"{where}: decision node '{node}' must stay uncoloured (master-plan.md §11.6)"]
    if "new" in classes and components:
        return [
            f"{where}: '{node}' has a component class; drop ':::new', the [+] label marks it (master-plan.md §11.6)"
        ]
    if "removed" in classes and len(classes) > 1:
        return [f"{where}: removed node '{node}' must use only the 'removed' class (master-plan.md §11.6)"]
    if label.startswith("[+]"):
        if not ("new" in classes or components):
            return [f"{where}: added node '{node}' needs its component class, or ':::new' when untyped"]
        if components and not has_style:
            return [f"{where}: added node '{node}' needs its green border style; run make fix-docs"]
    elif "new" in classes:
        return [f"{where}: '{node}' is new; start its quoted label with '[+]'"]
    if label.startswith("[-]") != ("removed" in classes):
        return [f"{where}: '{node}': a '[-]' label and the 'removed' class go together (master-plan.md §11.6)"]
    return []


def _check_link_style(indexes: str, value: str, links: list[bool], at: str) -> list[str]:
    if _same_style(value, STYLE.added_link):
        want_dotted, kind = False, "added (solid)"
    elif _same_style(value, STYLE.removed_link):
        want_dotted, kind = True, "removed (dotted -.->)"
    else:
        return [
            f"{at}: linkStyle must be '{STYLE.added_link}' (added) or '{STYLE.removed_link}' "
            "(removed), master-plan.md §11.6"
        ]
    errors = []
    for index in indexes.split(","):
        if not index.isdigit() or int(index) >= len(links):
            errors.append(f"{at}: linkStyle index {index} does not exist ({len(links)} links, counted from 0)")
        elif links[int(index)] != want_dotted:
            errors.append(f"{at}: linkStyle {index} is styled as {kind} but link {index} is not; recount the links")
    return errors


def _links(lines: list[str]) -> list[bool]:
    """Every link in definition order (mermaid's linkStyle index); True when dotted."""
    links: list[bool] = []
    for line in lines:
        if _NOT_EDGE_RE.match(line):
            continue
        text = re.sub(r'"[^"]*"', '""', line)
        text = re.sub(r"\|[^|]*\|", "", text)
        ops = list(_LINK_OP_RE.finditer(text))
        segments = re.split(_LINK_OP_RE, text)
        for k, op in enumerate(ops):
            count = (_node_join_count(segments[k]) + 1) * (_node_join_count(segments[k + 1]) + 1)
            links += ["." in op.group(0)] * count
    return links


def _node_join_count(segment: str) -> int:
    """Count `&` node joins outside node-shape labels."""
    depth = 0
    joins = 0
    for char in segment:
        if char in "[({":
            depth += 1
        elif char in "])}":
            depth = max(0, depth - 1)
        elif char == "&" and depth == 0:
            joins += 1
    return joins


def _node_info(lines: list[str]) -> dict[str, dict]:
    """Node id -> classes, shape opener and label start (after the opening quote)."""
    nodes: dict[str, dict] = {}

    def node(name: str) -> dict:
        return nodes.setdefault(name, {"classes": set(), "shape": "", "label": ""})

    for line in lines:
        if m := _CLASS_LINE_RE.match(line):
            for name in m.group(1).split(","):
                node(name)["classes"].add(m.group(2))
            continue
        if _NOT_EDGE_RE.match(line):
            continue
        found = [(m.start(), m.group(1)) for m in _NODE_RE.finditer(line)]
        for m in _NODE_RE.finditer(line):
            info = node(m.group(1))
            if not info["shape"]:
                info["shape"], info["label"] = m.group(2), line[m.end() :]
        for m in _INLINE_CLASS_RE.finditer(line):
            owner = re.search(r"([A-Za-z_][\w-]*)$", line[: m.start()])
            name = owner.group(1) if owner else next((n for pos, n in reversed(found) if pos < m.start()), None)
            if name:
                node(name)["classes"].add(m.group(1))
    return nodes


def _unknown_classes(names: set[str], where: str) -> list[str]:
    return [
        f"{where}: mermaid class '{n}' is not in the palette (master-plan.md §11.6)"
        for n in sorted(names - PALETTE.keys())
    ]


def _check_classdef(name: str, style: str, where: str) -> list[str]:
    if name not in PALETTE:
        return [f"{where}: mermaid class '{name}' is not in the palette (master-plan.md §11.6)"]
    if not _same_style(style, PALETTE[name]):
        return [f"{where}: classDef {name} must be '{PALETTE[name]}' (master-plan.md §11.6)"]
    return []


def _same_style(actual: str, expected: str) -> bool:
    return actual.replace(" ", "") == expected.replace(" ", "")


def fix_mermaid(path: Path) -> bool:
    """Rewrite palette `classDef` and subgraph `style` lines of every flowchart; True when changed."""
    lines = path.read_text(encoding="utf-8").split("\n")
    out: list[str] = []
    block: list[str] | None = None
    for line in lines:
        if block is None:
            out.append(line)
            if line.strip() == "```mermaid":
                block = []
            continue
        if line.strip().startswith("```"):
            out += _fix_block(block) + [line]
            block = None
            continue
        block.append(line)
    out += block or []
    text = "\n".join(out)
    if text == path.read_text(encoding="utf-8"):
        return False
    path.write_text(text, encoding="utf-8")
    return True


def _fix_block(block: list[str]) -> list[str]:
    body = [line for line in block if line.strip() and not line.strip().startswith("%%")]
    if not body or body[0].split()[0] not in FLOWCHART_TYPES:
        return block
    subgraphs = _subgraph_ids(block)
    nodes = _node_info(body[1:])
    added = [n for n, info in nodes.items() if info["label"].startswith("[+]") and info["classes"] & COMPONENT_CLASSES]
    kept: list[str] = []
    for line in block:
        if (m := _CLASSDEF_RE.match(line)) and m.group(1) in PALETTE:
            continue
        if (m := _STYLE_RE.match(line)) and (m.group(1) in subgraphs or m.group(1) in nodes):
            continue
        kept.append(line)
    while kept and not kept[-1].strip():
        kept.pop()
    used = set().union(*(info["classes"] for info in nodes.values())) if nodes else set()
    indent = re.match(r"\s*", body[1] if len(body) > 1 else "  ").group(0) or "  "
    order = [m.group(1) for line in block if (m := _SUBGRAPH_RE.match(line))]
    styles = [f"{indent}style {n} {STYLE.subgraph}" for n in order]
    styles += [f"{indent}style {n} {STYLE.added_node}" for n in added]
    defs = [f"{indent}classDef {n} {style}" for n, style in PALETTE.items() if n in used]
    return kept + styles + defs


def _subgraph_ids(block: list[str]) -> set[str]:
    return {m.group(1) for line in block if (m := _SUBGRAPH_RE.match(line))}


STYLE = load_style(Path(__file__).resolve().parents[1] / STYLE_FILE)
PALETTE = STYLE.palette
COMPONENT_CLASSES = set(PALETTE) - {"new", "removed", "fail"}


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
    root = Path(__file__).resolve().parents[1]
    if "--fix" in sys.argv[1:]:
        for path in markdown_files(root):
            if fix_mermaid(path):
                print(f"fix-docs: updated {path.relative_to(root)}")
    errors = run(root)
    for error in errors:
        print(f"check-docs: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
