# Rule proposals

A rule proposal (RP) is the only way a playbook rule is added, changed or removed (docs/10 §10.3). Agents may draft an RP; only humans approve it.

## Process
1. Copy the template below to `rule-proposals/RP-NNNN-short-title.md` (next free number) on a branch.
2. Include the exact text change to the affected file(s) in the same PR.
3. CI runs the budget check; a platform engineer triggers the eval run and pastes the summary.
4. Approval: `@org/platform-eng`, plus `@org/security` for anything touching X-rules, security, agent controls, workflows or scripts.
5. On merge, set `Status: accepted` and the target release. After 30 days in production, append the verification result.

## Decision criteria
| Criterion | Required |
|---|---|
| Evidence: ≥ 3 lessons in 30 days, an incident, a metric regression, or a new external standard | Yes |
| Can it be a check instead of an instruction? (lint, test, hook, ruleset) If yes, do that and skip the instruction | Considered and answered |
| Rule is imperative, has an ID, and states its check | Yes |
| Instruction budget still met | Yes (CI) |
| Eval: no regression > 5 pp; no new security-probe failure | Yes |
| Owner and review date | Yes |

## Template

```markdown
# RP-NNNN: <title>

- Status: proposed | accepted | rejected | retired
- Proposer: @handle (drafted by: human | agent/<model> launched by @handle)
- Affects: templates/backend-node/AGENTS.md (BE-5), docs/04-development-standards.md §4.9
- Change type: add | tighten | relax | remove | enforcement-only
- Target release: vX.Y.Z (MAJOR/MINOR/PATCH per CHANGELOG semantics)
- Owner / review date: @handle / YYYY-MM-DD

## Evidence
- Lessons: L-20261001-missing-tenant-scope (repo-a), L-… (repo-b), L-…
- Metrics / incidents: …

## Proposed text
Exact before/after lines.

## Enforcement
How compliance is checked (CI step, lint rule, hook, review checklist item). "Review only" needs a justification.

## Alternatives considered

## Eval result
Baseline vX.Y.Z vs candidate: pass rate __% → __% (n tasks × 3 runs), security probes: __/__ unchanged.

## Verification after 30 days
Recurrence of the lesson / metric change.
```
