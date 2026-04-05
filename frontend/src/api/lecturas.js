import client from "./client";

export async function getLecturas(equipoId = null) {
  const params = {};
  if (equipoId !== null && equipoId !== undefined) {
    params.equipo_id = equipoId;
  }

  const { data } = await client.get("/lecturas", { params });
  return data;
}

export async function getUltimaLectura(equipoId) {
  const { data } = await client.get(`/lecturas/latest/${equipoId}`);
  return data;
}
