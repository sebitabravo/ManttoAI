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
