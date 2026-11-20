---
description: Read when writing or updating an LLD, or when a change might need an ADR.
applyTo: 'docs/lld/**,docs/adr/**'
---
# LLDs and ADRs

- LLD before code: create `docs/lld/<area>.md` from `docs/templates/LLD.template.md`, or extend the existing one.
- Commit the LLD on a `docs/` branch or as the first commit of the feature branch.
- Status flow: `draft` → `approved` → `implemented` → `retired`; implementation waits for `approved`.
- One LLD spans several PRs; each PR links it and updates it when the design changed.
- Add a line to the LLD changelog in every PR that touches the area.
- Record moderate decisions (library, config layout, Make target, CI job, tenant field, limit) in the LLD "Decisions" section.
- Include "Existing" and "Proposed" mermaid diagrams (≤ ~10 nodes) with the same names and layout for unchanged parts.
- Added component: `N["[+] Name"]` + its class (`class N core`); `make fix-docs` adds its green dashed border.
- Use `:::new` only for an added untyped step; never with a component class. Removed: `X["[-] Name"]:::removed` only.
- Added links: `linkStyle <i> stroke:#2e7d32,stroke-width:2px`; removed links: `-.->` + `linkStyle <i> stroke:#9e9e9e,stroke-dasharray:5 4`.
- Count link indexes from 0 in definition order (`A & B --> C` = 2); `make check-docs` verifies them.
- Other nodes use the master-plan.md §11.6 palette classes and subgraph `style`, as in the template.
- Keep the template sections; write "n/a" rather than deleting one.
- ADRs are rare: only when master-plan.md §11.3 criteria apply (baseline D1–D27 change, new product type, weaker security, revenue/data model).
- Never create an ADR unprompted; write "ADR proposed: …" in the PR description and let the owner decide.
- When asked to write one: `docs/adr/NNNN-kebab-title.md` from `docs/templates/ADR.template.md` (MADR 4).
- ADR numbers are never reused; an accepted ADR is immutable.
- To change an accepted ADR, write a new one and set the old status to `superseded by NNNN`.
- ADRs are short (context, decision, consequences, status) and link the affected LLDs.
- Version upgrades, tuning, new targets, jobs or tenant fields are never ADRs.
- Run `make fix-docs` to add diagram styles from `docs/diagram-style.md` and validate mermaid blocks and templates.
