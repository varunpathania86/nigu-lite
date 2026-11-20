---
description: Read when removing or retiring a feature, service, role, Make target, workflow or product.
---
# Removing a feature

- Use a `feature/` or `chore/` branch (`git.instructions.md`); state what is removed and why in the PR.
- Check which tenants and VPS manifests use the feature before removing it.
- Decide data handling first: final backup, export or deletion, and how long backups are retained.
- Take a `make tenant-snapshot VPS= ID=` for each affected tenant before destructive changes.
- Never delete tenant data silently; document deletion in "Risk, rollback & data impact" of the PR.
- Remove the role tasks, templates, `group_vars` block, Compose services and Traefik routes together.
- Remove published ports, firewall rules, DNS records and Authelia rules the feature needed.
- DNS records are only deleted by the retire playbook; `make dns-sync` just reports orphans.
- Remove or update unit, integration and access tests; keep tests that prove the removal (e.g. route now 404).
- Remove Make targets, scripts, CI catalog entries and `versions.yml` pins that only the feature used.
- Update `deployments/schema.json`, the validator and `docs/templates/` when manifest or tenant keys go away.
- Set the feature's LLD status to `retired` and add a changelog line; do not delete the LLD.
- Mark an ADR `superseded by NNNN` only if one exists, and only when the owner asks; never create one unprompted.
- Update every README that mentions the feature, and its mermaid diagram.
- Remove or update instruction files and the `AGENTS.md` index (`instructions-maintenance.instructions.md`).
- Run `make lint test-unit scan` (+ `test-integration` when deployable behaviour changes).
- Plan rollback: redeploying the previous `<vps>.lock.yml` plus a snapshot restore.
