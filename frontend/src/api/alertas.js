import client from "./client";

export async function getAlertas() {
  const { data } = await client.get("/alertas");
  return data;
}

export async function marcarLeida(id) {
  const { data } = await client.patch(`/alertas/${id}/leer`);
  return data;
}
