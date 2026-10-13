# 2. Repository and storage model

## 2.1 Recommendation

**A dedicated, versioned `agentic-playbook` repository is the source of truth. Its managed files are vendored into each project repository by a sync workflow that opens a PR per release. Organisation-wide enforcement lives in GitHub org settings (rulesets, Actions policy) and reusable workflows referenced by pinned SHA.** Recorded as ADR-0002.

The core reason: agents read files that are *in the repository they are working in*, at the path they expect (`AGENTS.md`, `.github/…`). Anything that is not physically present at that path is invisible to most agents. Enforcement, by contrast, must not depend on project repos keeping copies honest, so it lives at org level.

## 2.2 Options evaluated

| Option | Versioning | Discoverable by agents | Enforceable | Drift risk | Ownership | Verdict |
|---|---|---|---|---|---|---|
| **Dedicated playbook repo + vendored managed files via sync PRs** | SemVer tags; each repo records its version | High: files sit at native paths | High when combined with rulesets + reusable workflows | Low: weekly sync PR, guard check detects edits | Clear: platform-eng owns source, repo owners own adoption | **Recommended** |
| GitHub template repository only | None after creation | High at creation | None | Very high: repos diverge on day one | Unclear after fork | Use only as the *bootstrap* for brand-new repos |
| Git submodule | Pinned commit | Low: most agents and many tools don't follow submodules; nested paths (`playbook/AGENTS.md`) aren't native | Low | Medium | Clear | Rejected: friction for humans, invisible to agents |
| Versioned package (npm/PyPI) | SemVer | Low: files land in `node_modules`/site-packages, which agents ignore and many tools exclude | Medium (postinstall copy is itself a supply-chain risk) | Medium | Clear | Rejected: language-specific, and lifecycle scripts are blocked by our own supply-chain policy |
| Org `.github` repository | Unversioned (default branch) | Partial: provides default issue/PR templates and community-health files to repos that lack them; does **not** provide `AGENTS.md`, CODEOWNERS or workflows to other repos | Low on its own | Medium | Clear | **Use as a complement** for default templates and `SECURITY.md` |
| Internal developer portal (Backstage TechDocs) | Inherits from source repo | None: agents don't browse portals | None | Low if rendered from the repo | Clear | **Use as a complement** for human discovery; never authoritative |
| Wiki (Confluence/Notion) | Page history, no releases | None (unless a connector is configured, and then it's untrusted remote content) | None | High | Diffuse | Rejected for rules; fine for meeting notes and onboarding narratives |

## 2.3 What lives where

| Artefact | Location | Enforced by |
|---|---|---|
| Handbook, ADRs, templates, scripts, evals | `agentic-playbook` repo | CODEOWNERS (platform-eng + security) |
| Root/package `AGENTS.md`, `CLAUDE.md`, `LESSONS.md`, PR/issue templates, CODEOWNERS skeleton, `.claude/` settings and hooks, Renovate config | Vendored into each project repo | `playbook-guard` workflow (detects drift, missing files, placeholders) |
| Reusable CI/security workflows | `agentic-playbook/.github/workflows/reusable-*.yml`, called as `uses: <org>/agentic-playbook/.github/workflows/reusable-ci-node.yml@<sha>` | Org ruleset requires the resulting check names |
| Default issue/PR templates, `SECURITY.md` | Org `.github` repo | GitHub community-health fallback |
| Required checks, review rules, merge restrictions | Org ruleset `agentic-baseline` | GitHub |
| SHA pinning, allowed actions | Org Actions policy | GitHub |
| Claude Code org policy (sandbox required, deny rules, managed CLAUDE.md) | Managed settings deployed by MDM | Claude Code client |
| Copilot / Cursor org policy | Copilot org settings; Cursor Team Rules | Vendor platforms |
| Human-friendly rendering | Backstage TechDocs pointing at `docs/` | n/a |

## 2.4 Adoption paths

**New repository** (target: 1 hour)
1. Create the repo from the org's language template repository (which already includes a bootstrap run).
2. Run `scripts/bootstrap.sh --profile <p>` if the template predates the current playbook version.
3. Fill placeholders, set CODEOWNERS, request the ruleset. Done when `playbook-guard` is green.

**Existing repository** (target: 1 to 2 days)
1. Run `bootstrap.sh` on a branch. It never overwrites an existing file without `--force`; instead it writes `<file>.playbook-new` and lists conflicts.
2. Merge conflicts manually: existing CI steps map to the required script names (`docs/06-testing-framework.md` §6.2).
3. Turn on gates in **report-only** mode for one week (`PLAYBOOK_ENFORCE=false` repo variable), fix findings, then flip to enforce.
4. Request the ruleset.

**Monorepo**: root profile once, then one package profile per app/service (`--package-dir`, `--skip-root`).

## 2.5 Ownership and update process

| Role | Who | Responsibilities |
|---|---|---|
| Playbook owner | Platform Engineering (`@org/platform-eng`) | Maintain source, cut releases, run evals, chair monthly rule review |
| Security co-owner | `@org/security` | Approve changes to security sections, agent controls, workflows, scripts |
| Repo adopter | Each repo's tech lead | Adopt, keep sync PRs merged within 10 business days, curate `LESSONS.md` |
| Contributors | Anyone (humans; agents via draft proposals) | Raise issues and rule proposals |

Release flow: rule proposal PR → owners' review → eval run attached → merge → release-please opens release PR → owner approves → tag `vX.Y.Z` → `playbook-sync` in adopted repos opens update PRs.

Compatibility: adopted repos may lag at most one MAJOR version. `playbook-guard` warns at one MINOR behind for > 30 days and fails at one MAJOR behind for > 60 days.

## 2.6 Org settings checklist (one-off, org admin)

| Setting | Value | Path |
|---|---|---|
| Actions: require full-length SHA pinning | On | Org → Settings → Actions → General → Policies |
| Actions: allowed actions | GitHub-owned + verified creators + explicit allowlist | same |
| Default `GITHUB_TOKEN` permissions | Read-only | same |
| Allow Actions to create/approve PRs | Off | same |
| Secret scanning + push protection | On for all repos | Org → Code security |
| Dependabot alerts / security updates | On | Org → Code security |
| Ruleset `agentic-baseline` on default branches | Require PR, 1 approval (2 for tier High via CODEOWNERS), dismiss stale approvals, require review from CODEOWNERS, require conversation resolution, required checks: `ci / verify`, `security / scan`, `playbook-guard`, block force-push, require linear history, empty bypass list | Org → Rulesets |
| Copilot cloud agent | Enabled only for pilot repos; firewall on; "auto-run workflows" off | Org → Copilot → Policies |

Note: the "require workflows to pass" ruleset rule and some org-ruleset features depend on the GitHub plan (Team vs Enterprise Cloud). Verify against your plan before relying on them.
