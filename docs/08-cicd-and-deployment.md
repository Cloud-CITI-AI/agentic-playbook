# 8. CI/CD and deployment

## 8.1 Reference pipeline

```mermaid
flowchart LR
  A[PR opened] --> B[lint + typecheck]
  B --> C[unit + component]
  C --> D[integration\nTestcontainers]
  D --> E[contract + diff coverage\n+ mutation on changed files]
  A --> S[security: CodeQL, dep review,\ngitleaks, zizmor, IaC]
  A --> G[playbook-guard + PR size]
  E --> F[build]
  F --> H[e2e: Playwright on preview\n+ axe + visual]
  S --> V{ci/verify + security/scan\n+ playbook-guard}
  H --> V
  G --> V
  V -->|human approval, merge queue| M[main]
  M --> R[release-please PR\nhuman approves]
  R --> I[image + SBOM + provenance\n+ image scan]
  I --> ST[staging: verify attestation,\nexpand migrations, deploy, smoke, ZAP, k6]
  ST -->|environment approval| P[production canary 5→25→50→100%\nauto-rollback on SLO breach]
```

Ordering principles: cheapest and most deterministic checks first, so agents get fast feedback; security scans run in parallel and never wait on tests; anything needing a deployed app (e2e, DAST) runs last.

Time budgets (p50): PR pipeline ≤ 15 min; main to staging ≤ 20 min; staging to production ≤ 60 min including canary. If exceeded, the platform team treats it as a defect.

Reusable implementations: `.github/workflows/reusable-ci-node.yml`, `reusable-ci-python.yml`, `reusable-security.yml` in this repo; project wrappers in `templates/project/.github/workflows/`.

## 8.2 Environments

| Environment | Created | Data | Deploy trigger | Access |
|---|---|---|---|---|
| Local | Developer/agent machine | Synthetic seeds | — | Developer |
| Preview | Per PR (frontend and BFF), torn down on close | Synthetic | PR push | Org members; never public without auth |
| Staging | Long-lived, production-like | Synthetic or masked (never raw production) | Release published | Engineers |
| Production | — | Real | Approval in GitHub Environment `production` | Deploy role via OIDC only |

Rules: same image digest promoted through environments (build once); environment differences only via config; infrastructure changes via IaC PRs with `plan` output attached and `apply` run by the pipeline, never by humans or agents from laptops.

## 8.3 Database migration safety

| Step | Release N | Release N+1 | Release N+2 |
|---|---|---|---|
| Add column | Add nullable column; code writes both old and new | Backfill job; code reads new | Add NOT NULL / constraint `NOT VALID` then `VALIDATE` |
| Rename column | Add new column + dual write | Backfill; switch reads | Drop old column (after verifying no reads) |
| Add index | `CREATE INDEX CONCURRENTLY` in its own migration (non-transactional) | — | — |
| Drop table | Stop all reads/writes; deploy | Verify via logs/query stats for one week | Drop |

Pipeline guarantees: migrations run before the new code (expand only), are linted by Squawk, run with `lock_timeout` and `statement_timeout`, and must be backward compatible with the running version (tested by running the previous release's integration suite against the new schema in CI for High-tier PRs).

## 8.4 Progressive delivery and rollback

| Mechanism | When | Rollback |
|---|---|---|
| Feature flags (OpenFeature + provider) | Any user-visible change of tier Medium/High | Flag off (seconds) |
| Canary (5% → 25% → 50% → 100%, 10 min analysis each) | Every production deploy | Automatic on SLO breach: error rate > SLO burn threshold or p99 latency > target |
| Blue/green | Stateful services where canary is impractical | Switch traffic back |
| Revert PR | Code defect not covered by flag | Revert merged within 30 min target; redeploy |

Rollback must never require a down-migration: expand/contract keeps the previous release compatible with the current schema.

## 8.5 Observability requirements (definition of "production-ready")

| Requirement | Detail | Check |
|---|---|---|
| OB-1 Traces | OpenTelemetry SDK; W3C trace context propagated across services | Trace visible end to end in staging smoke |
| OB-2 Metrics | RED (rate, errors, duration) per endpoint; USE for resources; business KPIs | Dashboard exists before first prod deploy |
| OB-3 Logs | Structured, correlated by `traceId` (§4.5) | Log query in runbook |
| OB-4 SLOs | Availability and latency SLOs per user-facing service; error budget policy (freeze features when budget exhausted) | SLO doc in repo `docs/slo.md` |
| OB-5 Alerts | Multi-window burn-rate alerts on SLOs; every alert links a runbook | Alert review quarterly |
| OB-6 Deployment markers | Deploy events annotated on dashboards with version and PR | Deploy workflow step |

## 8.6 Release notes automation

release-please groups commits by type into per-component release notes; the release PR is where a human adds "Upgrade notes" for breaking changes; on publish, the deploy workflow posts the notes and the attestation link to the release channel. Agent-authored changes appear with the PR number, which links to the disclosure.
