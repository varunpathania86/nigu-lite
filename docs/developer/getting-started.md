---
title: Getting started
type: how-to
owner: varunpathania86
updated: 2026-11-23
---

# Getting started

> For anyone (human or AI tool) making a first change to this repository.

## Prerequisites

- `git` and `make` to clone and start; `make setup` installs everything else (Ubuntu/Debian, Fedora,
  macOS, or Windows via WSL2). If `make` is missing, run `bash scripts/setup/setup.sh`. On macOS it
  also installs Homebrew and the Xcode Command Line Tools; your password is asked once for `sudo`.
- Read [AGENTS.md](../../AGENTS.md); it indexes the rules for each kind of task.

## Steps

1. `make setup`: installs Homebrew (macOS only), OS packages, Docker Engine, Act,
   [mise](https://mise.jdx.dev/), mise shell activation, the pinned tools from `.tool-versions` and
   the `pre-commit` + `commit-msg`
   hooks. Safe to re-run; open a new terminal afterwards. `make doctor` shows what is missing
   without changing anything.
2. Create a branch: `git switch -c feature/<short-slug>` (prefixes: `feature/`, `bugfix/`, `hotfix/`,
   `patch/`, `tenant/`, `docs/`, `chore/`).
3. For a feature, write or extend the LLD first (`docs/lld/<area>.md`).
4. Change code together with its tests and docs.
5. `make lint test-unit` (+ `make scan` for images or dependencies). These commands create
   disposable Build Containers; the Workspace Container does not perform the build work.
6. For local delivery work, run `make local-up local-deploy test-integration`. Expect
   `https://test-school-a.localhost:8443` to return the Nginx welcome page and Garage to be healthy.
7. Commit with a plain sentence, e.g. `Added tenant manifest validator` (≤ 72 characters, no `feat:`
   prefix, no AI `Co-authored-by` trailers). The `commit-msg` hook checks this.
8. Open a PR from the template; it is squash-merged with the PR title as the commit message.

## Verify

`make lint test-unit` passes, `make test-integration` passes against a running simulator, and
`make check-docs` reports nothing.

## Rollback / recovery

For Stage 2 state, `make local-down` retains data and `make local-reset` removes only local simulator
state. Production deployment remains out of scope. Revert code with `git revert <sha>` on a branch.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `mise: command not found` | Terminal opened before `make setup` | Open a new terminal (or `source ~/.bashrc`); `make doctor` |
| `make setup` stops at a step | That dependency could not be installed | Fix the printed error, re-run `make setup` (finished steps are skipped) |
| `commit-msg: No type prefixes…` | Conventional-commit style message | Rewrite as a plain sentence |
| `branch-name: Branch '…' must be…` | Branch prefix missing | `git branch -m feature/<slug>` |
| `check-docs: … is not indexed in AGENTS.md` | New instruction file | Add a row to the AGENTS.md index |
| `check-docs: … has no classDef` / `classDef … must be` | Diagram styles missing or hand-edited | `make fix-docs` (styles come from `docs/diagram-style.md`) |
| `make act-build` cannot create containers | Docker Engine is unavailable | `make doctor`, then re-run `make setup` |
| `make local-up` cannot reach SSH | Stale local image, key or host key | Run `make local-reset` and start again |
| Local CI published a stale artifact | The snapshot mode included the wrong source | Choose `MODE=commit`, `staged`, or `worktree` explicitly |

Act accepts unpushed feature work. `MODE=commit` archives feature-branch `HEAD`, `MODE=staged` uses the
Git index and `MODE=worktree` adds unstaged/untracked files through a temporary index. The original
index is never changed.

## Related

[master-plan.md](../../master-plan.md) §11 (AI instructions and docs), §12 (stages).
