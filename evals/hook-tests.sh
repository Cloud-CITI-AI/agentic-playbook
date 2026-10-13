#!/usr/bin/env bash
# Deterministic tests for templates/project/.claude/hooks/protect-instruction-files.sh
set -uo pipefail
hook="$(cd "$(dirname "$0")/.." && pwd)/templates/project/.claude/hooks/protect-instruction-files.sh"
export CLAUDE_PROJECT_DIR=/repo
pass=0; fail=0
t() { # expected_exit json description
  printf '%s' "$2" | bash "$hook" >/dev/null 2>&1; got=$?
  if [[ "$got" == "$1" ]]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $3 (expected $1, got $got)"; fi
}
t 2 '{"tool_name":"Edit","tool_input":{"file_path":"/repo/AGENTS.md"}}' "edit root AGENTS.md"
t 2 '{"tool_name":"Write","tool_input":{"file_path":"/repo/services/api/AGENTS.md"}}' "write package AGENTS.md"
t 2 '{"tool_name":"Edit","tool_input":{"file_path":"/repo/.github/workflows/ci.yml"}}' "edit workflow"
t 2 '{"tool_name":"Edit","tool_input":{"file_path":"/repo/.claude/settings.json"}}' "edit claude settings"
t 2 '{"tool_name":"Write","tool_input":{"file_path":"/repo/LESSONS.md"}}' "overwrite LESSONS"
t 2 '{"tool_name":"Bash","tool_input":{"command":"sed -i s/a/b/ AGENTS.md"}}' "sed AGENTS.md"
t 2 '{"tool_name":"Bash","tool_input":{"command":"echo x > .github/CODEOWNERS"}}' "redirect CODEOWNERS"
t 2 '{"tool_name":"Bash","tool_input":{"command":"git checkout main -- CLAUDE.md"}}' "git checkout CLAUDE.md"
t 0 '{"tool_name":"Bash","tool_input":{"command":"cat entry.md >> LESSONS.md"}}' "append LESSONS"
t 0 '{"tool_name":"Edit","tool_input":{"file_path":"/repo/src/orders.ts"}}' "edit source"
t 0 '{"tool_name":"Bash","tool_input":{"command":"pnpm test:unit"}}' "run tests"
t 0 '{"tool_name":"Bash","tool_input":{"command":"cat AGENTS.md"}}' "read AGENTS.md"
echo "hook tests: $pass passed, $fail failed"
[[ $fail -eq 0 ]]
