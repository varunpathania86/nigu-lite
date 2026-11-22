#!/usr/bin/env python3
"""Run a command and always emit a compact machine-readable CI job fragment."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("a command is required after --")
    started = time.monotonic()
    executable = shutil.which(command[0])
    command_name = Path(command[0]).name
    if executable is None or command_name not in {
        "pre-commit",
        "python",
        "python3",
        "trivy",
        "conftest",
        "make",
    }:
        raise ValueError(f"job command is not allow-listed: {command[0]}")
    completed = subprocess.run(  # noqa: S603  # command is allow-listed above and arguments come from Make
        [executable, *command[1:]], check=False
    )
    fragment = {
        "schema_version": 1,
        "job": args.job,
        "status": "success" if completed.returncode == 0 else "failure",
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_code": completed.returncode,
        "command": command,
        "summary": "Command completed" if completed.returncode == 0 else "Command failed",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fragment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
