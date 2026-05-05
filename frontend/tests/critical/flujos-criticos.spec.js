import { expect, test } from "../fixtures";

function cookieSesionMock() {
  return {
    name: "manttoai_token",
    value: "mock-session-token",
    domain: "127.0.0.1",
    path: "/",
    httpOnly: true,
    sameSite: "Lax",
  };
}

async function mockUsuarioAutenticado(page) {
  await page.route(/\/api(?:\/v1)?\/auth\/me$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        nombre: "Usuario Demo",
        email: "demo@manttoai.local",
        rol: "admin",
      }),
    });
  });
}

async function mockOnboardingCompletado(page) {
  await page.route(/\/api(?:\/v1)?\/onboarding\/status$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        onboarding_step: 5,
        onboarding_completed: true,
      }),
    });
  });
}

test.describe("Flujos críticos de usuario", () => {
  test("inicia sesión y navega al tablero", async ({ page }) => {
    let payloadLogin = null;
    let autenticado = false;

    await page.route(/\/api(?:\/v1)?\/auth\/me$/, async (route) => {
      if (!autenticado) {
        await route.fulfill({
          status: 401,
          contentType: "application/json",
          body: JSON.stringify({ detail: "No autenticado" }),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: 1,
          nombre: "Usuario Demo",
          email: "demo@manttoai.local",
          rol: "admin",
        }),
      });
    });

    await page.route(/\/api(?:\/v1)?\/auth\/login$/, async (route) => {
      payloadLogin = route.request().postDataJSON();
      autenticado = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "mock-session-token",
          token_type: "bearer",
        }),
      });
    });

    await mockOnboardingCompletado(page);

    await page.route(/\/api(?:\/v1)?\/dashboard\/resumen$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_equipos: 1,
          alertas_activas: 0,
          equipos_en_riesgo: 0,
          ultima_clasificacion: "normal",
          probabilidad_falla: 0.12,
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

    await page.goto("/login");
    await page.getByLabel("Email").fill("demo@manttoai.local");
    await page.getByLabel("Contraseña").fill("Clave123!");
    await page.getByRole("button", { name: "Continuar" }).click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(
      page.getByRole("heading", { name: /Centro de control/i })
    ).toBeVisible();
    expect(payloadLogin).toEqual({
      email: "demo@manttoai.local",
      password: "Clave123!",
    });
  });

  test("renderiza el dashboard con resumen y tendencias", async ({ page }) => {
    await page.context().addCookies([cookieSesionMock()]);
    await mockUsuarioAutenticado(page);
    await mockOnboardingCompletado(page);

    await page.route(/\/api(?:\/v1)?\/dashboard\/resumen$/, async (route) => {
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
              rubro: "industrial",
            },
            {
              id: 2,
              nombre: "Bomba secundaria",
              ultima_temperatura: 35.4,
              ultima_probabilidad: 0.22,
              alertas_activas: 0,
              rubro: "comercial",
            },
          ],
        }),
      });
    });

    await page.route(/\/api(?:\/v1)?\/lecturas(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: 1,
            equipo_id: 1,
            temperatura: 51.2,
            humedad: 60,
            vib_x: 0.2,
            vib_y: 0.1,
            vib_z: 0.3,
            timestamp: new Date().toISOString(),
          },
          {
            id: 2,
            equipo_id: 2,
            temperatura: 35.4,
            humedad: 55,
            vib_x: 0.1,
            vib_y: 0.2,
            vib_z: 0.2,
            timestamp: new Date().toISOString(),
          },
        ]),
      });
    });

    await page.goto("/dashboard");

    await expect(
      page.getByRole("heading", { name: /Centro de control/i })
    ).toBeVisible();
    await expect(page.getByRole("heading", { name: "Temperatura" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Vibración" })).toBeVisible();
    await expect(
      page.getByRole("cell", { name: "Compresor principal" }).first()
    ).toBeVisible();
    await expect(
      page.getByRole("cell", { name: "Bomba secundaria" }).first()
    ).toBeVisible();
  });

  test("marca alertas como leídas y refresca estado", async ({ page }) => {
    await page.context().addCookies([cookieSesionMock()]);
    await mockUsuarioAutenticado(page);
    await mockOnboardingCompletado(page);

    let alertaLeida = false;
    await page.route(/\/api(?:\/v1)?\/alertas(?:\/\d+\/leer)?(?:\?.*)?$/, async (route) => {
      const { method, url } = route.request();
      if (method === "PATCH" && /\/alertas\/\d+\/leer$/.test(url)) {
        alertaLeida = true;
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ leida: true }),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          alertaLeida
            ? [
                {
                  id: 11,
                  equipo_id: 1,
                  tipo: "temperatura",
                  mensaje: "Temperatura fuera de rango",
                  nivel: "alto",
                  email_enviado: true,
                  leida: true,
                  created_at: new Date().toISOString(),
                },
              ]
            : [
                {
                  id: 11,
                  equipo_id: 1,
                  tipo: "temperatura",
                  mensaje: "Temperatura fuera de rango",
                  nivel: "alto",
                  email_enviado: true,
                  leida: false,
                  created_at: new Date().toISOString(),
                },
              ]
        ),
      });
    });

    await page.goto("/alertas");

    await expect(page.getByRole("heading", { name: "Alertas" })).toBeVisible();
    await expect(page.getByText("Temperatura fuera de rango")).toBeVisible();

    await page.getByRole("button", { name: "Marcar como leída" }).click();
    await expect(
      page.getByRole("button", { name: "Marcar como leída" })
    ).toHaveCount(0);
    expect(alertaLeida).toBeTruthy();
  });
});
