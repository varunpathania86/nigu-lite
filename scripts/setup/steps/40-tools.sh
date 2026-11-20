# shellcheck shell=bash
# CLI tools pinned in .tool-versions (python, pre-commit, trivy, …).

step_describe() { echo "tools pinned in .tool-versions"; }

step_check() {
  local missing
  command -v mise >/dev/null || return 1
  missing="$(cd "$REPO_ROOT" && mise ls --current --missing)" || return 1
  [[ -z "$missing" ]]
}

step_install() { (cd "$REPO_ROOT" && mise install); }
