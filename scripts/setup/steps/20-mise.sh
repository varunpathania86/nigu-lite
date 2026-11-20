# shellcheck shell=bash
# mise installs every CLI tool pinned in .tool-versions. Its installer verifies the checksum.
MISE_VERSION="2026.11.10"

step_describe() { echo "mise >= $MISE_VERSION"; }

step_check() {
  command -v mise >/dev/null || return 1
  version_ge "$(mise --version | awk '{print $1}')" "$MISE_VERSION"
}

step_install() { curl -fsSL https://mise.run | MISE_VERSION="v$MISE_VERSION" sh; }
