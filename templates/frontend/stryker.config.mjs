// managed-by: agentic-playbook v1.0.0
/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  testRunner: "vitest",
  checkers: ["typescript"],
  tsconfigFile: "tsconfig.json",
  coverageAnalysis: "perTest",
  incremental: true,
  incrementalFile: ".stryker-tmp/incremental.json",   // cache in CI, never commit
  // Mutate logic, not markup: hooks, utils, state, formatting, validation.
  mutate: ["src/**/*.{ts,tsx}", "!src/**/*.test.{ts,tsx}", "!src/**/*.stories.tsx", "!src/gen/**", "!src/app/**/page.tsx", "!src/app/**/layout.tsx"],
  thresholds: { high: 80, low: 70, break: 60 },
  reporters: ["clear-text", "progress", "html", "json"],
};
