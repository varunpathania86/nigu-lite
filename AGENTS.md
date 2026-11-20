# AGENTS.md — rules for AI tools (Copilot, Roo Code, others)

Platform plan: [master-plan.md](master-plan.md). This repo is **public** (AGPL-3.0).

## Always-on rules

1. The `Makefile` is the only entry point; complex commands live in `scripts/` or `<product>/scripts/`.
2. Never commit secrets (only Ansible Vault-encrypted `vault.yml`) or real personal/tenant data.
3. Infrastructure as code: Jinja2 templates and service APIs, no shell scripts in Ansible roles.
4. Ansible variables only in `group_vars`, grouped by role, no defaults (`ansible.instructions.md`).
5. Every change updates its tests and docs **in the same change** (READMEs, LLD, instructions).
6. Run `make lint test-unit` before finishing; add `make scan` for images and dependencies.
7. Never edit upstream Gibbon/ERPNext code; ship pinned releases plus patches.
8. Write an LLD before implementing a feature; **never create an ADR unprompted**, propose it in the PR.
9. Branches, commit messages and PR titles follow `git.instructions.md`; never add AI `Co-authored-by` trailers.
10. Never weaken a security or isolation rule without an approved ADR.
11. When a convention changes, update the matching instruction file and this index (`instructions-maintenance.instructions.md`).

## Index — read the file for your task

All files are in `.github/instructions/`.

| When you are… | Read |
|---|---|
| Editing Ansible roles, playbooks or group_vars | `ansible.instructions.md` |
| Editing Compose templates, Traefik routes or Caddyfiles | `compose-traefik.instructions.md` |
| Changing the Gibbon FrankenPHP image or its config | `frankenphp-gibbon.instructions.md` |
| Adding a feature, service or product type | `feature-add.instructions.md` |
| Removing a feature | `feature-remove.instructions.md` |
| Changing tenants, VPS manifests or tenant migrations | `tenant.instructions.md` |
| Changing any code (unit tests) | `unit-tests.instructions.md` |
| Changing deployable behaviour (integration tests) | `integration-tests.instructions.md` |
| Changing resources or runtime settings | `benchmarks.instructions.md` |
| Running or configuring lint, pre-commit, Trivy | `quality-scan.instructions.md` |
| Deciding which documentation a change needs | `docs.instructions.md` |
| Writing an LLD or proposing an ADR | `adr-lld.instructions.md` |
| Changing Cloudflare, Traefik middlewares, Authelia, wg-portal, DBX | `edge-access.instructions.md` |
| Creating or updating a README | `readme.instructions.md` |
| Naming a branch, writing a commit or PR | `git.instructions.md` |
| Upgrading Gibbon, ERPNext or images | `upgrade.instructions.md` |
| Changing publish workflows, images or tenant packages | `release-publish.instructions.md` |
| Editing `.github/workflows/*` or `scripts/ci/*` | `github-actions.instructions.md` |
| Handling secrets, ports, personal data or ads | `security.instructions.md` |
| Working on the local VPS simulator | `local-env.instructions.md` |
| Finishing a change that altered a convention | `instructions-maintenance.instructions.md` |

`make check-docs` verifies that this index matches the files.
