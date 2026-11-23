#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=local/scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

ensure_docker
ensure_ssh_key
container_running || die "local simulator is not running; run make local-up"

if ! docker image inspect "$LOCAL_OPS_IMAGE" >/dev/null 2>&1; then
  build_image image-local-operations
fi

docker run --rm \
  --network host \
  --user "$(id -u):$(id -g)" \
  --volume "$LOCAL_ROOT:/workspace:ro" \
  --volume "$LOCAL_SSH:/ssh:ro" \
  --env HOME=/tmp/nigu-ops \
  --env ANSIBLE_PRIVATE_KEY_FILE=/ssh/id_ed25519 \
  --env ANSIBLE_HOST_KEY_CHECKING=True \
  "$LOCAL_OPS_IMAGE" \
  -i local/ansible/inventory.ini local/ansible/playbook.yml
