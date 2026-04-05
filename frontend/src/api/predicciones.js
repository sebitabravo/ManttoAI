import client from "./client";

export async function getPredicciones(equipoId) {
  const { data } = await client.get(`/predicciones/${equipoId}`);
  return data;
}
