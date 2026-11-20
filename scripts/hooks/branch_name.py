#!/usr/bin/env python3
"""pre-commit hook: reject commits on branches that break the naming rules (§11.5)."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from git_rules import check_branch  # noqa: E402


def current_branch() -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip()


def main() -> int:
    branch = current_branch()
    if not branch:  # detached HEAD (rebase, CI checkout)
        return 0
    errors = check_branch(branch)
    for error in errors:
        print(f"branch-name: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
