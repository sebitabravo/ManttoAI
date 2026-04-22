import { useEffect, useId, useRef } from "react";

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
  const titleId = `modal-title-${useId().replace(/:/g, "")}`;

  // Focus trap + Escape key handler
  useEffect(() => {
    if (!open) return;

    const dialog = dialogRef.current;
    const selector =
      'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])';

    const getFocusables = () => Array.from(dialog?.querySelectorAll(selector) || []);
    const ORIGINAL_OVERFLOW_KEY = "manttoaiOriginalOverflow";
    const MODAL_COUNT_KEY = "manttoaiModalCount";
    const MODAL_INDEX_KEY = "manttoaiModalIndex";

    const currentModalCount = Number(document.body.dataset[MODAL_COUNT_KEY] || 0) + 1;
    document.body.dataset[MODAL_COUNT_KEY] = String(currentModalCount);

    if (dialog) {
      dialog.dataset[MODAL_INDEX_KEY] = String(currentModalCount);
    }

    if (currentModalCount === 1) {
      document.body.dataset[ORIGINAL_OVERFLOW_KEY] = document.body.style.overflow || "";
      document.body.style.overflow = "hidden";
    }

    const isTopmostModal = () => {
      const topIndex = Number(document.body.dataset[MODAL_COUNT_KEY] || 0);
      const myIndex = Number(dialog?.dataset?.[MODAL_INDEX_KEY] || -1);
      return myIndex === topIndex;
    };

    const handleEscape = (e) => {
      if (e.key === "Escape" && onClose) {
        if (!isTopmostModal()) return;
        onClose();
      }
    };

    const handleTabTrap = (e) => {
      if (e.key !== "Tab") return;
      if (!isTopmostModal()) return;

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

    document.addEventListener("keydown", handleEscape);
    document.addEventListener("keydown", handleTabTrap);

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.removeEventListener("keydown", handleTabTrap);

      if (dialog) {
        delete dialog.dataset[MODAL_INDEX_KEY];
      }

      const nextModalCount = Math.max(Number(document.body.dataset[MODAL_COUNT_KEY] || 1) - 1, 0);
      document.body.dataset[MODAL_COUNT_KEY] = String(nextModalCount);

      if (nextModalCount === 0) {
        document.body.style.overflow = document.body.dataset[ORIGINAL_OVERFLOW_KEY] || "";
        delete document.body.dataset[ORIGINAL_OVERFLOW_KEY];
        delete document.body.dataset[MODAL_COUNT_KEY];
      }

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
            e.stopPropagation();
            onClose();
          }
        }}
        role="presentation"
      >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className="
          relative w-full max-w-lg max-h-[90vh] overflow-y-auto
          rounded-2xl bg-white p-6 shadow-apple border border-white/20
          focus:outline-none
        "
      >
        <h2 id={titleId} className="mb-4 text-lg font-semibold text-neutral-800">
          {title}
        </h2>
        <div className="text-neutral-700">
          {children}
        </div>
      </div>
    </div>
  );
}
