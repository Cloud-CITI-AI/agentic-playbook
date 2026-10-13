<!-- managed-by: agentic-playbook v1.0.0 — paste into an issue (or use the "Agent task" form). Delete the guidance comments. -->
# Task brief: <imperative title, e.g. "Add status filter to GET /v1/orders">

**Risk tier:** Low | Medium | High   **Launching human:** @   **Target package:** `services/orders-api`

## Goal
<!-- The user-visible outcome in 1 to 2 sentences. -->

## Context
<!-- Links only: relevant files, ADRs, prior PRs, designs. Do NOT paste secrets, customer data or production logs. -->
- Relevant code: `src/http/orders.routes.ts`, `src/data/orders.repository.ts`
- Related ADR / PR:

## Acceptance criteria
<!-- Numbered, testable. Each must map to a test or a screenshot in the PR. -->
1.
2.

## Out of scope / must not change
-

## Permissions for this task
- [ ] May add a runtime dependency
- [ ] May change the public API contract
- [ ] May add a database migration
- [ ] May update visual snapshots

## Hints and constraints
<!-- Known pitfalls, patterns to follow ("copy the approach in invoices.routes.ts"), performance limits. -->

## How a reviewer will verify
```
pnpm --filter orders-api test:integration -- orders
```

## Definition of done
Root `AGENTS.md` "Definition of done" plus:
-
