import { useId, useState } from "react";

/**
 * Tooltip informativo compacto para métricas y labels de contexto.
 * 
 * Versión corregida: posicionamiento seguro que no solapa elementos vecinos.
 * El tooltip aparece debajo del botón "?" con z-index alto y se limita
 * al ancho disponible del contenedor padre.
 *
 * Accesibilidad:
 * - Visible en hover y focus (teclado)
 * - role="tooltip" + aria-describedby
 */
export default function InfoTooltip({ label = "Ver información", text = "" }) {
  const tooltipId = useId();
  const [openedByTap, setOpenedByTap] = useState(false);

  function handleToggle() {
    setOpenedByTap((state) => !state);
  }

  function handleBlur() {
    setOpenedByTap(false);
  }

  function handleFocus() {
    setOpenedByTap(true);
  }

  return (
    <span 
      className="relative inline-flex items-center"
      onPointerEnter={handleFocus}
      onPointerLeave={handleBlur}
    >
      <button
        type="button"
        aria-label={label}
        aria-describedby={openedByTap ? tooltipId : undefined}
        aria-expanded={openedByTap}
        aria-controls={tooltipId}
        onClick={handleToggle}
        onBlur={handleBlur}
        onFocus={handleFocus}
        className="inline-flex h-[20px] w-[20px] flex-shrink-0 items-center justify-center rounded-full bg-neutral-100 text-[11px] font-semibold text-neutral-500 transition-colors duration-150 hover:bg-neutral-200 hover:text-neutral-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      >
        ?
      </button>

      {openedByTap && (
        <span
          id={tooltipId}
          role="tooltip"
          className="absolute left-1/2 -translate-x-1/2 top-full z-50 mt-2 max-w-[200px] rounded-lg bg-neutral-800 px-3 py-2 text-xs text-white shadow-lg"
        >
          {text}
          {/* Flecha del tooltip */}
          <span className="absolute -top-1 left-1/2 -translate-x-1/2 h-2 w-2 rotate-45 bg-neutral-800" />
        </span>
      )}
    </span>
  );
}
