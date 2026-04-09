import client from "./client";

export async function getDashboardResumen() {
  const { data } = await client.get("/api/v1/dashboard/resumen");
  return data;
}

export async function getDashboardLecturas(limit = 60) {
  const { data } = await client.get("/api/v1/lecturas", {
    params: { limit },
  });
  if (!Array.isArray(data)) {
    return [];
  }

  return data;
}

export async function getDashboardData() {
  const [resumen, lecturas] = await Promise.all([
    getDashboardResumen(),
    getDashboardLecturas(),
  ]);

  return { resumen, lecturas };
}
