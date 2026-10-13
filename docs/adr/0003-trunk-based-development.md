# ADR-0003: Trunk-based development with small, squash-merged PRs

- Status: accepted · Date: 2026-10-06 · Deciders: @org/platform-eng

## Context
DORA 2025: AI raises throughput and instability; small batches and strong version control are the capabilities that convert speed into outcomes. Agents generate large diffs easily.

## Decision
Single `main`; branches ≤ 2 days; squash merge; Conventional Commit PR titles; PR size gate (agent PRs ≤ 400 lines, others fail > 800); feature flags for incomplete work; merge queue for busy repos.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Trunk-based (chosen) | Small batches, fast integration, simple | Requires flags discipline |
| GitFlow | Familiar release staging | Long-lived branches, big merges, slow feedback |
| Release branches per version | Supports multiple supported versions | Only needed for shipped software with LTS; add per-repo by ADR |

## Consequences
Feature-flag hygiene becomes essential (flag owners, removal dates). Libraries with LTS lines may add release branches via a repo ADR.

## Compliance check
Ruleset (linear history, no direct push), `check-pr-size.sh`, PR title lint, stale-branch report.
