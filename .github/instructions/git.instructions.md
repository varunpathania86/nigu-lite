---
description: Read when creating a branch, writing a commit message, or opening a pull request.
---
# Git, commits and PRs

- Branch: `<prefix>/<lowercase-slug>`, optionally with an issue number (`feature/42-tenant-manifest`).
- Prefixes: `feature/`, `bugfix/`, `hotfix/`, `patch/`, `tenant/`, `docs/`, `chore/`; `main` is the only other allowed name.
- Use per master-plan.md §11.5: `patch/` for upstream bumps and patches (Renovate), `tenant/` for tenant changes, `docs/` for docs/instructions only.
- Commit subject and PR title: plain sentence, capital first letter, ≤ 72 characters, no trailing period.
- No type prefixes or scopes (`feat:`, `(feat)`, `fix(edu):`).
- Optional stage prefix while executing master-plan.md §12: `Stage 1 - Added CI scanning manifests and unit tests structure`.
- Leave a blank line between subject and body; the optional body says why and which tenants are affected.
- NEVER add `Co-authored-by` trailers for AI tools (Copilot, Roo Code, etc.); human co-authors are fine.
- Enforced by `scripts/hooks/commit_msg.py` and `scripts/hooks/branch_name.py`; rules live in `scripts/git_rules.py`.
- Never bypass hooks (`--no-verify`); CI re-checks PR title, branch and commits in `make ci-quality`.
- `main` ruleset (from S1): PR required, green Build, squash merge only, no force push or deletion.
- Keep history small: one squash-merged PR per stage where practical; the PR title becomes the commit.
- Open PRs from `.github/pull_request_template.md` and fill every section.
- Add a mermaid change diagram (≤ 10 nodes) for architecture, deployment or data-flow changes; mark it as in `adr-lld.instructions.md`.
- "Tests": list commands run (`make lint test-unit scan test-integration`) and benchmark links.
- "Docs & instructions updated": LLD link (required for features), READMEs, instruction files, "ADR proposed" if any.
- "Risk, rollback & data impact": tenants affected, backup/restore notes.
- Never commit secrets, real data or upstream code; `hotfix/` still needs CI and a PR.
