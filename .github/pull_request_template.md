## Summary

<!-- What and why. Link the issue and the stage (master-plan.md §12) if any. -->

## Change diagram

<!-- Required for architecture, deployment or data-flow changes; optional otherwise. ≤ 10 nodes.
Replace the example. Added node: "[+]" label + its component class (`make fix-docs` adds the green
dashed border); untyped added step: :::new. Removed node: "[-]" label + :::removed. Links are counted
from 0: added links get the green linkStyle, removed links are -.-> with the grey linkStyle.
Write only `class` and `linkStyle` lines; `make fix-docs` adds the rest (master-plan.md §11.6). -->

```mermaid
flowchart LR
  U[Platform staff] --> T[Traefik]
  T --> N["[+] Authelia forwardAuth"] --> D[(LLDAP)]
  T -.-> O["[-] Basic auth file"]:::removed
  linkStyle 1,2 stroke:#2e7d32,stroke-width:2px
  linkStyle 3 stroke:#9e9e9e,stroke-dasharray:5 4
  class U user
  class T edge
  class N core
  class D data
  style N stroke:#2e7d32,stroke-width:2.5px,stroke-dasharray:5 3
  classDef user fill:#eceff1,stroke:#455a64,color:#1a1a1a
  classDef edge fill:#ffe0b2,stroke:#e65100,color:#1a1a1a
  classDef core fill:#e1bee7,stroke:#6a1b9a,color:#1a1a1a
  classDef data fill:#b2dfdb,stroke:#00695c,color:#1a1a1a
  classDef removed fill:#f5f5f5,stroke:#9e9e9e,stroke-dasharray:5 4,color:#757575
```

## Changes

- **core:**
- **erp:**
- **edu:**
- **repo / CI / docs:**

## Tests

<!-- Commands run and new/updated tests; benchmark result links if resources changed. -->

- [ ] `make lint test-unit`
- [ ] `make scan` (images or dependencies changed)
- [ ] `make test-integration` (deployable behaviour changed)

## Docs & instructions updated

- LLD: <!-- docs/lld/<area>.md — required for features -->
- READMEs:
- `.github/instructions/*` / `AGENTS.md`:
- ADR proposed: <!-- only if master-plan.md §11.3 criteria apply; otherwise "No" -->

## Risk, rollback & data impact

<!-- Tenants affected, migrations, backup/restore notes, rollback steps. -->

## Checklist

- [ ] No secrets (except Vault-encrypted files) and no real personal or tenant data
- [ ] Upstream Gibbon/ERPNext code untouched (patches only)
- [ ] Trivy clean, or findings justified in `.trivyignore` with reason + expiry
- [ ] PR title is a plain sentence (≤ 72 characters, no `feat:` prefix)
