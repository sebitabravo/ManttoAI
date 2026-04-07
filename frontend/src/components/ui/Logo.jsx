import { memo } from "react";

/**
 * Componente de logo de marca ManttoAI.
 * Círculo azul con inicial "M" — consistente con el favicon de index.html.
 *
 * Props:
 *  - size: número (ancho y alto en px). Por defecto 24.
 *  - title: string opcional. Si se pasa, el SVG es semántico (role="img" + <title>)
 *           para lectores de pantalla. Si se omite, es decorativo (aria-hidden=true).
 *
 * Uso decorativo (cuando hay texto visible al lado):
 *   <Logo size={24} />
 *
 * Uso semántico (cuando el logo aparece solo sin texto):
 *   <Logo size={52} title="ManttoAI — Mantenimiento Predictivo" />
 *
 * Memoizado con React.memo para evitar re-renders innecesarios en layouts
 * que se re-renderizan frecuentemente (Header, Sidebar).
 */

/** Color de marca principal OKLCH — azul petróleo industrial */
export const BRAND_COLOR = "oklch(55% 0.110 250)"; // primary-500

const Logo = memo(function Logo({ size = 24, title }) {
  // Si no hay título, el SVG es puramente decorativo y se oculta a tecnologías asistivas
  const esDecorativo = !title;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      aria-hidden={esDecorativo}
      focusable="false"
      role={esDecorativo ? undefined : "img"}
      xmlns="http://www.w3.org/2000/svg"
    >
      {title ? <title>{title}</title> : null}
      <circle cx="16" cy="16" r="16" fill={BRAND_COLOR} />
      <text
        x="16"
        y="22"
        fontSize="20"
        fontWeight="700"
        textAnchor="middle"
        fontFamily="system-ui, sans-serif"
        fill="white"
      >
        M
      </text>
    </svg>
  );
});

export default Logo;
