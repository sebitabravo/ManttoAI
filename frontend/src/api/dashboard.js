import client from "./client";

export async function getDashboardResumen() {
  const { data } = await client.get("/dashboard/resumen");
  return data;
}

export async function getDashboardLecturas(limit = 60) {
  const { data } = await client.get("/lecturas", {
    params: { limit },
  });
  if (!Array.isArray(data)) {
    return [];
  }

  return data.slice(0, limit);
}

export async function getDashboardData() {
  const [resumen, lecturas] = await Promise.all([
    getDashboardResumen(),
    getDashboardLecturas(),
  ]);

  return { resumen, lecturas };
}
