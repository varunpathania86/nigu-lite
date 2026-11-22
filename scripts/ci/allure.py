#!/usr/bin/env python3
"""Run unit tests and generate an Allure report with restored history."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

PYTEST = shutil.which("pytest") or "pytest"
ALLURE = shutil.which("allure") or "allure"


def copy_history(source: Path, target: Path) -> None:
    if not source.is_dir():
        return
    target.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        destination = target / path.name
        if path.is_dir():
            shutil.copytree(path, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(path, destination)


def generate(root: Path, output: Path, history: Path, results: Path) -> int:
    shutil.rmtree(results, ignore_errors=True)
    shutil.rmtree(output, ignore_errors=True)
    results.mkdir(parents=True)
    copy_history(history, results / "history")
    completed = subprocess.run(  # noqa: S603  # fixed local test command
        [PYTEST, "-q", "tests/unit", f"--alluredir={results}"],
        cwd=root,
        check=False,
    )
    subprocess.run(  # noqa: S603  # fixed Allure command and generated paths
        [ALLURE, "generate", str(results), "--clean", "-o", str(output)],
        cwd=root,
        check=True,
    )
    shutil.rmtree(history, ignore_errors=True)
    copy_history(output / "history", history)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    return generate(args.root.resolve(), args.output, args.history, args.results)


if __name__ == "__main__":
    raise SystemExit(main())
