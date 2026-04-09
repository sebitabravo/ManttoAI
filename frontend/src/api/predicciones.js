import client from "./client";

export async function getPredicciones(equipoId) {
  const { data } = await client.get(`/api/v1/predicciones/${equipoId}`);
  return data;
}
