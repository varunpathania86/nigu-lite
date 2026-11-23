#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=local/scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

ensure_docker
if docker container inspect "$LOCAL_CONTAINER" >/dev/null 2>&1; then
  docker rm -f "$LOCAL_CONTAINER" >/dev/null
fi
echo "Local VPS simulator stopped; named data volumes were retained"
