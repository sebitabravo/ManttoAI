export const ESTADOS = {
  operativo: "Operativo",
  monitoreo: "En monitoreo",
  detenido: "Detenido",
};

// Severidad de nivel de alerta — usar tokens semánticos del design system
export const NIVELES_ALERTA = {
  bajo: "success",
  medio: "warning",
  alto: "danger",
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

// Dashboard: 60s default - resumen general (reduce rate limits)
export const DASHBOARD_POLLING_INTERVAL_MS = resolvePollingInterval(
  ENV_DASHBOARD_POLLING_INTERVAL_MS,
  60000
);

// Alertas: 30s default - critico pero reduce requests
export const ALERTAS_POLLING_INTERVAL_MS = resolvePollingInterval(
  ENV_ALERTAS_POLLING_INTERVAL_MS,
  30000
);

// Lista de equipos: 60s default - menos critico
export const EQUIPOS_POLLING_INTERVAL_MS = resolvePollingInterval(
  ENV_EQUIPOS_POLLING_INTERVAL_MS,
  60000
);

// === Constantes de negocio ===

// Prefijos telefónicos de Latinoamérica
export const PAISES_TELEFONO = [
  { codigo: "+54", pais: "Argentina", bandera: "🇦🇷" },
  { codigo: "+56", pais: "Chile", bandera: "🇨🇱" },
  { codigo: "+51", pais: "Perú", bandera: "🇵🇪" },
  { codigo: "+57", pais: "Colombia", bandera: "🇨🇴" },
  { codigo: "+55", pais: "Brasil", bandera: "🇧🇷" },
];

// Avatares disponibles para selección de perfil de usuario
export const AVATARES = [
  { id: "user", emoji: "👤", label: "Usuario" },
  { id: "person", emoji: "🧑", label: "Persona" },
  { id: "man", emoji: "👨", label: "Hombre" },
  { id: "woman", emoji: "👩", label: "Mujer" },
  { id: "robot", emoji: "🤖", label: "Robot" },
  { id: "alien", emoji: "👽", label: "Alien" },
  { id: "cat", emoji: "🐱", label: "Gato" },
  { id: "dog", emoji: "🐶", label: "Perro" },
];

// Mapa rápido para buscar emoji por ID
export const AVATAR_MAP = AVATARES.reduce((acc, av) => {
  acc[av.id] = av.emoji;
  return acc;
}, {});
