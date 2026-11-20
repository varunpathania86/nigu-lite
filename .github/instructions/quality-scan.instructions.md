---
description: Read when changing lint, pre-commit, editorconfig, Trivy or IaC scan config, or when a lint/scan check fails.
applyTo: '.pre-commit-config.yaml,.editorconfig,.trivyignore,.yamllint.yml,policy/**'
---
# Quality and scanning

- Run `make lint` (pre-commit on all files + Ansible syntax checks) before every commit.
- Run `make scan` (Trivy fs, config, secret) before every PR; `scan-images` for built images.
- `make setup` installs hooks; tool versions come from `.tool-versions` only.
- Fix findings; do not suppress them, disable rules or lower severities to get green.
- `.trivyignore` entries need a comment with the reason and an expiry date; remove expired entries.
- Accepted IaC findings go in `policy/iac/accepted.yml` with reason + expiry (master-plan.md §7.5).
- Exclude only upstream or generated code (`**/vendor/`, `**/upstream/`); never exclude our own code.
- Inline `noqa`/`# shellcheck disable` only with a reason on the same line, and only where a fix is impossible.
- Follow `.editorconfig`: LF, final newline, no trailing whitespace, tabs in the Makefile.
- Linters: yamllint, ansible-lint, shellcheck, shfmt, hadolint, markdownlint-cli2, ruff, actionlint, zizmor.
- Blocking in CI: Trivy CRITICAL/HIGH with a fix available; advisory: `iac-security.yml` (`make iac-scan`).
- Secrets found by Trivy or push protection: rotate the secret first, then remove it; history is public.
- Pin new pre-commit hooks by version; Renovate updates them.
- Adding or swapping a linter is an LLD decision, not an ADR; update this file and `AGENTS.md` if the commands change.
- `make ci-quality` must pass locally exactly as in CI.
