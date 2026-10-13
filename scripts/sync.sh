#!/usr/bin/env bash
# Thin wrapper used by workflows.  sync.sh --check [--enforce true|false]   |   sync.sh --apply --version vX.Y.Z
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${1:-}" in
  --check) shift; enforce="true"; [[ "${1:-}" == "--enforce" ]] && enforce="$2"; exec python3 "$here/playbook_sync.py" check --enforce "$enforce";;
  --apply) shift; [[ "${1:-}" == "--version" ]] || { echo "--version required" >&2; exit 2; }; exec python3 "$here/playbook_sync.py" apply --version "$2";;
  *) echo "usage: sync.sh --check [--enforce true|false] | --apply --version vX.Y.Z" >&2; exit 2;;
esac
