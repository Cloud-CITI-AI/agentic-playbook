# Changelog

All notable changes to the playbook are documented here. Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer 2.0.0](https://semver.org/).

Version semantics for the playbook:
- **MAJOR**: a rule becomes stricter in a way that can fail existing compliant repos (new required check, lower threshold), or a managed file moves.
- **MINOR**: new optional guidance, new template, new rule that is warn-only for one release.
- **PATCH**: wording, typo, link fix, no behavioural change for agents or CI.

Every entry that changes agent behaviour must reference its rule proposal (`RP-NNNN`) and the eval run that validated it.

## [Unreleased]

## [1.0.0] - 2026-10-06
### Added
- Initial handbook (sections 0 to 14), glossary, ADR-0001 to ADR-0004.
- Managed project templates: root `AGENTS.md`, `CLAUDE.md`, `LESSONS.md`, PR and issue templates, CODEOWNERS, CI/security/release/deploy/guard/sync workflows, Claude Code settings and protection hook, Renovate config.
- Profiles: frontend (Next.js), backend-node, backend-python, each with a package `AGENTS.md`, test configuration and worked examples.
- Scripts: `bootstrap.sh`, `sync.sh`, `check-instruction-budget.sh`, `check-pr-size.sh`, `validate-lessons.py`, `agent-metrics.py`.
- Evals: harness and three seed tasks.
