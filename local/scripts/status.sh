#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=local/scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

ensure_docker
container_running || die "local simulator is not running"

docker exec "$LOCAL_CONTAINER" systemctl is-active ssh >/dev/null
docker exec "$LOCAL_CONTAINER" systemctl is-active docker >/dev/null
docker exec "$LOCAL_CONTAINER" docker inspect -f '{{.State.Health.Status}}' nigu-local-traefik-1
docker exec "$LOCAL_CONTAINER" docker inspect -f '{{.State.Health.Status}}' nigu-local-garage-1

curl --fail --silent --show-error --insecure \
  --resolve "test-school-a.localhost:${LOCAL_HTTPS_PORT}:127.0.0.1" \
  "https://test-school-a.localhost:${LOCAL_HTTPS_PORT}/" |
  grep -q 'Welcome to nginx!'
echo "Local edge, Docker, Traefik and Garage are healthy"
