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

export async function updateUmbral(id, payload) {
  const { data } = await client.put(`/umbrales/${id}`, payload);
  return data;
}
