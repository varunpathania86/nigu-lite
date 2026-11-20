---
title: Getting started
type: how-to
owner: varunpathania86
updated: 2026-11-20
---

# Getting started

> For anyone (human or AI tool) making a first change to this repository.

## Prerequisites

- `git`, `make`, `docker` and [mise](https://mise.jdx.dev/) (`curl https://mise.run | sh`).
- Read [AGENTS.md](../../AGENTS.md); it indexes the rules for each kind of task.

## Steps

1. `make setup`: installs the pinned tools from `.tool-versions` and the `pre-commit` + `commit-msg` hooks.
2. Create a branch: `git switch -c feature/<short-slug>` (prefixes: `feature/`, `bugfix/`, `hotfix/`,
   `patch/`, `tenant/`, `docs/`, `chore/`).
3. For a feature, write or extend the LLD first (`docs/lld/<area>.md`).
4. Change code together with its tests and docs.
5. `make lint test-unit` (+ `make scan` for images or dependencies).
6. Commit with a plain sentence, e.g. `Added tenant manifest validator` (≤ 72 characters, no `feat:`
   prefix, no AI `Co-authored-by` trailers). The `commit-msg` hook checks this.
7. Open a PR from the template; it is squash-merged with the PR title as the commit message.

## Verify

`make lint test-unit` passes, and `make check-docs` reports nothing.

## Rollback / recovery

Nothing is deployable yet. Revert a commit with `git revert <sha>` on a branch and open a PR.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `mise: command not found` | mise not on `PATH` | Add `~/.local/bin` to `PATH`, then `eval "$(mise activate bash)"` |
| `commit-msg: No type prefixes…` | Conventional-commit style message | Rewrite as a plain sentence |
| `branch-name: Branch '…' must be…` | Branch prefix missing | `git branch -m feature/<slug>` |
| `check-docs: … is not indexed in AGENTS.md` | New instruction file | Add a row to the AGENTS.md index |

## Related

[master-plan.md](../../master-plan.md) §11 (AI instructions and docs), §12 (stages).
