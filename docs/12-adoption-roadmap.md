# 12. Adoption roadmap

## 12.1 Phases

| Phase | Duration | Scope | Exit criteria (measured) |
|---|---|---|---|
| 0 Foundations | 2 to 3 weeks | Org settings (§2.6), agent identities, managed settings via MDM, playbook v1.0 released, eval suite with ≥ 10 tasks, baseline DORA and PR metrics captured for pilot repos (pre-adoption) | Settings audit passes; kill switch rehearsed once; baseline metrics recorded |
| 1 Pilot | 6 to 8 weeks | 2 to 3 teams, 3 to 5 repos (selection §12.2); playbook enforced; agents used for Low/Medium tiers only | Agent acceptance ≥ 50%; revert ≤ 8%; change fail rate not worse than baseline; ≥ 15 LESSONS entries; ≥ 2 RPs decided; developer survey ≥ 3.5/5 on "the rules help" |
| 2 Expand | 8 to 12 weeks | All teams on the primary stacks; High tier allowed with plan approval; reusable workflows mandatory via ruleset | 80% of active repos on current MAJOR; required checks on all default branches; agent revert ≤ 5%; review turnaround ≤ 8 h |
| 3 Optimise | ongoing | SLSA Build L3, full eval suite monthly, cross-repo lesson aggregation, quarterly prunes | Phase 3 targets in §9.1 trending green for two consecutive quarters |

Rollback criterion for any phase: if change fail rate or escaped defects rise > 25% over baseline for two consecutive months in adopted repos, pause expansion and run a review.

## 12.2 Pilot selection criteria

| Criterion | Want | Avoid |
|---|---|---|
| Test health | Existing CI with reasonable tests | Repos with no tests (agents can't verify) |
| Criticality | Medium business criticality | Payment core, auth, anything with active incidents |
| Team | Volunteer team with a tech lead who will curate LESSONS | Teams under deadline pressure |
| Stack | Matches a profile (Next.js, Node, Python) | Exotic stacks (no profile yet) |
| Change volume | ≥ 10 PRs/week (enough data) | Dormant repos |
| Mix | At least one frontend and one backend repo | All-frontend or all-backend pilots |

## 12.3 Training

| Audience | Format | Content | Completion check |
|---|---|---|---|
| All engineers | 90-min workshop + recorded | Non-negotiables, task briefs, reviewing agent PRs (RV-1 to RV-9), LESSONS, kill switch awareness | Short quiz; first agent PR reviewed with a coach |
| Tech leads | 2-h session | Adoption steps, REPO-SPECIFIC blocks, lessons triage, RP process, metrics | Repo adopted |
| Reviewers of High tier | 1-h session | Security checklist, agent-specific risks, prompt-injection examples | Paired review |
| Security / platform | Half day | Managed settings, eval suite, kill switch rehearsal | Rehearsal executed |

Writing good task briefs is a skill, and teaching it is the highest-return training item.

## 12.4 Communication

Monthly playbook release notes; a `#agentic-playbook` channel; office hours weekly in phase 1; scorecards shared with teams, not used for individual performance evaluation (doing so would incentivise gaming the label and the metrics).
