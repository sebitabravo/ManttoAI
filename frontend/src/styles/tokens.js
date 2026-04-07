/**
 * Tokens de diseño del sistema ManttoAI.
 * Centraliza valores repetidos de spacing, tipografía y bordes
 * para evitar magic numbers dispersos en los componentes.
 *
 * Uso: import { RADIUS, SPACING, FONT_SIZE } from "../styles/tokens";
 */

/** Radio de borde por contexto */
export const RADIUS = {
  sm: 8,   // ítem de nav, chips
  md: 10,  // botones
  lg: 16,  // cards, secciones
};

/** Espaciado base (px) */
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

/** Tamaños de fuente (px) */
export const FONT_SIZE = {
  xs: 12,   // badges, labels pequeños
  sm: 13,   // texto secundario, subtítulos
  base: 14, // texto de interfaz general
  md: 16,   // títulos de sidebar
  lg: 22,   // título de login
};

/** Colores neutros de texto */
export const TEXT_COLOR = {
  primary: "#111827",   // títulos y texto principal
  secondary: "#374151", // texto de interfaz
  muted: "#6b7280",     // texto secundario y placeholders
};

/** Colores de borde y fondo */
export const SURFACE = {
  border: "#e5e7eb",
  borderInput: "#d1d5db",
  bg: "#f8fafc",        // fondo de sidebar y página
  bgCard: "#ffffff",
};
