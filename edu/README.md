# edu

> GibbonEdu for many schools in one FrankenPHP container, one database per school.
> Owner: varunpathania86 · Status: experimental (planned for Stage 4)

## Overview

```mermaid
flowchart LR
  U["Staff, students, parents"] --> H["school-a.schooledu.in"] --> T[Traefik]
  T --> G["Gibbon · FrankenPHP<br/>one Caddy block per school"]
  G --> D[("MariaDB: one DB per school")]
  P["tenants/school-id/<br/>signed package"] --> G
  class U user
  class H,T edge
  class G,P app
  class D data
  classDef user fill:#eceff1,stroke:#455a64,color:#1a1a1a
  classDef edge fill:#ffe0b2,stroke:#e65100,color:#1a1a1a
  classDef app fill:#bbdefb,stroke:#1565c0,color:#1a1a1a
  classDef data fill:#b2dfdb,stroke:#00695c,color:#1a1a1a
```

## Quick start

Not deployable yet. From Stage 4: `make image-build PRODUCT=edu APP=gibbon`, `make tenant-new PRODUCT=edu ID=<id>`.

## Structure

Planned: `ansible/`, `images/gibbon/`, `scripts/`, `tenants/<school-id>/` (README, `tenant.yml`, `vault.yml`,
`assets/`, `migrations/`).

## Configuration

Schools are defined in `tenants/<id>/tenant.yml` and selected per VPS in `deployments/<vps>.yml`, each with
an explicit `gibbon_version`. School services are ad-free.

## Operations

See master-plan.md §5 (routing, isolation, health checks, Saturday upgrades and rollback).

## Tests

From Stage 4: isolation suite (cross-school file, DB and session access must fail), host routing, upgrade
and rollback drill, `edu-*` benchmarks.

## Related

[Baseline ADR](../docs/adr/0001-platform-baseline.md) (D7, D8) · master-plan.md §5, §7, §9.1
