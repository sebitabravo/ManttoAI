import { useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";
import { LayoutGrid, Cpu, Bell, Clock, MessageSquare, Settings } from "lucide-react";

import Logo from "../ui/Logo";
import useAuth from "../../hooks/useAuth";

const items = [
  { to: "/dashboard", label: "Dashboard", Icon: LayoutGrid },
  { to: "/equipos", label: "Equipos", Icon: Cpu },
  { to: "/alertas", label: "Alertas", Icon: Bell },
  { to: "/historial", label: "Historial", Icon: Clock },
  { to: "/chat-historial", label: "Historial IA", Icon: MessageSquare, adminOnly: true },
  { to: "/admin", label: "Admin", Icon: Settings, adminOnly: true },
];

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
                  <item.Icon size={18} aria-hidden="true" />
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
