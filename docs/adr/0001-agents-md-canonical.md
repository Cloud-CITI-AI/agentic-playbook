# ADR-0001: AGENTS.md is the canonical agent instruction file

- Status: accepted · Date: 2026-10-06 · Deciders: @org/platform-eng, @org/security

## Context
We use several agents (Claude Code, Copilot, Cursor, Codex). Each has its own file conventions. Duplicated rules drift. AGENTS.md is now a Linux Foundation-hosted standard read natively by Copilot, Cursor and Codex. Claude Code reads AGENTS.md only when no CLAUDE.md exists on the path, and supports `@AGENTS.md` imports. Research shows generated or bloated context files lower success and raise cost.

## Decision
`AGENTS.md` (root and per package) is the single source of agent rules. `CLAUDE.md` contains `@AGENTS.md` plus ≤ 40 lines of Claude-specific rules. `.github/copilot-instructions.md` covers Copilot review focus only. No `.cursorrules`; `.cursor/rules/*.mdc` only for glob-scoped rules. Files are human-written and within budget.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| AGENTS.md canonical + thin tool shims (chosen) | One source, standard, portable | Some tools may load root rules twice (token cost) |
| CLAUDE.md canonical, symlink AGENTS.md | Simplest for Claude | Symlinks break on Windows clones; other tools are the majority |
| Separate files per tool | Tool-specific tuning | Drift, contradictions, triple maintenance |

## Consequences
Budget script enforces sizes and the import line. Tool-specific behaviour must be justified as genuinely tool-specific.

## Compliance check
`scripts/check-instruction-budget.sh` (import line, budgets, anti-patterns) in `playbook-guard`.
