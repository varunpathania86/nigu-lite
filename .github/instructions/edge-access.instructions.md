---
description: Read when changing Cloudflare records/settings/cache rules, Traefik middlewares, Authelia rules, LLDAP groups, wg-portal or DBX/Dozzle exposure.
applyTo: 'core/ansible/roles/edge/**,core/ansible/roles/identity/**,core/ansible/roles/cloudflare/**'
---
# Edge and staff access

- Source of truth: master-plan.md §3.3 (routing), §3.4 (Cloudflare), §4.2 (DBX), §4.3 (identity), §13.1 (access matrix).
- Tenant routers (`<company>.erpos.in`, `<school>.schooledu.in`) never get Authelia; tenants use native login only.
- Staff tools live only on `nigu.in` hosts; never add a staff tool on `erpos.in` or `schooledu.in` without an LLD.
- `dbx`/`logs` middleware order is fixed: `vpn-only → authelia → dbx-trusted-auth → secure-headers`.
- `vpn-only` uses `ipAllowList` without `ipStrategy` (checks the TCP peer); DBX and Dozzle publish no port.
- `dbx-trusted-auth` overwrites `X-DBX-Auth` with the Vault secret; the rendered route file is `0600`.
- `dbx`/`logs` are DNS-only `A` records to `10.10.0.1`; never proxy them through Cloudflare.
- The node record `vpsNN.nigu.in` is DNS-only; WireGuard `51820/udp` is never proxied.
- Tenant hostnames are one proxied `CNAME` each to the node record; keep them one level deep.
- Authelia keeps `default_policy: deny` and `two_factor` for every staff rule; `support` is denied `vpn` and `dbx`.
- wg-portal logins go through the OIDC policy `vpn_admin_ops` (groups `admin`, `ops` only).
- Cloudflare tokens are least privilege, one purpose each (`cf_dns_token`, `cf_zone_token`, `cf_acme_token`), in Vault.
- Cache rules: allow-list ERPNext `/assets/*` only; bypass `/private/*`, `/api/*`, `/app*` and all school hosts.
- Origin lockdown: 443/80 only from Cloudflare ranges in `DOCKER-USER`; SSH only on `wg0`.
- Manage Cloudflare via the role (`make dns-sync VPS=`, `make cdn-purge VPS=`); no manual dashboard edits; no silent pruning.
- Any matrix change updates `tests/integration/access/` and is verified with `make access-check VPS=`.
- Never weaken an access rule without an accepted ADR (`security.instructions.md`).
