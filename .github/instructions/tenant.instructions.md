---
description: Read when onboarding, changing or retiring a tenant, editing VPS manifests, or writing tenant migrations.
applyTo: '**/tenants/**,deployments/**'
---
# Tenants and VPS manifests

- Use a `tenant/` branch; scaffold with `make tenant-new PRODUCT= ID=` from `docs/templates/tenant/`.
- Manifests select (`deployments/<vps>.yml`), `tenants/<id>/tenant.yml` defines; see master-plan.md §7.1, §7.2.
- New VPS manifests start from `docs/templates/vps-manifest.template.yml`; set `tls.mode` explicitly.
- Respect validator rules: unique placement, reserved IDs (master-plan.md §3.3), ≤ 10 tenants per product per VPS.
- Every school states `gibbon_version` (must exist in `versions.yml`); exactly one `canary` school per VPS.
- Production needs `tls.mode: letsencrypt` and `dns.provider: cloudflare`; exactly one `control_plane: true`.
- Tenant README: role-based contacts only (e.g. "school office"); no personal names, phones or e-mails.
- Never commit real personal data, production exports or uploads; the repo and packages are public.
- `vault.yml` must be Vault-encrypted and never enters tenant packages.
- `assets/` holds static files only (logo, header, CSS overrides).
- Migrations: add a new numbered file `migrations/NNNN-<summary>.sql` (edu) or `.json` (erp).
- Never edit an applied migration; a changed checksum fails validation, so write a new one.
- Include a version guard (`-- requires: gibbon >= x` or `"requires": {"erpnext": ">= x"}`).
- Forward-only: no down scripts; rollback is restoring the pre-migration snapshot.
- Use synthetic or tenant-approved reference data only; `sqlfluff` must pass.
- Test on `tests/tenants/` test tenants first (`make local-deploy`); preview with `make tenant-migrate VPS= ID= CHECK=1`.
- Schema changes update `deployments/schema.json`, the validator, templates and `tests/unit/`.
- Retiring a tenant: final snapshot, retire playbook removes DNS records; update the tenant README.
