import { expect, test } from "@playwright/test";

test("sin token no se puede acceder al dashboard", async ({ page }) => {
  // Simular que no hay sesión activa - el backend devuelve 401
  await page.route(/\/api(?:\/v1)?\/auth\/me$/, async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "No autenticado" }),
    });
  });

  await page.goto("/dashboard");

  await expect(page).toHaveURL(/\/login$/);
  // El h1 del login ahora muestra "ManttoAI" (branding actualizado en issue #53)
  await expect(page.getByRole("heading", { name: "ManttoAI" })).toBeVisible();
});

test("el usuario puede iniciar sesión y entrar al dashboard", async ({ page }) => {
  let loginPayload = null;
  let isLoggedIn = false;

  // Mock /api(/v1)/auth/me: devuelve 401 hasta que el usuario haga login
  await page.route(/\/api(?:\/v1)?\/auth\/me$/, async (route) => {
    if (isLoggedIn) {
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
    } else {
      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "No autenticado" }),
      });
    }
  });

  // Mock /api(/v1)/auth/login: marca como logueado y devuelve token
  await page.route(/\/api(?:\/v1)?\/auth\/login$/, async (route) => {
    loginPayload = route.request().postDataJSON();
    isLoggedIn = true;

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "mock-session-token",
        token_type: "bearer",
      }),
    });
  });

  // Mock endpoints del dashboard para que no fallen
  await page.route(/\/api(?:\/v1)?\/dashboard\/resumen$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        total_equipos: 1,
        alertas_activas: 0,
        equipos_en_riesgo: 0,
        ultima_clasificacion: "normal",
        probabilidad_falla: 0.1,
        equipos: [],
      }),
    });
  });

  await page.route(/\/api(?:\/v1)?\/lecturas(?:\?.*)?$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  await page.route(/\/api(?:\/v1)?\/auth\/logout$/, async (route) => {
    isLoggedIn = false;
    await route.fulfill({ status: 204, body: "" });
  });

  // Navegar a login
  await page.goto("/login");
  // El h1 del login ahora muestra "ManttoAI" (branding actualizado en issue #53)
  await expect(page.getByRole("heading", { name: "ManttoAI" })).toBeVisible();

  // Llenar formulario y enviar
  await page.getByLabel("Email").fill("demo@example.com");
  await page.getByLabel("Contraseña").fill("123456");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();

  // Verificar redirección al dashboard
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: /Centro de control operacional/i })).toBeVisible();

  // Verificar que el payload del login fue correcto
  expect(loginPayload).toEqual({
    email: "demo@example.com",
    password: "123456",
  });

  // Verificar sessionStorage tiene el usuario
  await expect
    .poll(() =>
      page.evaluate(
        () => JSON.parse(window.sessionStorage.getItem("manttoai_user") || "null")?.email
      )
    )
    .toBe("demo@example.com");

  // Hacer logout
  await page.getByRole("button", { name: "Salir" }).click();

  // Verificar redirección a login y limpieza de sessionStorage
  await expect(page).toHaveURL(/\/login$/);
  await expect.poll(() => page.evaluate(() => window.sessionStorage.getItem("manttoai_user"))).toBeNull();
});
