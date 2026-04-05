import client from "./client";

export async function getAlertas({ equipoId = null, soloNoLeidas = false, limite = 100 } = {}) {
  const params = {
    solo_no_leidas: soloNoLeidas,
    limite,
  };

  if (equipoId !== null && equipoId !== undefined) {
    params.equipo_id = equipoId;
  }

  const { data } = await client.get("/alertas", { params });
  return data;
}

export async function marcarLeida(id) {
  const { data } = await client.patch(`/alertas/${id}/leer`);
  return data;
}
