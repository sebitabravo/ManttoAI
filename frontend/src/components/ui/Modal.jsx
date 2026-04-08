import { useEffect, useRef } from "react";

/**
 * Modal del sistema de diseño ManttoAI.
 * 
 * Características:
 * - Overlay semitransparente con backdrop
 * - Contenido centrado con scroll interno si es necesario
 * - Focus trap automático
 * - Cierre con Escape key
 * - Accesibilidad completa con ARIA
 * 
 * Props:
 * - open: boolean — mostrar/ocultar modal
 * - title: string — título semántico (h2)
 * - onClose: function — callback al cerrar (Escape o click fuera)
 * - children: contenido del modal
 */
export default function Modal({ open = false, title = "Modal", onClose, children }) {
  const dialogRef = useRef(null);

  // Focus trap + Escape key handler
  useEffect(() => {
    if (!open) return;

    const dialog = dialogRef.current;
    const selector =
      'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])';

    const getFocusables = () => Array.from(dialog?.querySelectorAll(selector) || []);
    const previousOverflow = document.body.style.overflow;

    const handleEscape = (e) => {
      if (e.key === "Escape" && onClose) {
        onClose();
      }
    };

    const handleTabTrap = (e) => {
      if (e.key !== "Tab") return;

      const focusables = getFocusables();
      if (focusables.length === 0) {
        e.preventDefault();
        return;
      }

      const first = focusables[0];
      const last = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    // Guardar foco anterior
    const previousFocus = document.activeElement;

    // Dar foco al primer elemento interactivo o al contenedor
    const focusables = getFocusables();
    (focusables[0] || dialog)?.focus();
    document.body.style.overflow = "hidden";

    document.addEventListener("keydown", handleEscape);
    document.addEventListener("keydown", handleTabTrap);

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.removeEventListener("keydown", handleTabTrap);
      document.body.style.overflow = previousOverflow;
      // Restaurar foco
      previousFocus?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/40 p-4"
      onClick={(e) => {
        // Cerrar al hacer click en el backdrop (fuera del contenido)
        if (e.target === e.currentTarget && onClose) {
          onClose();
        }
      }}
      role="presentation"
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabIndex={-1}
        className="
          relative w-full max-w-lg max-h-[90vh] overflow-y-auto
          rounded-lg border border-neutral-300 bg-neutral-100 p-5 shadow
          focus:outline-none
        "
      >
        <h2 id="modal-title" className="text-lg font-semibold text-neutral-800 mb-4">
          {title}
        </h2>
        <div className="text-neutral-700">
          {children}
        </div>
      </div>
    </div>
  );
}
