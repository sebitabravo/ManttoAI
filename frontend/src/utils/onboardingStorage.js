/**
 * Persistencia del estado del onboarding en localStorage.
 *
 * Archivo separado del componente para cumplir con la regla
 * react-refresh/only-export-components (Fast Refresh).
 */

const STORAGE_KEY = "manttoai_onboarding_done";

/**
 * Verifica si el onboarding ya fue completado.
 */
export function isOnboardingDone() {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

/**
 * Marca el onboarding como completado.
 */
export function markOnboardingDone() {
  try {
    localStorage.setItem(STORAGE_KEY, "true");
  } catch {
    // localStorage puede no estar disponible (ej. modo privado)
  }
}
