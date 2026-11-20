---
description: Read when creating or updating any README (root, product, tenant, tests, deployments, local).
applyTo: '**/README.md'
---
# READMEs

- Every product, tenant, `tests/`, `deployments/` and `local/` folder has a README.
- Start from `docs/templates/README.template.md`; tenants use `docs/templates/tenant/README.template.md`.
- Keep the template sections in order: Overview, Quick start, Structure, Configuration, Operations, Tests, Related.
- First line after the title: one-line purpose, owner and status.
- Include exactly one high-level mermaid diagram (≤ 10 nodes); detail belongs in the LLD.
- Show commands only as Make targets (e.g. `make local-up`, `make deploy VPS=`); never raw tool invocations.
- Link the LLD, related READMEs and master-plan.md sections instead of copying content.
- Keep READMEs in sync: update them in the same PR as the code, targets or structure they describe.
- Remove sections and diagram nodes for removed features.
- Public repo: no secrets, personal data or real tenant data.
- Tenant READMEs list role-based contacts only (e.g. "school office"); no names, phones or e-mails.
- Use relative links; check they resolve after moving files.
- Keep it short: an operator should find how to run, configure and test the folder in under a minute.
- Run `make check-docs` and `make lint` (markdownlint, mermaid checks) before committing.
- List README changes under "Docs & instructions updated" in the PR.
