import { expect, test } from "../fixtures";

test("equipos, alertas e historial consumen backend real", async ({ page }) => {
  const pageErrors = [];
  page.on("pageerror", (error) => {
    pageErrors.push(error.message);
  });

  const now = new Date();
  const oneMinuteAgo = new Date(now.getTime() - 60 * 1000);
  const twoMinutesAgo = new Date(now.getTime() - 2 * 60 * 1000);

  const equipos = [
    {
      id: 1,
      nombre: "Compresor principal",
      estado: "operativo",
      ubicacion: "Sala 1",
      tipo: "Compresor",
    },
    {
      id: 2,
      nombre: "Bomba respaldo",
      estado: "monitoreo",
      ubicacion: "Sala 2",
      tipo: "Bomba",
    },
  ];

  const lecturas = [
    {
      id: 7001,
      equipo_id: 1,
      temperatura: 51.2,
      humedad: 60.3,
      vib_x: 0.28,
      vib_y: 0.22,
      vib_z: 0.19,
      timestamp: now.toISOString(),
    },
    {
      id: 7002,
      equipo_id: 1,
      temperatura: 49.4,
      humedad: 59.9,
      vib_x: 0.25,
      vib_y: 0.2,
      vib_z: 0.18,
      timestamp: oneMinuteAgo.toISOString(),
    },
    {
      id: 7003,
      equipo_id: 2,
      temperatura: 36.5,
      humedad: 54.1,
      vib_x: 0.14,
      vib_y: 0.12,
      vib_z: 0.16,
      timestamp: twoMinutesAgo.toISOString(),
    },
  ];

  const mantenciones = [
    {
      id: 9001,
      equipo_id: 1,
      tipo: "preventiva",
      descripcion: "Revisión de rodamientos",
      estado: "ejecutada",
    },
    {
      id: 9002,
      equipo_id: 2,
      tipo: "correctiva",
      descripcion: "Cambio de sello mecánico",
      estado: "programada",
    },
  ];

  let alertasStore = [
    {
      id: 3001,
      equipo_id: 1,
      tipo: "temperatura",
      mensaje: "Temperatura fuera de rango",
      nivel: "alto",
      email_enviado: true,
      leida: false,
      created_at: now.toISOString(),
    },
    {
      id: 3002,
      equipo_id: 2,
      tipo: "vibracion",
      mensaje: "Vibración elevada",
      nivel: "medio",
      email_enviado: false,
      leida: true,
      created_at: oneMinuteAgo.toISOString(),
    },
  ];

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
            ultima_temperatura: 36.5,
            ultima_probabilidad: 0.22,
            alertas_activas: 0,
          },
        ],
      }),
    });
  });

  await page.route("**/api/v1/equipos**", async (route) => {
    const requestUrl = new URL(route.request().url());
    const maybeId = requestUrl.pathname.split("/").at(-1);

    if (maybeId && maybeId !== "equipos" && /^\d+$/.test(maybeId)) {
      const foundEquipo = equipos.find((equipo) => Number(equipo.id) === Number(maybeId));
      if (!foundEquipo) {
        await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Equipo no encontrado" }) });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(foundEquipo),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(equipos),
    });
  });

  await page.route("**/api/v1/lecturas**", async (route) => {
    const requestUrl = new URL(route.request().url());
    const equipoId = requestUrl.searchParams.get("equipo_id");

    const payload = equipoId
      ? lecturas.filter((lectura) => Number(lectura.equipo_id) === Number(equipoId))
      : lecturas;

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(payload),
    });
  });

  await page.route("**/api/v1/predicciones/**", async (route) => {
    const requestUrl = new URL(route.request().url());
    const maybeId = requestUrl.pathname.split("/").at(-1);

    if (Number(maybeId) === 1) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          equipo_id: 1,
          clasificacion: "alerta",
          probabilidad: 0.68,
          modelo_version: "rf-mvp",
        }),
      });
      return;
    }

    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Predicción no encontrada para el equipo" }),
    });
  });

  await page.route("**/api/v1/umbrales**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  await page.route("**/api/v1/mantenciones**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(mantenciones),
    });
  });

  await page.route("**/api/v1/alertas**", async (route) => {
    const request = route.request();
    const requestUrl = new URL(request.url());

    if (request.method() === "PATCH" && requestUrl.pathname.endsWith("/leer")) {
      const alertaId = Number(requestUrl.pathname.split("/").at(-2));

      alertasStore = alertasStore.map((alerta) => {
        if (alerta.id === alertaId) {
          return { ...alerta, leida: true };
        }

        return alerta;
      });

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ id: alertaId, leida: true }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(alertasStore),
    });
  });

  await page.goto("/equipos");

  await expect(page.getByRole("heading", { name: "Equipos", exact: true })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Compresor principal" }).first()).toBeVisible();
  await expect(page.getByRole("cell", { name: "Bomba respaldo" }).first()).toBeVisible();
  await expect(page.getByRole("cell", { name: "51.20 °C" }).first()).toBeVisible();

  await page.getByRole("link", { name: "Ver detalle" }).first().click();

  await expect(page).toHaveURL(/\/equipos\/1$/);
  await expect(page.getByRole("heading", { name: "Detalle del equipo 1" })).toBeVisible();
  // El label y el porcentaje están en nodos hermanos dentro de la sección de predicción;
  // se verifica cada parte por separado para ser robusto ante cambios de layout.
  await expect(page.getByText("Probabilidad de falla")).toBeVisible();
  await expect(page.getByText("68.0 %")).toBeVisible();
  await expect(page.getByRole("cell", { name: "Revisión de rodamientos" })).toBeVisible();

  await page.getByRole("link", { name: "Alertas" }).click();

  await expect(page).toHaveURL(/\/alertas$/);
  await expect(page.getByRole("heading", { name: "Alertas" })).toBeVisible();
  await expect(page.getByText("Temperatura fuera de rango")).toBeVisible();
  await page.getByRole("button", { name: "Marcar como leída" }).first().click();
  await expect(page.getByText("No quedan alertas pendientes por marcar como leídas.")).toBeVisible();

  await page.getByRole("link", { name: "Historial" }).click();

  await expect(page).toHaveURL(/\/historial$/);
  await expect(page.getByRole("heading", { name: "Historial" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "51.20 °C" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Cambio de sello mecánico" })).toBeVisible();

  expect(pageErrors).toEqual([]);
});
