import client from "./client";

export async function getMantenciones() {
  const { data } = await client.get("/mantenciones");
  return data;
}

export async function createMantencion(payload) {
  const { data } = await client.post("/mantenciones", payload);
  return data;
}
