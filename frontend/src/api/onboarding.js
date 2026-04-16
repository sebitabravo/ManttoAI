import client from "./client";

/**
 * Obtiene el estado actual del onboarding del usuario.
 * @returns {Promise<{onboarding_step: number|null, onboarding_completed: boolean}>}
 */
export async function getOnboardingStatus() {
  const { data } = await client.get("/onboarding/status");
  return data;
}

/**
 * Actualiza el paso actual del onboarding.
 * @param {number} step - Paso actual (1-5)
 * @returns {Promise<{onboarding_step: number|null, onboarding_completed: boolean}>}
 */
export async function updateOnboardingStep(step) {
  const { data } = await client.patch("/onboarding/step", { step });
  return data;
}

/**
 * Marca el onboarding como completado.
 * @param {Object} payload - Datos de los recursos creados
 * @param {number} payload.equipo_id - ID del equipo creado
 * @param {number} [payload.api_key_id] - ID de la API key creada (opcional)
 * @returns {Promise<void>}
 */
export async function completeOnboarding(payload) {
  await client.post("/onboarding/complete", payload);
}

/**
 * Resetea el onboarding para volver a realizar el wizard (solo admin).
 * @returns {Promise<void>}
 */
export async function resetOnboarding() {
  await client.post("/onboarding/reset");
}
