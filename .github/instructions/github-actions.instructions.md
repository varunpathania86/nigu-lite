---
description: Read when editing GitHub Actions workflows or the CI scripts they call.
applyTo: '.github/workflows/**,scripts/ci/**'
---
# GitHub Actions

- Design and job tables: master-plan.md §7.5; publish specifics: `release-publish.instructions.md`.
- Every workflow follows catalog → plan → matrix of work → report.
- GitHub and Act run source through the same disposable Build Container contract (`ci-build.instructions.md`).
- Catalog and plan come from `scripts/ci/catalog.py` and `scripts/ci/plan.py`, same as `make ci-catalog` / `make ci-plan BASE=`.
- Jobs call `make` targets only (`ci-module`, `ci-quality`, `ci-report`); no inline tool commands.
- Pass expressions to `run:` only through `env:` (script injection, zizmor).
- Pin every action by commit SHA with a version comment; Renovate keeps them current.
- Declare `permissions:` per job, read-only by default; `security-events: write` only on the report job that uploads SARIF.
- Set `timeout-minutes` on every job; PR runs use `cancel-in-progress: true`, Publish uses `false`.
- An empty matrix skips the job; independent legs use bounded `max-parallel` with `fail-fast: false`.
- Each job writes `report/<job>[-<leg>].json` and `.md`; the `report` job runs `if: always()` and builds `report.md` + `report.html`.
- Keep SARIF upload for persistent code scanning; Reviewdog consumes the same SARIF for PR review comments.
- Reviewdog publishes `github-pr-check` and `github-pr-review`; a sticky PR summary remains visible even when SARIF has no findings.
- Reviewdog is non-blocking (`fail-level=none`); Trivy's original exit code remains the blocking security gate.
- Dependency Review posts CVE and licence changes on same-repository PRs.
- Static DevSecOps reports deploy only for `main` and tags to `gh-pages` subfolders; feature branches never publish Pages.
- Upload `<workflow>-report-<run_number>` (14 days); `part-*` fragments keep 1 day.
- Blocking: `build.yml`, `publish.yml`, `integration.yml`; advisory: `iac-security.yml` (findings never fail it).
- Use `pull_request`; never `pull_request_target` with a checkout of PR code.
- Fork PRs get a read-only token and no secrets; Publish and Integration never run on fork code.
- CI never has the Vault password; rendering uses `tests/fixtures/dummy-secrets.yml`.
- Readable names: `Build module · gibbon`; scheduled/manual runs set `run-name`.
- Add unit tests for `scripts/ci/` changes; run `make lint` (actionlint, zizmor) before committing.
- Promoting an advisory rule to blocking updates `docs/lld/ci.md`.
