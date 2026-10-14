# Changelog

All notable changes to the playbook are documented here. Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer 2.0.0](https://semver.org/).

Version semantics for the playbook:
- **MAJOR**: a rule becomes stricter in a way that can fail existing compliant repos (new required check, lower threshold), or a managed file moves.
- **MINOR**: new optional guidance, new template, new rule that is warn-only for one release.
- **PATCH**: wording, typo, link fix, no behavioural change for agents or CI.

Every entry that changes agent behaviour must reference its rule proposal (`RP-NNNN`) and the eval run that validated it.

## [Unreleased]
### Added
- `docs/08-cicd-and-deployment.md` §8.6.1: how to adapt the single-package `release.yml` template for multi-package repos (matrix from `paths_released` and per-package versions, lowercase image names). Documentation only; no template or rule change.

## [1.2.0] - 2026-10-13
### Fixed
- `protect-instruction-files.sh` now works on Windows. Before this, it called `python3`, which on Windows is often the Microsoft Store placeholder (exit 49), so every call ended in a non-blocking error and nothing was protected. It now uses the first of `python3`, `python` or `py` that actually runs, and blocks (fails closed) when there is no Python or the hook input cannot be parsed.
- Windows paths: backslashes in file paths, the project directory and commands are normalised, and path matching is case-insensitive.
- Commands that name a protected directory without a trailing slash (`rm -rf .github`) are now blocked.
- An overwrite can no longer hide behind the `LESSONS.md` append exception in the same command. Appends are matched in Python, not with BSD-incompatible `sed` flags.
### Added
- The hook checks PowerShell tool calls (`Set-Content`, `Add-Content`, `Out-File`, `New-Item`, `Remove-Item`, `Copy-Item`, `Move-Item`, `Rename-Item`, `Clear-Content`, their aliases, and `[IO.File]` writes). The project template's hook matcher now includes `PowerShell`.
- `evals/hook-tests.sh`: 18 new cases (30 in total), covering Windows paths, PowerShell, the closed gaps, a broken `python3` stub and no Python at all.

This changes agent behaviour, so it is a MINOR release. No RP or eval run backs it: it was added at the cloudcitiwa owner's direct request (timesheet build report, rule proposal 5).

## [1.1.0] - 2026-10-13
### Added
- Project template `.claude/settings.json`: a `PowerShell(...)` deny rule for every `Bash(...)` deny rule, plus `Invoke-WebRequest`/`iwr` and `Invoke-RestMethod`/`irm`, which `curl` and `wget` alias to in Windows PowerShell. On Windows, Claude Code runs commands through its PowerShell tool, so the Bash-only rules never matched there. This changes agent behaviour (it adds denials), but no RP or eval run backs it: it was added at the cloudcitiwa owner's direct request after the timesheet build on Windows.

## [1.0.4] - 2026-10-13
### Fixed
- `reusable-ci-node.yml`, `test` job: build each package's workspace dependencies (`pnpm --filter "{.}^..." --if-present run build`) before lint. Packages that import workspace libraries exported from `dist` failed lint and typecheck with "type could not be resolved".
- `reusable-ci-node.yml`, `e2e` job: build the whole workspace from the repo root, because an e2e stack can start services the tested package does not depend on.

## [1.0.3] - 2026-10-13
### Fixed
- Project template `playbook-sync.yml`: suppress zizmor's `artipacked` finding on its checkout, with the reason inline. The job needs persisted credentials to `git push` the sync branch, and it uploads no artifacts. Before this, `security / workflows` failed on medium severity.

## [1.0.2] - 2026-10-13
### Changed
- Every third-party action in the reusable workflows and project templates is pinned to a commit SHA (`@<sha> # <tag>`), as zizmor's blanket policy requires.
- `reusable-security.yml`: CodeQL is skipped when `codeql-languages` is `'[]'`, and the new boolean input `dependency-review` (default `true`) turns off dependency review. Both need GitHub Code Security on private repos.
- Project template `security.yml` exposes `dependency-review`; `playbook-sync.yml` scopes its GitHub App token to `contents` and `pull-requests` write.

## [1.0.1] - 2026-10-13
### Fixed
- `templates/project/.github/workflows/security.yml`: grant `pull-requests: write` to the reusable security workflow. Its `dependency-review` job requests that permission (to comment its summary on failure), and a caller granting only `read` made every security run fail at startup.

## [1.0.0] - 2026-10-06
### Added
- Initial handbook (sections 0 to 14), glossary, ADR-0001 to ADR-0004.
- Managed project templates: root `AGENTS.md`, `CLAUDE.md`, `LESSONS.md`, PR and issue templates, CODEOWNERS, CI/security/release/deploy/guard/sync workflows, Claude Code settings and protection hook, Renovate config.
- Profiles: frontend (Next.js), backend-node, backend-python, each with a package `AGENTS.md`, test configuration and worked examples.
- Scripts: `bootstrap.sh`, `sync.sh`, `check-instruction-budget.sh`, `check-pr-size.sh`, `validate-lessons.py`, `agent-metrics.py`.
- Evals: harness and three seed tasks.
