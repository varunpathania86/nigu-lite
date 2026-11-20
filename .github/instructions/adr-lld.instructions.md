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
- Mark added nodes `:::new` and removed nodes `:::removed`; keep the template's `classDef` lines.
- Keep the template sections; write "n/a" rather than deleting one.
- ADRs are rare: only when master-plan.md §11.3 criteria apply (baseline D1–D27 change, new product type, weaker security, revenue/data model).
- Never create an ADR unprompted; write "ADR proposed: …" in the PR description and let the owner decide.
- When asked to write one: `docs/adr/NNNN-kebab-title.md` from `docs/templates/ADR.template.md` (MADR 4).
- ADR numbers are never reused; an accepted ADR is immutable.
- To change an accepted ADR, write a new one and set the old status to `superseded by NNNN`.
- ADRs are short (context, decision, consequences, status) and link the affected LLDs.
- Version upgrades, tuning, new targets, jobs or tenant fields are never ADRs.
- Run `make check-docs` to validate mermaid blocks and templates.
