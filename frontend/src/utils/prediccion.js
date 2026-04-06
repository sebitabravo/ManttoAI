/**
 * Utilidades para interpretar y visualizar predicciones del modelo ML.
 * Mapea clasificaciones a colores, etiquetas y niveles de severidad.
 */

/**
 * Configuración visual por clasificación de riesgo.
 * Clave: valor exacto que devuelve el backend (clasificacion).
 */
const CLASIFICACION_CONFIG = {
  normal: {
    label: "Normal",
    color: "#16a34a",       // verde
    bgColor: "#dcfce7",
    borderColor: "#86efac",
    emoji: "✅",
    nivel: 0,
  },
  advertencia: {
    label: "Advertencia",
    color: "#d97706",       // amarillo/ámbar
    bgColor: "#fef3c7",
    borderColor: "#fcd34d",
    emoji: "⚠️",
    nivel: 1,
  },
  critico: {
    label: "Crítico",
    color: "#dc2626",       // rojo
    bgColor: "#fee2e2",
    borderColor: "#fca5a5",
    emoji: "🔴",
    nivel: 2,
  },
};

/** Configuración por defecto cuando no hay predicción o la clasificación es desconocida */
const CONFIG_DESCONOCIDA = {
  label: "Sin predicción",
  color: "#6b7280",
  bgColor: "#f3f4f6",
  borderColor: "#d1d5db",
  emoji: "—",
  nivel: -1,
};

/**
 * Devuelve la configuración visual para una clasificación dada.
 * Usa null/undefined explícito en vez de falsy para no descartar el string "0".
 * @param {string|null|undefined} clasificacion - Clasificación del modelo
 * @returns {object} Configuración con color, label, emoji, etc.
 */
export function getConfigPrediccion(clasificacion) {
  if (clasificacion === null || clasificacion === undefined) return CONFIG_DESCONOCIDA;
  const clave = String(clasificacion).toLowerCase().trim();
  return CLASIFICACION_CONFIG[clave] ?? CONFIG_DESCONOCIDA;
}

/**
 * Convierte probabilidad (0-1) a porcentaje formateado.
 * Clampa el valor al rango [0, 1] antes de formatear.
 * @param {number|null|undefined} probabilidad
 * @returns {string}
 */
export function formatPorcentajeRiesgo(probabilidad) {
  // null y undefined se descartan explícitamente antes de Number() porque Number(null) === 0
  if (probabilidad === null || probabilidad === undefined) return "—";
  const num = Number(probabilidad);
  if (!Number.isFinite(num)) return "—";
  const clamped = Math.min(Math.max(num, 0), 1);
  return `${(clamped * 100).toFixed(1)} %`;
}
