---
description: Read for any change; decides which documentation types must be created or updated.
---
# Documentation

- Update docs in the same change as the code; a PR without matching docs is incomplete.
- Doc types and when each is required: master-plan.md §11.3.
- README: every product, tenant, `tests/`, `deployments/`, `local/`; see `readme.instructions.md`.
- LLD (default): `docs/lld/<area>.md`, written before code for any feature or moderate change.
- One LLD per area or feature (e.g. `gibbon.md`, `ci.md`, `capacity.md`), not per PR; each PR links and updates it.
- ADR: rare, release- or sprint-level only; never create one unprompted.
- If a change seems to meet the ADR criteria, write "ADR proposed: …" in the PR; the owner decides.
- SDD (`docs/sdd/`): when system boundaries, products or trust zones change, usually with an ADR.
- Developer docs (`docs/developer/`): setup, workflows, runbooks, troubleshooting; from `docs/templates/DEV.template.md`.
- Always start from `docs/templates/` (ADR, LLD, SDD, README, DEV, `tenant/README`, tenant and VPS manifest templates).
- Writing LLDs or ADRs: follow `adr-lld.instructions.md`.
- Use mermaid for diagrams; keep them small (≤ 10 nodes in READMEs and PRs).
- Write short, plain sentences; link master-plan.md sections instead of copying them.
- Public repo: no secrets, personal data or real tenant data in any doc.
- Convention changes also update instructions (`instructions-maintenance.instructions.md`).
- List every doc change under "Docs & instructions updated" in the PR.
- Run `make check-docs` and `make lint` (markdownlint, mermaid checks) before committing.
