#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-status}"
NAME="nigu-s1-registry"
PORT="${NIGU_REGISTRY_PORT:-5000}"
IMAGE="registry:2@sha256:a3d8aaa63ed8681a604f1dea0aa03f100d5895b6a58ace528858a7b332415373"

case "$ACTION" in
  up)
    if docker container inspect "$NAME" >/dev/null 2>&1; then
      docker start "$NAME" >/dev/null
    else
      docker run -d --name "$NAME" --restart unless-stopped \
        -p "127.0.0.1:${PORT}:5000" -v nigu-s1-registry-data:/var/lib/registry "$IMAGE" >/dev/null
    fi
    echo "Local registry is available at 127.0.0.1:${PORT}"
    ;;
  status)
    docker container inspect -f '{{.State.Status}}' "$NAME" 2>/dev/null || {
      echo "Local registry is not running" >&2
      exit 1
    }
    ;;
  down)
    if docker container inspect "$NAME" >/dev/null 2>&1; then
      docker rm -f "$NAME" >/dev/null
    fi
    echo "Local registry stopped; its named volume is retained"
    ;;
  *)
    echo "usage: registry.sh [up|status|down]" >&2
    exit 2
    ;;
esac
