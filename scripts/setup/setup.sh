#!/usr/bin/env bash
# Developer machine setup: runs every step in scripts/setup/steps/ in file-name order.
# Each step defines step_describe, step_check and step_install (.github/instructions/dev-setup.instructions.md).
# Usage: setup.sh            install whatever is missing (make setup)
#        setup.sh --check    report only, change nothing (make doctor)
set -euo pipefail

SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SETUP_DIR/../.." && pwd)"
STEPS_DIR="${SETUP_STEPS_DIR:-$SETUP_DIR/steps}"
MODE="${1:-install}"
export REPO_ROOT
# shellcheck source=scripts/setup/lib.sh
source "$SETUP_DIR/lib.sh"

[[ "$MODE" == install || "$MODE" == --check ]] || die "usage: setup.sh [--check]"

run_step() {
  local step="$1" name fn
  name="$(basename "$step" .sh)"
  # shellcheck source=/dev/null
  source "$step"
  for fn in step_describe step_check step_install; do
    declare -F "$fn" >/dev/null || die "$name: missing function $fn"
  done
  if step_check; then
    report ok "$name" "$(step_describe)"
    return 0
  fi
  if [[ "$MODE" == --check ]]; then
    report missing "$name" "$(step_describe)"
    return 1
  fi
  report install "$name" "$(step_describe)"
  step_install
  if step_check; then
    report ok "$name" "$(step_describe)"
  else
    report failed "$name" "$(step_describe)"
    return 1
  fi
}

failed=0
for step in "$STEPS_DIR"/[0-9][0-9]-*.sh; do
  [[ -e "$step" ]] || die "no steps found in $STEPS_DIR"
  # Subshell: a step cannot leak functions or variables into the next one.
  if ! (run_step "$step"); then
    failed=1
    # Later steps depend on earlier ones, so stop installing at the first failure.
    [[ "$MODE" == --check ]] || break
  fi
done

if [[ "$failed" -ne 0 ]]; then
  [[ "$MODE" == --check ]] && die "machine is not ready; run: make setup"
  die "setup failed; fix the step above and re-run: make setup"
fi
[[ "$MODE" == --check ]] || echo "Ready. Open a new terminal so mise is on PATH, then run: make lint test-unit"
