#!/usr/bin/env python3
"""Publish planned images and tenant packages to an explicitly selected registry."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from scripts.ci.package import package_tenant

BINARIES = {name: shutil.which(name) or name for name in ("cosign", "docker", "oras", "trivy")}
LOCAL_KEY_DIR: Path | None = None


def command(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> None:
    resolved = (BINARIES.get(args[0], args[0]), *args[1:])
    subprocess.run(  # noqa: S603  # only explicit CI tool arguments are passed
        resolved, check=True, env=env, cwd=cwd
    )


def local_key_dir() -> Path:
    global LOCAL_KEY_DIR
    if LOCAL_KEY_DIR is None:
        LOCAL_KEY_DIR = Path(tempfile.mkdtemp(prefix="nigu-cosign-"))
    return LOCAL_KEY_DIR


def sign(reference: str, local: bool) -> dict[str, Any]:
    if local:
        key_dir = local_key_dir()
        key = key_dir / "cosign.key"
        environment = os.environ.copy()
        environment["COSIGN_PASSWORD"] = ""
        if not key.is_file():
            command("cosign", "generate-key-pair", f"--output-key-prefix={str(key_dir / 'cosign')}", env=environment)
            command(
                "cosign",
                "signing-config",
                "create",
                "--no-default-fulcio",
                "--no-default-oidc",
                "--no-default-rekor",
                "--no-default-tsa",
                "--out",
                str(key_dir / "signing-config.json"),
            )
        command(
            "cosign",
            "sign",
            "--yes",
            f"--signing-config={key_dir / 'signing-config.json'}",
            "--allow-insecure-registry",
            "--key",
            str(key),
            reference,
            env=environment,
        )
        command(
            "cosign",
            "verify",
            "--allow-insecure-registry",
            "--insecure-ignore-tlog=true",
            "--key",
            str(key_dir / "cosign.pub"),
            reference,
            env=environment,
        )
        identity = "local-test-key"
    else:
        command("cosign", "sign", "--yes", reference)
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        command(
            "cosign",
            "verify",
            "--certificate-oidc-issuer",
            "https://token.actions.githubusercontent.com",
            "--certificate-identity-regexp",
            rf"https://github.com/{repository}/\.github/workflows/publish\.yml@refs/(heads/main|tags/v.*)",
            reference,
        )
        identity = "GitHub Actions OIDC"
    return {"verified": True, "identity": identity}


def attest_sbom(reference: str, sbom: Path, local: bool) -> None:
    arguments = ["cosign", "attest", "--yes", "--predicate", str(sbom), "--type", "cyclonedx"]
    environment = None
    if local:
        key_dir = local_key_dir()
        environment = os.environ.copy()
        environment["COSIGN_PASSWORD"] = ""
        arguments.extend(
            [
                f"--signing-config={key_dir / 'signing-config.json'}",
                "--allow-insecure-registry",
                "--key",
                str(key_dir / "cosign.key"),
            ]
        )
    arguments.append(reference)
    command(*arguments, env=environment)
    verify = ["cosign", "verify-attestation", "--type", "cyclonedx"]
    if local:
        verify.extend(
            [
                "--allow-insecure-registry",
                "--insecure-ignore-tlog=true",
                "--key",
                str(local_key_dir() / "cosign.pub"),
            ]
        )
    else:
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        verify.extend(
            [
                "--certificate-oidc-issuer",
                "https://token.actions.githubusercontent.com",
                "--certificate-identity-regexp",
                rf"https://github.com/{repository}/\.github/workflows/publish\.yml@refs/(heads/main|tags/v.*)",
            ]
        )
    verify.append(reference)
    command(*verify, env=environment)


def publish(
    plan: dict[str, Any],
    registry: str,
    root: Path,
    output: Path,
    source_commit: str,
    local: bool,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    if not local:
        token = os.environ.get("GITHUB_TOKEN")
        actor = os.environ.get("GITHUB_ACTOR", "github-actions")
        if not token:
            raise ValueError("GITHUB_TOKEN is required for GHCR publication")
        subprocess.run(  # noqa: S603  # registry and actor are CI-owned values
            [BINARIES["docker"], "login", registry, "--username", actor, "--password-stdin"],
            input=token,
            text=True,
            check=True,
        )
    artifacts: list[dict[str, Any]] = []
    for module in plan.get("modules", []):
        module_type = module["type"]
        if module_type == "image":
            path = root / module["path"]
            containerfile = "Containerfile" if (path / "Containerfile").is_file() else "Dockerfile"
            reference = f"{registry}/nigu-lite/{module['id']}:sha-{source_commit[:12]}"
            command("docker", "build", "--file", str(path / containerfile), "--tag", reference, str(path))
            command(
                "trivy",
                "image",
                "--skip-db-update",
                "--skip-check-update",
                "--exit-code",
                "1",
                "--severity",
                "HIGH,CRITICAL",
                "--ignore-unfixed",
                reference,
            )
            command("docker", "push", reference)
            digest = (
                subprocess.run(  # noqa: S603  # module-generated registry reference and fixed Docker executable
                    [BINARIES["docker"], "inspect", "--format={{index .RepoDigests 0}}", reference],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                .stdout.strip()
                .split("@")[-1]
            )
            digest_reference = f"{reference.rsplit(':', 1)[0]}@{digest}"
            sbom = output / f"{module['id']}.cdx.json"
            command(
                "trivy",
                "image",
                "--skip-db-update",
                "--skip-check-update",
                "--format",
                "cyclonedx",
                "--output",
                str(sbom),
                reference,
            )
            artifact_kind = "image"
        elif module_type == "tenant":
            path = root / module["path"]
            archive = output / f"{module['id']}.tar.gz"
            package = package_tenant(path, archive)
            tenant_ref = f"{registry}/nigu-lite/{package['product']}/tenants/{package['tenant']}"
            reference = f"{tenant_ref}:sha-{source_commit[:12]}"
            oras_args = ["oras", "push"]
            if local:
                oras_args.append("--plain-http")
            oras_args.extend([reference, f"{archive.name}:application/vnd.nigu.tenant-package.v1.tar+gzip"])
            command(*oras_args, cwd=output)
            resolve = [BINARIES["oras"], "resolve"]
            if local:
                resolve.append("--plain-http")
            resolve.append(reference)
            digest = subprocess.run(  # noqa: S603  # validated ORAS registry reference
                resolve, check=True, capture_output=True, text=True
            ).stdout.strip()
            digest_reference = f"{reference.rsplit(':', 1)[0]}@{digest}"
            sbom = output / f"{module['id']}.package.json"
            sbom.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            artifact_kind = "tenant"
        else:
            continue
        signature = sign(digest_reference, local)
        if artifact_kind == "image":
            attest_sbom(digest_reference, sbom, local)
        artifacts.append(
            {
                "kind": artifact_kind,
                "name": module["id"],
                "reference": reference,
                "digest": digest,
                "signature": signature,
                "sbom": str(sbom),
            }
        )
    metadata = {"schema_version": 1, "source_commit": source_commit, "registry": registry, "artifacts": artifacts}
    (output / "published.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "parts").mkdir(parents=True, exist_ok=True)
    (output / "parts" / "publish.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "job": "publish",
                "status": "success",
                "duration_seconds": 0,
                "summary": f"Published and verified {len(artifacts)} artifacts",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if local and LOCAL_KEY_DIR is not None:
        shutil.rmtree(LOCAL_KEY_DIR, ignore_errors=True)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", default=os.environ.get("GITHUB_SHA", "local"))
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    plan_document = json.loads(args.plan.read_text(encoding="utf-8"))
    publish(plan_document, args.registry, args.root.resolve(), args.output, args.source_commit, args.local)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
