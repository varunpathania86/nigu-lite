---
description: Read when changing deployable behaviour (roles, templates, images, routing, access, backups) or integration tests.
applyTo: 'tests/integration/**'
---
# Integration tests

- Location: `tests/integration/` (pytest + httpx, optional Playwright for UI smoke).
- Run against the local simulator only: `make local-up local-deploy`, then `make test-integration` (master-plan.md §8).
- Use the test tenants in `tests/tenants/` (two per product) with synthetic data; never real tenants.
- Every deployable change adds or updates a case: health, routing, login, isolation, backup → restore.
- Isolation: school A must not read school B files, DB or sessions; same for ERP sites.
- Health: one unhealthy test school must not affect the other; `/_health` is never public.
- Access matrix changes (master-plan.md §13.1) update the table-driven cases in `tests/integration/access/`.
- Regression: a fixed deployable bug gets a case that fails without the fix.
- Migrations: apply every test-tenant migration on a fresh DB and on one upgraded from the previous version.
- Upgrades use `tests/integration/upgrade/` via `make upgrade-test` (`upgrade.instructions.md`).
- Talk to the object store only through the S3 API (MinIO locally).
- Tests must be idempotent and leave the simulator reusable; `make local-reset` wipes everything.
- CI runs `integration.yml` on merge to `main` and manually, not on PRs.
- So paste the local `make test-integration` result in the PR "Tests" section.
- A failed post-merge run blocks the next `make deploy`; fix forward on a `bugfix/` branch.
- Keep fast logic checks in `tests/unit/`; integration tests cover cross-service behaviour only.
- Update `tests/README.md` when adding a new suite or fixture.
