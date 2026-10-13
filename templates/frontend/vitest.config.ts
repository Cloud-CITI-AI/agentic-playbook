// managed-by: agentic-playbook v1.0.0
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"], // registers @testing-library/jest-dom, MSW server, vitest-axe matchers
    include: ["src/**/*.test.{ts,tsx}"],
    restoreMocks: true,
    coverage: {
      provider: "v8",
      // cobertura feeds diff-cover in CI (diff coverage is the gate, not global %)
      reporter: ["text-summary", "cobertura", "html"],
      reportsDirectory: "coverage",
      exclude: ["src/**/*.stories.tsx", "src/gen/**", "src/test/**"],
    },
  },
});
