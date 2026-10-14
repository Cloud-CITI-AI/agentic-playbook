#!/usr/bin/env bash
# Adopt the agentic playbook in the current repository. Read before running.
# Usage: bootstrap.sh --version vX.Y.Z [--profile frontend|backend-node|backend-python --package-dir DIR] [--skip-root] [--force]
set -euo pipefail
version=""; args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) version="$2"; args+=("$1" "$2"); shift 2;;
    *) args+=("$1"); shift;;
  esac
done
[[ -n "$version" ]] || { echo "--version is required" >&2; exit 2; }
git rev-parse --is-inside-work-tree >/dev/null || { echo "run from a git repository root" >&2; exit 2; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$here/playbook_sync.py" && -d "$here/../templates" ]]; then
  pb="$here/.."
else
  # Downloaded standalone: fetch the release tarball for the requested version.
  tmp="$(mktemp -d)"
  curl -fsSL "https://github.com/cloud-citi-ai/agentic-playbook/archive/refs/tags/${version}.tar.gz" | tar -xz -C "$tmp" --strip-components=1
  pb="$tmp"
fi
python3 "$pb/scripts/playbook_sync.py" bootstrap "${args[@]}"
command -v lefthook >/dev/null && lefthook install || echo "lefthook not found: install it, then run 'lefthook install'"
