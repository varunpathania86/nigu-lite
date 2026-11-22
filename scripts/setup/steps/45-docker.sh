#!/usr/bin/env bash
# shellcheck shell=bash

step_describe() { echo "Docker Engine for Build Containers"; }

step_check() {
  command -v docker >/dev/null && docker info >/dev/null 2>&1
}

step_install() {
  if ! command -v docker >/dev/null; then
    case "$(os_family)" in
      debian) pkg_install docker.io ;;
      fedora) pkg_install docker ;;
      macos) brew install --cask docker ;;
      *) die "Docker Engine must be installed for this OS" ;;
    esac
  fi
  if [[ "$(os_family)" == "debian" || "$(os_family)" == "fedora" ]]; then
    as_root systemctl enable --now docker
    as_root usermod -aG docker "$(id -un)"
    echo "Log out and back in if the docker group was newly added."
  elif [[ "$(os_family)" == "macos" ]]; then
    open -a Docker
  fi
}
