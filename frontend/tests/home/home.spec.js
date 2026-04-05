import { expect, test } from "@playwright/test";

function createFakeJwtToken() {
  const nowInSeconds = Math.floor(Date.now() / 1000);
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const payload = Buffer.from(
    JSON.stringify({ sub: "demo@example.com", exp: nowInSeconds + 3600 })
  ).toString("base64url");

  return `${header}.${payload}.signature`;
}

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
        access_token: createFakeJwtToken(),
        token_type: "bearer",
      }),
    });
  });

  await page.goto("/login");
  await page.getByLabel("Email").fill("demo@example.com");
  await page.getByLabel("Contraseña").fill("123456");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(() => {
        const storedToken = window.localStorage.getItem("manttoai_token") || "";
        return storedToken.split(".").length;
      })
    )
    .toBe(3);
  await expect
    .poll(() =>
      page.evaluate(
        () => JSON.parse(window.localStorage.getItem("manttoai_user") || "null")?.email
      )
    )
    .toBe("demo@example.com");

  expect(loginPayload).toEqual({
    email: "demo@example.com",
    password: "123456",
  });

  await page.getByRole("button", { name: "Salir" }).click();

  await expect(page).toHaveURL(/\/login$/);
  await expect.poll(() => page.evaluate(() => window.localStorage.getItem("manttoai_token"))).toBeNull();
  await expect.poll(() => page.evaluate(() => window.localStorage.getItem("manttoai_user"))).toBeNull();
});
