export const ESTADOS = {
  operativo: "Operativo",
  monitoreo: "En monitoreo",
  detenido: "Detenido",
};

export const NIVELES_ALERTA = {
  bajo: "#10b981",
  medio: "#f59e0b",
  alto: "#ef4444",
};

const ENV_DASHBOARD_POLLING_INTERVAL_MS = Number(
  import.meta.env.VITE_DASHBOARD_POLLING_INTERVAL_MS
);

export const DASHBOARD_POLLING_INTERVAL_MS = Number.isFinite(
  ENV_DASHBOARD_POLLING_INTERVAL_MS
)
  ? Math.max(1000, ENV_DASHBOARD_POLLING_INTERVAL_MS)
  : 15000;
