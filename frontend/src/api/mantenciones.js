import client from "./client";

export async function getMantenciones({ equipoId = null, limit = null, order = "desc" } = {}) {
  const params = {};
  if (equipoId !== null && equipoId !== undefined) {
    params.equipo_id = equipoId;
  }
  if (limit !== null && limit !== undefined) {
    params.limit = limit;
  }
  if (order) {
    params.order = order;
  }

  const { data } = await client.get("/api/v1/mantenciones", { params });
  return data;
}

export async function createMantencion(payload) {
  const { data } = await client.post("/api/v1/mantenciones", payload);
  return data;
}

export async function updateMantencion(id, payload) {
  const { data } = await client.put(`/api/v1/mantenciones/${id}`, payload);
  return data;
}
