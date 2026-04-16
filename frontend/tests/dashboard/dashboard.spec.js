import { expect, test } from "../fixtures";

test("dashboard consume API real y reemplaza placeholders", async ({ page }) => {
  const pageErrors = [];
  page.on("pageerror", (error) => {
    pageErrors.push(error.message);
  });

  const now = new Date();
  const oneMinuteAgo = new Date(now.getTime() - 60 * 1000);
  const twoMinutesAgo = new Date(now.getTime() - 2 * 60 * 1000);

  // Establecer cookie de sesión antes de navegar
  await page.context().addCookies([
    {
      name: "manttoai_token",
      value: "mock-session-token",
      domain: "127.0.0.1",
      path: "/",
      httpOnly: true,
      sameSite: "Lax",
    },
  ]);

  await page.route(/\/api(?:\/v1)?\/auth\/me$/, async (route) => {
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

  // Mock de onboarding completado (requerido por OnboardingGuard)
  await page.route("**/api/v1/onboarding/status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        onboarding_step: 3,
        onboarding_completed: true,
      }),
    });
  });

  await page.route("**/api/v1/dashboard/resumen", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        total_equipos: 2,
        alertas_activas: 1,
        equipos_en_riesgo: 1,
        ultima_clasificacion: "alerta",
        probabilidad_falla: 0.68,
        equipos: [
          {
            id: 1,
            nombre: "Compresor principal",
            ultima_temperatura: 51.2,
            ultima_probabilidad: 0.68,
            alertas_activas: 1,
          },
          {
            id: 2,
            nombre: "Bomba respaldo",
            ultima_temperatura: 35.4,
            ultima_probabilidad: 0.22,
            alertas_activas: 0,
          },
        ],
      }),
    });
  });

  await page.route("**/api/v1/lecturas**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 1001,
          equipo_id: 1,
          temperatura: 51.2,
          humedad: 60.1,
          vib_x: 0.28,
          vib_y: 0.21,
          vib_z: 0.18,
          timestamp: now.toISOString(),
        },
        {
          id: 1002,
          equipo_id: 2,
          temperatura: 35.4,
          humedad: 54.3,
          vib_x: 0.12,
          vib_y: 0.16,
          vib_z: 0.15,
          timestamp: oneMinuteAgo.toISOString(),
        },
        {
          id: 1003,
          equipo_id: 1,
          temperatura: 49.8,
          humedad: 59.6,
          vib_x: 0.26,
          vib_y: 0.2,
          vib_z: 0.17,
          timestamp: twoMinutesAgo.toISOString(),
        },
      ]),
    });
  });

  await page.goto("/dashboard");

  await expect(page.getByRole("heading", { name: /Centro de control operacional/i })).toBeVisible();
  const probabilidadCard = page.locator("article").filter({ has: page.locator("span", { hasText: "Probabilidad de falla" }) });
  await expect(probabilidadCard).toBeVisible();
  await expect(probabilidadCard.getByText("68.0 %", { exact: true })).toBeVisible();

  await expect(page.getByRole("heading", { name: "Temperatura" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vibración" })).toBeVisible();
  await expect(
    page.getByText("Placeholder del gráfico temporal de temperatura.")
  ).toHaveCount(0);
  await expect(
    page.getByText("Placeholder del gráfico temporal de vibración.")
  ).toHaveCount(0);

  await expect(page.getByRole("cell", { name: "Compresor principal" }).first()).toBeVisible();
  await expect(page.getByRole("cell", { name: "Bomba respaldo" }).first()).toBeVisible();
  await expect(page.getByRole("cell", { name: "51.20 °C" }).first()).toBeVisible();
  await expect(page.getByRole("cell", { name: "35.40 °C" }).first()).toBeVisible();

  expect(pageErrors).toEqual([]);
});
