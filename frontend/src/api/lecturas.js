import client from "./client";

export async function getLecturas(equipoId = null, limit = 100) {
  const params = {};
  if (equipoId !== null && equipoId !== undefined) {
    params.equipo_id = equipoId;
  }
  if (limit !== null && limit !== undefined) {
    params.limit = limit;
  }

  const { data } = await client.get("/lecturas", { params });
  return data;
}

export async function getUltimaLectura(equipoId) {
  if (equipoId === null || equipoId === undefined) {
    throw new Error("getUltimaLectura requiere equipoId");
  }

  const { data } = await client.get(`/lecturas/latest/${equipoId}`);
  return data;
}
