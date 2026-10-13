# 14. Self-review against the quality bar, and known gaps

## 14.1 Quality bar

| Criterion (from the brief) | Assessment | Evidence |
|---|---|---|
| Specific over generic: every rule states what, why, how checked | Met for rules in sections 4 to 10 (tables with a "Check" column). Partly met for a few review-only rules (naming, scope creep) where no reliable automation exists; they are labelled "Review". | docs/04 to 10 |
| Machine-followable instruction files | Met: imperative rules with IDs, exact commands, explicit Always/Never, conflict behaviour ("stop and ask"), placeholders that CI refuses to ship. Tested: budgets, sync check, tamper detection. | templates/**/AGENTS.md; scripts tested on a scratch repo |
| Opinionated with rationale; alternatives mentioned | Met: ADR-0001 to 0004 plus options tables in docs/02, 05, 06. | docs/adr |
| Consistent terminology, one glossary | Met; cross-references corrected to section numbers. | docs/glossary.md |
| Enterprise: auditability, traceability, least privilege | Met in design (§7.6, §7.7, N1 to N10); depends on org settings being applied (§2.6). | docs/07 |
| Complete rather than short | All 13 required sections present plus research summary, glossary, ADRs and self-review. Some implementation pieces are skeletons (see gaps). | this repo |
| Sources cited with dates; disagreements noted; unverified flagged | Met. | docs/00, docs/13 |

## 14.2 What was tested

| Component | Test |
|---|---|
| Protection hook | 12 deterministic cases (`evals/hook-tests.sh`), all pass |
| Bootstrap / check / apply | Scratch repo: bootstrap root + 3 profiles; placeholder warnings vs errors by enforce mode; tamper in managed file detected; apply to new version preserves filled placeholders and REPO-SPECIFIC blocks |
| Instruction budgets | All template chains within budget (root 52/150; packages 24 to 30/80; CLAUDE.md 7/40) |
| PR size gate | Agent 500-line PR fails; human 500-line PR warns |
| LESSONS validation | Schema pass; edit to existing entry rejected; digest flags security-severity lesson for promotion |
| Workflows | All YAML parses; not executed on GitHub (no org available) |
| Shell scripts | shellcheck clean at warning level |

## 14.3 Known gaps (explicit)

| # | Gap | Impact | Suggested fix / owner |
|---|---|---|---|
| G1 | Version-lag enforcement (warn 30 days / fail 60 days, docs/02 §2.5) is specified but not implemented in `playbook_sync.py check` | Repos can lag silently apart from weekly sync PRs | Add a release-date lookup via `gh release list`; platform-eng |
| G2 | Eval fixture repo and hidden tests not built; harness adapters exist only for Claude Code and Codex CLIs | Eval gate (docs/10 §10.4) cannot run yet | Build fixture repo in phase 0; budget model spend |
| G3 | Deploy workflow has cloud-agnostic placeholders (OIDC login, canary, rollback) | Needs per-platform implementation | Decide cloud (open question 1) |
| G4 | Claude Code `settings.json` key names and permission-rule syntax verified at concept level only; vendor docs change often | A wrong key may be ignored silently | Verify against the current settings reference before rollout; test with `/permissions` and `/sandbox` |
| G5 | Hook Bash detection is heuristic (e.g. `python -c` writing a file is not caught) | Defence in depth only | CODEOWNERS + ruleset + `playbook-guard` remain authoritative (ADR-0004) |
| G6 | Python profile references project-specific helpers not provided: `scripts/export_openapi.py`, `scripts/mutation_gate.py`; mutmut runs on the whole domain, not changed files | Python repos must add them at adoption | Add reference implementations in v1.1 |
| G7 | commitlint config, ESLint/Ruff shared configs and Squawk config are referenced but not shipped as packages | Each repo configures its own in phase 1 | Publish `@org/eslint-config`, `@org/commitlint-config` |
| G8 | Cross-repo lesson aggregation is manual (per-repo digests only) | Platform team must read digests | Org-level aggregation job reading LESSONS.md via API, v1.1 |
| G9 | DORA five collection pipeline not included (only agent PR metrics) | Scorecard needs a data source | Adopt Four Keys or a vendor; map definitions in docs/09 |
| G10 | release-please config assumes Node release type | Python packages need `release-type: python` | Adjust per package at adoption |
| G11 | GraphQL rules are in docs only; no template or CI step (graphql-inspector) | Only matters for GraphQL repos | Add when the first GraphQL BFF adopts |
| G12 | Agent-assisted work done in IDEs without a trailer is undetectable | Under-counts agent involvement | Accepted; disclosure field in PR template plus culture |
| G13 | Action versions are conservative majors; must be SHA-pinned at adoption (`pinact run`) | Org SHA policy fails unpinned workflows | Bootstrap prints the step; Renovate maintains pins |
| G14 | No primary source validates the LESSONS promotion thresholds or eval gate margins | Thresholds may be wrong | Review after phase 1 using data |
