# <Tenant display name> (`<tenant-id>`)
> Product: <erp|edu> · Apps: <gibbon|erpnext> · Status: <onboarding|active|retiring>

<!-- PUBLIC REPO: no personal names, phone numbers or e-mail addresses. Role-based contacts only;
     personal contact details live in vault.yml or outside the repository. -->

## Overview
```mermaid
flowchart LR
  U[Tenant users] --> H["<tenant-id>.<schooledu.in|erpos.in>"] --> A[App on vpsNN] --> D[(Tenant database)]
  class U user
  class H edge
  class A app
  class D data
  classDef user fill:#eceff1,stroke:#455a64,color:#1a1a1a
  classDef edge fill:#ffe0b2,stroke:#e65100,color:#1a1a1a
  classDef app fill:#bbdefb,stroke:#1565c0,color:#1a1a1a
  classDef data fill:#b2dfdb,stroke:#00695c,color:#1a1a1a
```

## Domains
| Hostname | App | Notes |
|---|---|---|
| `<tenant-id>.<domain>` | <app> | Cloudflare proxied CNAME → `vpsNN.nigu.in` |

## Contacts
| Role | Channel |
|---|---|
| <School office / Accounts team> | <ticket queue or shared role mailbox reference> |

## Placement and versions
<!-- Which deployments/<vps>.yml selects this tenant; pinned app version; canary or not. -->

## Assets and migrations
<!-- assets/: logo, header, CSS overrides. migrations/: NNNN-<summary>.sql|json, starting with 0001-bootstrap. -->

## Special notes
<!-- Agreed exceptions, custom domains (paid), data retention requests. -->
