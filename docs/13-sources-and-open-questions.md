# 13. Sources and open questions

All accessed 2026-10-06 unless stated. Type: P = primary (standard body, vendor docs, paper), S = secondary, V = vendor research.

## 13.1 Sources

| # | Source | Type | Used for |
|---|---|---|---|
| 1 | Anthropic, "How Claude remembers your project", https://code.claude.com/docs/en/claude-md | P | CLAUDE.md loading, AGENTS.md interplay, 200-line guidance, managed settings, hooks |
| 2 | Anthropic, Claude Code sandboxing, https://code.claude.com/docs/en/sandboxing | P | AG-3, AG-4 |
| 3 | GitHub Docs, custom instructions for Copilot CLI, https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions | P | Copilot file loading |
| 4 | GitHub Docs, risks and mitigations for Copilot cloud agent, https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations | P | AG-7, AG-8 |
| 5 | Cursor Docs, Rules, https://cursor.com/docs/rules | P | Cursor loading |
| 6 | AGENTS.md / Agentic AI Foundation, https://agents.md ; https://agentic-ai.readthedocs.io/en/latest/Standards/agents-md/ | P/S | Standard status |
| 7 | Gloaguen et al., "Evaluating AGENTS.md", arXiv:2602.11988 (Feb 2026), summaries at https://academy.dair.ai/blog/agents-md-evaluation | P/S | Budgets, no generated files |
| 8 | Vaughan, critique of the ETH paper, https://codex.danielvaughan.com/2026/04/13/what-eth-zurich-paper-gets-wrong-right-about-agents-md/ | S | Disagreement |
| 9 | DORA metrics guide and history, https://dora.dev/guides/dora-metrics/ ; https://dora.dev/guides/dora-metrics/history/ | P | Five metrics |
| 10 | Google Cloud, 2025 DORA report announcement and AI Capabilities Model, https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report | P | AI amplifies; small batches |
| 11 | METR RCT (July 2025) and follow-up summaries, https://larridin.com/blog/ai-vs-human-developer-productivity | P/S | Productivity evidence |
| 12 | OWASP Top 10:2025, https://owasp.org/Top10/2025/ | P | Risk mapping |
| 13 | OWASP ASVS 5.0.0 (May 2025), https://github.com/OWASP/ASVS | P | Control baseline |
| 14 | OWASP Top 10 for Agentic Applications 2026 (Dec 2025), summary https://docs.modulos.ai/frameworks/owasp-top-10-agentic | P/S | Agent risks |
| 15 | Veracode 2025 GenAI Code Security Report press release, https://www.veracode.com/press-release/ai-generated-code-poses-major-security-risks-in-nearly-half-of-all-development-tasks-veracode-research-reveals/ | V | AI code security rate |
| 16 | Invariant Labs, GitHub MCP exploit (May 2025), https://invariantlabs.ai/blog/mcp-github-vulnerability | P | Prompt injection via issues |
| 17 | DevClass on the lethal trifecta, https://www.devclass.com/ai-ml/2025/05/27/researchers-warn-of-prompt-injection-vulnerability-in-github-mcp-with-no-obvious-fix/1623458 | S | AG-6 |
| 18 | GitHub changelog, SHA pinning enforcement (2025-08-15), https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/ | P | SCS-1 |
| 19 | GitHub Docs, artifact attestations, https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds | P | SLSA levels |
| 20 | Node.js docs PR on `min-release-age`, https://github.com/nodejs/learn/pull/73 ; pnpm vs Shai-Hulud, https://www.sqli.com/int-en/insights/pnpm-vs-shai-hulud-npm-security | P/S | DP-3 |
| 21 | AIDev dataset (Li et al., July 2025), https://www.alphaxiv.org/abs/2507.15003v1 ; Pinna et al., arXiv:2602.08915 | P | Agent PR acceptance |
| 22 | Mutation testing for AI-generated tests, https://www.augmentcode.com/guides/mutation-testing-ai-generated-code | V | Mutation gate rationale |
| 23 | Conventional Commits 1.0.0, SemVer 2.0.0, Keep a Changelog 1.1.0, RFC 9457 | P | Conventions |
| 24 | Google, Core Web Vitals thresholds, https://web.dev/articles/vitals | P | FA-5 |
| 25 | GitHub Docs, required workflows deprecated in favour of rulesets, https://docs.github.com/actions/using-workflows/required-workflows | P | §2.3 |

## 13.2 Unverified or weakly evidenced

| Claim | Status |
|---|---|
| CodeRabbit (Dec 2025): AI PRs carry ~1.7× more bugs | Seen only via secondary source; vendor; not used for any threshold |
| Size budgets (150/80/250 lines) | Judgement anchored on Anthropic guidance; no empirical optimum exists |
| Mutation break threshold 60% | Common practice; no study ties it to defect rates |
| Exact Claude Code `settings.json` sandbox keys and permission-rule syntax | Verified at concept level; confirm key names against the current settings reference before rollout (docs move quickly) |
| pnpm 11 `allowBuilds` vs pnpm 10 `onlyBuiltDependencies` | Version-dependent; check your pnpm version |
| Org ruleset "require workflows" availability | Plan-dependent (Team vs Enterprise Cloud) |
| Action major versions in templates (`checkout@v4` etc.) | Deliberately conservative; Renovate will propose current majors and pins |

## 13.3 Open questions for the organisation

1. Which cloud provider(s)? The deploy workflow is cloud-agnostic; the OIDC and canary steps need concrete commands.
2. Do we allow agents to work on High-tier paths at all in phase 2, or only humans with agent assistance?
3. Who funds and operates the eval suite (model spend, a maintained fixture repo)?
4. Transcript retention: vendor platform or export to our audit store? Legal and privacy need to decide.
5. Should agent PR metrics be visible per launching human? Recommendation: no (team level only) to avoid gaming.
6. GraphQL usage: any existing BFFs that need the GQL rules immediately?
7. Is GitHub Enterprise Cloud in place (affects rulesets, audit-log streaming, Copilot policy granularity)?
