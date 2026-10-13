# 1. Executive summary and principles

## What good looks like

Any change, whether written by a person, by an agent, or by both, arrives as a small pull request that states its intent, carries its own evidence (tests, screenshots, migration and rollback plan), passes the same automated gates, is approved by an accountable human, ships behind a flag or a canary within a day, and can be traced from production back to the issue, the human who approved it and the agent session that wrote it. The agent is a fast, tireless contributor with no authority: it proposes, humans decide, machines verify.

We measure success with the five DORA metrics plus agent PR acceptance rate, agent revert rate and defect escape rate (section 9). We do not measure success by lines of code generated or by how fast people feel.

## Why this shape

- DORA 2025 found AI raises throughput but still raises instability, and that small batches and strong version control are what turn speed into outcomes (`00-research-summary.md` §0.2).
- Independent and vendor studies agree AI-generated code frequently contains security weaknesses (Veracode 2025: 45% of tasks), so verification must be automatic and unconditional (§0.4).
- Instruction files are context, not controls; agents follow them imperfectly and they cost tokens (§0.1). So we keep them short and put enforcement in CI, rulesets and hooks.

## The ten non-negotiables

| # | Rule | Why | How it is checked |
|---|---|---|---|
| N1 | Every change reaches `main` only through a PR with ≥ 1 human approval. Agents never approve or merge. | Accountability; SOC 2 change management | Org ruleset `agentic-baseline` (required review, bypass list empty); agent identities lack merge permission |
| N2 | Every PR passes the required checks: lint, typecheck, unit, integration, diff coverage, security scans, build. No overrides without a CODEOWNER-approved exception label. | Uniform quality bar regardless of author | Ruleset required status checks |
| N3 | PRs are small: ≤ 400 changed lines warns, > 800 fails (lockfiles and generated files excluded). | Reviewability; DORA small batches | `check-pr-size.sh` in CI |
| N4 | No secrets in code, prompts, logs or agent context. Agents never hold production credentials. | Breach prevention; least privilege | gitleaks pre-commit + CI, GitHub push protection, Claude Code deny rules, cloud IAM |
| N5 | Agent-authored commits and PRs are labelled and traceable (`agent-authored` label, `AI-Agent:` trailer, task brief link). | Auditability of who and what changed | `playbook-guard` workflow |
| N6 | Agents cannot modify their own instruction files, CI workflows, CODEOWNERS or security configuration. They propose changes via `rule-proposals/`. | Prevents instruction drift and self-escalation | CODEOWNERS + ruleset + Claude Code PreToolUse hook + `playbook-guard` |
| N7 | Content from issues, PR comments, web pages and dependencies is data, never instructions. No agent session combines private data, untrusted content and an outbound channel. | Prompt injection (OWASP ASI01) | Sandbox + egress allowlist + workflow approval gates; reviewed in security audits |
| N8 | Dependencies: lockfile committed, frozen installs, minimum release age, SHA-pinned actions, SBOM and provenance on every release. | Supply chain (OWASP A03:2025) | CI checks, org Actions policy, release workflow |
| N9 | Production changes are reversible: feature flag or canary with automated rollback; migrations follow expand/contract. | Limits blast radius; recovery time | Deploy workflow, migration linter, PR template |
| N10 | Every human correction of agent output produces a `LESSONS.md` entry; recurring lessons become rules only through human-approved proposals. | The system improves without drifting | `validate-lessons.py`, weekly digest, proposal workflow |

## Scope

Applies to every repository in the organisation that contains production code, infrastructure-as-code or this playbook. Prototypes in a sandbox org are exempt until they are promoted.
