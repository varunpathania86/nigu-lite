#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="${MODE:-worktree}"
TARGET="${1:-ci-quality}"
shift || true
MAKE_ARGS=("$@")
BASE="${BASE:-origin/main}"
IMAGE_NAME="${NIGU_CI_IMAGE:-nigu-ci-local}"
mkdir -p "$ROOT/.cache/build-containers"
TEMP="$(mktemp -d "$ROOT/.cache/build-containers/run-XXXXXX")"
trap 'rm -rf "$TEMP"' EXIT

SNAPSHOT="$TEMP/source.tar"
SOURCE="$TEMP/source"
HOME_DIR="$TEMP/home"
OUTPUT="$ROOT/report/act"
mkdir -p "$SOURCE" "$HOME_DIR" "$OUTPUT"

"$ROOT/scripts/act/python.sh" "$ROOT/scripts/ci/snapshot.py" \
  --root "$ROOT" --mode "$MODE" --output "$SNAPSHOT" --metadata "$OUTPUT/snapshot.json"
tar -xf "$SNAPSHOT" -C "$SOURCE"

if git -C "$ROOT" rev-parse --verify "$BASE" >/dev/null 2>&1; then
  MERGE_BASE="$(git -C "$ROOT" merge-base "$BASE" HEAD)"
  printf '%s\n' "$MERGE_BASE" >"$OUTPUT/merge-base.txt"
  git -C "$ROOT" diff --name-only --diff-filter=ACMR "$MERGE_BASE"...HEAD >"$OUTPUT/changed-paths.txt"
  if [[ "$MODE" == "staged" || "$MODE" == "worktree" ]]; then
    git -C "$ROOT" diff --cached --name-only --diff-filter=ACMR >>"$OUTPUT/changed-paths.txt"
  fi
  if [[ "$MODE" == "worktree" ]]; then
    git -C "$ROOT" diff --name-only --diff-filter=ACMR >>"$OUTPUT/changed-paths.txt"
    git -C "$ROOT" ls-files --others --exclude-standard >>"$OUTPUT/changed-paths.txt"
  fi
  sort -u "$OUTPUT/changed-paths.txt" -o "$OUTPUT/changed-paths.txt"
else
  echo "Base '$BASE' is unavailable; pass BASE=<branch>" >&2
  exit 1
fi
if [[ -d "$ROOT/report/parts" ]]; then
  mkdir -p "$OUTPUT/parts"
  cp -R "$ROOT/report/parts/." "$OUTPUT/parts/"
fi
if [[ -n "${NEEDS:-}" ]]; then
  printf '%s' "$NEEDS" >"$OUTPUT/needs.json"
else
  printf '{}\n' >"$OUTPUT/needs.json"
fi

INPUT_HASH="$(
  { cat "$SOURCE/.github/build/Containerfile" "$SOURCE/requirements-ci.txt" \
      "$SOURCE/.pre-commit-config.yaml"; } | sha256sum | awk '{print substr($1,1,16)}'
)"
IMAGE="${IMAGE_NAME}:${INPUT_HASH}"
echo "Build Container: target=$TARGET image=$IMAGE"
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker build --file "$SOURCE/.github/build/Containerfile" --tag "$IMAGE" "$SOURCE"
fi

DOCKER_ARGS=()
if [[ "$TARGET" == "ci-module" || "$TARGET" == "ci-iac" || "$TARGET" == "ci-publish" ]]; then
  DOCKER_ARGS+=(--volume /var/run/docker.sock:/var/run/docker.sock)
  DOCKER_ARGS+=(--group-add "$(stat -c '%g' /var/run/docker.sock)")
fi
NETWORK=none
[[ "$TARGET" == "ci-publish" ]] && NETWORK=host
for variable in GITHUB_TOKEN GITHUB_SHA GITHUB_REPOSITORY GITHUB_REPOSITORY_OWNER GITHUB_ACTOR GITHUB_REF_NAME \
  ACTIONS_ID_TOKEN_REQUEST_URL ACTIONS_ID_TOKEN_REQUEST_TOKEN; do
  [[ -n "${!variable:-}" ]] && DOCKER_ARGS+=(--env "$variable=${!variable}")
done

docker run --rm \
  --user "$(id -u):$(id -g)" \
  --network "$NETWORK" \
  --volume "$SOURCE:/source:ro" \
  --volume "$OUTPUT:/output:rw" \
  --volume "$HOME_DIR:/home:rw" \
  "${DOCKER_ARGS[@]}" \
  --env NIGU_BUILD_CONTAINER=1 \
  --env HOME=/home \
  --env BASE="$BASE" \
  --env NIGU_MODE="$MODE" \
  --env NIGU_HOST_OUTPUT="$OUTPUT" \
  "$IMAGE" \
  "cp -a /source/. /workspace/; git config --global --add safe.directory /workspace; \
  cd /workspace; git init -q -b feature/build-snapshot; git add -A; \
  make '$TARGET' OUT_DIR=/output BASE='$BASE' PATHS_FILE=/output/changed-paths.txt ${MAKE_ARGS[*]}"
