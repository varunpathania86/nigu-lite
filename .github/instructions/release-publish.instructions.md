---
description: Read when changing image builds, publish workflows, tenant packages, signing, VPS lock files or GHCR settings.
applyTo: '.github/workflows/publish.yml,deployments/*.lock.yml,**/images/**'
---
# Release and publish

- Source of truth: master-plan.md §7.4 (artifacts, signing, ruleset) and §7.5 (`publish.yml` jobs).
- PRs build and scan only; merge to `main` pushes `sha-<commit>` tags; tag `vX.Y.Z` creates a release.
- Image tags: `<upstream-version>-<build>` and `sha-<commit>`; deploys always pin by digest.
- Tenant packages contain only `tenant.yml`, `README.md`, `assets/`, `migrations/`; never `vault.yml` or other secrets.
- Package dry runs enforce the content allow-list, secret scan and size limit (`make tenant-package PRODUCT= ID=`).
- Push tenant packages as OCI artifacts with ORAS to `ghcr.io/<owner>/nigu-lite/tenants/<product>/<id>`.
- Sign every image and package with keyless cosign (GitHub Actions OIDC); no signing keys to store.
- Deploy verifies signatures against the `publish.yml` identity on `main` or a `v*` tag.
- Attach a CycloneDX SBOM to every image; Trivy gate before push.
- `lock-vps` resolves digests into `<vps>.lock.yml`; `make deploy VPS=` commits it to `deployments/`.
- Never hand-edit lock files; rollback is redeploying an older lock.
- GHCR packages are public and linked to the repo; VPSs pull anonymously, no registry tokens on servers.
- Third-party images are not rebuilt; pin them by digest in `versions.yml`.
- Only `publish-*` jobs get `packages: write`; only `release` gets `contents: write`.
- One Publish at a time (`cancel-in-progress: false`); never run Publish on fork code.
- Release notes come from PR titles, so titles follow `git.instructions.md`.
- Workflow mechanics: `github-actions.instructions.md`.
