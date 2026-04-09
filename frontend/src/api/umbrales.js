import client from "./client";

export async function getUmbrales() {
  const { data } = await client.get("/api/v1/umbrales");
  return data;
}

export async function updateUmbral(id, payload) {
  const { data } = await client.put(`/api/v1/umbrales/${id}`, payload);
  return data;
}
