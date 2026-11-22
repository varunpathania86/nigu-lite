# Test Company B (`test-company-b`)

> Product: erp · Apps: erpnext · Status: test-only

## Overview

```mermaid
flowchart LR
  U["Synthetic test user"] --> H["test-company-b.erpos.in"]
  H --> P["Tenant package fixture"]
  P --> V["Validator and CI planner"]
  class U user
  class H edge
  class P app
  class V tool
  classDef user fill:#eceff1,stroke:#455a64,color:#1a1a1a
  classDef edge fill:#ffe0b2,stroke:#e65100,color:#1a1a1a
  classDef app fill:#bbdefb,stroke:#1565c0,color:#1a1a1a
  classDef tool fill:#fff9c4,stroke:#f9a825,color:#1a1a1a
```

## Domains

| Hostname | App | Notes |
|---|---|---|
| `test-company-b.erpos.in` | ERPNext | Synthetic package fixture only |

## Contacts

| Role | Channel |
|---|---|
| Platform test team | Repository issue tracker |

## Placement and versions

Not selected by a production or local runtime manifest. This second ERP tenant supports path-planning
and duplicate-placement test cases.

## Assets and migrations

`assets/` contains synthetic branding. `migrations/0001-bootstrap.json` contains no customer data.

## Special notes

Synthetic data only. This tenant is never deployed to a runtime.
