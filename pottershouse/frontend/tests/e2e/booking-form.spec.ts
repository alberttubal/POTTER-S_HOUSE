import { test, expect } from "@playwright/test";

test("booking form tab order inside form", async ({ page }) => {
  await page.goto("/contact");
  await page.locator("#customer_name").focus();
  await page.keyboard.press("Tab");
  await expect(page.locator("#phone")).toBeFocused();
});
