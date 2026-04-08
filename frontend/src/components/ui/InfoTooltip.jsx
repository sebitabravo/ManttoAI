import { useId, useState } from "react";

/**
 * Tooltip informativo compacto para métricas y labels de contexto.
 *
 * Accesibilidad:
 * - Visible en hover y focus (teclado)
 * - role="tooltip" + aria-describedby
 * - Botón con touch target mínimo de 44px a través del contenedor
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
      className="group relative inline-flex min-h-[32px] items-center"
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
        className="relative inline-flex h-5 w-5 items-center justify-center rounded-full border border-neutral-300 bg-neutral-50 text-[11px] font-semibold text-neutral-600 transition-all duration-150 ease-out-quart hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 after:absolute after:-inset-3 after:content-['']"
      >
        ?
      </button>

      <span
        id={tooltipId}
        role="tooltip"
        aria-hidden={!openedByTap}
        className={`pointer-events-none absolute left-0 top-full z-20 mt-1 w-56 rounded-md border border-neutral-300 bg-neutral-50 px-2.5 py-2 text-xs text-neutral-700 shadow-lg transition-opacity duration-150 ease-out-quart ${
          openedByTap ? "opacity-100" : "opacity-0"
        }`}
      >
        {text}
      </span>
    </span>
  );
}
