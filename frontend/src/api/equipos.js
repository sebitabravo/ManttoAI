import client from "./client";

export async function getEquipos() {
  const { data } = await client.get("/api/v1/equipos");
  return data;
}

export async function getEquipo(id) {
  const { data } = await client.get(`/api/v1/equipos/${id}`);
  return data;
}

export async function createEquipo(payload) {
  const { data } = await client.post("/api/v1/equipos", payload);
  return data;
}

export async function updateEquipo(id, payload) {
  const { data } = await client.put(`/api/v1/equipos/${id}`, payload);
  return data;
}

// Elimina un equipo por ID — expone el endpoint DELETE /equipos/{id} del backend
export async function deleteEquipo(id) {
  await client.delete(`/api/v1/equipos/${id}`);
}
