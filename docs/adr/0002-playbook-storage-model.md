# ADR-0002: Dedicated playbook repository with vendored managed files

- Status: accepted · Date: 2026-10-06 · Deciders: @org/platform-eng

## Context
Agents only read files present in the repository they work in. Enforcement must not depend on project repos keeping copies honest. We need versioning, auditability and an update path.

## Decision
Source of truth: `<org>/agentic-playbook` (SemVer releases). Managed files are vendored into project repos by `bootstrap.sh` and updated by the `playbook-sync` workflow (PR per release). Org-level enforcement through rulesets, Actions policy and reusable workflows pinned by SHA. The org `.github` repo supplies default community-health files; Backstage renders docs for discovery.

## Options considered
See `docs/02-repository-and-storage-model.md` §2.2 (template repo only, submodule, package, org `.github` only, portal, wiki).

## Consequences
Weekly sync PRs add review load (mitigated by small releases). Local rules live only inside REPO-SPECIFIC blocks. A GitHub App (`playbook-bot`) is required to open sync PRs.

## Compliance check
`sync.sh --check` in `playbook-guard`; version-lag warnings; adoption dashboard from `.playbook-version` across repos.
