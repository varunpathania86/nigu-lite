#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=local/scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

ensure_docker
docker rm -f "$LOCAL_CONTAINER" >/dev/null 2>&1 || true
docker volume rm nigu-local-docker nigu-local-data >/dev/null 2>&1 || true
docker network rm "$LOCAL_NETWORK" >/dev/null 2>&1 || true
rm -f "$LOCAL_SSH/known_hosts"
echo "Local VPS simulator state was reset"
