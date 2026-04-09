import client from "./client";

export async function getUmbrales() {
  const { data } = await client.get("/umbrales");
  return data;
}

export async function updateUmbral(id, payload) {
  const { data } = await client.put(`/umbrales/${id}`, payload);
  return data;
}
