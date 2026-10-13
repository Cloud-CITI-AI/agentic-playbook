#!/usr/bin/env bash
# managed-by: agentic-playbook v1.2.0
# PreToolUse hook: blocks agent edits to protected paths (rule X1) and existing LESSONS.md entries.
# Exit 2 = block; stderr is shown to the agent. Exit 0 = allow.
# Defence in depth only: CODEOWNERS, rulesets and the playbook-guard workflow are the real controls.
# Works on Linux, macOS and Windows (Git Bash): Bash and PowerShell tool calls, Windows paths.
set -euo pipefail

block() {
  echo "BLOCKED by playbook rule X1: '$1' is a protected path. Do not retry via another tool. Describe the change you need under 'Rule proposal' in the PR description." >&2
  exit 2
}

# A Python that actually runs. On Windows, `python3` is often the Microsoft Store placeholder,
# which exits 49; fall back to `python` or `py`. Without Python the hook cannot check anything,
# so it fails closed instead of letting every call through.
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import json, os' >/dev/null 2>&1; then PY="$c"; break; fi
done
if [[ -z "$PY" ]]; then
  echo "BLOCKED: the instruction-file protection hook needs Python 3 (python3, python or py) and found none. Ask a human to install Python; do not work around this hook." >&2
  exit 2
fi

input="$(cat)"
# field <name>: prints one normalised field of the hook input (backslashes become forward slashes).
field() {
  printf '%s' "$input" | "$PY" -c '
import json, os, sys
d = json.load(sys.stdin)
t = d.get("tool_input") or {}
what = sys.argv[1]
if what == "tool":
    print(d.get("tool_name", ""))
elif what == "command":
    print((t.get("command") or "").replace("\\", "/"))
elif what == "path":
    p = (t.get("file_path") or t.get("notebook_path") or "").replace("\\", "/")
    root = (os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).replace("\\", "/").rstrip("/")
    if root and p.lower().startswith(root.lower() + "/"):
        p = p[len(root) + 1:]
    print(p)
' "$1"
}

tool="$(field tool)" || block "<unreadable hook input>"

# Protected paths (case-insensitive: Windows and macOS file systems usually are).
PROTECTED_PATH='(^|/)(AGENTS\.md|CLAUDE\.md|CODEOWNERS|renovate\.json)$|(^|/)\.(github|claude|cursor)(/|$)|(^|/)infra/prod(/|$)'
PROTECTED_IN_CMD='(AGENTS\.md|CLAUDE\.md|CODEOWNERS|renovate\.json|\.github\b|\.claude\b|\.cursor\b|infra/prod\b|LESSONS\.md)'
# Write-capable commands: Bash, then PowerShell cmdlets and their aliases, then .NET file writes.
WRITES='(>|\btee\b|\bsed\b.*-i|\bperl\b.*-i|\bmv\b|\bcp\b|\brm\b|\bln\b|\btruncate\b|\bgit +(checkout|restore|rm|mv)\b|\b(Set-Content|Add-Content|Out-File|New-Item|Remove-Item|Move-Item|Copy-Item|Rename-Item|Clear-Content|sc|ac|ni|ri|del|erase|rd|rmdir|move|copy|cpi|mi|ren|rni|clc)\b|\[(System\.)?IO\.File\])'
# The one allowed write to a protected file: appending a new entry to LESSONS.md (Python regex).
LESSONS_APPEND='(>>\s*|\b(Add-Content|ac)\s+(-Path\s+)?)["'"'"']?(\./)?LESSONS\.md["'"'"']?'

if [[ "$tool" == "Bash" || "$tool" == "PowerShell" ]]; then
  cmd="$(field command)" || block "<unreadable command>"
  if printf '%s' "$cmd" | grep -Eqi "$WRITES" && printf '%s' "$cmd" | grep -Eqi "$PROTECTED_IN_CMD"; then
    # Allow a pure append to LESSONS.md: nothing else writes, and no other protected path is named.
    # Python, not sed: BSD sed (macOS) has no case-insensitive flag.
    rest="$(printf '%s' "$cmd" | "$PY" -c 'import re, sys; sys.stdout.write(re.sub(sys.argv[1], "", sys.stdin.read(), flags=re.I))' "$LESSONS_APPEND")"
    if [[ "$rest" != "$cmd" ]] && ! printf '%s' "$rest" | grep -Eqi "$WRITES" \
       && ! printf '%s' "$cmd" | grep -Eqi '(AGENTS\.md|CLAUDE\.md|CODEOWNERS|renovate\.json|\.github\b|\.claude\b|\.cursor\b|infra/prod\b)'; then
      exit 0
    fi
    block "$cmd"
  fi
  exit 0
fi

rel="$(field path)" || block "<unreadable path>"

if printf '%s' "$rel" | grep -Eqi "$PROTECTED_PATH"; then
  block "$rel"
fi

# LESSONS.md: Write (full overwrite) is blocked; Edit is allowed only if old_string is empty-ish append at the end.
if printf '%s' "$rel" | grep -Eqi '(^|/)LESSONS\.md$'; then
  if [[ "$tool" == "Write" ]]; then
    block "$rel (use an append, not a full rewrite)"
  fi
  # For Edit/MultiEdit, CI (validate-lessons.py) verifies existing entries are unchanged.
fi
exit 0
