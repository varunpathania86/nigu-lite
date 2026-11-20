# shellcheck shell=bash
# Base commands that every later step and Make target needs.
COMMANDS=(git curl make tar)

step_describe() { echo "${COMMANDS[*]}"; }

step_check() {
  local cmd
  for cmd in "${COMMANDS[@]}"; do
    command -v "$cmd" >/dev/null || return 1
  done
}

step_install() { pkg_install git curl make tar ca-certificates; }
