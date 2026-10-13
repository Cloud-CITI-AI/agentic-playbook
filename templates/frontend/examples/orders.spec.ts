// Worked example: Playwright e2e — happy path, error state, accessibility scan, visual check (FE-8, FE-13).
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Orders page", () => {
  test("filters to closed orders", async ({ page }) => {
    await page.goto("/orders");
    await page.getByRole("radio", { name: "Closed" }).check();
    await expect(page.getByRole("row").filter({ hasText: "Open" })).toHaveCount(0);
    await expect(page).toHaveURL(/status=closed/);
  });

  test("shows a recoverable error when the API fails", async ({ page }) => {
    await page.route("**/api/orders**", (route) => route.fulfill({ status: 503, contentType: "application/problem+json", body: JSON.stringify({ title: "Unavailable" }) }));
    await page.goto("/orders");
    await expect(page.getByRole("alert")).toContainText("couldn't load orders");
    await expect(page.getByRole("button", { name: "Try again" })).toBeEnabled();
  });

  test("has no serious or critical accessibility violations", async ({ page }) => {
    await page.goto("/orders");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]).analyze();
    const blocking = results.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
    expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
  });

  test("matches the visual baseline", async ({ page }) => {
    await page.goto("/orders?fixture=stable");   // deterministic fixture data; never real data
    await expect(page).toHaveScreenshot("orders.png", { fullPage: true });
  });
});
