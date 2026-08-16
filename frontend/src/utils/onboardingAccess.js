const ONBOARDING_ROLES = new Set(["admin", "tecnico"]);

/**
 * Indica si el usuario puede ejecutar la configuración persistente inicial.
 * Los visualizadores tienen acceso de lectura y no deben entrar al wizard.
 */
export function canManageOnboarding(user) {
  return ONBOARDING_ROLES.has(user?.rol);
}
