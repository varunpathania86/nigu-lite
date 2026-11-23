#!/usr/bin/env bash
# shellcheck shell=bash

step_describe() { echo "OpenSSH client and key generator"; }

step_check() {
  command -v ssh >/dev/null && command -v ssh-keygen >/dev/null
}

step_install() {
  case "$(os_family)" in
    debian) pkg_install openssh-client ;;
    fedora) pkg_install openssh-clients ;;
    macos) step_check || die "macOS OpenSSH client is missing" ;;
    *) die "OpenSSH client is required for local Ansible access" ;;
  esac
}
