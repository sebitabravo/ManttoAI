import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../../hooks/useAuth";
import Button from "../ui/Button";
import { AVATAR_MAP } from "../../utils/constants";
import { resetOnboarding } from "../../api/onboarding";
import { clearOnboardingDone } from "../../utils/onboardingStorage";

/**
 * Menú de usuario — Estilo Apple.
 * 
 * Botón trigger: avatar circular, sin borders pesados.
 * Dropdown: fondo blanco, sin borders, sombra Apple.
 * Items: hover sutil, texto limpio.
 */

export default function UserMenu({ onReplayTour }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [loadingReset, setLoadingReset] = useState(false);
  const triggerRef = useRef(null);
  const panelRef = useRef(null);

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
      if (e.key === "Escape") { setOpen(false); triggerRef.current?.focus(); }
    }

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

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
        className="inline-flex items-center gap-2 rounded-full bg-neutral-100 pl-1 pr-3 py-1 text-sm transition-colors duration-200 hover:bg-neutral-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      >
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-primary-500 text-lg font-semibold text-white">
          {avatarEmoji || initials}
        </span>
        <span className="hidden text-neutral-600 font-medium sm:inline">{user?.nombre || "Invitado"}</span>
      </button>

      {open && (
        <div
          ref={panelRef}
          role="menu"
          aria-label="Menú de usuario"
          className="absolute right-0 mt-2 w-60 rounded-2xl bg-white p-2 shadow-apple z-40"
        >
          {/* Info del usuario */}
          <div className="px-3 py-2.5 mb-1">
            <p className="m-0 text-sm font-semibold text-neutral-600">{user?.nombre}</p>
            <p className="m-0 text-xs text-neutral-400">{user?.email}</p>
          </div>

          {/* Configuración (solo admin) */}
          {isAdmin && (
            <div className="border-t border-neutral-100 pt-1 pb-1">
              <p className="px-3 py-1.5 text-[10px] font-medium uppercase tracking-wide text-neutral-400">Configuración</p>
              <button
                type="button"
                role="menuitem"
                disabled={loadingReset}
                onClick={handleResetWizard}
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-neutral-600 transition-colors duration-200 hover:bg-neutral-100 disabled:opacity-50"
              >
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
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-neutral-600 transition-colors duration-200 hover:bg-neutral-100"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="10 8 16 12 10 16 10 8" />
                </svg>
                Ver tour del producto
              </button>
            </div>
          )}

          {/* Perfil */}
          <div className="border-t border-neutral-100 pt-1 pb-1">
            <button
              type="button"
              role="menuitem"
              onClick={() => { setOpen(false); navigate("/perfil"); }}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-neutral-600 transition-colors duration-200 hover:bg-neutral-100"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Mi Perfil
            </button>
          </div>

          {/* Cerrar sesión */}
          <div className="border-t border-neutral-100 pt-1">
            <button
              type="button"
              role="menuitem"
              onClick={handleLogout}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-danger-600 transition-colors duration-200 hover:bg-danger-50"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              Cerrar sesión
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
