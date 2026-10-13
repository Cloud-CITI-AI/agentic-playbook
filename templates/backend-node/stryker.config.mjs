// managed-by: agentic-playbook v1.0.0
/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  testRunner: "vitest",
  vitest: { configFile: "vitest.config.ts", project: "unit" },
  checkers: ["typescript"],
  coverageAnalysis: "perTest",
  incremental: true,
  incrementalFile: ".stryker-tmp/incremental.json",
  mutate: ["src/domain/**/*.ts", "!src/**/*.test.ts"],   // domain logic is where mutation score matters most
  thresholds: { high: 80, low: 70, break: 60 },
  reporters: ["clear-text", "progress", "html", "json"],
};
