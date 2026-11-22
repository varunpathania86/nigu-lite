---
description: Read when editing Build Containers, CI scripts, Act orchestration, reports or local registry publication.
applyTo: '.github/build/**,scripts/ci/**,scripts/act/**,.github/workflows/**'
---
# CI and Build Containers

- The Workspace Container edits source and starts containers; it does not lint, test, scan, build or publish directly.
- Transfer an immutable Git tree: commit, isolated staged index or isolated worktree index.
- Never mount a live Workspace source read-write into a Build Container.
- Mount source as `/source` read-only; copy it to disposable `/workspace` for tools that require Git metadata.
- Write reports and artifact metadata only under `/output`.
- Build Containers are non-root, ephemeral and destroyed after the command.
- GitHub Actions and Act use the same Build Container image and Make targets.
- Workflow jobs call Make targets; expressions reach shell commands only through environment variables.
- Pin all Actions by commit SHA and give each job only the permissions it needs.
- `worktree` and `staged` results are non-production and cannot publish to GHCR or create a release lock.
- Act publishes only to the persistent local registry with `local-*` test identities.
- GHCR publication requires trusted `main` or `v*` GitHub context and keyless Cosign OIDC.
- Every workflow produces `report.md`, `report.html`, JSON fragments and retained raw evidence.
- Empty matrices are skipped with a report reason.
- Production registry artifacts are images or ORAS tenant packages signed and pinned by digest.
- Tenant packages never include `vault.yml`, secrets or files outside the allow-list.
- Reports and packages must not contain private signing keys, tokens or Vault contents.
- Add focused unit tests for every `scripts/ci/` or `scripts/act/` behavior change.
- Update `docs/lld/ci.md` and the relevant READMEs in the same PR.
- Run `make lint test-unit scan`; run Act for workflow or snapshot changes.
