#!/usr/bin/env bash
set -euo pipefail

ssh-keygen -A

if [[ -r /run/local-ssh/authorized_keys ]]; then
  install -d -m 0700 -o ops -g ops /home/ops/.ssh
  install -m 0600 -o ops -g ops /run/local-ssh/authorized_keys /home/ops/.ssh/authorized_keys
fi

exec "$@"
