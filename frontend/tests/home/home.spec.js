import { expect, test } from "@playwright/test";

test("el usuario puede entrar al dashboard demo", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "ManttoAI Predictivo" })).toBeVisible();
  await page.getByRole("button", { name: "Entrar en modo demo" }).click();
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
});
