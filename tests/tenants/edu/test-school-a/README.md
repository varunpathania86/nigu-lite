# Test School A (`test-school-a`)

> Product: edu · Apps: gibbon · Status: test-only

## Overview

```mermaid
flowchart LR
  U["Synthetic test user"] --> H["test-school-a.schooledu.in"]
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
| `test-school-a.schooledu.in` | Gibbon | Synthetic package fixture only |

## Contacts

| Role | Channel |
|---|---|
| Platform test team | Repository issue tracker |

## Placement and versions

Not selected by a production or local runtime manifest. The fixture uses the same schema as a real
school and is used only by CI package and planner tests.

## Assets and migrations

`assets/` contains synthetic branding. `migrations/0001-bootstrap.sql` creates one empty fixture table.

## Special notes

Synthetic data only. No children, staff or real school data is present.
