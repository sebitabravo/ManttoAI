/**
 * Utilidades para interpretar y visualizar predicciones del modelo ML.
 * Mapea clasificaciones a estilos semánticos, etiquetas y niveles de severidad.
 *
 * Los colores se resuelven desde tokens de Tailwind (sin estilos inline),
 * para mantener consistencia con el design system industrial.
 *
 * Correspondencia de severidad:
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
    dotClass: "bg-success-600",
    textClass: "text-success-700",
    barClass: "bg-success-600",
    surfaceClass: "border-success-300 bg-success-50",
    chipClass: "border-success-300 bg-success-100 text-success-800",
    nivel: 0,
  },
  alerta: {
    label: "Alerta",
    dotClass: "bg-warning-600",
    textClass: "text-warning-700",
    barClass: "bg-warning-600",
    surfaceClass: "border-warning-300 bg-warning-50",
    chipClass: "border-warning-300 bg-warning-100 text-warning-800",
    nivel: 1,
  },
  falla: {
    label: "Falla",
    dotClass: "bg-danger-600",
    textClass: "text-danger-700",
    barClass: "bg-danger-600",
    surfaceClass: "border-danger-300 bg-danger-50",
    chipClass: "border-danger-300 bg-danger-100 text-danger-800",
    nivel: 2,
  },
};

/** Configuración por defecto cuando no hay predicción o la clasificación es desconocida */
const CONFIG_DESCONOCIDA = {
  label: "Sin predicción",
  dotClass: "bg-neutral-400",
  textClass: "text-neutral-600",
  barClass: "bg-neutral-400",
  surfaceClass: "border-neutral-300 bg-neutral-100",
  chipClass: "border-neutral-300 bg-neutral-200 text-neutral-700",
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
