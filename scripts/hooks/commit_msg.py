#!/usr/bin/env python3
"""commit-msg hook: enforce plain-sentence commit messages (master-plan.md §11.5)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from git_rules import check_message  # noqa: E402


def main(argv: list[str]) -> int:
    message = Path(argv[1]).read_text(encoding="utf-8")
    errors = check_message(message)
    for error in errors:
        print(f"commit-msg: {error}", file=sys.stderr)
    if errors:
        print(
            "Example: 'Added tenant manifest validator' (see .github/instructions/git.instructions.md)", file=sys.stderr
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
