---
description: Read when bumping Gibbon, ERPNext, India Compliance, FrankenPHP/PHP or any image or tool version.
applyTo: 'versions.yml,.tool-versions'
---
# Upgrades

- Work on a `patch/` branch (e.g. `patch/gibbon-<new>`); Renovate uses the same prefix.
- Follow master-plan.md §5.5 step by step; never skip the rehearsal or the rollback drill.
- Bump `versions.yml` (version + checksum or digest); CLI tools in `.tool-versions` only.
- Rebase `patches/`; read the upstream changelog for DB, PHP and config changes.
- Record behaviour changes in the upgrade report and update `docs/lld/gibbon.md` (or the product LLD).
- Version upgrades are never ADRs.
- Rehearse locally on test tenants: `make upgrade-test PRODUCT= APP= FROM= TO=`.
- The rehearsal runs: deploy old with seed data → snapshot → new → DB update → integration, isolation, health → benchmark → rollback drill.
- Attach the upgrade report and benchmark results (`benchmarks.instructions.md`) to the PR.
- Production: Saturdays, one VPS + product at a time with `make upgrade VPS= PRODUCT=`.
- Snapshot every tenant first (`make tenant-snapshot`, restic tag `pre-<new>`); maintenance on during DB updates.
- Gibbon: canary school (`canary: true`) first, healthy 30–60 min, then waves; ≤ 2 versions per VPS.
- Rollback: set the old version in the manifest, deploy, `make tenant-restore VPS= ID= SNAPSHOT=pre-<new>`, pass `/_health`.
- Rollback window ends Sunday 18:00 IST; after that fix forward on a `hotfix/` branch.
- ERPNext: one bench, maintenance window, per-site `bench backup`; upgrade only when India Compliance supports the target.
- Product DB updates run first, then pending tenant migrations that require the new version.
- Remove the old container only after the rollback window, when no tenant references the old version.
- Images must pass Trivy and be signed before any deploy (`release-publish.instructions.md`).
