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
    await use(page);
  },
});

export { expect } from "@playwright/test";
