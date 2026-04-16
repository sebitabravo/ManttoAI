import { expect, test } from "../fixtures";

test.describe("Onboarding Wizard", () => {
  test.beforeEach(async ({ page }) => {
    // Configurar cookie de sesión
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

    // Mock del endpoint de usuario autenticado
    await page.route(/\/api(?:\/v1)?\/auth\/me$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: 1,
          nombre: "Test User",
          email: "test@example.com",
          rol: "admin",
        }),
      });
    });
  });

  test("completa el wizard de onboarding exitosamente",
    { tag: ["@critical", "@e2e", "@onboarding", "@ONBOARDING-E2E-001"] },
    async ({ page }) => {
      // Mock del estado inicial del onboarding (no completado)
      await page.route("**/api/v1/onboarding/status", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: 1,
            onboarding_completed: false,
          }),
        });
      });

      // Mock de actualización de paso
      await page.route("**/api/v1/onboarding/step", async (route) => {
        const requestBody = await route.request().postDataJSON();
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: requestBody.step,
            onboarding_completed: false,
          }),
        });
      });

      // Mock de creación de equipo (full-setup)
      await page.route("**/api/v1/equipos/full-setup", async (route) => {
        const requestBody = await route.request().postDataJSON();
        await route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({
            equipo: {
              id: 1,
              ...requestBody,
              descripcion: "Equipo monitoreado por ManttoAI",
              estado: "operativo",
            },
            umbral_temperatura_id: 101,
            umbral_vibracion_id: 102
          }),
        });
      });

      // Mock de creación de umbrales
      await page.route("**/api/v1/umbrales/equipo/1", async (route) => {
        const requestBody = await route.request().postDataJSON();
        await route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({
            id: Math.floor(Math.random() * 1000),
            equipo_id: 1,
            ...requestBody,
          }),
        });
      });

      // Mock de creación de API key
      await page.route("**/api/v1/api-keys", async (route) => {
        await route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({
            id: 1,
            key: "mantto_test_api_key_1234567890",
            key_prefix: "mantto_test",
            device_id: "equipo_1",
            is_active: true,
            created_at: new Date().toISOString(),
            last_used_at: null,
            revoked_at: null,
          }),
        });
      });

      // Variable para controlar el estado del onboarding
      let onboardingCompleted = false;

      // Mock de status que cambia después de completar
      await page.route("**/api/v1/onboarding/status", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: onboardingCompleted ? 5 : 1,
            onboarding_completed: onboardingCompleted,
          }),
        });
      });

      // Mock de completación del onboarding
      await page.route("**/api/v1/onboarding/complete", async (route) => {
        onboardingCompleted = true;
        await route.fulfill({
          status: 204,
          contentType: "application/json",
          body: "",
        });
      });

      // Navegar al wizard
      await page.goto("/onboarding");

      // PASO 1: Bienvenida
      await expect(page.getByRole("heading", { name: "Bienvenido a ManttoAI" })).toBeVisible();
      await expect(page.getByText("Paso 1 de 5")).toBeVisible();
      await expect(page.getByRole("button", { name: "Comenzar" })).toBeVisible();

      // Avanzar al paso 2
      await page.getByRole("button", { name: "Comenzar" }).click();

      // PASO 2: Crear equipo
      await expect(page.getByRole("heading", { name: "Crea tu primer equipo" })).toBeVisible();
      await expect(page.getByText("Paso 2 de 5")).toBeVisible();

      // Llenar formulario
      await page.getByLabel("Nombre del equipo *").fill("Motor de prueba");
      await page.getByLabel("Ubicación").fill("Planta de pruebas");

      // Avanzar (equipo + umbrales se crean juntos en paso 2 usando full-setup)
      await page.getByRole("button", { name: "Siguiente" }).click();

      // PASO 3: Umbrales (el frontend muestra paso 3 por compatibilidad)
      await expect(page.getByRole("heading", { name: "Configura umbrales de alerta" })).toBeVisible();
      await expect(page.getByText("Paso 3 de 5")).toBeVisible();
      
      // Verificar campos pre-llenados
      await expect(page.getByLabel("Temperatura máxima (°C)")).toHaveValue("80");
      await expect(page.getByLabel("Vibración máxima (g)")).toHaveValue("0.5");

      // Avanzar al paso 4
      await page.getByRole("button", { name: "Siguiente" }).click();

      // PASO 4: Generar API Key
      await expect(page.getByRole("heading", { name: "Conecta tu dispositivo IoT" })).toBeVisible();
      await expect(page.getByText("Paso 4 de 5")).toBeVisible();

      // Generar API Key
      await page.getByRole("button", { name: "Generar API Key" }).click();

      // Verificar que se muestra la API Key
      await expect(page.getByText("API Key generada exitosamente")).toBeVisible();
      await expect(page.locator(".font-mono")).toContainText("mantto_test_api_key_");

      // Avanzar al paso 5
      await page.getByRole("button", { name: "Siguiente" }).click();

      // PASO 5: Finalización
      await expect(page.getByRole("heading", { name: "¡Todo listo!" })).toBeVisible();
      await expect(page.getByText("Paso 5 de 5")).toBeVisible();
      await expect(page.getByText("Motor de prueba")).toBeVisible();
      await expect(page.getByRole("button", { name: "Ir al Dashboard" })).toBeVisible();

      // Finalizar el wizard
      await page.getByRole("button", { name: "Ir al Dashboard" }).click();

      // Verificar redirección al dashboard
      await expect(page).toHaveURL("/dashboard");
    }
  );

  test("permite saltar el wizard",
    { tag: ["@medium", "@e2e", "@onboarding", "@ONBOARDING-E2E-002"] },
    async ({ page }) => {
      let onboardingCompleted = false;

      // Mock dinámico del estado del onboarding
      await page.route("**/api/v1/onboarding/status", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: onboardingCompleted ? 5 : 1,
            onboarding_completed: onboardingCompleted,
          }),
        });
      });

      // Mock de completación del onboarding
      await page.route("**/api/v1/onboarding/complete", async (route) => {
        onboardingCompleted = true;
        await route.fulfill({
          status: 204,
          contentType: "application/json",
          body: "",
        });
      });

      // Navegar al wizard
      await page.goto("/onboarding");

      // Verificar que el botón de saltar está visible
      await expect(page.getByRole("button", { name: "Saltar y configurar después" })).toBeVisible();

      // Saltar el wizard
      await page.getByRole("button", { name: "Saltar y configurar después" }).click();

      // Esperar a que redireccione
      await page.waitForTimeout(1000);

      // Verificar redirección al dashboard
      await expect(page).toHaveURL("/dashboard");
    }
  );

  test("permite navegar entre pasos",
    { tag: ["@medium", "@e2e", "@onboarding", "@ONBOARDING-E2E-003"] },
    async ({ page }) => {
      // Mock del estado inicial del onboarding
      await page.route("**/api/v1/onboarding/status", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: 1,
            onboarding_completed: false,
          }),
        });
      });

      // Mock de actualización de paso
      await page.route("**/api/v1/onboarding/step", async (route) => {
        const requestBody = await route.request().postDataJSON();
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: requestBody.step,
            onboarding_completed: false,
          }),
        });
      });

      // Navegar al wizard
      await page.goto("/onboarding");

      // Avanzar al paso 2
      await page.getByRole("button", { name: "Comenzar" }).click();
      await expect(page.getByText("Paso 2 de 5")).toBeVisible();

      // Volver al paso 1
      await page.getByRole("button", { name: "Anterior" }).click();
      await expect(page.getByText("Paso 1 de 5")).toBeVisible();
      await expect(page.getByRole("heading", { name: "Bienvenido a ManttoAI" })).toBeVisible();

      // Avanzar nuevamente al paso 2
      await page.getByRole("button", { name: "Comenzar" }).click();
      await expect(page.getByText("Paso 2 de 5")).toBeVisible();
    }
  );

  test("muestra error cuando falla la creación de equipo",
    { tag: ["@low", "@e2e", "@onboarding", "@ONBOARDING-E2E-004"] },
    async ({ page }) => {
      let stepUpdateCallCount = 0;

      // Mock del estado inicial del onboarding (empieza en paso 1)
      await page.route("**/api/v1/onboarding/status", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: 1,
            onboarding_completed: false,
          }),
        });
      });

      // Mock de actualización de paso
      await page.route("**/api/v1/onboarding/step", async (route) => {
        const requestBody = await route.request().postDataJSON();
        stepUpdateCallCount++;
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            onboarding_step: requestBody.step,
            onboarding_completed: false,
          }),
        });
      });

      // Mock de error al crear equipo (full-setup)
      await page.route("**/api/v1/equipos/full-setup", async (route) => {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            detail: "Error al crear equipo",
          }),
        });
      });

      // Navegar al wizard
      await page.goto("/onboarding");

      // Paso 1: Click enComenzar para avanzar al paso 2
      await page.getByRole("button", { name: "Comenzar" }).click();

      // Esperar a que actualice el paso
      await page.waitForTimeout(500);

      // Paso 2: Verificar que estamos en el formulario de equipo
      await expect(page.getByText("Nombre del equipo")).toBeVisible({ timeout: 10000 });

      // Llenar formulario
      await page.getByLabel("Nombre del equipo *").fill("Motor de prueba");

      // Intentar avanzar (debería fallar)
      await page.getByRole("button", { name: "Siguiente" }).click();

      // Verificar que se muestra el error
      await expect(page.getByText(/Error al crear equipo|No se pudo crear/i)).toBeVisible({ timeout: 10000 });
    }
  );
});
