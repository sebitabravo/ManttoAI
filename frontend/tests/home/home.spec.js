import { expect, test } from "@playwright/test";

test("sin token no se puede acceder al dashboard", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ManttoAI Predictivo" })).toBeVisible();
});

test("el usuario puede iniciar sesión y entrar al dashboard", async ({ page }) => {
  let loginPayload = null;

  await page.route("**/api/auth/login", async (route) => {
    loginPayload = route.request().postDataJSON();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "cookie-session-token",
        token_type: "bearer",
      }),
    });
  });

  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        nombre: "demo",
        email: "demo@example.com",
        rol: "visualizador",
      }),
    });
  });

  await page.route("**/api/auth/logout", async (route) => {
    await route.fulfill({ status: 204, body: "" });
  });

  await page.goto("/login");
  await page.getByLabel("Email").fill("demo@example.com");
  await page.getByLabel("Contraseña").fill("123456");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(
        () => JSON.parse(window.sessionStorage.getItem("manttoai_user") || "null")?.email
      )
    )
    .toBe("demo@example.com");

  expect(loginPayload).toEqual({
    email: "demo@example.com",
    password: "123456",
  });

  await page.getByRole("button", { name: "Salir" }).click();

  await expect(page).toHaveURL(/\/login$/);
  await expect.poll(() => page.evaluate(() => window.sessionStorage.getItem("manttoai_user"))).toBeNull();
});
