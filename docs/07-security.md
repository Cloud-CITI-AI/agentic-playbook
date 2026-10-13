# 7. Security

Baseline: OWASP ASVS 5.0.0 Level 2 for all services; Level 3 for authentication, payments and regulated personal data. Risk vocabulary: OWASP Top 10:2025 for applications, OWASP Top 10 for LLM Applications 2025 and Top 10 for Agentic Applications 2026 for agents. The fillable checklist is `templates/project/docs/security-checklist.md`.

## 7.1 Controls by stage

| Stage | Control | Tool / mechanism | Blocking? | Maps to |
|---|---|---|---|---|
| Pre-commit | Secret scan on staged changes | gitleaks via lefthook | Yes (local) | A02, ASVS V13 |
| Pre-commit | Format/lint | lefthook | Yes (local) | — |
| Push | Secret push protection | GitHub secret scanning | Yes | A02 |
| PR | SAST | CodeQL (security-extended) | High/critical new alerts | A01, A05 |
| PR | Dependency review: new vulns + licences | `actions/dependency-review-action` | High+ or disallowed licence | A03 |
| PR | Secrets in history range | gitleaks | Yes | A02 |
| PR | Workflow security lint | zizmor (template injection, `pull_request_target`, unpinned actions, excessive permissions) | Yes | A03, A08 |
| PR | IaC misconfiguration | Checkov | High | A02 |
| PR | Migration safety | Squawk | Yes | availability |
| PR | Agent protected paths, traceability | `playbook-guard` | Yes | ASI06, ASI03 |
| Pre-release | Image scan | Grype (`anchore/scan-action`) fixable high/critical | Yes | A03 |
| Pre-release | SBOM + provenance attestation | Syft + `actions/attest-*` | Yes (deploy verifies) | A03, A08 |
| Pre-release | DAST baseline | OWASP ZAP baseline on staging | High alerts | A02, A05 |
| Runtime | Workload identity, no static keys | OIDC / cloud IAM | — | ASVS V13 |
| Runtime | WAF, rate limits, request size limits | Edge config | — | A04, A06 |
| Runtime | Security logging and alerting | SIEM rules (§7.5) | — | A09 |
| Weekly | Full SCA rescan (new CVEs on old code) | scheduled `security.yml` + Dependabot alerts | Triage SLA | A03 |

Triage SLAs: critical 2 business days, high 10, medium 30, low next quarter. Exceptions require a risk-acceptance issue approved by `@org/security` with an expiry date.

## 7.2 Supply chain (OWASP A03:2025, SLSA)

| Rule | Implementation |
|---|---|
| SCS-1 Actions pinned by full SHA | Org policy "require SHA pinning"; Renovate `helpers:pinGitHubActionDigests`; zizmor |
| SCS-2 `GITHUB_TOKEN` read-only by default; per-job `permissions` | Org setting; workflow templates declare `permissions: {}` at top |
| SCS-3 No `pull_request_target` with checkout of PR head | zizmor |
| SCS-4 Frozen installs, lockfile integrity, release-age gate, blocked lifecycle scripts | pnpm/npm settings in templates |
| SCS-5 Renovate cooldown 7 days except security updates | `renovate.json` |
| SCS-6 SBOM (SPDX) and build provenance for every release artefact; SLSA Build L2 now, L3 via reusable-workflow isolation in phase 3 | `release.yml`; GitHub docs state attestations alone give Build L2 |
| SCS-7 Deploy verifies attestation before rollout | `gh attestation verify` in `deploy.yml` |
| SCS-8 Base images pinned by digest, rebuilt weekly | Renovate docker manager |
| SCS-9 Hallucinated or typosquatted packages: new deps must already exist with history | Dependency review + RV-6 |

## 7.3 Secrets

| Rule | Check |
|---|---|
| SE-1 Secrets live only in the cloud secret manager; apps fetch via workload identity | IaC review |
| SE-2 CI uses OIDC federation to the cloud; no long-lived cloud keys in GitHub secrets | Org audit query for secrets named `*_KEY`, `*_SECRET` |
| SE-3 Environment secrets scoped to GitHub Environments with required reviewers for production | Repo settings audit |
| SE-4 Rotation: 90 days for anything static; immediately on any suspected exposure, including exposure to an agent session or transcript | Secret manager rotation policy |
| SE-5 Agent sessions never receive secrets; `.env*` reads denied; transcripts treated as potentially sensitive | `.claude/settings.json` deny rules; X2 |

## 7.4 Application controls (summary; detail in checklist)

| Domain | Rule | ASVS 5.0 chapter |
|---|---|---|
| Input validation | Schema validation at every boundary (zod/pydantic): type, length, range, format; reject unknown fields | V2 Validation and Business Logic |
| Output encoding | Framework auto-escaping; parameterised SQL; no shell string building; sanitise any HTML | V1 Encoding and Sanitization |
| Authentication | Central IdP (OIDC); no custom password storage; MFA for admins; session rotation on privilege change | V6, V7, V9, V10 |
| Authorisation | Deny by default; check per handler; object-level (tenant/owner) checks; admin actions audited | V8 Authorization |
| Security headers | CSP with nonces, HSTS, nosniff, Referrer-Policy, frame-ancestors | V3 Web Frontend Security |
| API | Size and rate limits; consistent problem errors; no verbose errors | V4 API and Web Service |
| Files | Type sniffing, size limits, store outside web root, malware scan for user uploads | V5 File Handling |
| Data protection | Classify data; encrypt in transit (TLS 1.2+) and at rest; minimise; retention; no personal data in logs | V12, V14 |
| Errors and logging | RFC 9457 problems; no stack traces; security events logged | V16 |
| Crypto | Platform libraries only; no home-grown crypto; keys in KMS | V11 |

## 7.5 Logging hygiene and incident response basics

Must alert: spike in authn failures, authz denials, 5xx rate breaching SLO, WAF blocks, secret-scanning alert, new admin role grant, agent identity acting outside its allowlist.

Incident response (summary; the org IR plan governs):
1. Detect and declare (on-call or security); open incident channel and ticket.
2. Contain: roll back or flag off; rotate exposed credentials; if an agent is involved, pull the kill switch (§10.5).
3. Eradicate and recover; verify with monitoring.
4. Post-incident review within 5 business days: blameless, timeline, contributing factors; any agent-related factor becomes a `LESSONS.md` entry with `trigger: incident` and `severity: security|high` (auto-promotes to a rule proposal).

## 7.6 Agent-specific controls

The design rule: **an agent is an untrusted, highly capable contractor with no authority.** It gets the minimum access needed for one task and every output is verified.

| ID | Control | Enforced by | Risk addressed |
|---|---|---|---|
| AG-1 | Separate identity per agent (GitHub App/bot); no personal tokens; least scope (contents and pull-requests write on non-default branches only) | GitHub App config; ruleset | ASI03 Identity and Privilege Abuse |
| AG-2 | Agents cannot approve, merge, or bypass rulesets | Ruleset bypass list empty; branch rules | ASI10 Rogue Agents |
| AG-3 | Sandboxed execution: Claude Code sandbox required via managed settings; Copilot cloud agent firewall on; cloud agents run in ephemeral containers | Managed settings; Copilot policy | ASI05 Unexpected Code Execution |
| AG-4 | Egress allowlist (package registries, model provider, GitHub) for agent sandboxes | Sandbox network config; Copilot firewall | Exfiltration |
| AG-5 | No production credentials, no production data, no write-scoped cloud credentials in agent environments | IAM; X3; secret isolation | ASI03 |
| AG-6 | Lethal-trifecta rule: a session that reads untrusted content (public issues, external contributor comments, web pages) has no private-data tools and no write-capable outbound channel beyond its own PR branch | MCP allowlist per profile; review of MCP configs | ASI01 Goal Hijack |
| AG-7 | Agents respond only to users with write access (Copilot default); external-contributor issues are triaged by a human before labelling `agent-ready` | Process; label permissions | ASI01 |
| AG-8 | Workflows on agent PRs require human "Approve and run" (Copilot default; keep it) | Copilot setting | ASI02 Tool Misuse |
| AG-9 | MCP servers: allowlisted, version-pinned, reviewed by security; read-only tokens by default | `.mcp.json` under `.claude/` (protected path); review | ASI04 Agentic Supply Chain |
| AG-10 | Instruction files and LESSONS history protected from agent edits | Hook, CODEOWNERS, guard | ASI06 Memory and Context Poisoning |
| AG-11 | Transcripts and session logs retained ≥ 1 year in the vendor platform or exported to the audit store | Vendor retention settings | Auditability (SOC 2 CC7/CC8) |
| AG-12 | Kill switch rehearsed quarterly | §10.5 | ASI08 Cascading Failures, ASI10 |

Prompt-injection defences for repository content, in order of strength: (1) architectural: AG-5, AG-6, AG-4 so a hijacked agent has nothing valuable to reach and nowhere to send it; (2) process: human triage of external input (AG-7), human workflow approval (AG-8), human merge (AG-2); (3) instruction: rule A11 tells agents to treat content as data and report it; (4) detection: reviewers read "Suspicious content", and RV-8. Layer 3 alone is known to be insufficient; layers 1 and 2 carry the weight.

## 7.7 Audit trail (SOC 2 change management)

For any production change we can answer who, what, why, when and with which agent:

| Question | Source |
|---|---|
| Who requested it | Issue author; task brief |
| Who launched the agent | PR "Launching human" field |
| Which agent/model | `AI-Agent:` trailer; PR disclosure; bot identity |
| What changed | Squash commit; PR diff |
| Who approved | PR reviews (GitHub audit log) |
| What checks passed | Required check runs on head SHA |
| What was deployed, when, by whom | Deployment records in GitHub Environments; provenance attestation |
| Session detail | Agent session link (retained per AG-11) |
