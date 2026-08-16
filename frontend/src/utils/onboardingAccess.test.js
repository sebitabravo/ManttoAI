import { describe, expect, it } from "vitest";

import { canManageOnboarding } from "./onboardingAccess";

describe("canManageOnboarding", () => {
  it("permite onboarding a los roles con permisos de configuración", () => {
    expect(canManageOnboarding({ rol: "admin" })).toBe(true);
    expect(canManageOnboarding({ rol: "tecnico" })).toBe(true);
  });

  it("rechaza onboarding para cuentas de solo lectura", () => {
    expect(canManageOnboarding({ rol: "visualizador" })).toBe(false);
    expect(canManageOnboarding(null)).toBe(false);
  });
});
