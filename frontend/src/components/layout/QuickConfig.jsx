import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../../hooks/useAuth";
import { resetOnboarding } from "../../api/onboarding";
import { clearOnboardingDone } from "../../utils/onboardingStorage";

/**
 * Dropdown de configuración rápida en el header.
 *
 * Opciones disponibles (solo admin):
 * - Repetir asistente: resetea el wizard de onboarding y navega a /onboarding
 * - Ver tour del producto: limpia el flag de localStorage y lanza el tour
 *
 * Se cierra al hacer clic fuera del menú, con Escape o al seleccionar una opción.
 */
export default function QuickConfig({ onReplayTour }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [abierto, setAbierto] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  // Solo visible para admins
  if (user?.rol !== "admin") return null;

  async function handleResetWizard() {
    if (loading) return;
    setLoading(true);
    try {
      await resetOnboarding();
      setAbierto(false);
      navigate("/onboarding", { replace: true });
    } catch (err) {
      console.error("Error al resetear onboarding:", err);
    } finally {
      setLoading(false);
    }
  }

  function handleReplayTour() {
    clearOnboardingDone();
    setAbierto(false);
    onReplayTour?.();
  }

  // Cerrar al hacer clic fuera
  function handleBlur(e) {
    if (!dropdownRef.current?.contains(e.relatedTarget)) {
      setAbierto(false);
    }
  }

  return (
    <div className="relative" ref={dropdownRef} onBlur={handleBlur}>
      {/* Botón trigger */}
      <button
        type="button"
        onClick={() => setAbierto((a) => !a)}
        className="flex items-center justify-center rounded-sm p-1.5 text-neutral-500 transition-colors duration-150 hover:bg-neutral-200 hover:text-neutral-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
        aria-label="Configuración rápida"
        aria-expanded={abierto}
        aria-haspopup="true"
      >
        {/* Ícono de engranaje */}
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      </button>

      {/* Dropdown */}
      {abierto && (
        <div
          className="absolute right-0 top-full z-50 mt-1 w-56 rounded-md border border-neutral-200 bg-neutral-100 py-1 shadow-md"
          role="menu"
          aria-label="Opciones de configuración"
        >
          <button
            type="button"
            role="menuitem"
            disabled={loading}
            onClick={handleResetWizard}
            className="flex w-full items-center gap-2.5 px-3 py-2 text-left text-sm text-neutral-700 transition-colors duration-100 hover:bg-neutral-200 focus:outline-none focus-visible:bg-neutral-200 disabled:opacity-50"
          >
            {/* Ícono de replay */}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <polyline points="1 4 1 10 7 10" />
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
            </svg>
            Repetir asistente
          </button>
          <button
            type="button"
            role="menuitem"
            onClick={handleReplayTour}
            className="flex w-full items-center gap-2.5 px-3 py-2 text-left text-sm text-neutral-700 transition-colors duration-100 hover:bg-neutral-200 focus:outline-none focus-visible:bg-neutral-200"
          >
            {/* Ícono de tour/play */}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="10" />
              <polygon points="10 8 16 12 10 16 10 8" />
            </svg>
            Ver tour del producto
          </button>
        </div>
      )}
    </div>
  );
}
