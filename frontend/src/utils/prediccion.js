/**
 * Utilidades para interpretar y visualizar predicciones del modelo ML.
 * Mapea clasificaciones a colores, etiquetas y niveles de severidad.
 *
 * Los colores usan OKLCH para mantener consistencia con tailwind.config.js.
 * Correspondencia con tokens del design system:
 * - normal  → success-*
 * - alerta  → warning-*
 * - falla   → danger-*
 */

/**
 * Configuración visual por clasificación de riesgo.
 * Clave: valor exacto que devuelve el backend (clasificacion).
 * Valores posibles según prediccion_service.py: "normal", "alerta", "falla".
 */
const CLASIFICACION_CONFIG = {
  normal: {
    label: "Normal",
    color: "oklch(45% 0.160 145)",      // success-600 verde industrial
    bgColor: "oklch(96% 0.030 145)",     // success-50
    borderColor: "oklch(90% 0.060 145)", // success-100
    emoji: "✅",
    nivel: 0,
  },
  alerta: {
    label: "Alerta",
    color: "oklch(55% 0.170 85)",        // warning-600 amarillo-naranja
    bgColor: "oklch(96% 0.025 85)",      // warning-50
    borderColor: "oklch(92% 0.055 85)",  // warning-100
    emoji: "⚠️",
    nivel: 1,
  },
  falla: {
    label: "Falla",
    color: "oklch(50% 0.195 25)",        // danger-600 rojo industrial
    bgColor: "oklch(96% 0.022 25)",      // danger-50
    borderColor: "oklch(92% 0.048 25)",  // danger-100
    emoji: "🔴",
    nivel: 2,
  },
};

/** Configuración por defecto cuando no hay predicción o la clasificación es desconocida */
const CONFIG_DESCONOCIDA = {
  label: "Sin predicción",
  color: "oklch(55% 0.018 250)",        // neutral-500
  bgColor: "oklch(96% 0.005 250)",      // neutral-100
  borderColor: "oklch(92% 0.008 250)",  // neutral-200
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
