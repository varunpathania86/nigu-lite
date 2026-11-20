---
description: Read when a change affects resources, runtime, capacity or performance, or when editing benchmark scenarios.
applyTo: 'tests/benchmarks/**'
---
# Benchmarks

- Benchmark before and after any change to runtime, threads, workers, limits, caches or image versions.
- Scenarios live in `tests/benchmarks/scenarios/` (k6): `edu-*`, `erp-*`, `capacity-10x10`, `stress-10x10`.
- Generate data with `make bench-tenants` (synthetic, never committed); run with `make bench SCENARIO=`.
- Each run: 5 min ramp-up, 15 min steady, 2 min ramp-down (master-plan.md §9.1).
- Store results as `tests/benchmarks/results/<YYYY-MM-DD>-<scenario>.json` (raw k6 + resource snapshot) and `.md`.
- The `.md` states environment, commit, versions, key numbers, comparison to the previous run and to the targets, and a conclusion.
- Always compare with the previous result of the same scenario; link both in the PR "Tests" section.
- Targets are in master-plan.md §9.1 until calibrated, then in `docs/lld/capacity.md`.
- Change targets only through `docs/lld/capacity.md` with benchmark evidence in the PR.
- Local simulator runs are for before/after comparison only, never acceptance.
- Acceptance runs hit the origin over WireGuard with the tenant `Host` header, k6 on a separate machine.
- `capacity-10x10` gates a VPS's 10th tenant of a product; both 10x10 scenarios run before real tenants (S6).
- Missing a target: tune first, then lower the per-VPS limit (LLD + validator) or scale out.
- Changing the 10 + 10 model itself needs an ADR; propose it, never create it.
- Never benchmark against real tenants or through Cloudflare.
