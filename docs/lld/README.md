# Low-Level Designs

One LLD per area or feature (`<area>.md`, e.g. `ci.md`, `tenant-manifest.md`, `gibbon.md`), written from
[LLD.template.md](../templates/LLD.template.md) **before** the first implementation PR and updated by later PRs.
Status flow: `draft` → `approved` → `implemented` → `retired`.

Moderate decisions (a library, a config layout, a Make target, a CI job, a tenant field) go in the LLD's
"Decisions" section, not in an ADR.

No LLDs yet; the first one (`ci.md`) opens Stage 1.
