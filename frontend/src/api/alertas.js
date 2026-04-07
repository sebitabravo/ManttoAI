import client from "./client";

// limite default alineado con el backend (router alertas.py: default=50)
export async function getAlertas({ equipoId = null, soloNoLeidas = false, limite = 50 } = {}) {
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
