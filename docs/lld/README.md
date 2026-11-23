# Low-Level Designs

One LLD per area or feature (`<area>.md`, e.g. `ci.md`, `tenant-manifest.md`, `gibbon.md`), written from
[LLD.template.md](../templates/LLD.template.md) **before** the first implementation PR and updated by later PRs.
Status flow: `draft` → `approved` → `implemented` → `retired`.

Moderate decisions (a library, a config layout, a Make target, a CI job, a tenant field) go in the LLD's
"Decisions" section, not in an ADR.

Stage 1 LLDs:

- [`ci.md`](ci.md): Workspace, Build Container, Act, registry and report architecture.
- [`tenant-manifest.md`](tenant-manifest.md): deployment and tenant schema and validation.
- [`local-environment.md`](local-environment.md): Stage 2 VPS simulator and local Ansible delivery.
