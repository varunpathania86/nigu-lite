#!/usr/bin/env python3
"""Export a plan as GitHub Actions step outputs without shell-side JSON handling."""

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    with args.output.open("a", encoding="utf-8") as stream:
        stream.write(f"modules={json.dumps(plan['modules'], separators=(',', ':'))}\n")
        stream.write(f"any={str(plan['any']).lower()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
