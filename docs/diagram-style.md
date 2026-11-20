# Diagram style

> Single source of the mermaid colours and styles (rules: master-plan.md §11.6).

GitHub cannot import styles from another file, so every diagram carries its own copy of the lines it
uses. Do not copy them by hand: write `class <ids> <class>`, `[+]` / `[-]` labels and `subgraph <id>`,
then run `make fix-docs`. It adds, corrects and removes the `classDef` lines, the subgraph `style`
lines and the green border `style` of added component nodes from the block below; `make check-docs`
reports anything left. Only `linkStyle` lines are written by hand (they need the link index).

To change a colour, edit only this block and run `make fix-docs`; the change needs an LLD note and is
listed under "Docs & instructions updated" in the PR.

```mermaid
flowchart LR
  subgraph STYLE["subgraph: transparent, grey border"]
    U[user]
    E[edge]
    A[app]
    C[core]
    D[(data)]
    T[tool]
    F[fail]
  end
  S[plain step] --> Q{decision}
  A -->|"added link"| NA["[+] added app node"]
  NA -->|"added link"| NS["[+] added untyped step"]:::new
  A -.->|"removed link"| X["[-] removed node"]:::removed
  linkStyle 1,2 stroke:#2e7d32,stroke-width:2px
  linkStyle 3 stroke:#9e9e9e,stroke-dasharray:5 4
  class U user
  class E edge
  class A,NA app
  class C core
  class D data
  class T tool
  class F fail
  style STYLE fill:transparent,stroke:#78909c,stroke-width:1.5px
  style NA stroke:#2e7d32,stroke-width:2.5px,stroke-dasharray:5 3
  classDef user fill:#eceff1,stroke:#455a64,color:#1a1a1a
  classDef edge fill:#ffe0b2,stroke:#e65100,color:#1a1a1a
  classDef app fill:#bbdefb,stroke:#1565c0,color:#1a1a1a
  classDef core fill:#e1bee7,stroke:#6a1b9a,color:#1a1a1a
  classDef data fill:#b2dfdb,stroke:#00695c,color:#1a1a1a
  classDef tool fill:#fff9c4,stroke:#f9a825,color:#1a1a1a
  classDef fail fill:#ffcdd2,stroke:#c62828,color:#1a1a1a
  classDef new fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,stroke-dasharray:5 3,color:#1a1a1a
  classDef removed fill:#f5f5f5,stroke:#9e9e9e,stroke-dasharray:5 4,color:#757575
```

| Class | Use for |
|---|---|
| `user` | People and external clients |
| `edge` | Traffic entry and network access: Cloudflare, Traefik, wg-portal, DNS records |
| `app` | Tenant-facing applications: Gibbon, ERPNext, tenant packages |
| `core` | Shared platform services (the `core/` product): LLDAP, Authelia, Beszel, DBX, backups |
| `data` | Data stores and registries: MariaDB, SQLite volumes, object store, GHCR |
| `tool` | Repo, CI and operator tooling: GitHub Actions, Ansible, Make targets, manifests |
| `fail` | Runtime failure, deny and rollback outcomes |
| Added component (`[+]` + its class) | Change diagrams only: keeps its component fill, green dashed border added by `make fix-docs` |
| `new` | Change diagrams only: added node that is no component (a plain step); label starts with `[+]` |
| `removed` | Change diagrams only: removed node, fully greyed out; label starts with `[-]` |
| Added link | `linkStyle <index> stroke:#2e7d32,stroke-width:2px` on a solid arrow |
| Removed link | `-.->` plus `linkStyle <index> stroke:#9e9e9e,stroke-dasharray:5 4` |
