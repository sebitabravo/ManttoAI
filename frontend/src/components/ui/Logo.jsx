import { memo } from "react";

/**
 * Logo de marca ManttoAI — Estilo Apple.
 * Círculo Apple Blue con inicial "M".
 *
 * Props:
 *  - size: número (ancho y alto en px). Por defecto 24.
 *  - title: string opcional. Si se pasa, el SVG es semántico.
 *
 * Memoizado para evitar re-renders innecesarios.
 */
const Logo = memo(function Logo({ size = 24, title, className = "" }) {
  const esDecorativo = !title;

  return (
    <svg
      className={`flex-shrink-0 ${className}`.trim()}
      width={size}
      height={size}
      viewBox="0 0 32 32"
      aria-hidden={esDecorativo}
      focusable="false"
      role={esDecorativo ? undefined : "img"}
      xmlns="http://www.w3.org/2000/svg"
    >
      {title && <title>{title}</title>}
      {/* Círculo Apple Blue */}
      <circle cx="16" cy="16" r="16" fill="#0071e3" />
      {/* Inicial M */}
      <text
        x="16"
        y="21.5"
        fontSize="17"
        fontWeight="600"
        textAnchor="middle"
        fontFamily="Inter, -apple-system, SF Pro Display, system-ui, sans-serif"
        fill="#ffffff"
      >
        M
      </text>
    </svg>
  );
});

export default Logo;
