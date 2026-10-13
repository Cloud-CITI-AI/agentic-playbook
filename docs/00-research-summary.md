# 0. Research summary

Research window: sources dated 2024 to October 2026, accessed 2026-10-06. "Unverified" marks claims I could not confirm from a primary source. Vendor research is labelled as such because vendors sell the remedy for the problem they measure.

## 0.1 Agent instruction conventions

**Findings**
- AGENTS.md is the cross-tool standard. It was launched by OpenAI, Factory, Sourcegraph/Amp and Google in August 2025 and donated to the Linux Foundation's Agentic AI Foundation on 9 December 2025 (https://agentic-ai.readthedocs.io/en/latest/Standards/agents-md/ ; https://dev.to/dublecc/agentsmd-inside-the-open-standard-for-briefing-coding-agents-4fag, accessed 2026-10-06). Nested AGENTS.md files in subdirectories are supported for monorepos.
- Claude Code: reads `CLAUDE.md` by walking up from the working directory, concatenating rather than overriding; subdirectory files load on demand. Since v2.1.277 it can read `AGENTS.md` directly, but only when no `CLAUDE.md` exists on the path; the documented portable pattern is a `CLAUDE.md` whose first line is `@AGENTS.md`. Anthropic's guidance is to target under 200 lines per file, and it states plainly that CLAUDE.md is context, not enforcement: use hooks, permission rules and managed settings for anything that must hold (https://code.claude.com/docs/en/claude-md, accessed 2026-10-06).
- GitHub Copilot: reads `.github/copilot-instructions.md`, path-scoped `.github/instructions/**/*.instructions.md` (with `applyTo` globs), and `AGENTS.md` (root file treated as primary). Copilot CLI also reads `CLAUDE.md`. GitHub combines files but "does not define a general precedence order" (https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions, accessed 2026-10-06).
- Cursor: `.cursorrules` is legacy; project rules are `.cursor/rules/*.mdc` with `description`/`globs`/`alwaysApply` frontmatter; plain markdown goes in `AGENTS.md`, which Cursor reads natively; Team Rules apply before project rules (https://cursor.com/docs/rules, accessed 2026-10-06).
- Evidence on effectiveness: Gloaguen et al. (ETH Zurich / LogicStar, arXiv:2602.11988, Feb 2026) found LLM-generated context files reduced task success by about 3% and raised inference cost by over 20%; developer-written files gave about a 4% gain, also at higher cost. Directory overviews did not help agents find files faster (https://arxiviq.substack.com/p/evaluating-agentsmd-are-repository ; https://academy.dair.ai/blog/agents-md-evaluation, accessed 2026-10-06).

**Where sources disagree**
- Practitioner guides recommend rich AGENTS.md files (architecture overviews, directory maps); the ETH study says those sections add cost without benefit. Critics of the study note it covered Python repositories with niche tasks and argue it tested poor context rather than the concept (https://codex.danielvaughan.com/2026/04/13/what-eth-zurich-paper-gets-wrong-right-about-agents-md/, accessed 2026-10-06).
- Size budgets vary: Anthropic says under 200 lines per CLAUDE.md; community guides cite 500 lines for AGENTS.md. Neither is empirically derived.

**Decisions taken into the playbook**
1. `AGENTS.md` is canonical. `CLAUDE.md` is `@AGENTS.md` plus a short Claude-only section. Copilot gets a review-focused `copilot-instructions.md`. Cursor needs nothing extra. (ADR-0001)
2. Human-written, terse, command-first files only. Generated context files are forbidden. No directory maps or architecture essays in instruction files.
3. Budget: root ≤ 150 lines, package ≤ 80 lines, any loaded chain ≤ 250 lines. Enforced by `scripts/check-instruction-budget.sh`.
4. Anything that must hold is enforced outside the instruction file: CI, rulesets, CODEOWNERS, Claude Code hooks and managed settings. Instruction files describe the enforcement; they are not the enforcement.

## 0.2 Enterprise SDLC frameworks

**Findings**
- DORA now uses five metrics in two factors: throughput (deployment frequency, change lead time, failed deployment recovery time) and instability (change fail rate, deployment rework rate) (https://dora.dev/guides/dora-metrics/ ; https://dora.dev/guides/dora-metrics/history/, accessed 2026-10-06). "Four keys" in the brief is out of date; this playbook tracks all five.
- DORA 2025 (*State of AI-assisted Software Development*, Sept 2025, ~5,000 respondents): AI adoption ~90%; AI now correlates with higher throughput but still with higher instability; "AI amplifies what's already there". Its AI Capabilities Model names seven amplifying capabilities, including strong version control practices and working in small batches (https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report ; https://cloud.google.com/blog/products/ai-machine-learning/from-adoption-to-impact-putting-the-dora-ai-capabilities-model-to-work/, accessed 2026-10-06).
- Productivity evidence is mixed. METR's RCT (July 2025) found experienced open-source developers 19% slower with early-2025 tools while believing they were faster; METR's early-2026 follow-up leaned toward a speed-up but METR flagged it as unreliable; a Google RCT found ~21% speed-up on an enterprise task with wide intervals (https://larridin.com/blog/ai-vs-human-developer-productivity ; https://blog.codercops.com/blog/ai-coding-productivity-2x-not-10x-metr-2026, accessed 2026-10-06).

**Decisions**
1. Trunk-based development with short-lived branches (≤ 2 days), squash merge, PR titles in Conventional Commits 1.0.0, SemVer, release-please for human-approved releases. GitFlow rejected (long-lived branches multiply the large-batch problem DORA flags). (ADR-0003)
2. Small batches enforced mechanically: PR size gate (≤ 400 changed lines warn, ≤ 800 hard fail) and agent tasks scoped to one PR.
3. Measure, don't assume, productivity: the scorecard tracks DORA five plus agent-specific metrics; perceived speed is never a success criterion.
4. ADRs (Nygard format, MADR-compatible) for any decision that changes architecture, dependencies or a playbook rule.

## 0.3 Quality gates and testing

**Findings**
- AI-written tests can reach high line coverage while asserting little; mutation score exposes this (https://www.augmentcode.com/guides/mutation-testing-ai-generated-code, accessed 2026-10-06 — vendor). StrykerJS supports incremental mode for PR-scoped runs (https://oneuptime.com/blog/post/2026-01-25-mutation-testing-with-stryker/view, accessed 2026-10-06).
- CodeRabbit's December 2025 analysis reported AI-authored PRs carried ~1.7× more bugs than human PRs (cited via https://codex.danielvaughan.com/2026/04/21/mutation-testing-codex-cli-ai-generated-tests-quality-verification/ — vendor, secondary; unverified against the original).

**Where sources disagree**: test pyramid (many unit tests) vs testing trophy (integration-heavy, Kent C. Dodds). They optimise for different failure modes; neither is proven superior.

**Decisions**
1. Backend: pyramid-ish with real-database integration tests (Testcontainers) as the main confidence layer; no mocked database for repository code. Frontend: trophy-ish (component tests with Testing Library carry most weight; a thin layer of Playwright end-to-end).
2. Coverage gate on **changed lines** (diff coverage ≥ 80%), not global coverage. Global coverage is reported, never gated.
3. Mutation testing gate on changed domain-logic files (break < 60%, target ≥ 75%), incremental on PRs, full nightly.
4. Flaky tests: quarantine within 24 hours, fix or delete within 10 business days; retries are not a fix.

## 0.4 Security

**Findings**
- OWASP Top 10:2025 (announced Nov 2025, finalised Jan 2026) added A03 Software Supply Chain Failures and A10 Mishandling of Exceptional Conditions, and folded SSRF into A01 (https://owasp.org/Top10/2025/ ; https://www.fastly.com/blog/new-2025-owasp-top-10-list-what-changed-what-you-need-to-know, accessed 2026-10-06).
- OWASP ASVS 5.0.0 (May 2025): ~350 requirements, 17 chapters, three levels (https://github.com/OWASP/ASVS, accessed 2026-10-06).
- OWASP Top 10 for Agentic Applications 2026 (published 9 Dec 2025): ASI01 Agent Goal Hijack through ASI10 Rogue Agents; it extends, not replaces, the LLM Top 10 (https://cycode.com/blog/owasp-top-10-agentic-applications/ ; https://docs.modulos.ai/frameworks/owasp-top-10-agentic, accessed 2026-10-06).
- Veracode 2025 GenAI Code Security Report: across 80 tasks and 100+ models, generated code introduced OWASP Top 10 vulnerabilities in 45% of cases, and security performance was not improving with newer models (https://www.veracode.com/press-release/ai-generated-code-poses-major-security-risks-in-nearly-half-of-all-development-tasks-veracode-research-reveals/, accessed 2026-10-06 — vendor).
- Prompt injection through repository content is real: Invariant Labs showed a malicious public GitHub issue could steer an MCP-connected agent into leaking private-repo data via a public PR, an architectural rather than a code flaw (https://invariantlabs.ai/blog/mcp-github-vulnerability, May 2025). Simon Willison's "lethal trifecta" (private data + untrusted content + an exfiltration channel) is the clearest design rule (https://www.devclass.com/ai-ml/2025/05/27/researchers-warn-of-prompt-injection-vulnerability-in-github-mcp-with-no-obvious-fix/1623458).
- Supply chain: the tj-actions/changed-files tag-rewrite compromise (March 2025) and the Shai-Hulud npm worms (Sept and Nov 2025). GitHub now lets orgs enforce full-SHA pinning and block actions (https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/). pnpm 11 enables a 1-day `minimumReleaseAge` by default; npm 11.10+ has `min-release-age` (off by default); Renovate and Dependabot support cooldowns (https://github.com/nodejs/learn/pull/73 ; https://www.sqli.com/int-en/insights/pnpm-vs-shai-hulud-npm-security, accessed 2026-10-06).
- GitHub artifact attestations give SLSA v1.0 Build L2 by default and L3 with reusable-workflow isolation (https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds).
- Agent tool security: Claude Code's sandbox enforces filesystem and network isolation and can be mandated via managed settings (https://code.claude.com/docs/en/sandboxing). Copilot's cloud agent pushes only to `copilot/*` branches, its PR workflows need a write-access human to approve before running, and it is firewalled by default (https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations).

**Decisions**
1. ASVS 5.0 Level 2 is the baseline for every service; Level 3 for services handling payment, authentication or regulated personal data.
2. Supply chain: SHA-pinned actions (org policy on), pnpm with `minimumReleaseAge` ≥ 1440 min, `--frozen-lockfile`, lifecycle scripts blocked except an allowlist, Renovate with 7-day cooldown for non-security updates, SBOM + build provenance attestations on every release artifact.
3. Agents never hold the lethal trifecta. Concretely: agent sessions that read untrusted content (public issues, external PR comments, web pages) run with no secrets and egress restricted to an allowlist; agents never have production credentials.
4. Agents cannot approve, merge, edit their own instruction files, edit CI workflows or change security configuration. These are enforced by rulesets, CODEOWNERS and hooks, not by asking nicely.

## 0.5 CI/CD and deployment

**Decisions** (drawing on GitHub docs above, Google SRE practice and DORA capabilities; no single source decides these):
1. Pipeline order: fast, cheap and deterministic first (lint, typecheck, unit), then integration, security scans in parallel, build with provenance, end-to-end against an ephemeral environment, deploy.
2. Cloud access via OIDC federation only; no long-lived cloud keys in GitHub secrets.
3. Environments `preview → staging → production`; production requires a human approval via GitHub Environments; canary with automated SLO-based rollback.
4. Database migrations use expand/contract; destructive steps ship in a later release than the code that stops using the column; migrations linted (Squawk for Postgres).
5. OpenTelemetry for traces/metrics/logs; every service has SLOs and an error budget policy.

## 0.6 Code review in the agent era

**Findings**: Agent-authored PRs are accepted less often than human PRs. In the AIDev dataset (456k agent PRs, data to mid-2025), agent acceptance rates ranged roughly 35% to 64% against a human baseline of 76.8%, and task type strongly affects acceptance (documentation highest, new features lower) (https://www.alphaxiv.org/abs/2507.15003v1 ; https://arxiv.org/abs/2602.08915, accessed 2026-10-06). Researchers caution acceptance alone can mask maintenance burden.

**Decisions**: PRs carry evidence (tests run, screenshots for UI, migration plan, rollback plan, task brief link); two-key rule (agent-authored PR needs one human approval from someone other than the human who launched the agent for production-impacting paths); AI review bots are advisory and never count as an approval.

## 0.7 Where to store the playbook

**Decision** (ADR-0002): a dedicated, versioned `agentic-playbook` repository is the source of truth; managed files are vendored into each repo by a sync workflow that opens PRs; the org `.github` repository holds default community-health files; reusable workflows are called by pinned SHA; org rulesets enforce required checks. Backstage TechDocs may render the handbook for discovery but is not authoritative. Full evaluation in `docs/02-repository-and-storage-model.md`.

## 0.8 Self-regulation and learning loops

**Findings**: Anthropic's own guidance is to add to CLAUDE.md when the agent makes the same mistake twice or a review catches something it should have known, and to prune periodically (https://code.claude.com/docs/en/claude-md). Claude Code's auto memory is machine-local and not shared, so it cannot be the team's learning store. No primary source describes a validated enterprise "lessons loop"; the design in section 10 is our own and should be treated as an experiment with metrics.

**Decisions**: `LESSONS.md` append-only log in each repo; weekly digest; promotion threshold (3 occurrences in 30 days, or 1 security/incident); rule proposals reviewed by humans, validated by evals, released via SemVer; quarterly prune.
