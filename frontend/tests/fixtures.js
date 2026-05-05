/**
 * Fixtures compartidos para tests E2E de Playwright.
 *
 * Proporciona un contexto de browser con el onboarding desactivado
 * para que los tests no sean interferidos por el tour guiado.
 */
import { test as base } from "@playwright/test";

/**
 * Extiende el test base con fixtures compartidos.
 */
export const test = base.extend({
  // Inyecta localStorage antes de cada test para desactivar el onboarding
  page: async ({ page }, use) => {
    await page.addInitScript(() => {
      window.localStorage.setItem("manttoai_onboarding_done", "true");
    });

    // Mock por defecto para notificaciones del topbar.
    // Evita redirecciones espurias a /login cuando un test no stubbea alertas.
    await page.route(/\/api(?:\/v1)?\/alertas(?:\?.*)?$/, async (route) => {
      if (route.request().method() === "PATCH") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ ok: true }),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });

    await use(page);
  },
});

export { expect } from "@playwright/test";
