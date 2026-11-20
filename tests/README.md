# tests

> Automated tests for the platform. Owner: varunpathania86 · Status: active (unit tests only)

## Overview

```mermaid
flowchart LR
  M["make test-unit"] --> U["tests/unit<br/>scripts, validators"]
  M2["make test-integration (S2+)"] --> I["tests/integration<br/>local VPS + test tenants"]
  M3["make bench (S4+)"] --> B["tests/benchmarks<br/>k6 scenarios"]
  class M,M2,M3 tool
  classDef tool fill:#fff9c4,stroke:#f9a825,color:#1a1a1a
```

## Quick start

`make test-unit`

## Structure

| Path | Purpose |
|---|---|
| `unit/` | Python `unittest` tests for `scripts/` (git rules, docs checks); later validators and template rendering |

`integration/`, `tenants/` and `benchmarks/` are added in the stages that need them (master-plan.md §9, §12).

## Configuration

None.

## Operations

Run in CI from Stage 1 (`build.yml` → `quality`).

## Tests

Each code change adds or updates focused tests here (`.github/instructions/unit-tests.instructions.md`).

## Related

master-plan.md §9 (testing strategy and benchmarks).
