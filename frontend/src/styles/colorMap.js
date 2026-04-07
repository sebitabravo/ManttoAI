/**
 * Mapeo de colores hard-coded legacy → clases Tailwind
 * 
 * Usado durante la migración del rescue UI/UX para reemplazar
 * colores inline (#xxx) por clases del sistema de diseño.
 * 
 * Uso en componentes:
 * 
 * ANTES:
 *   <div className="bg-white border-gray-200 text-gray-900">
 * 
 * DESPUÉS:
 *   <div className="bg-neutral-100 border-neutral-200 text-neutral-700">
 * 
 * Este archivo será eliminado tras completar la migración.
 */

export const COLOR_MAP = {
  // === FONDOS ===
  "#ffffff": "bg-neutral-100",    // superficie elevada (cards)
  "#fff": "bg-neutral-100",
  "#f8fafc": "bg-neutral-50",     // fondo de página
  "#f9fafb": "bg-neutral-50",
  "#f3f4f6": "bg-neutral-100",
  
  // === BORDES ===
  "#e5e7eb": "border-neutral-200",  // border subtle
  "#d1d5db": "border-neutral-300",  // border default (inputs)
  "#9ca3af": "border-neutral-400",
  
  // === TEXTO ===
  "#111827": "text-neutral-700",   // headings, títulos
  "#1f2937": "text-neutral-700",
  "#374151": "text-neutral-600",   // texto principal
  "#4b5563": "text-neutral-500",   // texto secundario
  "#6b7280": "text-neutral-400",   // texto muted, placeholders
  "#9ca3af": "text-neutral-400",
  
  // === PRIMARIO (azul) ===
  "#1d4ed8": "bg-primary-600 text-white", // botones primarios (legacy)
  "#2563eb": "bg-primary-500",
  "#3b82f6": "bg-primary-400",
  "#60a5fa": "bg-primary-300",
  "#dbeafe": "bg-primary-50",
  
  // === SUCCESS (verde) ===
  "#10b981": "bg-success-600",
  "#34d399": "bg-success-500",
  "#6ee7b7": "bg-success-400",
  "#d1fae5": "bg-success-50",
  
  // === WARNING (amarillo-naranja) ===
  "#f59e0b": "bg-warning-600",
  "#fbbf24": "bg-warning-500",
  "#fcd34d": "bg-warning-400",
  "#fef3c7": "bg-warning-50",
  
  // === DANGER (rojo) ===
  "#dc2626": "bg-danger-600",
  "#ef4444": "bg-danger-500",
  "#f87171": "bg-danger-400",
  "#fee2e2": "bg-danger-50",
};

/**
 * Mapeo semántico para estados de alertas
 */
export const ALERT_COLORS = {
  critica: {
    bg: "bg-danger-50",
    border: "border-danger-500",
    text: "text-danger-700",
    badge: "bg-danger-600 text-white",
  },
  alta: {
    bg: "bg-danger-50",
    border: "border-danger-400",
    text: "text-danger-600",
    badge: "bg-danger-500 text-white",
  },
  media: {
    bg: "bg-warning-50",
    border: "border-warning-500",
    text: "text-warning-700",
    badge: "bg-warning-600 text-white",
  },
  baja: {
    bg: "bg-warning-50",
    border: "border-warning-400",
    text: "text-warning-600",
    badge: "bg-warning-500 text-neutral-900",
  },
  info: {
    bg: "bg-primary-50",
    border: "border-primary-400",
    text: "text-primary-700",
    badge: "bg-primary-600 text-white",
  },
};

/**
 * Mapeo semántico para estados de equipos
 */
export const EQUIPO_COLORS = {
  operativo: {
    bg: "bg-success-50",
    border: "border-success-500",
    text: "text-success-700",
    badge: "bg-success-600 text-white",
  },
  advertencia: {
    bg: "bg-warning-50",
    border: "border-warning-500",
    text: "text-warning-700",
    badge: "bg-warning-600 text-neutral-900",
  },
  critico: {
    bg: "bg-danger-50",
    border: "border-danger-500",
    text: "text-danger-700",
    badge: "bg-danger-600 text-white",
  },
  detenido: {
    bg: "bg-neutral-100",
    border: "border-neutral-400",
    text: "text-neutral-600",
    badge: "bg-neutral-500 text-white",
  },
  mantenimiento: {
    bg: "bg-primary-50",
    border: "border-primary-400",
    text: "text-primary-700",
    badge: "bg-primary-600 text-white",
  },
};

/**
 * Paleta para gráficos Chart.js
 * Colores en formato OKLCH convertidos a RGB para Chart.js
 */
export const CHART_COLORS = {
  temperatura: "rgb(176, 88, 56)",    // primary-600
  humedad: "rgb(66, 165, 245)",       // primary-400
  vibracion_x: "rgb(220, 38, 38)",    // danger-600
  vibracion_y: "rgb(251, 146, 60)",   // warning-500
  vibracion_z: "rgb(34, 197, 94)",    // success-600
  grid: "rgb(226, 232, 240)",         // neutral-200
  text: "rgb(100, 116, 139)",         // neutral-500
};
