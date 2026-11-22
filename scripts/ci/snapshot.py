#!/usr/bin/env python3
"""Create immutable Git tree snapshots without changing the real index."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

GIT = shutil.which("git")
if GIT is None:
    raise RuntimeError("git executable is required")


def git(root: Path, *args: str, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(  # noqa: S603  # fixed Git executable and Git-owned arguments
        [GIT, *args],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _snapshot_environment(root: Path, temporary: Path) -> dict[str, str]:
    environment = os.environ.copy()
    object_directory = temporary / "objects"
    object_directory.mkdir()
    real_objects = Path(git(root, "rev-parse", "--git-common-dir")) / "objects"
    if not real_objects.is_absolute():
        real_objects = root / real_objects
    environment["GIT_OBJECT_DIRECTORY"] = str(object_directory)
    environment["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(real_objects.resolve())
    return environment


def resolve_tree(root: Path, mode: str, temporary: Path) -> tuple[str, bool, dict[str, str] | None]:
    if mode == "commit":
        return git(root, "rev-parse", "HEAD^{tree}"), True, None
    environment = _snapshot_environment(root, temporary)
    if mode == "staged":
        return git(root, "write-tree", env=environment), False, environment
    if mode != "worktree":
        raise ValueError(f"unknown snapshot mode: {mode}")
    git_dir = Path(git(root, "rev-parse", "--git-dir"))
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    index = temporary / "index"
    real_index = git_dir / "index"
    if real_index.exists():
        shutil.copy2(real_index, index)
    environment["GIT_INDEX_FILE"] = str(index)
    git(root, "add", "-A", "--", ".", env=environment)
    return git(root, "write-tree", env=environment), False, environment


def create_snapshot(root: Path, mode: str, output: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="nigu-snapshot-") as temporary_directory:
        tree, reproducible, environment = resolve_tree(root, mode, Path(temporary_directory))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("wb") as stream:
            subprocess.run(  # noqa: S603  # fixed Git executable and resolved tree object
                [GIT, "archive", "--format=tar", tree],
                cwd=root,
                env=environment,
                check=True,
                stdout=stream,
            )
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
    head = git(root, "rev-parse", "HEAD")
    return {
        "schema_version": 1,
        "mode": mode,
        "head": head,
        "tree": tree,
        "archive_sha256": digest,
        "archive": str(output),
        "reproducible_from_commit": reproducible,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--mode", choices=("commit", "staged", "worktree"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    metadata = create_snapshot(args.root.resolve(), args.mode, args.output.resolve())
    text = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
