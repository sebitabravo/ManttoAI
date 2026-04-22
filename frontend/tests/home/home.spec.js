import { expect, test } from "../fixtures";

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

  // Mock de onboarding completado (requerido por OnboardingGuard)
  // Usar una variable para que el mock funcione después del logout
  let isOnboardingCompleted = false;
  await page.route(/\/api(?:\/v1)?\/onboarding\/status$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        onboarding_step: isOnboardingCompleted ? 5 : 3,
        onboarding_completed: isOnboardingCompleted,
      }),
    });
  });

  // Navegar a login
  await page.goto("/login");
  // El h1 del login ahora muestra "ManttoAI" (branding actualizado en issue #53)
  await expect(page.getByRole("heading", { name: "ManttoAI" })).toBeVisible();

  // Llenar formulario y enviar
  await page.getByLabel("Email").fill("demo@example.com");
  await page.getByLabel("Contraseña").fill("123456");
  await page.getByRole("button", { name: "Continuar" }).click();

  // Esperar a que la URL cambie (cualquier página autenticada)
  await page.waitForURL(/\/(dashboard|onboarding|equipos)$/, { timeout: 15000 });

  // Verificar que no stayed en login
  await expect(page).not.toHaveURL(/\/login$/);

  // Verificar que el payload del login fue correcto
  expect(loginPayload).toEqual({
    email: "demo@example.com",
    password: "123456",
  });

  // Verificar que el usuario llegó a una página autenticada exitosa
  // (no stayed en login y puede ver contenido del dashboard o wizard)
});
