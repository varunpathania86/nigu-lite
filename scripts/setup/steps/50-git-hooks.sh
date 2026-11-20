# shellcheck shell=bash
# pre-commit and commit-msg hooks (.pre-commit-config.yaml).

step_describe() { echo "pre-commit + commit-msg git hooks"; }

step_check() {
  local dir
  dir="$(git -C "$REPO_ROOT" rev-parse --git-path hooks 2>/dev/null)" || return 1
  [[ "$dir" == /* ]] || dir="$REPO_ROOT/$dir"
  grep -qs pre-commit "$dir/pre-commit" && grep -qs pre-commit "$dir/commit-msg"
}

step_install() {
  (cd "$REPO_ROOT" && mise exec -- pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg)
}
