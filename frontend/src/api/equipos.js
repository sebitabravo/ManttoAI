import client from "./client";

export async function getEquipos() {
  const { data } = await client.get("/equipos");
  return data;
}

export async function getEquipo(id) {
  const { data } = await client.get(`/equipos/${id}`);
  return data;
}

export async function createEquipo(payload) {
  const { data } = await client.post("/equipos", payload);
  return data;
}

export async function updateEquipo(id, payload) {
  const { data } = await client.put(`/equipos/${id}`, payload);
  return data;
}

// Elimina un equipo por ID — expone el endpoint DELETE /equipos/{id} del backend
export async function deleteEquipo(id) {
  await client.delete(`/equipos/${id}`);
}

// Crea equipo con umbrales en una sola transacción atómica (backend)
// Devuelve: { equipo, umbral_temperatura_id, umbral_vibracion_id }
export async function createEquipoFull(payload) {
  const { data } = await client.post("/equipos/full-setup", payload);
  return data;
}
