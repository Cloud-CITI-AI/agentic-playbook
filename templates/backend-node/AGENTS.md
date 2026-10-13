<!-- managed-by: agentic-playbook v1.0.0 | profile: backend-node | adds to root AGENTS.md; may tighten, never loosen -->
# AGENTS.md — <<FILL: package name, e.g. services/orders-api>> (Node.js / TypeScript service)

## Commands (run in this directory)
| Purpose | Command |
|---|---|
| Dev | `pnpm dev` |
| Full gate | `pnpm verify` (= lint + typecheck + test:unit + test:integration + build) |
| Unit | `pnpm test:unit` (Vitest; no I/O) |
| Integration | `pnpm test:integration` (Vitest + Testcontainers Postgres; Docker required) |
| Contract | `pnpm test:contract` (validates responses against `openapi.yaml`) |
| Mutation (changed files) | `pnpm test:mutation` |
| New migration | `pnpm db:migration:new <name>` then `pnpm db:migration:lint` |
| Regenerate API types | `pnpm api:generate` |

## Structure
- BE-1. Layers: `src/http/` (routes, request parsing, response mapping) → `src/domain/` (business logic, pure, no I/O imports) → `src/data/` (repositories, SQL). Domain code must not import from `http/` or `data/`; depend on interfaces.
- BE-2. Configuration is parsed once in `src/config.ts` with zod at startup; the process exits on invalid config. No `process.env` access elsewhere.

## API
- BE-3. `openapi.yaml` is the contract and is updated in the same PR as the handler. Breaking changes (removed/renamed fields, new required inputs, changed status codes) require a new version path or explicit approval in the brief.
- BE-4. Errors are returned as RFC 9457 `application/problem+json` with a stable `type` URI and the request ID. Throw `AppError` subclasses from `src/errors.ts`; never throw strings or raw `Error` from domain code.
- BE-5. Every handler performs authorisation explicitly (deny by default) and scopes data access by tenant/owner. A handler without an authz check fails review.
- BE-6. List endpoints paginate (cursor-based, max page size <<FILL: 100>>).

## Data
- BE-7. SQL only through `<<FILL: Kysely / Drizzle / Prisma>>` or parameterised queries. String-built SQL is forbidden.
- BE-8. Migrations are forward-only and expand/contract: add nullable column → backfill → enforce constraint in a later release; drop in a later release still. Create indexes `CONCURRENTLY`. Set `lock_timeout` ≤ 5s. Migrations are protected from editing once merged.
- BE-9. Repository tests run against real Postgres (Testcontainers). Never mock the database client.

## Reliability
- BE-10. Every outbound call has a timeout (default <<FILL: 2000>> ms), bounded retries with jitter only for idempotent operations, and a circuit breaker for dependencies listed in `<<FILL: src/clients/>>`.
- BE-11. Handle `unhandledRejection`/`uncaughtException` by logging and exiting; never continue in an unknown state. Graceful shutdown on SIGTERM within <<FILL: 25>> s.
- BE-12. Logging: `pino` JSON via `src/log.ts`; include `requestId`, `traceId`; levels: `error` (needs action), `warn` (degraded), `info` (business events), `debug` (off in prod). No personal data, tokens or full request bodies.

<!-- REPO-SPECIFIC:START -->
<!-- REPO-SPECIFIC:END -->
