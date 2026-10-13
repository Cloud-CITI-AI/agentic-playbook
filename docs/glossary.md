# Glossary

Terms are defined once here and used consistently across the playbook.

| Term | Definition |
|---|---|
| Agent | An AI system that reads and edits code and runs commands with some autonomy (Claude Code, Cursor agent, Copilot coding/cloud agent, Codex, Devin-style agents). Inline autocomplete is not an agent. |
| Agent session | One continuous run of an agent against a task, from brief to PR. Identified by the tool's session or run ID, recorded in the PR. |
| Agent-authored PR | A PR where an agent wrote ≥ 50% of the diff, or opened the PR. Must carry the `agent-authored` label. |
| Agent-assisted change | A human-authored PR where an agent wrote < 50% of the diff. Trailer recommended, label optional. |
| Launching human | The person who wrote the task brief and started the agent session. Accountable for the PR until it merges. |
| Approving human | The reviewer whose approval satisfies the ruleset. For risk tier High, must differ from the launching human. |
| Task brief | The structured request given to an agent (`templates/agent-task-brief.md`). |
| Instruction file | A file an agent loads as standing context: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.cursor/rules/*.mdc`. |
| Managed file | A file copied from this playbook into a project repo, carrying a `managed-by: agentic-playbook` header. Overwritten on sync. |
| Repository-specific section | A delimited block inside a managed file that sync preserves, for local rules. |
| Rule ID | A stable identifier for an instruction-file rule (e.g. `A3`, `N2`, `FE-4`), used for overrides and lessons. |
| Lesson | An entry in `LESSONS.md` recording a human correction, revert or tweak of agent output. |
| Rule proposal (RP) | A PR to this repository that adds, changes or removes a rule, using `rule-proposals/README.md`. |
| Risk tier | Low / Medium / High classification of a change (section 5.2) that sets review depth and approvals. |
| Diff coverage | Percentage of changed executable lines exercised by tests in the PR. |
| Mutation score | Percentage of injected faults (mutants) that the tests detect. |
| Lethal trifecta | Agent access to private data + exposure to untrusted content + an exfiltration channel at the same time (Willison, 2025). |
| Kill switch | The documented set of actions that stops all agent activity org-wide within 15 minutes (section 10.5). |
| DORA five | Deployment frequency, change lead time, failed deployment recovery time, change fail rate, deployment rework rate. |
| Expand/contract | Migration pattern: add new schema (expand), migrate code and data, remove old schema (contract) in a later release. |
| Escaped defect | A defect found in production that was introduced by a change which passed all gates. |
