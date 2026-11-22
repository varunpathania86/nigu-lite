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
    parser.add_argument("--record-exit-code", type=int)
    parser.add_argument("--summary", default="")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if args.record_exit_code is not None and command:
        parser.error("--record-exit-code cannot be combined with a command")
    if args.record_exit_code is None and not command:
        parser.error("a command is required after --")
    started = time.monotonic()
    if args.record_exit_code is not None:
        exit_code = args.record_exit_code
    else:
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
        exit_code = completed.returncode
    fragment = {
        "schema_version": 1,
        "job": args.job,
        "status": "success" if exit_code == 0 else "failure",
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_code": exit_code,
        "command": command or ["recorded status"],
        "summary": args.summary or ("Command completed" if exit_code == 0 else "Command failed"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fragment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
