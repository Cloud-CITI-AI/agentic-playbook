// managed-by: agentic-playbook v1.0.0
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    coverage: { provider: "v8", reporter: ["text-summary", "cobertura"], exclude: ["src/gen/**", "**/*.test.ts"] },
    projects: [
      { test: { name: "unit", include: ["src/**/*.test.ts"], exclude: ["src/**/*.int.test.ts", "src/**/*.contract.test.ts"], environment: "node" } },
      {
        test: {
          name: "integration",
          include: ["src/**/*.int.test.ts"],
          globalSetup: ["./test/global-setup.ts"],   // starts one Postgres Testcontainer, runs migrations
          testTimeout: 30_000,
          hookTimeout: 120_000,
          pool: "forks",
        },
      },
      { test: { name: "contract", include: ["src/**/*.contract.test.ts"], globalSetup: ["./test/global-setup.ts"] } },
    ],
  },
});
