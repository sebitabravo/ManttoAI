import client from "./client";

export async function getUmbrales(equipoId) {
  const config = Number.isFinite(Number(equipoId))
    ? { params: { equipo_id: Number(equipoId) } }
    : undefined;
  const { data } = config
    ? await client.get("/umbrales", config)
    : await client.get("/umbrales");
  return data;
}

/**
 * Crea un nuevo umbral para un equipo específico.
 * @param {number} equipoId - ID del equipo
 * @param {Object} payload - Datos del umbral
 * @param {string} payload.sensor_tipo - Tipo de sensor (temperatura, vibracion)
 * @param {number} payload.valor_max - Valor máximo del umbral
 * @param {string} payload.condicion - Condición (mayor_que, menor_que)
 * @param {string} payload.nivel_severidad - Nivel de severidad (bajo, medio, alto)
 * @param {string} payload.mensaje - Mensaje de la alerta
 * @returns {Promise<Object>} El umbral creado
 */
export async function createUmbral(equipoId, payload) {
  const { data } = await client.post(`/umbrales/equipo/${equipoId}`, payload);
  return data;
}

export async function updateUmbral(id, payload) {
  const { data } = await client.put(`/umbrales/${id}`, payload);
  return data;
}
