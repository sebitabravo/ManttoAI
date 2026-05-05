import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Settings, RotateCcw, Play } from "lucide-react";

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
        className="flex items-center justify-center rounded-lg p-1.5 text-neutral-500 transition-colors duration-150 hover:bg-neutral-100 hover:text-neutral-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
        aria-label="Configuración rápida"
        aria-expanded={abierto}
        aria-haspopup="true"
      >
        <Settings size={18} aria-hidden="true" />
      </button>

      {/* Dropdown */}
      {abierto && (
        <div
          className="absolute right-0 top-full z-50 mt-1 w-56 rounded-2xl bg-white py-1 shadow-apple"
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
            <RotateCcw size={16} aria-hidden="true" />
            Repetir asistente
          </button>
          <button
            type="button"
            role="menuitem"
            onClick={handleReplayTour}
            className="flex w-full items-center gap-2.5 px-3 py-2 text-left text-sm text-neutral-700 transition-colors duration-100 hover:bg-neutral-200 focus:outline-none focus-visible:bg-neutral-200"
          >
            <Play size={16} aria-hidden="true" />
            Ver tour del producto
          </button>
        </div>
      )}
    </div>
  );
}
