# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Use GitHub's private reporting instead:
**Security → Report a vulnerability** on this repository.

Include the affected component (`core`, `erp`, `edu`, CI), steps to reproduce and the impact.
You will get an acknowledgement within 7 days. Fixes are released as soon as practical, and
reporters are credited unless they prefer otherwise.

## Scope

- Code, configuration, workflows and published images/packages of this repository.
- Upstream projects (GibbonEdu, ERPNext, Frappe, India Compliance and third-party images) should be
  reported to their maintainers; tell us as well if our deployment is affected.

## Handling of secrets

This repository is public. It must never contain secrets other than Ansible Vault-encrypted files,
and never real personal data. If you find one, report it privately as above.
