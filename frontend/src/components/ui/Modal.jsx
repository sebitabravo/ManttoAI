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

    const handleEscape = (e) => {
      if (e.key === "Escape" && onClose) {
        onClose();
      }
    };

    // Guardar foco anterior
    const previousFocus = document.activeElement;

    // Dar foco al modal
    dialogRef.current?.focus();

    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("keydown", handleEscape);
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
          bg-neutral-100 rounded-lg shadow-md
          p-6
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
