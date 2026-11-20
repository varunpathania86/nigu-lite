# shellcheck shell=bash
# macOS only (no-op elsewhere): Homebrew backs pkg_install; its installer also adds the Xcode Command Line Tools.
# Homebrew/install has no release tags, so pin a commit and the installer's SHA-256; bump both together.
BREW_INSTALL_COMMIT="c9c975046f78e6e6d662deb801bd461ebd6a54ed"
BREW_INSTALL_SHA256="8fd2f1a5287a7c2e3d7362924c677edcc04c5a0e16448c77132d056bc88cf1ed"

step_describe() {
  if [[ "$(os_family)" == macos ]]; then
    echo "Homebrew + brew shellenv in $(shell_rc_file)"
  else
    echo "Homebrew (macOS only, not needed here)"
  fi
}

step_check() {
  [[ "$(os_family)" == macos ]] || return 0
  command -v brew >/dev/null && grep -qs 'brew shellenv' "$(shell_rc_file)"
}

step_install() {
  local script rc_file
  if ! command -v brew >/dev/null; then
    script="$(mktemp)"
    curl -fsSL "https://raw.githubusercontent.com/Homebrew/install/$BREW_INSTALL_COMMIT/install.sh" -o "$script"
    if [[ "$(sha256_of "$script")" != "$BREW_INSTALL_SHA256" ]]; then
      rm -f "$script"
      die "Homebrew installer checksum mismatch; re-pin it in scripts/setup/steps/05-homebrew.sh"
    fi
    echo "  Homebrew needs administrator rights; enter your macOS password once:"
    sudo -v
    # NONINTERACTIVE skips the installer's "press RETURN" prompt; sudo is already cached above.
    NONINTERACTIVE=1 /bin/bash "$script"
    rm -f "$script"
    brew_env || die "Homebrew installer finished but brew was not found"
  fi
  rc_file="$(shell_rc_file)"
  grep -qs 'brew shellenv' "$rc_file" && return 0
  mkdir -p "$(dirname "$rc_file")"
  if [[ "$(shell_name)" == fish ]]; then
    printf '\n# Added by nigu-lite make setup\n%s shellenv | source\n' "$(command -v brew)" >>"$rc_file"
  else
    # shellcheck disable=SC2016 # $(...) must expand in the user's shell, not here
    printf '\n# Added by nigu-lite make setup\neval "$(%s shellenv)"\n' "$(command -v brew)" >>"$rc_file"
  fi
}
