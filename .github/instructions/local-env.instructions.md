---
description: Read when working on the local VPS simulator, deployments/local.yml or local test runs.
applyTo: 'local/**,deployments/local.yml'
---
# Local environment

- Design: master-plan.md §8; the simulator is `local/Dockerfile` (Ubuntu 24.04 + systemd + sshd + Docker).
- Use only Make targets: `make local-up`, `make local-deploy`, `make local-down`, `make local-reset`.
- Ansible reaches the simulator over SSH exactly as a real VPS; run the same playbooks, no local-only forks.
- Prefer the Sysbox runtime; fall back to `--privileged` with its own `/var/lib/docker` volume.
- Tag kernel, firewall, sysctl and swap tasks `host_kernel`; they are skipped locally.
- Need full fidelity? Use `make local-vm` (Multipass or libvirt).
- Docker Engine, Multipass and other host tools are installed by `make setup` steps (`dev-setup.instructions.md`).
- `deployments/local.yml` uses `tls.mode: selfsigned` and `dns.provider: none`; the Cloudflare role never runs locally.
- Local hostnames use `*.localhost` (or `*.lvh.me`/`nip.io` for tools), taken from the test tenants.
- `deployments/local.yml` selects only test tenants from `tests/tenants/`; synthetic data only.
- Object store is MinIO (`endpoint: http://minio:9000`), same `object_store` block as production, pinned by digest.
- Create the MinIO bucket via Ansible and the S3 API, not shell.
- wg-portal and LLDAP test users (`admin`, `ops`, `support`) run locally for access tests.
- Keep the simulator capped at ~8 GB RAM like the VPS.
- `make local-reset` wipes everything; tests must not depend on leftover state.
- Run `make test-integration`, `make restore-test` and before/after `make bench SCENARIO=` here.
- Local benchmarks are for comparison only, never acceptance.
- Update `local/README.md` when targets, ports or prerequisites change.
