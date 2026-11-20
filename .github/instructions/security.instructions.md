---
description: Read when touching secrets, ports, firewall, exposure, personal data, repo settings, supply chain or ads.
---
# Security

- The repo is PUBLIC (AGPL-3.0): everything committed, including history, is readable by anyone.
- No secrets in git except Ansible Vault-encrypted files (`vault.yml`); edit with `make vault-edit FILE=`.
- Vault password: long random (≥ 32 characters), never reused, never in git or CI.
- No personal data or real tenant data; synthetic data only in tests; tenant READMEs use role-based contacts.
- A leaked secret is rotated first, then removed; rewriting history does not un-leak it.
- Exposure (master-plan.md §13): public 443/80 only from Cloudflare ranges (`DOCKER-USER`), `51820/udp` for WireGuard.
- DB ports are never published; SSH only on `wg0` with keys, user `ops`, no root.
- Staff tools follow master-plan.md §13.1 and `edge-access.instructions.md`; tenant routers never use Authelia.
- Tenant isolation: DB + user per tenant, Frappe site isolation, Gibbon controls in master-plan.md §5.2.
- Supply chain: pin images by digest and actions by SHA; Trivy image/SBOM; verify cosign signatures at deploy.
- Signing is keyless cosign via GitHub OIDC; GHCR packages are public and contain no secrets.
- `main` ruleset from S1: PR + green Build, squash only, no force push or deletion.
- Fork PRs never get secrets; never use `pull_request_target` with a checkout of PR code.
- Ads: no ads on Gibbon or any school surface; ERP ads only after the S7 review, never on tenant-data pages (master-plan.md §10).
- No behavioural, age or role targeting; never send tenant or student data to advertisers.
- Never weaken a security rule or isolation control without an accepted ADR; propose it in the PR.
- Report vulnerabilities privately per `SECURITY.md`; never in public issues.
- Run `make scan` (Trivy secret/fs/config) before every PR.
