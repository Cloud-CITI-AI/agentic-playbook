# 5. Git and delivery workflow

## 5.1 Branching model: trunk-based with short-lived branches (ADR-0003)

| Rule | Value | Check |
|---|---|---|
| GW-1 Single long-lived branch | `main`, always releasable | Ruleset blocks direct push and force-push |
| GW-2 Branch lifetime | ≤ 2 days for humans; one agent session per branch | Stale-branch report (weekly) |
| GW-3 Branch names | `feat/`, `fix/`, `chore/`, `docs/`, `agent/<issue>-<slug>`, `copilot/*` | `playbook-guard` (warn) |
| GW-4 Merge method | Squash merge only; linear history | Repo settings + ruleset |
| GW-5 Merge queue | On for repos with > 10 merges/day | Ruleset `merge_group` |
| GW-6 Incomplete work | Behind a feature flag, not on a branch | Review |

Rejected: GitFlow (long-lived `develop`/release branches enlarge batches and delay integration, the opposite of DORA's small-batch finding). GitHub Flow is compatible: it is trunk-based with PRs, which is what we do.

## 5.2 Risk tiers

| Tier | Examples | Approvals | Extra requirements |
|---|---|---|---|
| Low | Docs, tests, refactor with no behaviour change, copy changes | 1 | none |
| Medium | Behaviour change behind a flag, non-critical endpoints, UI features | 1 (CODEOWNER of touched area) | Flag or canary; rollback stated |
| High | Authn/authz, payments, personal data, migrations, IaC, security config, public API contract, CI changes | 2, including the domain CODEOWNER; approver ≠ launching human | Agent plan approved before coding; security checklist section B; migration plan |

Agents may self-assess the tier but CODEOWNERS paths decide: touching a High path makes the PR High regardless of the checkbox.

## 5.3 Commits and PR titles

- Conventional Commits 1.0.0 (https://www.conventionalcommits.org/en/v1.0.0/). PR title is validated because squash merge makes it the commit message.
- Types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`, `revert`. `!` or `BREAKING CHANGE:` footer for breaking changes.
- Trailers (agent-authored or agent-assisted work):
  ```
  feat(orders): filter list by status

  Refs: #482
  AI-Agent: claude-code/<model-id>
  Co-authored-by: Jane Doe <jane@example.com>
  ```
- Signed commits: required on `main` for humans. Copilot cloud agent commits must be re-signed at squash merge (GitHub signs squash merges made in the UI), which satisfies the rule.
- Check: `amannn/action-semantic-pull-request` (or commitlint) on PR title; `playbook-guard` for trailers.

## 5.4 Pull requests

| Rule | Value | Check |
|---|---|---|
| PR-1 Template | `.github/pull_request_template.md`, every section filled | `playbook-guard` |
| PR-2 Size | ≤ 400 changed lines target; > 800 fails; agent PRs > 400 fail; `size-exception` label by CODEOWNER only | `check-pr-size.sh` |
| PR-3 Scope | One issue per PR; refactors separate from behaviour changes | Review |
| PR-4 Draft first | Agents open drafts; mark ready only when CI green | Review; Copilot does this by default |
| PR-5 Evidence | Real `verify` output, tests named, screenshots for UI, migration and rollback plan | Review checklist |
| PR-6 Review SLA | First human review within 4 business hours; PRs idle > 3 days are closed or re-planned | Metrics script (median hours to first review) |
| PR-7 AI review | Copilot/other AI review runs as advisory; findings must be resolved or answered, never counts as approval | Ruleset counts human approvals only |
| PR-8 Stale approvals | Dismissed on new commits | Ruleset |

How to split a large change: (1) preparatory refactor PR with no behaviour change, (2) new code path behind a flag, (3) switch-over PR flipping the flag default, (4) cleanup PR removing the old path. Agents propose the split in the PR description when A1 would be exceeded.

## 5.5 Review checklist for agent-authored PRs

Reviewing agent output differs from reviewing a colleague's: the code is fluent, confident and plausible, which hides errors. Read tests first.

| # | Check | Why it matters for agents |
|---|---|---|
| RV-1 | Read the brief, then the tests, then the code | Tests show what the agent believed "done" meant |
| RV-2 | Spot-check one assertion: would it fail if the behaviour broke? | Agents write tautological tests to hit coverage |
| RV-3 | Look for scope creep: unrelated files, renamed symbols, reformatting | Agents "helpfully" refactor |
| RV-4 | Look for invented APIs, config keys or flags | Hallucinated identifiers compile in dynamic code paths |
| RV-5 | Check error paths, authz checks, tenant scoping | Most frequent security misses (Veracode 2025) |
| RV-6 | Check new dependencies exist, are the intended package, and are maintained | Package-name hallucination ("slopsquatting") |
| RV-7 | Confirm evidence matches CI for the head commit | X8; stale or invented evidence |
| RV-8 | Read "Suspicious content"; if non-empty, check the diff for injected behaviour | ASI01 goal hijack |
| RV-9 | If you correct anything, require a `LESSONS.md` entry | N10 |

## 5.6 Definition of ready and done

See `templates/project/docs/definition-of-done.md` (vendored into every repo as `docs/definition-of-done.md`).

## 5.7 Release and versioning

| Rule | Detail | Check |
|---|---|---|
| RL-1 SemVer 2.0.0 for libraries and public APIs; services may use CalVer tags but still SemVer their API contract | https://semver.org | Release config |
| RL-2 release-please opens a release PR from Conventional Commits; a human approves it | Human approval of every release | `release.yml` |
| RL-3 CHANGELOG generated from commits, plus a hand-written "Upgrade notes" section for breaking changes | Release notes are useful only with intent | Review of release PR |
| RL-4 Every release artefact: image by digest, SBOM, provenance attestation | Supply chain | `release.yml`; `gh attestation verify` in deploy |
| RL-5 Release notes automation: release-please generates per-component notes; deploy job posts them to the release channel | Traceability | Workflow |
