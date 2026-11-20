---
description: Read when adding a feature, service, role, Make target, workflow or product type.
---
# Adding a feature

- Start on a `feature/` branch (`git.instructions.md`).
- Write or extend the LLD first: `docs/lld/<area>.md` from `docs/templates/LLD.template.md`.
- Reuse an existing LLD when the area already has one; one LLD usually spans several PRs.
- The LLD must be `approved` by the owner before implementation code is merged.
- Record moderate decisions (library, config layout, Make target, CI job, tenant field) in the LLD "Decisions" section.
- Never create an ADR unprompted; if master-plan.md §11.3 criteria apply, write "ADR proposed: …" in the PR.
- Expose new operations only as Make targets; put logic in `scripts/` or `<product>/scripts/`.
- Follow the domain rules: `ansible`, `compose-traefik`, `tenant`, `security` and `edge-access` instruction files.
- New manifest or tenant keys: update `deployments/schema.json`, the validator, templates in `docs/templates/` and unit tests.
- Add focused unit tests (`unit-tests.instructions.md`) and integration cases for deployable behaviour.
- Run a benchmark if the feature changes resources or runtime (`benchmarks.instructions.md`).
- Create or update the README of every touched product/folder (`readme.instructions.md`).
- New tools, directories, targets or conventions update the instructions and `AGENTS.md` index in the same PR.
- New developer dependencies (CLI, Docker, Node …) get a `make setup` step in the same PR (`dev-setup.instructions.md`).
- New images or packages follow `release-publish.instructions.md`; new workflows follow `github-actions.instructions.md`.
- Never add ads to Gibbon or tenant-data surfaces; never expose new ports publicly without review.
- Run `make lint test-unit scan` (+ `test-integration`, `bench` when relevant) before opening the PR.
- Fill every PR template section; include a mermaid change diagram for architecture or data-flow changes.
- Update the LLD changelog with the PR and set it to `implemented` when the last PR merges.
