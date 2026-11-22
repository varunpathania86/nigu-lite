#!/usr/bin/env bash
set -euo pipefail
if command -v mise >/dev/null 2>&1; then
  exec mise exec python@3.14.10 -- python "$@"
fi
exec python3 "$@"
