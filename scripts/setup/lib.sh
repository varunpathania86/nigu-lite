# shellcheck shell=bash
# Helpers shared by scripts/setup/setup.sh and its steps (sourced, never executed).

# mise installs here; later steps must find it in the same run.
export PATH="$HOME/.local/bin:$PATH"

# Puts Homebrew on PATH when installed (Apple Silicon or Intel prefix); no-op elsewhere.
brew_env() {
  local brew
  for brew in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if [[ -x "$brew" ]]; then
      eval "$("$brew" shellenv)"
      return 0
    fi
  done
  return 1
}
brew_env || true

report() { printf '  %-8s %-20s %s\n' "$1" "$2" "${3:-}"; }

die() {
  printf 'setup: %s\n' "$*" >&2
  exit 1
}

# True when version $1 >= version $2.
version_ge() { [[ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -n 1)" == "$2" ]]; }

sha256_of() {
  if command -v sha256sum >/dev/null; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

# Prints bash, zsh or fish (anything else is treated as bash).
shell_name() {
  case "$(basename "${SHELL:-bash}")" in
    zsh) echo zsh ;;
    fish) echo fish ;;
    *) echo bash ;;
  esac
}

# Startup file of the developer's login shell.
shell_rc_file() {
  case "$(shell_name)" in
    zsh) echo "$HOME/.zshrc" ;;
    fish) echo "$HOME/.config/fish/config.fish" ;;
    *) echo "$HOME/.bashrc" ;;
  esac
}

# Prints debian, fedora, macos or unknown.
os_family() {
  if [[ "$(uname -s)" == Darwin ]]; then
    echo macos
    return
  fi
  local ids=""
  # shellcheck source=/dev/null
  [[ -r /etc/os-release ]] && ids="$(. /etc/os-release && echo " ${ID:-} ${ID_LIKE:-} ")"
  case "$ids" in
    *" debian "* | *" ubuntu "*) echo debian ;;
    *" fedora "* | *" rhel "*) echo fedora ;;
    *) echo unknown ;;
  esac
}

as_root() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

# Installs OS packages; callers pass names that exist on every supported OS family.
pkg_install() {
  case "$(os_family)" in
    debian) as_root apt-get update -qq && as_root env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$@" ;;
    fedora) as_root dnf install -y -q "$@" ;;
    macos)
      command -v brew >/dev/null || die "Homebrew is missing; re-run make setup (step 05-homebrew installs it)"
      brew install "$@"
      ;;
    *) die "unsupported OS (Ubuntu/Debian, Fedora, macOS or WSL2); install manually: $*" ;;
  esac
}
