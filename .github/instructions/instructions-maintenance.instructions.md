---
description: Read after any change that adds, removes or alters a tool, directory, Make target, product type or convention.
applyTo: '.github/instructions/**,AGENTS.md'
---
# Maintaining instructions

- Update instructions in the same PR when (master-plan.md §11.2):
  - a tool, directory, Make target, product type or convention is introduced or removed;
  - an instruction turned out wrong, missing or contradicted by the code;
  - the same review comment appears twice.
- Edit the smallest relevant file; do not duplicate a rule across files, link instead.
- Keep every `*.instructions.md` between 20 and 30 lines including front matter; split or merge when outside.
- Front matter: `description:` (when to read the file) and `applyTo:` only where a file glob fits.
- Write terse imperative bullets; no mermaid diagrams; link master-plan.md sections for detail.
- Use paths, Make targets and names exactly as they exist in the repo.
- Update the `AGENTS.md` index when adding, renaming or removing a file; keep `AGENTS.md` ≤ 60 lines.
- `make check-docs` validates the index, line counts, front matter, templates and mermaid blocks.
- Never weaken a security rule without an accepted ADR.
- When code and an instruction disagree, fix whichever is wrong in the same PR.
- Keep `.github/instructions/` the single source; nothing large in `.roo/rules/` (loaded on every request).
- List every instruction change under "Docs & instructions updated" in the PR.
- Use a `docs/` branch for instruction-only changes (`git.instructions.md`).
- Run `make check-docs lint` before committing.
