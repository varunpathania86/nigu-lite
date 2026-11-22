#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EVENT="${EVENT:-pull_request}"
MODE="${MODE:-worktree}"
WORKFLOW="${1:-build.yml}"

if [[ -d "$ROOT/report" ]]; then
  find "$ROOT/report" -mindepth 1 -delete
fi

set +e
mise exec act@0.2.98 -- act "$EVENT" \
  --trust-project-actrc \
  --workflows "$ROOT/.github/workflows/$WORKFLOW" \
  --env "NIGU_LOCAL_MODE=$MODE" \
  --env "NIGU_LOCAL_BUILD=true" \
  --env "NIGU_REGISTRY_PORT=5000"
STATUS=$?
set -e
for output in "$ROOT/report" "$ROOT/.cache/build-containers"; do
  [[ -d "$output" ]] || continue
  docker run --rm \
    --volume "$output:/output" \
    ubuntu:24.04@sha256:9c7f200c07e3d4a03e7249d2c16bf66a51120fb876aa2242cf31451412543289 \
    chown -R "$(id -u):$(id -g)" /output
done
exit "$STATUS"
