import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../../hooks/useAuth";
import Button from "../ui/Button";
import { AVATAR_MAP } from "../../utils/avatares";
import { resetOnboarding } from "../../api/onboarding";
import { clearOnboardingDone } from "../../utils/onboardingStorage";

/**
 * Menú de usuario integrado con opciones de configuración.
 * 
 * Muestra en un solo dropdown:
 * - Opciones de configuración (solo admin): Repetir asistente, Ver tour
 * - Mi Perfil
 * - Cerrar sesión
 * 
 * Props:
 *  - onReplayTour: callback opcional para lanzar el tour de producto
 */
export default function UserMenu({ onReplayTour }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [loadingReset, setLoadingReset] = useState(false);
  const triggerRef = useRef(null);
  const panelRef = useRef(null);

  // Obtener el emoji del avatar seleccionado o usar iniciales
  const avatarEmoji = user?.avatar ? AVATAR_MAP[user.avatar] : null;
  const initials = avatarEmoji || (user?.nombre || "?")
    .split(" ")
    .map((p) => p[0]?.toUpperCase() || "")
    .slice(0, 2)
    .join("");

  useEffect(() => {
    if (!open) return undefined;

    function onPointerDown(e) {
      if (!(e.target instanceof Node)) return;
      if (panelRef.current?.contains(e.target) || triggerRef.current?.contains(e.target)) return;
      setOpen(false);
    }

    function onKey(e) {
      if (e.key === "Escape") {
        setOpen(false);
        triggerRef.current?.focus();
      }
    }

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Resetear wizard de onboarding y navegar
  async function handleResetWizard() {
    if (loadingReset) return;
    setLoadingReset(true);
    try {
      await resetOnboarding();
      setOpen(false);
      navigate("/onboarding", { replace: true });
    } catch (err) {
      console.error("Error al resetear onboarding:", err);
    } finally {
      setLoadingReset(false);
    }
  }

  // Lanzar tour de producto
  function handleReplayTour() {
    clearOnboardingDone();
    setOpen(false);
    onReplayTour?.();
  }

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  const isAdmin = user?.rol === "admin";

  return (
    <div className="relative">
      <button
        ref={triggerRef}
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((s) => !s)}
        className="inline-flex items-center gap-2 rounded-full border border-neutral-300 bg-neutral-50 px-2 py-1.5 text-sm text-neutral-800 hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      >
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 text-lg font-semibold text-white">{avatarEmoji || initials}</span>
        <span className="hidden sm:inline">{user?.nombre || "Invitado"}</span>
      </button>

      {open ? (
        <div
          ref={panelRef}
          role="menu"
          aria-label="Menú de usuario"
          className="absolute right-0 mt-2 w-60 rounded-lg border border-neutral-200 bg-white shadow-lg z-40"
        >
          {/* Info del usuario */}
          <div className="px-3 py-2 border-b border-neutral-100">
            <p className="m-0 text-sm font-semibold text-neutral-800">{user?.nombre}</p>
            <p className="m-0 text-xs text-neutral-500">{user?.email}</p>
          </div>

          {/* Opciones de configuración (solo admin) */}
          {isAdmin && (
            <div className="border-b border-neutral-100 px-2 py-1.5">
              <p className="px-2 py-1 text-xs font-medium text-neutral-400 uppercase tracking-wide">Configuración</p>
              <button
                type="button"
                role="menuitem"
                disabled={loadingReset}
                onClick={handleResetWizard}
                className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
              >
                {/* Ícono de replay */}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <polyline points="1 4 1 10 7 10" />
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                </svg>
                Repetir asistente
              </button>
              <button
                type="button"
                role="menuitem"
                onClick={handleReplayTour}
                className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm text-neutral-700 hover:bg-neutral-50"
              >
                {/* Ícono de tour/play */}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="10 8 16 12 10 16 10 8" />
                </svg>
                Ver tour del producto
              </button>
            </div>
          )}

          {/* Perfil */}
          <div className="border-b border-neutral-100 px-2 py-1.5">
            <button
              type="button"
              role="menuitem"
              onClick={() => { setOpen(false); navigate("/perfil"); }}
              className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm text-neutral-700 hover:bg-neutral-50"
            >
              {/* Ícono de usuario */}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Mi Perfil
            </button>
          </div>

          {/* Cerrar sesión */}
          <div className="px-2 py-1.5">
            <Button type="button" variant="outline" className="w-full justify-start" onClick={handleLogout}>
              {/* Ícono de logout */}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="mr-2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              Cerrar sesión
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
