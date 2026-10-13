<!-- managed-by: agentic-playbook v1.0.0 | profile: frontend | adds to root AGENTS.md; may tighten, never loosen -->
# AGENTS.md — <<FILL: package name, e.g. apps/web>> (Next.js / React / TypeScript)

## Commands (run in this directory)
| Purpose | Command |
|---|---|
| Dev server | `pnpm dev` |
| Full gate | `pnpm verify` (= lint + typecheck + test:unit + build) |
| Unit and component tests | `pnpm test:unit` (Vitest + Testing Library); single file: `pnpm test:unit path/to/file.test.tsx` |
| End-to-end, accessibility, visual | `pnpm test:e2e` (Playwright; needs `pnpm build` first) |
| Update visual baselines | `pnpm test:e2e --update-snapshots` — only when the UI change is intended; attach before/after images to the PR |
| Mutation (changed files) | `pnpm test:mutation` |
| Bundle and performance check | `pnpm perf:check` |

## Architecture
- FE-1. App Router. Components are Server Components by default. Add `"use client"` only for state, effects, browser APIs or event handlers, at the smallest component that needs it.
- FE-2. Server state: <<FILL: Server Components + fetch with revalidate  OR  TanStack Query>>. Local UI state: `useState`/`useReducer`. Do not add a global state library; propose it instead.
- FE-3. Data access from the browser goes through `<<FILL: src/lib/api/>>` only. Never call third-party APIs from client components with credentials.
- FE-4. Component files: one exported component, typed props interface named `<Component>Props`, test file next to it (`Button.test.tsx`).
- FE-5. Styling: <<FILL: Tailwind with design tokens in tailwind.config.ts  OR  CSS Modules>>. Use existing design-system components from `<<FILL: src/components/ui/>>` before writing new ones.

## Accessibility (WCAG 2.2 AA — not overridable)
- FE-6. Use semantic elements (`button`, `a`, `nav`, `label`). No click handlers on `div`/`span`.
- FE-7. Every interactive element is keyboard reachable with a visible focus state; every input has a programmatic label; images have meaningful `alt` or `alt=""` if decorative.
- FE-8. Component tests query by role/label (`getByRole`), not by test ID, unless no accessible name exists. Each new page gets an axe scan in `e2e/a11y.spec.ts`; zero serious or critical violations.

## Performance budgets (checked by `pnpm perf:check` and Lighthouse CI)
- FE-9. Per route: first-load JS ≤ <<FILL: 170>> KB gzip; LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at p75 on the reference profile. Use `next/image` and `next/font`. Lazy-load below-the-fold client components.

## Security
- FE-10. No `dangerouslySetInnerHTML` unless the input passes through `<<FILL: src/lib/sanitize.ts>>` (DOMPurify) and the PR flags it.
- FE-11. Only `NEXT_PUBLIC_*` variables reach the browser; never put secrets or internal URLs in them.
- FE-12. Do not weaken the Content-Security-Policy or security headers in `<<FILL: next.config.ts / middleware.ts>>` (protected path).

## Testing specifics
- FE-13. A new component needs: render test, interaction test for each handler, axe check. A new page needs: one Playwright happy-path test and one error-state test.
- FE-14. Network in component tests is mocked with MSW handlers in `<<FILL: src/test/msw/>>`; never hit real APIs.

<!-- REPO-SPECIFIC:START -->
<!-- REPO-SPECIFIC:END -->
