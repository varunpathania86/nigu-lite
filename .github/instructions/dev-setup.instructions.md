---
description: Read when a change needs a new tool, runtime or system package on developer machines (CLI, Docker, Node, minikube …).
applyTo: 'scripts/setup/**,.tool-versions'
---
# Developer machine setup

- Goal: after `git clone`, `make setup` is the only command; developers never install anything by hand.
- `make setup` runs `scripts/setup/setup.sh`, which runs every `scripts/setup/steps/NN-<name>.sh` in order.
- Docker Engine is the only Workspace-side build daemon; Act and local CI use it to create Build Containers.
- `make doctor` runs the same steps check-only and changes nothing; use it to diagnose a machine.
- Every new dependency ships with its setup in the same PR; code or a Make target needing an uninstalled tool is incomplete.
- Prefer, in order: a `.tool-versions` pin → another mise backend (`aqua:`, `pipx:`, `npm:`, `ubi:`) → a new step file.
- Add a step only for what mise cannot install: Docker Engine, OS packages, kernel modules, group membership.
- Act is pinned in `.tool-versions`; its project configuration may access the Docker socket only in orchestration scripts.
- A step defines `step_describe` (one line), `step_check` (read-only, exit 0 when ready) and `step_install`.
- Steps are idempotent: re-running `make setup` on a ready machine changes nothing and prints `ok` for each step.
- `step_check` verifies the real requirement (version, daemon running, group membership), not just a file.
- Number steps in tens (`60-docker.sh`); a step may rely only on lower-numbered steps.
- Pin a version (exact or minimum) in the step or `.tool-versions`; never install an unpinned "latest".
- Use `pkg_install`, `as_root` and `version_ge` from `scripts/setup/lib.sh`; support Ubuntu/Debian, Fedora, macOS, WSL2.
- Never require a manual prerequisite: bootstrap package managers too (`05-homebrew.sh` on macOS); only the `sudo` password is typed.
- Download only over HTTPS from the vendor, verifying a checksum or signature where one is published.
- If a manual action is unavoidable (e.g. log out after joining the `docker` group), print it from `step_install`.
- Never put secrets or tokens in setup; credentials come from Vault or the user's own login (`gh auth login`).
- Update `docs/developer/getting-started.md` and master-plan.md §7.3 when steps change.
- Test on a clean machine or container: `make doctor` fails, `make setup` passes, `make doctor` passes; note it in the PR.
- `make test-unit` covers the step runner (`tests/unit/test_setup.py`); extend it when the runner changes.
