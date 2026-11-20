---
status: proposed            # proposed | accepted | rejected | deprecated | superseded by NNNN
date: YYYY-MM-DD
decision-makers: <owner>
consulted: <people/AI tools asked>
informed: <who is told>
release: <release or sprint, e.g. v1.2 / 2027-S03>
supersedes: <NNNN or none>
---

# NNNN — <Short decision title as a statement, e.g. "Run each school in its own Gibbon container">

## Context and problem statement
<!-- 2–5 sentences: the situation, the forces, why decide now. Link the evidence (benchmark, incident, LLD). -->

## Decision drivers
- <driver, e.g. RAM per tenant ≤ 50 MB>
- <driver, e.g. no cross-school file access>

## Existing solution
<!-- How it works today. Required unless greenfield; then write "None". -->
```mermaid
flowchart LR
  A[Today: component] --> B[(Dependency)]
  class A app
  class B data
  classDef app fill:#bbdefb,stroke:#1565c0,color:#1a1a1a
  classDef data fill:#b2dfdb,stroke:#00695c,color:#1a1a1a
```

## Considered options
1. <Option 1 — chosen>
2. <Option 2>
3. <Do nothing>

## Decision outcome
Chosen: **<option>**, because <one-sentence justification tied to the drivers>.

### Proposed solution
```mermaid
flowchart LR
  A[Today: component] --> N["[+] New component"] --> B[(Dependency)]
  A -.-> X["[-] Old part"]:::removed
  linkStyle 0,1 stroke:#2e7d32,stroke-width:2px
  linkStyle 2 stroke:#9e9e9e,stroke-dasharray:5 4
  class A app
  class N core
  class B data
  style N stroke:#2e7d32,stroke-width:2.5px,stroke-dasharray:5 3
  classDef app fill:#bbdefb,stroke:#1565c0,color:#1a1a1a
  classDef core fill:#e1bee7,stroke:#6a1b9a,color:#1a1a1a
  classDef data fill:#b2dfdb,stroke:#00695c,color:#1a1a1a
  classDef removed fill:#f5f5f5,stroke:#9e9e9e,stroke-dasharray:5 4,color:#757575
```

### Consequences
- Good: <…>
- Bad / accepted trade-off: <…>
- Follow-up: <LLDs to create/update, migration, tenants affected>

### Confirmation
<!-- How we will know it is implemented and working: tests, benchmark, review, metric. -->

## Pros and cons of the options
### <Option 2>
- Good: <…>
- Bad: <…>

## More information
<!-- Links: LLDs, PRs, upstream docs, related ADRs. -->
