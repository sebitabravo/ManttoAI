import client from "./client";

export async function getLecturas(equipoId) {
  const { data } = await client.get("/lecturas", { params: { equipo_id: equipoId } });
  return data;
}

export async function getUltimaLectura(equipoId) {
  const { data } = await client.get(`/lecturas/latest/${equipoId}`);
  return data;
}
