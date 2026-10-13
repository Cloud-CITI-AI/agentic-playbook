// managed-by: agentic-playbook v1.0.0
import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.E2E_BASE_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,          // X4: a stray test.only fails CI
  retries: process.env.CI ? 1 : 0,       // one retry ONLY to detect flakes; a pass-on-retry is reported as flaky (docs/06 §6.5)
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }], ["json", { outputFile: "test-results/results.json" }]] : "list",
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01, animations: "disabled" },
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : { command: "pnpm start", url: baseURL, reuseExistingServer: !process.env.CI, timeout: 120_000 },
});
