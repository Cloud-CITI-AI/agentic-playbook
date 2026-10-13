#!/usr/bin/env bash
# Eval harness (skeleton with working control flow; the agent invocation is adapter-specific).
# Usage: run-evals.sh --agent claude-code|codex|copilot --tasks seed|all --runs N --playbook-ref REF
set -euo pipefail
agent=claude-code; set_name=seed; runs=3; ref=HEAD
while [[ $# -gt 0 ]]; do case "$1" in
  --agent) agent=$2; shift 2;; --tasks) set_name=$2; shift 2;; --runs) runs=$2; shift 2;; --playbook-ref) ref=$2; shift 2;;
  *) echo "unknown arg $1" >&2; exit 2;; esac; done
here="$(cd "$(dirname "$0")" && pwd)"
out="$here/results/$ref"; mkdir -p "$out"
tasks=("$here"/tasks/*.yml); [[ "$set_name" == seed ]] && tasks=("$here"/tasks/T00[1-3]*.yml)

run_agent() { # $1 workdir  $2 brief file
  case "$agent" in
    claude-code) (cd "$1" && claude -p "$(cat "$2")" --output-format json --max-turns 60 > agent-output.json) ;;
    codex)       (cd "$1" && codex exec --full-auto "$(cat "$2")" > agent-output.txt) ;;
    *) echo "adapter for $agent not implemented" >&2; return 2 ;;
  esac
}

for t in "${tasks[@]}"; do
  id=$(python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1]))['id'])" "$t")
  ref_tag=$(python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1]))['fixture_ref'])" "$t")
  for i in $(seq 1 "$runs"); do
    wd=$(mktemp -d)
    git clone -q --branch "$ref_tag" "https://github.com/<org>/agentic-playbook-eval-fixture" "$wd"
    (cd "$wd" && python3 "$here/../scripts/playbook_sync.py" apply --version "$ref" >/dev/null)   # apply candidate playbook
    python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1]))['brief'])" "$t" > "$wd/.brief"
    # Isolation: run inside a container with no secrets and egress limited to the model API (see README).
    run_agent "$wd" "$wd/.brief" || true
    python3 "$here/score.py" run --task "$t" --workdir "$wd" > "$out/${id}-run${i}.json" || true
    rm -rf "$wd"
  done
done
python3 "$here/score.py" summarise "$out"
