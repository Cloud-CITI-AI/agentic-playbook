# 6. Testing framework

## 6.1 Strategy per layer

| Layer | Frontend | Backend | Gate | Owner |
|---|---|---|---|---|
| Static | ESLint (incl. jsx-a11y), tsc strict | ESLint/Ruff, tsc/mypy strict | Zero warnings | Every PR |
| Unit | Pure functions, hooks (Vitest) | Domain logic, no I/O (Vitest/pytest) | Diff coverage ≥ 80% (combined unit+integration) | Every PR |
| Component | Testing Library + MSW + axe, by role | n/a | Every new component: render, interaction, axe | Every PR |
| Integration | n/a (or BFF route handlers) | Real Postgres via Testcontainers; real queues where feasible | Every repository and migration covered | Every PR |
| Contract | Generated API types from OpenAPI | Responses validated against OpenAPI; `oasdiff breaking`; Pact only for service-to-service where the consumer team asks | Breaking change fails without approval | Every PR |
| End-to-end | Playwright: happy path + error state per page; axe scan; visual snapshots | Smoke tests post-deploy | Required on PRs touching `apps/*` | PR + post-deploy |
| Mutation | Stryker incremental on changed logic files | Stryker / mutmut on `domain/` | Break < 60%, target ≥ 75% | PR (changed files); nightly full |
| Performance | Lighthouse CI + size-limit | k6 smoke on staging after deploy; full load test before major launches | Budgets in §4.10 and SLO thresholds | PR (FE budgets); deploy (BE) |
| Security | see section 7 | | | |

Shape: backend is pyramid-shaped with a thick integration layer against a real database; frontend is trophy-shaped with most weight on component tests. Pyramid vs trophy is a genuine disagreement in the field; we pick per layer by where defects in our stack actually come from (data access on the backend, interaction and state on the frontend), and we will revisit using escaped-defect data (section 9).

## 6.2 Required script names (identical in every package)

| Script / target | Meaning | Must be |
|---|---|---|
| `verify` | Everything a PR needs locally, fastest-first | < 10 min on a laptop; exit non-zero on any failure |
| `lint` | Lint + format check | No auto-fix in CI |
| `typecheck` | Type checker | Strict |
| `test:unit` / `test-unit` | Unit (and component) tests with coverage (cobertura XML) | No network, no Docker |
| `test:integration` / `test-integration` | Integration tests | Docker allowed; no external network |
| `test:contract` / `test-contract` | Contract checks | |
| `test:e2e` | End-to-end | Against a built app or `E2E_BASE_URL` |
| `test:mutation` / `test-mutation` | Mutation, incremental | Fails below break threshold |
| `build` | Production build | |
| `format` | Auto-format (local only) | |

`package.json` fragments: `templates/frontend/package.scripts.json`, `templates/backend-node/package.scripts.json`. Python: `templates/backend-python/Makefile`. CI calls these names and nothing else, so agents and humans run exactly what CI runs.

Local commands:
```bash
pnpm -r verify                          # all TS packages
pnpm --filter <pkg> test:unit -- path   # one file
pnpm --filter <pkg> test:e2e -- --ui    # Playwright UI mode
make -C services/pricing verify         # a Python package
```

## 6.3 Coverage and mutation thresholds

| Metric | Gate | Rationale |
|---|---|---|
| Diff coverage (changed executable lines) | ≥ 80% | Measures the code being changed now; global % rewards padding old code |
| Global line coverage | Reported only | Vanity metric when gated; agents game it with assertion-free tests |
| Mutation score on changed domain/logic files | break < 60%, target ≥ 75% | Detects tests that execute code without checking it, a known weakness of AI-written tests |
| Branch coverage | Reported | Useful for review, noisy as a gate |

Exemptions: generated code, type-only files, framework glue (`page.tsx`, `layout.tsx`, `main.ts`). Listed in configs, not ad hoc.

Diff coverage implementation: `diff-cover coverage/cobertura-coverage.xml --compare-branch=origin/main --fail-under=80` (works for both stacks).

## 6.4 Test data management

| Rule | Check |
|---|---|
| TD-1 No production data in tests, fixtures, seeds or agent context, ever | Review; DLP scan on fixtures (gitleaks custom rules for emails/phone patterns) |
| TD-2 Factories (e.g. `@faker-js/faker` with fixed seed, `factory_boy`) over static fixtures | Review |
| TD-3 Each test creates its own data and isolates by unique tenant ID or transaction rollback | Integration examples |
| TD-4 Deterministic: fixed seeds, frozen clocks (`vi.useFakeTimers`, `freezegun`), no real network | Lint bans `Date.now()` in domain code without clock injection |
| TD-5 Visual tests use a `fixture=stable` mode with deterministic data | e2e example |
| TD-6 Seeds for local/dev are synthetic, versioned with migrations | Review |

## 6.5 Flaky-test policy

| Step | Rule | Tooling |
|---|---|---|
| Detect | A test that fails then passes on retry in CI is flaky. Playwright allows 1 retry in CI solely to detect this; Vitest/pytest do not retry | Playwright JSON report `flaky` status; CI annotation |
| Quarantine | Within 24 h: move to quarantine (`test.fixme` with issue link / `@pytest.mark.quarantine`), open issue labelled `flaky-test` assigned to CODEOWNER | Quarantined tests run nightly, not on PRs |
| Fix | Fix or delete within 10 business days; deletion needs a replacement test or explicit approval | Weekly report of open `flaky-test` issues |
| Measure | Flake rate = flaky runs / total runs per week; target < 1% | CI analytics |
| Never | Blanket retries, increased timeouts without root cause, `sleep` | Lint for `waitForTimeout`, `time.sleep` in tests |

Agents must not quarantine tests (X4). A human applies the quarantine.

## 6.6 Worked examples

| Example | File |
|---|---|
| Component test with role queries, keyboard, axe | `templates/frontend/examples/OrderStatusFilter.test.tsx` |
| Playwright happy path, error state, axe, visual | `templates/frontend/examples/orders.spec.ts` |
| Testcontainers global setup (Node) | `templates/backend-node/examples/test/global-setup.ts` |
| Repository integration test (tenant scoping, injection) | `templates/backend-node/examples/orders.repository.int.test.ts` |
| Typed errors → problem+json | `templates/backend-node/examples/errors.ts`, `templates/backend-python/examples/errors.py` |
| Fail-fast config | `templates/backend-node/examples/config.ts` |
| k6 smoke with SLO thresholds | `templates/backend-node/examples/load-smoke.js` |
| pytest + Testcontainers | `templates/backend-python/examples/tests/integration/` |

TDD flow for agents fixing bugs (rule A2): write the failing test → run it and paste the failure in the PR → fix → run again → paste the pass. Reviewers check the failure output exists.
