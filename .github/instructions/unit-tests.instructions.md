---
description: Read for any code change; how to write and maintain unit tests.
applyTo: 'tests/unit/**,scripts/**'
---
# Unit tests

- Every code change gets focused unit tests in the same PR.
- Location: `tests/unit/`, mirroring the code area (e.g. `tests/unit/test_git_rules.py` for `scripts/git_rules.py`).
- Use Python stdlib `unittest` for now; no extra test dependencies without an LLD decision.
- Run with `make test-unit`; CI runs it in `build.yml` → `quality` via `make ci-quality`.
- Name files `test_<module>.py` and methods `test_<behaviour>` describing the expected outcome.
- Test behaviour, not constants, defaults, re-exports or language features.
- Cover the edge cases the change introduces: valid input, each rejection path, boundaries.
- Write each case once; prefer table-driven cases with `subTest` over copy-paste.
- Scope: manifest and tenant validators, Jinja2 rendering (Compose, Caddyfile, Traefik routes, Cloudflare payloads), scripts, CI catalog/plan/report.
- Render templates with `tests/fixtures/dummy-secrets.yml`; never real secrets or Vault passwords.
- Use synthetic data only; test tenants live in `tests/tenants/`.
- Tests must be deterministic and offline: no network, Docker, SSH or wall-clock dependence.
- Use temporary directories inside the test (`tempfile`) and clean up; never write into the repo tree.
- When behaviour changes, update the affected tests in the same change; never delete a failing test to go green.
- A bug fix adds a test that fails without the fix.
- Keep tests fast; slow end-to-end checks belong in `tests/integration/` (`integration-tests.instructions.md`).
- Update `tests/README.md` when adding a new test area or runner.
