import { useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";

import Logo from "../ui/Logo";
import useAuth from "../../hooks/useAuth";

const items = [
  { to: "/dashboard", label: "Dashboard", icon: "grid" },
  { to: "/equipos", label: "Equipos", icon: "cpu" },
  { to: "/alertas", label: "Alertas", icon: "bell" },
  { to: "/historial", label: "Historial", icon: "clock" },
  { to: "/chat-historial", label: "Historial IA", icon: "message", adminOnly: true },
  { to: "/admin", label: "Admin", icon: "settings", adminOnly: true },
];

/**
 * Iconos inline SVG para navegación.
 */
const icons = {
  grid: (
    <svg aria-label="Dashboard" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
    </svg>
  ),
  cpu: (
    <svg aria-label="Equipos" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <rect x="9" y="9" width="6" height="6" />
      <line x1="9" y1="1" x2="9" y2="4" />
      <line x1="15" y1="1" x2="15" y2="4" />
      <line x1="9" y1="20" x2="9" y2="23" />
      <line x1="15" y1="20" x2="15" y2="23" />
      <line x1="20" y1="9" x2="23" y2="9" />
      <line x1="20" y1="14" x2="23" y2="14" />
      <line x1="1" y1="9" x2="4" y2="9" />
      <line x1="1" y1="14" x2="4" y2="14" />
    </svg>
  ),
  bell: (
    <svg aria-label="Alertas" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  ),
  clock: (
    <svg aria-label="Historial" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  ),
  message: (
    <svg aria-label="Historial IA" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
  ),
  settings: (
    <svg aria-label="Admin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  ),
};

/**
 * Sidebar de navegación principal — Estilo Apple Minimal.
 * 
 * Características Apple:
 * - Fondo limpio sin bordes pesados
 * - Items con hover sutil
 * - Estado activo con fondo tenue y texto destacado
 * - Iconos monoline
 * - Focus trap en modo drawer
 */
export default function Sidebar({
  className = "",
  sidebarAbierto = false,
  onNavClick,
  onClose,
  retornarFocoRef,
}) {
  const asideRef = useRef(null);
  const { user } = useAuth();

  // Filtrar items según el rol del usuario
  const filteredItems = items.filter((item) => {
    if (item.adminOnly) {
      return user && user.rol === "admin";
    }
    return true;
  });

  useEffect(() => {
    if (!sidebarAbierto) {
      retornarFocoRef?.current?.focus();
      return;
    }

    const primerEnlace = asideRef.current?.querySelector("a");
    primerEnlace?.focus();

    function onKeyDown(e) {
      if (e.key !== "Tab") return;

      const focusables = asideRef.current?.querySelectorAll(
        'a, button, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusables || focusables.length === 0) return;

      const primero = focusables[0];
      const ultimo = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === primero) {
        e.preventDefault();
        ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault();
        primero.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [sidebarAbierto, retornarFocoRef]);

  return (
    <aside
      id="nav-sidebar"
      ref={asideRef}
      className={`layout-sidebar flex flex-col bg-white ${className}`}
      role={sidebarAbierto ? "dialog" : undefined}
      aria-modal={sidebarAbierto ? "true" : undefined}
      aria-label="Menú de navegación"
    >
      {/* Header del sidebar con logo */}
      <div className="flex h-14 items-center justify-between px-5">
        <div className="flex items-center gap-3">
          <Logo size={28} />
          <span className="text-base font-semibold text-neutral-600 tracking-tight">
            ManttoAI
          </span>
        </div>

        {/* Botón cerrar en mobile */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar menú de navegación"
          className={`h-8 w-8 flex items-center justify-center rounded-lg text-neutral-400 transition-colors duration-200 hover:bg-neutral-100 hover:text-neutral-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 md:hidden ${
            sidebarAbierto ? "flex" : "hidden"
          }`}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      {/* Navegación principal */}
      <nav className="flex-1 px-3 py-4">
        <ul className="flex flex-col gap-1">
          {filteredItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                onClick={onNavClick}
                className={({ isActive }) =>
                  `
                    flex items-center gap-3 px-3 py-[11px] rounded-lg
                    text-sm font-medium
                    transition-all duration-200
                    no-underline
                    focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500
                    ${
                      isActive
                        ? "bg-primary-50 text-primary-600"
                        : "text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700"
                    }
                  `.replace(/\s+/g, " ").trim()
                }
              >
                <span className="flex-shrink-0 opacity-70">
                  {icons[item.icon]}
                </span>
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer del sidebar — info de versión */}
      <div className="px-5 py-4">
        <p className="text-xs text-neutral-400">
          ManttoAI v1.0
        </p>
      </div>
    </aside>
  );
}
