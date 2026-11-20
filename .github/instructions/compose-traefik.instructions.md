---
description: Read when editing Compose templates, Traefik static/dynamic routes or middlewares, or Caddyfile templates.
applyTo: '**/ansible/roles/**/templates/**'
---
# Compose, Traefik and Caddy

- Write Compose files, Traefik routes and Caddyfiles as Jinja2 templates in the owning role; no hand-edited files on hosts.
- Deploy Compose with `community.docker.docker_compose_v2`; no `docker compose` shell calls.
- Pin every image by digest from `versions.yml`; never use `latest` or floating tags.
- Every service needs `mem_limit`, `cpus`, a `healthcheck` and a restart policy.
- Publish no ports except Traefik 443/80 and WireGuard `51820/udp`; DB, admin UIs and apps stay on internal networks.
- Traefik uses the file provider only: one explicit `Host(...)` router per tenant hostname; no Docker labels, no catch-all or default-tenant route.
- Every router has TLS (`tls: {}`, VPS wildcard per `tls.mode`) and the `secure-headers` middleware.
- Tenant routers (`*.erpos.in`, `*.schooledu.in`) never get Authelia or any staff middleware (master-plan.md §13.1).
- `dbx`/`logs` routers keep the order `vpn-only → authelia → dbx-trusted-auth`; see `edge-access.instructions.md`.
- Trust `X-Forwarded-*` only from Cloudflare ranges (`forwardedHeaders.trustedIPs`) at the entrypoint.
- One Traefik service per school with `healthCheck.path=/_health` and the school hostname (master-plan.md §5.4).
- Never route `/_health` or `/_health/*` publicly; Caddy allows them only from the Docker network.
- Caddy: `auto_https off`, plain HTTP `:8080` internal only, one site block per school in `Caddyfile.d/<school>.caddyfile`.
- Keep the container health site (`:8081`) free of PHP and DB access.
- Rendered files holding secrets (e.g. `dbx.yml`) are mode `0600`; secrets come from Vault.
- Add render tests in `tests/unit/` and check rendered config with `make iac-scan` (advisory, master-plan.md §7.5).
- Changing routing or exposure also updates `tests/integration/` cases and the relevant LLD.
