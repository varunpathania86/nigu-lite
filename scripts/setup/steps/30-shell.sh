# shellcheck shell=bash
# Activates mise in new terminals so tools from .tool-versions are on PATH.
SHELL_NAME="$(shell_name)"
RC_FILE="$(shell_rc_file)"

step_describe() { echo "mise activation in ${RC_FILE/#$HOME/\~}"; }

step_check() { grep -qs 'mise activate' "$RC_FILE"; }

step_install() {
  mkdir -p "$(dirname "$RC_FILE")"
  if [[ "$SHELL_NAME" == fish ]]; then
    printf '\n# Added by nigu-lite make setup\nfish_add_path ~/.local/bin\nmise activate fish | source\n' >>"$RC_FILE"
  else
    # shellcheck disable=SC2016 # $HOME and $(...) must expand in the user's shell, not here
    printf '\n# Added by nigu-lite make setup\nexport PATH="$HOME/.local/bin:$PATH"\neval "$(mise activate %s)"\n' \
      "$SHELL_NAME" >>"$RC_FILE"
  fi
}
