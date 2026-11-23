#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=local/scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

ensure_docker
ensure_ssh_key

if ! docker image inspect "$LOCAL_VPS_IMAGE" >/dev/null 2>&1; then
  build_image image-local-vps
fi

docker network inspect "$LOCAL_NETWORK" >/dev/null 2>&1 || docker network create "$LOCAL_NETWORK" >/dev/null

if ! container_running; then
  docker rm -f "$LOCAL_CONTAINER" >/dev/null 2>&1 || true
  docker run -d \
    --name "$LOCAL_CONTAINER" \
    --hostname local-vps \
    --network "$LOCAL_NETWORK" \
    --user 0:0 \
    --privileged \
    --cgroupns=host \
    --stop-signal SIGRTMIN+3 \
    --tmpfs /run \
    --tmpfs /run/lock \
    --volume /sys/fs/cgroup:/sys/fs/cgroup:rw \
    --volume nigu-local-docker:/var/lib/docker \
    --volume nigu-local-data:/opt/nigu-local \
    --volume "$LOCAL_SSH/authorized_keys:/run/local-ssh/authorized_keys:ro" \
    --publish "127.0.0.1:${LOCAL_SSH_PORT}:22" \
    --publish "127.0.0.1:${LOCAL_HTTPS_PORT}:443" \
    "$LOCAL_VPS_IMAGE" >/dev/null
fi

known_hosts="$LOCAL_SSH/known_hosts"
rm -f "$known_hosts"
for _ in $(seq 1 60); do
  if ssh -i "$LOCAL_SSH/id_ed25519" \
    -o BatchMode=yes \
    -o ConnectTimeout=2 \
    -o StrictHostKeyChecking=accept-new \
    -o UserKnownHostsFile="$known_hosts" \
    -p "$LOCAL_SSH_PORT" ops@127.0.0.1 true >/dev/null 2>&1; then
    echo "Local VPS simulator is ready on SSH port $LOCAL_SSH_PORT"
    exit 0
  fi
  sleep 2
done

docker logs "$LOCAL_CONTAINER" >&2
die "local VPS simulator did not become ready"
