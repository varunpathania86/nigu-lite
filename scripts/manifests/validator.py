#!/usr/bin/env python3
"""Validate VPS and tenant manifests without contacting a host."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

RESERVED_IDS = {
    "admin",
    "auth",
    "beszel",
    "dbx",
    "grafana",
    "ldap",
    "logs",
    "mon",
    "status",
    "vpn",
    "www",
}
VAULT_HEADER = "$ANSIBLE_VAULT;1.1;AES256"
VAULT_KEY_PATTERN = re.compile(r"^(vault_|.*password.*|.*secret.*|.*token.*)$", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    file: str
    path: str = "$"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _schema_errors(path: Path, document: Any, schema_path: Path) -> list[Finding]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        Finding(
            code="schema",
            file=str(path),
            path="$." + ".".join(str(item) for item in error.absolute_path),
            message=error.message,
        )
        for error in sorted(validator.iter_errors(document), key=_validation_sort_key)
    ]


def _validation_sort_key(error: ValidationError) -> tuple[str, ...]:
    return tuple(str(item) for item in error.absolute_path)


def _tenant_paths(root: Path) -> dict[tuple[str, str], Path]:
    paths: dict[tuple[str, str], Path] = {}
    for product in ("erp", "edu"):
        product_root = root / product / "tenants"
        test_root = root / "tests" / "tenants" / product
        for base in (product_root, test_root):
            if not base.is_dir():
                continue
            for tenant in sorted(base.glob("*/tenant.yml")):
                paths[(product, tenant.parent.name)] = tenant
    return paths


def _manifest_paths(root: Path) -> list[Path]:
    deployments = root / "deployments"
    return sorted(path for path in deployments.glob("*.yml") if not path.name.endswith(".lock.yml"))


def _tenant_findings(root: Path, schema_path: Path) -> tuple[list[Finding], dict[tuple[str, str], dict[str, Any]]]:
    findings: list[Finding] = []
    tenants: dict[tuple[str, str], dict[str, Any]] = {}
    for key, path in _tenant_paths(root).items():
        product, tenant_id = key
        try:
            document = _yaml(path)
        except yaml.YAMLError as error:
            findings.append(Finding("yaml", f"invalid YAML: {error}", str(path)))
            continue
        findings.extend(_schema_errors(path, document, schema_path))
        if not isinstance(document, dict):
            continue
        tenants[key] = document
        if document.get("id") != tenant_id:
            findings.append(Finding("tenant-id", f"folder id '{tenant_id}' differs from tenant id", str(path), "$.id"))
        if document.get("product") != product:
            findings.append(Finding("tenant-product", f"tenant product must be '{product}'", str(path), "$.product"))
        if tenant_id in RESERVED_IDS or tenant_id.startswith("vps"):
            findings.append(Finding("reserved-id", f"tenant id '{tenant_id}' is reserved", str(path), "$.id"))
        expected_app = {"erp": "erpnext", "edu": "gibbon"}[product]
        if document.get("apps") != [expected_app]:
            findings.append(
                Finding("tenant-app", f"{product} tenant must select exactly '{expected_app}'", str(path), "$.apps")
            )
        expected_domain = f"{tenant_id}.erpos.in" if product == "erp" else f"{tenant_id}.schooledu.in"
        domains = document.get("domains", {})
        if domains.get("primary") != expected_domain:
            findings.append(
                Finding(
                    "tenant-domain",
                    f"primary domain must be '{expected_domain}'",
                    str(path),
                    "$.domains.primary",
                )
            )
        findings.extend(_tenant_file_findings(path.parent))
    return findings, tenants


def _tenant_file_findings(directory: Path) -> list[Finding]:
    findings: list[Finding] = []
    for required in ("README.md", "tenant.yml", "assets", "migrations"):
        if not (directory / required).exists():
            findings.append(Finding("tenant-file", f"missing required tenant path '{required}'", str(directory)))
    vault = directory / "vault.yml"
    if not vault.is_file():
        return findings
    text = vault.read_text(encoding="utf-8")
    if not text.startswith(VAULT_HEADER):
        findings.append(Finding("vault-encryption", "vault.yml must be Ansible Vault encrypted", str(vault)))
    return findings


def validate(root: Path) -> list[Finding]:
    root = root.resolve()
    findings, tenants = _tenant_findings(root, root / "deployments" / "tenant.schema.json")
    schema_path = root / "deployments" / "schema.json"
    versions_path = root / "versions.yml"
    versions = _yaml(versions_path) if versions_path.is_file() else {}
    gibbon_versions = set((versions.get("gibbon") or {}).keys()) if isinstance(versions, dict) else set()
    placements: dict[tuple[str, str], list[str]] = defaultdict(list)
    hosts: dict[str, str] = {}
    node_records: dict[str, str] = {}
    control_planes: list[str] = []

    manifests = _manifest_paths(root)
    for path in manifests:
        try:
            document = _yaml(path)
        except yaml.YAMLError as error:
            findings.append(Finding("yaml", f"invalid YAML: {error}", str(path)))
            continue
        findings.extend(_schema_errors(path, document, schema_path))
        if not isinstance(document, dict):
            continue
        manifest_name = str(path)
        host = str(document.get("host", ""))
        node_record = str(document.get("node_record", ""))
        if host != path.stem and host:
            findings.append(Finding("manifest-host", "host must match the manifest filename", manifest_name, "$.host"))
        if host in hosts:
            findings.append(Finding("duplicate-host", f"host already used by {hosts[host]}", manifest_name, "$.host"))
        hosts[host] = manifest_name
        if node_record in node_records:
            findings.append(
                Finding(
                    "duplicate-node-record",
                    f"node_record already used by {node_records[node_record]}",
                    manifest_name,
                    "$.node_record",
                )
            )
        node_records[node_record] = manifest_name
        if document.get("control_plane") is True:
            control_planes.append(manifest_name)
        _validate_environment(path, document, findings)
        products = document.get("products") or {}
        for product, selection in products.items():
            values = selection.get("tenants") if isinstance(selection, dict) else None
            tenant_items = (
                values.items()
                if product == "edu" and isinstance(values, dict)
                else (((tenant, None) for tenant in values) if isinstance(values, list) else ())
            )
            for tenant_id, tenant_options in tenant_items:
                placements[(product, tenant_id)].append(manifest_name)
                if (product, tenant_id) not in tenants:
                    findings.append(
                        Finding(
                            "unknown-tenant",
                            f"tenant '{tenant_id}' is not defined",
                            manifest_name,
                            f"$.products.{product}",
                        )
                    )
                if product == "edu" and isinstance(tenant_options, dict):
                    version = tenant_options.get("gibbon_version")
                    if version not in gibbon_versions:
                        findings.append(
                            Finding(
                                "gibbon-version",
                                f"Gibbon version '{version}' is not in versions.yml",
                                manifest_name,
                                f"$.products.edu.tenants.{tenant_id}.gibbon_version",
                            )
                        )
            if product == "edu" and isinstance(values, dict) and values:
                canaries = sum(bool(item.get("canary")) for item in values.values() if isinstance(item, dict))
                if canaries != 1:
                    findings.append(
                        Finding(
                            "canary",
                            "a VPS hosting Gibbon needs exactly one canary",
                            manifest_name,
                            "$.products.edu",
                        )
                    )

    for (product, tenant_id), manifest_names in sorted(placements.items()):
        if len(manifest_names) > 1:
            for manifest_name in manifest_names:
                findings.append(
                    Finding(
                        "duplicate-placement",
                        f"{product} tenant '{tenant_id}' is selected by multiple manifests",
                        manifest_name,
                        f"$.products.{product}",
                    )
                )
    production_manifests = (
        [path for path in manifests if (document := _safe_yaml(path)).get("environment") == "production"]
        if manifests
        else []
    )
    if production_manifests and len(control_planes) != 1:
        findings.append(
            Finding(
                "control-plane",
                "production manifests need exactly one control plane",
                str(root / "deployments"),
            )
        )
    return sorted(findings, key=lambda item: (item.file, item.path, item.code, item.message))


def _safe_yaml(path: Path) -> dict[str, Any]:
    try:
        document = _yaml(path)
    except yaml.YAMLError:
        return {}
    return document if isinstance(document, dict) else {}


def _validate_environment(path: Path, document: dict[str, Any], findings: list[Finding]) -> None:
    environment = document.get("environment")
    dns = document.get("dns", {}).get("provider") if isinstance(document.get("dns"), dict) else None
    tls = document.get("tls", {}).get("mode") if isinstance(document.get("tls"), dict) else None
    if environment == "production":
        if dns != "cloudflare":
            findings.append(
                Finding("production-dns", "production requires cloudflare DNS", str(path), "$.dns.provider")
            )
        if tls != "letsencrypt":
            findings.append(Finding("production-tls", "production requires letsencrypt TLS", str(path), "$.tls.mode"))
    try:
        ipaddress.ip_address(document.get("public_ip", ""))
    except ValueError:
        findings.append(Finding("ip-address", "public_ip must be a valid IPv4 address", str(path), "$.public_ip"))


def has_secret_key(document: Any) -> bool:
    if isinstance(document, dict):
        return any(VAULT_KEY_PATTERN.match(str(key)) or has_secret_key(value) for key, value in document.items())
    if isinstance(document, list):
        return any(has_secret_key(value) for value in document)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    findings = validate(args.root)
    result = {"valid": not findings, "findings": [item.to_dict() for item in findings]}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
