export const ESTADOS = {
  operativo: "Operativo",
  monitoreo: "En monitoreo",
  detenido: "Detenido",
};

// Colores de nivel de alerta — valores OKLCH consistentes con tailwind.config.js
export const NIVELES_ALERTA = {
  bajo: "oklch(45% 0.160 145)",    // success-600
  medio: "oklch(55% 0.170 85)",    // warning-600
  alto: "oklch(50% 0.195 25)",     // danger-600
};

// === Intervalos de polling por página ===
// Configurables via variables de entorno VITE_*

const ENV_DASHBOARD_POLLING_INTERVAL_MS = Number(
  import.meta.env.VITE_DASHBOARD_POLLING_INTERVAL_MS
);

const ENV_ALERTAS_POLLING_INTERVAL_MS = Number(
  import.meta.env.VITE_ALERTAS_POLLING_INTERVAL_MS
);

const ENV_EQUIPOS_POLLING_INTERVAL_MS = Number(
  import.meta.env.VITE_EQUIPOS_POLLING_INTERVAL_MS
);

const ENV_EQUIPO_DETALLE_POLLING_INTERVAL_MS = Number(
  import.meta.env.VITE_EQUIPO_DETALLE_POLLING_INTERVAL_MS
);

/**
 * Resuelve intervalo de polling con validación y fallback.
 * @param {number} envValue - Valor de variable de entorno
 * @param {number} defaultMs - Valor por defecto en milisegundos
 * @returns {number} Intervalo válido (mínimo 1000ms)
 */
function resolvePollingInterval(envValue, defaultMs) {
  return Number.isFinite(envValue) ? Math.max(1000, envValue) : defaultMs;
}

// Dashboard: 15s default - resumen general
export const DASHBOARD_POLLING_INTERVAL_MS = resolvePollingInterval(
  ENV_DASHBOARD_POLLING_INTERVAL_MS,
  15000
);

// Alertas: 10s default - crítico para seguridad operacional
export const ALERTAS_POLLING_INTERVAL_MS = resolvePollingInterval(
  ENV_ALERTAS_POLLING_INTERVAL_MS,
  10000
);

// Lista de equipos: 20s default - menos crítico
export const EQUIPOS_POLLING_INTERVAL_MS = resolvePollingInterval(
  ENV_EQUIPOS_POLLING_INTERVAL_MS,
  20000
);

// Detalle de equipo: 15s default - lecturas y predicciones en tiempo real
export const EQUIPO_DETALLE_POLLING_INTERVAL_MS = resolvePollingInterval(
  ENV_EQUIPO_DETALLE_POLLING_INTERVAL_MS,
  15000
);
