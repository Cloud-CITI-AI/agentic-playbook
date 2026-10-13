# 9. Quality bar: what good looks like

## 9.1 Rubric

Targets are set per phase of adoption (section 12). "Elite" bands are our targets, informed by but not copied from DORA benchmarks, which change yearly and are self-reported.

| Metric | Definition | Source | Phase 1 (pilot) | Phase 3 (target) |
|---|---|---|---|---|
| Deployment frequency | Production deploys per service per week | Deployment events (GitHub Environments) | ≥ 2/week | ≥ daily |
| Change lead time | Median first commit → production | Git + deployments | ≤ 3 days | ≤ 1 day |
| Change fail rate | % deploys needing rollback, hotfix or flag-off within 24 h | Deployments + incidents | ≤ 20% | ≤ 10% |
| Failed deployment recovery time | Median time from failed deploy to restored service | Incidents | ≤ 4 h | ≤ 1 h |
| Deployment rework rate | % deploys that are unplanned fixes for production issues | Deploys labelled `hotfix`/`incident` | ≤ 20% | ≤ 10% |
| Defect escape rate | Escaped defects / total defects found (per month) | Bug form "Found in production?" | ≤ 25% | ≤ 10% |
| Agent PR acceptance rate | Merged / closed agent PRs (30 days) | `scripts/agent-metrics.py` | ≥ 50% | ≥ 70% (human baseline in public data ≈ 77%) |
| Agent revert rate | Agent PRs reverted within 14 days of merge / merged agent PRs | same | ≤ 8% | ≤ 3% |
| Agent vs human escaped defects | Escaped defects per 100 merged PRs, split by authorship | Bug form "Introducing PR" + label | Measured | Agent ≤ human |
| Review turnaround | Median hours to first human review | metrics script | ≤ 8 business h | ≤ 4 business h |
| Review rounds | Median CHANGES_REQUESTED + 1 | metrics script | ≤ 3 | ≤ 2 |
| Median PR size | Changed lines | metrics script | ≤ 400 | ≤ 250 |
| Lessons → rules latency | Days from promotion candidate to decided RP | Playbook repo | ≤ 30 | ≤ 14 |
| Flake rate | Flaky runs / runs | CI | ≤ 3% | ≤ 1% |

Anti-goals (never targets): lines of code, number of agent PRs, % of code written by AI, self-reported speed-up. Optimising these produces large, low-value PRs. Public evidence on productivity is mixed (section 0.2); outcomes are what we measure.

## 9.2 Example scorecard (monthly, per team)

| Metric | Target | Value | Trend | Status |
|---|---|---|---|---|
| Deploy frequency | ≥ daily | 4.2/week | ↑ | 🟡 |
| Lead time | ≤ 1 day | 1.6 days | ↓ | 🟡 |
| Change fail rate | ≤ 10% | 7% | → | 🟢 |
| Recovery time | ≤ 1 h | 38 min | ↓ | 🟢 |
| Rework rate | ≤ 10% | 12% | ↑ | 🔴 investigate |
| Defect escape | ≤ 10% | 9% | → | 🟢 |
| Agent acceptance | ≥ 70% | 64% (n=47) | ↑ | 🟡 |
| Agent revert (14d) | ≤ 3% | 4.3% (2/46) | → | 🟡 |
| First review | ≤ 4 h | 5.5 h | ↑ | 🟡 |
| Median PR size | ≤ 250 | 210 | ↓ | 🟢 |

Notes field (required when any row is red): cause, owner, action, due date. Small samples (n < 20) are reported but not judged.

## 9.3 Measurement notes and limitations

- Agent detection relies on the `agent-authored` label and bot identities; agent-assisted human PRs are not counted as agent PRs. `playbook-guard` enforces the label when a trailer is present, which limits under-counting.
- Revert detection matches "Revert" PRs referencing the PR number or merge SHA within 14 days; fix-forward commits are not counted (rework rate covers them partly). Treat as a lower bound.
- Acceptance rate is confounded by task type (documentation tasks are accepted far more often than features in public data). Compare like with like using issue labels.
- DORA metrics come from deployment and incident data, not surveys. Use the Four Keys-style pipeline or the vendor of choice; definitions above are authoritative for us.
