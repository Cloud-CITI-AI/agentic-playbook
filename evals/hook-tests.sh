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

# Gaps closed in v1.2.0
t 2 '{"tool_name":"Bash","tool_input":{"command":"rm -rf .github"}}' "remove protected dir without trailing slash"
t 2 '{"tool_name":"Bash","tool_input":{"command":"echo x > LESSONS.md; echo y >> LESSONS.md"}}' "overwrite hidden behind a LESSONS append"
t 2 '{"tool_name":"Edit","tool_input":{"file_path":"/repo/agents.md"}}' "case-insensitive file name"

# PowerShell tool
t 2 '{"tool_name":"PowerShell","tool_input":{"command":"Set-Content -Path .claude\\settings.json -Value x"}}' "PowerShell Set-Content claude settings"
t 2 '{"tool_name":"PowerShell","tool_input":{"command":"Copy-Item x.md AGENTS.md"}}' "PowerShell Copy-Item AGENTS.md"
t 2 '{"tool_name":"PowerShell","tool_input":{"command":"Remove-Item -Recurse .github\\workflows"}}' "PowerShell Remove-Item workflows"
t 2 '{"tool_name":"PowerShell","tool_input":{"command":"\"x\" | Out-File CODEOWNERS"}}' "PowerShell Out-File CODEOWNERS"
t 2 '{"tool_name":"PowerShell","tool_input":{"command":"[IO.File]::WriteAllText(\"CLAUDE.md\", \"x\")"}}' "PowerShell .NET write CLAUDE.md"
t 0 '{"tool_name":"PowerShell","tool_input":{"command":"Add-Content -Path LESSONS.md -Value $entry"}}' "PowerShell append LESSONS"
t 0 '{"tool_name":"PowerShell","tool_input":{"command":"Get-Content AGENTS.md"}}' "PowerShell read AGENTS.md"
t 0 '{"tool_name":"PowerShell","tool_input":{"command":"pnpm verify"}}' "PowerShell run verify"

# Windows paths (backslashes, drive letter, different case)
CLAUDE_PROJECT_DIR='C:\repo'
t 2 '{"tool_name":"Edit","tool_input":{"file_path":"C:\\repo\\AGENTS.md"}}' "Windows path AGENTS.md"
t 2 '{"tool_name":"Edit","tool_input":{"file_path":"c:\\Repo\\.github\\workflows\\ci.yml"}}' "Windows path workflow, other case"
t 2 '{"tool_name":"Write","tool_input":{"file_path":"C:\\repo\\LESSONS.md"}}' "Windows path overwrite LESSONS"
t 0 '{"tool_name":"Edit","tool_input":{"file_path":"C:\\repo\\apps\\web\\src\\page.tsx"}}' "Windows path source file"
CLAUDE_PROJECT_DIR=/repo

# Interpreter selection
stub="$(mktemp -d)"; printf '#!/bin/sh\necho "Python was not found" >&2\nexit 49\n' > "$stub/python3"; chmod +x "$stub/python3"
PATH="$stub:$PATH" t 2 '{"tool_name":"Edit","tool_input":{"file_path":"/repo/AGENTS.md"}}' "python3 is a broken stub: falls back and still blocks"
PATH="$stub:$PATH" t 0 '{"tool_name":"Edit","tool_input":{"file_path":"/repo/src/orders.ts"}}' "python3 is a broken stub: falls back and allows"
nopy="$(mktemp -d)"; for b in bash cat grep sed printf; do p="$(command -v "$b")"; [[ "$p" == /* ]] && ln -s "$p" "$nopy/$b"; done
printf '%s' '{"tool_name":"Edit","tool_input":{"file_path":"/repo/src/orders.ts"}}' | PATH="$nopy" "$(command -v bash)" "$hook" >/dev/null 2>&1; got=$?
if [[ "$got" == 2 ]]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: no Python at all blocks (expected 2, got $got)"; fi
rm -rf "$stub" "$nopy"

echo "hook tests: $pass passed, $fail failed"
[[ $fail -eq 0 ]]
