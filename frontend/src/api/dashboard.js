import client from "./client";

export async function getDashboardResumen() {
  const { data } = await client.get("/dashboard/resumen");
  return data;
}
