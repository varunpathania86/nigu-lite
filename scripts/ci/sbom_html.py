#!/usr/bin/env python3
"""Render a searchable CycloneDX package and licence inventory."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def components(document: dict[str, Any]) -> list[dict[str, str]]:
    inventory: list[dict[str, str]] = []
    for component in document.get("components", []):
        licenses: list[str] = []
        for item in component.get("licenses", []):
            license_info = item.get("license", {})
            licenses.append(str(license_info.get("id") or license_info.get("name") or item.get("expression", "")))
        inventory.append(
            {
                "type": str(component.get("type", "")),
                "group": str(component.get("group", "")),
                "name": str(component.get("name", "")),
                "version": str(component.get("version", "")),
                "licenses": ", ".join(value for value in licenses if value) or "UNKNOWN",
                "purl": str(component.get("purl", "")),
            }
        )
    return sorted(inventory, key=lambda item: (item["group"], item["name"], item["version"]))


def render(document: dict[str, Any]) -> str:
    items = components(document)
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(item['type'])}</td>"
        f"<td>{html.escape(item['group'])}</td>"
        f"<td>{html.escape(item['name'])}</td>"
        f"<td><code>{html.escape(item['version'])}</code></td>"
        f"<td>{html.escape(item['licenses'])}</td>"
        f"<td><code>{html.escape(item['purl'])}</code></td>"
        "</tr>"
        for item in items
    )
    empty = '<tr><td colspan="6">No components were found in this SBOM.</td></tr>' if not rows else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CycloneDX package and licence inventory</title>
<style>
    body {{ font: 16px/1.45 sans-serif; margin: 2rem; color: #1a1a1a; }}
    input {{ width: min(36rem, 100%); padding: .65rem; margin: 0 0 1rem; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #cfd8dc; padding: .55rem; text-align: left; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: #eceff1; }}
    code {{ overflow-wrap: anywhere; }}
    .meta {{ color: #455a64; }}
</style>
</head>
<body>
<h1>CycloneDX package and licence inventory</h1>
<p class="meta">{len(items)} components. Raw data:
<a href="sbom.cdx.json" download>sbom.cdx.json</a>.</p>
<label for="filter">Filter package, version or licence:</label>
<input id="filter" type="search" autocomplete="off">
<table id="inventory">
<thead><tr><th>Type</th><th>Group</th><th>Name</th><th>Version</th><th>Licences</th><th>PURL</th></tr></thead>
<tbody>{rows}{empty}</tbody>
</table>
<script>
const filter = document.getElementById("filter");
const rows = [...document.querySelectorAll("#inventory tbody tr")];
filter.addEventListener("input", () => {{
    const query = filter.value.toLowerCase();
    rows.forEach((row) => row.hidden = !row.textContent.toLowerCase().includes(query));
}});
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sbom", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = json.loads(args.sbom.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(document), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
