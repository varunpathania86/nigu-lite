#!/usr/bin/env bash
# shellcheck disable=SC2034 # Variables are consumed by lifecycle scripts that source this file.
set -euo pipefail

LOCAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCAL_CACHE="$LOCAL_ROOT/.cache/local"
LOCAL_SSH="$LOCAL_CACHE/ssh"
LOCAL_CONTAINER="nigu-local-vps"
LOCAL_NETWORK="nigu-local-host"
LOCAL_SSH_PORT=2222
LOCAL_HTTPS_PORT=8443
LOCAL_TAG="${NIGU_LOCAL_IMAGE_TAG:-stage2}"
LOCAL_VPS_IMAGE="local-nigu/image-local-vps:${LOCAL_TAG}"
LOCAL_OPS_IMAGE="local-nigu/image-local-operations:${LOCAL_TAG}"

die() {
  echo "local: $*" >&2
  exit 1
}

ensure_docker() {
  command -v docker >/dev/null 2>&1 || die "Docker is required; run make setup"
  docker info >/dev/null 2>&1 || die "Docker daemon is unavailable"
}

ensure_ssh_key() {
  mkdir -p "$LOCAL_SSH"
  if [[ ! -f "$LOCAL_SSH/id_ed25519" ]]; then
    ssh-keygen -q -t ed25519 -N "" -C "nigu-local" -f "$LOCAL_SSH/id_ed25519"
  fi
  chmod 0600 "$LOCAL_SSH/id_ed25519"
  chmod 0644 "$LOCAL_SSH/id_ed25519.pub"
  cp "$LOCAL_SSH/id_ed25519.pub" "$LOCAL_SSH/authorized_keys"
  chmod 0644 "$LOCAL_SSH/authorized_keys"
}

build_image() {
  local module="$1"
  NIGU_LOCAL_IMAGE_TAG="$LOCAL_TAG" MODE="${MODE:-worktree}" \
    make -C "$LOCAL_ROOT" container-module ID="$module" TYPE=image
}

container_running() {
  [[ "$(docker inspect -f '{{.State.Running}}' "$LOCAL_CONTAINER" 2>/dev/null || true)" == "true" ]]
}
