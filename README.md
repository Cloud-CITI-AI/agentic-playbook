# Agentic Coding Playbook

Version: see `VERSION` · Owner: Platform Engineering (`@org/platform-eng`) · Status: v1.0.0 (pilot)

This repository is the single source of truth for how humans and AI coding agents build, test, secure and ship software in our organisation. It contains:

- **Handbook** (`docs/`): the rules, the reasoning behind them, and how each rule is checked.
- **Managed templates** (`templates/`): files that are copied into every adopting repository (agent instruction files, PR/issue templates, CI workflows, hooks, checklists).
- **Reusable CI** (`.github/workflows/reusable-*.yml`): called by project repositories by pinned commit SHA.
- **Scripts** (`scripts/`): bootstrap, sync, budget checks, PR size gate, lessons validation, agent metrics.
- **Evals** (`evals/`): a regression suite that every playbook release must pass before it ships.

---

## How to use this playbook

### 1. Which document do I read?

| You are… | Read first | Then |
|---|---|---|
| A developer starting on an adopted repo | `docs/01-executive-summary.md` | `docs/05-git-and-delivery-workflow.md`, the repo's own `AGENTS.md` |
| A tech lead adopting the playbook in a repo | `docs/02-repository-and-storage-model.md` | "Adopt in a repository" below, `docs/12-adoption-roadmap.md` |
| A reviewer of agent-authored PRs | `docs/05-git-and-delivery-workflow.md` §5.5 (review checklist) | `docs/07-security.md` §7.6 (agent controls) |
| Security / compliance | `docs/07-security.md` | `docs/10-self-regulation.md` §10.5 (guardrails) |
| Platform team (owners) | Everything | `docs/10-self-regulation.md`, `docs/13-sources-and-open-questions.md` |
| An AI agent | The repo's `AGENTS.md` (loaded automatically). Do **not** read this handbook unless your task brief tells you to. | |

Agents get the short machine-followable rules in `AGENTS.md`; humans get the reasoning in `docs/`. Keeping them separate is deliberate (see `docs/03-agent-instruction-files.md` §3.2 and ADR-0001).

### 2. Adopt in a repository (about 1 hour for a new repo, 1 to 2 days for an existing one)

```bash
# From the root of the target repository, on a new branch:
git switch -c chore/adopt-agentic-playbook

# Pick the profile(s) that match the repo: frontend | backend-node | backend-python (comma-separated for monorepos)
curl -fsSL https://raw.githubusercontent.com/cloud-citi-ai/agentic-playbook/v1.0.0/scripts/bootstrap.sh -o /tmp/bootstrap.sh
less /tmp/bootstrap.sh            # read it before running; never pipe remote scripts straight into a shell
bash /tmp/bootstrap.sh --version v1.0.0 --profile frontend --package-dir apps/web
bash /tmp/bootstrap.sh --version v1.0.0 --profile backend-node --package-dir services/api --skip-root
```

Then complete the checklist the script prints:

1. Replace every `<<FILL: …>>` placeholder (the script lists them; CI fails while any remain).
2. Wire the required `package.json` scripts / `Makefile` targets listed in `docs/06-testing-framework.md` §6.2.
3. Set CODEOWNERS teams in `.github/CODEOWNERS`.
4. Ask an org admin to apply the `agentic-baseline` ruleset to the repo (`docs/02-repository-and-storage-model.md` §2.6).
5. Open the PR. The `playbook-guard` workflow verifies the adoption.

### 3. Day-to-day use

- **Giving an agent work:** copy `templates/agent-task-brief.md` into the issue (or use the "Agent task" issue form). A good brief is the single biggest predictor of an acceptable agent PR.
- **Reviewing an agent PR:** use the PR template's evidence section and the review checklist. Do not merge without the evidence.
- **When you correct, revert or tweak agent output:** ask the agent (or do it yourself) to append an entry to `LESSONS.md` in the same PR. This is how the playbook learns.
- **Proposing a rule change:** open a PR against this repo using `rule-proposals/README.md`. Agents may draft proposals; only humans approve.

### 4. Staying current

A scheduled workflow in each adopted repo (`playbook-sync`) checks weekly for a new playbook release and opens a PR with the updated managed files. Review it like any dependency update. Managed files carry a header (`managed-by: agentic-playbook vX.Y.Z`); local edits to them are overwritten, so put local rules in the clearly marked "Repository-specific" sections instead.

### 5. Reporting a problem with the playbook

Open an issue in this repo with the label `playbook-bug` (a rule is wrong or contradictory) or `playbook-gap` (something is missing). Include the repo, the PR and the rule ID.

---

## Repository layout

```
agentic-playbook/
├── README.md                     # this file: what it is and how to use it
├── AGENTS.md / CLAUDE.md         # rules for agents editing THIS repo
├── CHANGELOG.md · VERSION        # release history (SemVer)
├── docs/
│   ├── 00-research-summary.md        # findings, disagreements, decisions (start here for the "why")
│   ├── 01-executive-summary.md       # what good looks like + the ten non-negotiables
│   ├── 02-repository-and-storage-model.md
│   ├── 03-agent-instruction-files.md
│   ├── 04-development-standards.md
│   ├── 05-git-and-delivery-workflow.md
│   ├── 06-testing-framework.md
│   ├── 07-security.md
│   ├── 08-cicd-and-deployment.md
│   ├── 09-quality-bar.md
│   ├── 10-self-regulation.md
│   ├── 11-templates-appendix.md
│   ├── 12-adoption-roadmap.md
│   ├── 13-sources-and-open-questions.md
│   ├── 14-self-review.md             # quality-bar review + explicit gaps
│   ├── glossary.md
│   └── adr/                          # ADR-0001 to ADR-0004
├── templates/
│   ├── agent-task-brief.md
│   ├── project/                  # copied into every adopting repo (root level)
│   ├── frontend/                 # Next.js/React package profile
│   ├── backend-node/             # Node.js/TypeScript service profile
│   └── backend-python/           # Python service profile
├── scripts/                      # bootstrap, sync, budget, PR size, lessons, metrics
├── evals/                        # agent-output regression suite
├── rule-proposals/               # how rules get proposed, reviewed, promoted
└── .github/workflows/            # reusable CI + this repo's own CI
```

## Licence and ownership

Internal use. Changes require approval from `@org/platform-eng` plus `@org/security` for anything under `docs/07-security.md`, `templates/project/.claude/`, `templates/project/.github/workflows/` or `scripts/`.
