---
description: Read when changing the Gibbon FrankenPHP image, php.ini, tenant-guard, health.php or Gibbon patches.
applyTo: 'edu/images/gibbon/**'
---
# FrankenPHP and Gibbon

- One FrankenPHP container per Gibbon version serves all schools; at most two versions per VPS (master-plan.md §5, §5.5).
- Download the pinned Gibbon release at image build with the checksum from `versions.yml`; never commit upstream code.
- Change upstream behaviour only through `patches/*.patch` plus config templates (master-plan.md §5.3).
- Keep every isolation control in master-plan.md §5.2: per-school DB user, Caddy path rules, global `php_ini`, `tenant-guard.php`, read-only code.
- Never relax `open_basedir`, `disable_functions`, `allow_url_include=Off` or `expose_php=Off` without an accepted ADR.
- `tenant-guard.php` may only tighten `open_basedir` and set a per-school `session.save_path`; never widen.
- Mount Gibbon code read-only; only `uploads/` and session dirs are writable, per school.
- Install modules and themes through image builds, never through the Gibbon admin UI.
- Caddy blocks `config.php`, dotfiles, `/installer`, and PHP in `uploads/`; static uploads are served without PHP.
- Send `Cache-Control: private, no-store` on every school response; no edge or origin caching.
- No ads, trackers or third-party scripts on any Gibbon surface (master-plan.md §10).
- `health.php` is ours, baked into the image, uses only that school's DB credentials and returns JSON (master-plan.md §5.4).
- Bound `memory_limit`, `max_execution_time`, upload sizes, `max_threads`, `max_requests` and container limits.
- Build with `make image-build PRODUCT=edu APP=gibbon`; Trivy must be clean or justified (`quality-scan.instructions.md`).
- Every change runs the isolation suite: school A cannot read school B files, DB or sessions.
- Benchmark runtime or thread changes (`benchmarks.instructions.md`); version bumps follow `upgrade.instructions.md`.
- Record design changes in `docs/lld/gibbon.md`.
