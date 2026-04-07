/**
 * Tokens de diseño del sistema ManttoAI.
 * 
 * DEPRECATED: Usar clases Tailwind directamente.
 * Este archivo se mantiene temporalmente para retrocompatibilidad
 * durante la migración del rescue de UI/UX.
 * 
 * MIGRACIÓN:
 * - Colores: usar bg-neutral-*, text-neutral-*, border-neutral-*
 * - Bordes: usar rounded, rounded-md, rounded-lg
 * - Texto: usar text-xs, text-sm, text-base, text-md, text-lg, text-xl
 * - Espaciado: usar p-*, m-*, gap-* de Tailwind
 * 
 * Este archivo será eliminado en fase de polish.
 */

/** @deprecated Usar rounded-sm (6px), rounded (8px), rounded-md (10px), rounded-lg (12px) */
export const RADIUS = {
  sm: 6,   // chips, badges, nav items
  md: 8,   // botones, inputs
  lg: 12,  // cards principales, modales
};

/** @deprecated Usar clases Tailwind p-*, m-*, gap-* */
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

/** @deprecated Usar text-xs, text-sm, text-base, text-md, text-lg, text-xl */
export const FONT_SIZE = {
  xs: 12,   // badges, labels pequeños
  sm: 13,   // texto secundario, subtítulos
  base: 14, // texto de interfaz general
  md: 16,   // títulos de sidebar
  lg: 18,   // page headers
  xl: 22,   // título de login, dashboard
};

/** @deprecated Usar text-neutral-700, text-neutral-500, text-neutral-400 */
export const TEXT_COLOR = {
  primary: "oklch(40% 0.020 250)",   // text-neutral-600
  secondary: "oklch(55% 0.018 250)", // text-neutral-500
  muted: "oklch(70% 0.015 250)",     // text-neutral-400
};

/** @deprecated Usar bg-neutral-*, border-neutral-* */
export const SURFACE = {
  border: "oklch(92% 0.008 250)",    // border-neutral-200
  borderInput: "oklch(85% 0.012 250)", // border-neutral-300
  bg: "oklch(98% 0.003 250)",        // bg-neutral-50 (página)
  bgCard: "oklch(96% 0.005 250)",    // bg-neutral-100 (cards)
};
