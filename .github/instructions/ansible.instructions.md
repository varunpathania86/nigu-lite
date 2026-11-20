---
description: Read when editing Ansible roles, playbooks, group_vars, inventories, ansible.cfg or requirements.yml.
applyTo: '**/ansible/**'
---
# Ansible

- Run playbooks only through Make targets (`make deploy VPS=`, `make local-deploy`); never call `ansible-playbook` directly in docs or CI.
- Put complex logic in `scripts/` or `<product>/scripts/`, not in the Makefile.
- Define every variable only in `group_vars`; never in role `defaults/` or `vars/`, playbooks or tasks.
- Group variables by role with a `# --- Role: <name> ---` comment; image names, versions and ports first in each group.
- No default values (`| default(...)`, role defaults); a missing variable must fail the run.
- Image and artifact pins come from `versions.yml`, CLI tool pins from `.tool-versions`.
- Secrets only as Ansible Vault values (`vault_*`), edited with `make vault-edit FILE=`.
- Keep tasks deterministic: minimise `when:`/if-else on variables; prefer explicit values and linear flows.
- Use Jinja2 templates for every config file (YAML, JSON, TOML, INI, Caddyfile, Traefik routes, ldif, Compose).
- If templates are not enough, use the service API (`ansible.builtin.uri`, `community.*` modules); never `shell`/`command` in roles.
- Tasks must be idempotent: a second run reports no changes; use `changed_when`/`creates` only where a module cannot.
- Put generic host dependencies (Python, packages Ansible needs) in a separate `pre_tasks.yml` included by the playbook, not in roles.
- Tag kernel/firewall/sysctl/swap tasks `host_kernel` so the local simulator can skip them (master-plan.md §8).
- Pull external roles and collections via `requirements.yml`; keep them gitignored (e.g. `ansible/**/geerlingguy.*/`).
- Update `requirements.yml` whenever you add an Ansible dependency; pin versions.
- When paths or roles move, update each affected playbook's `ansible.cfg` (`roles_path`, `collections_path`) and `requirements.yml`.
- Validate manifests before any remote task; deploys require `VPS=` (master-plan.md §7.1).
- Add or update Jinja2 render tests in `tests/unit/` for every template change (see `unit-tests.instructions.md`).
- Run `make lint test-unit` (ansible-lint, yamllint, syntax check) before committing.
