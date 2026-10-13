# AGENTS.md — agentic-playbook repository

This repository defines the rules other agents follow. Changes here affect every repo in the organisation, so the bar is higher than usual.

## Commands
| Purpose | Command |
|---|---|
| Validate everything | `python3 -m py_compile scripts/*.py && shellcheck scripts/*.sh && bash evals/hook-tests.sh` |
| Check template budgets | see `.github/workflows/playbook-ci.yml` step "Template instruction budgets" |
| Run seed evals | `bash evals/run-evals.sh --tasks seed --agent <agent>` |

## Always
- PB-1. Any change to a rule (anything under `templates/**/AGENTS.md`, `CLAUDE.md`, Copilot instructions, `.claude/`, or the non-negotiables) must come with a rule proposal file in `rule-proposals/` (see its README). Draft it; humans decide.
- PB-2. Keep docs and templates consistent: if you change a rule ID, threshold or script name, update every reference (`grep -rn` the ID) in the same PR.
- PB-3. Cite sources with URL and access date for any factual claim; mark unverified claims as unverified.
- PB-4. Scripts: Python standard library (PyYAML allowed), bash with `set -euo pipefail`; add or update a test in `evals/hook-tests.sh` or a fixture when behaviour changes.
- PB-5. Add an entry under `## [Unreleased]` in `CHANGELOG.md` referencing the RP number.

## Never
- PB-X1. Never edit this file, `CLAUDE.md`, `CODEOWNERS` or `.github/` (protected; propose instead).
- PB-X2. Never relax a security rule (X*, AG-*, SCS-*, SE-*) without an RP approved by security; never mark an X rule "overridable".
- PB-X3. Never generate instruction-file content in bulk; write each rule deliberately and keep budgets.
- PB-X4. Never add a dependency to scripts beyond the standard library and PyYAML.
