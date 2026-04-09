import { useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";

import Logo from "../ui/Logo";
import useAuth from "../../hooks/useAuth";

const items = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/equipos", label: "Equipos" },
  { to: "/alertas", label: "Alertas" },
  { to: "/historial", label: "Historial" },
  { to: "/admin", label: "Admin", adminOnly: true },
];

/**
 * Sidebar de navegación principal.
 * 
 * Comportamiento responsive:
 * - Desktop (>768px): sidebar fijo persistente
 * - Tablet/Mobile (<=768px): drawer superpuesto con focus trap
 * 
 * Accesibilidad:
 * - role="dialog" + aria-modal cuando actúa como drawer
 * - Focus trap en modo drawer (Tab/Shift+Tab circulares)
 * - Restauración de foco al cerrar
 * 
 * Props:
 *  - className: clases CSS adicionales (usadas por Layout para el drawer en tablet)
 *  - sidebarAbierto: estado del drawer (para atributos ARIA y gestión de foco)
 *  - onClose: callback para cerrar drawer desde botón interno mobile
 *  - onNavClick: callback al hacer clic en un ítem de nav (cierra el drawer en tablet)
 *  - retornarFocoRef: ref al botón que abrió el drawer (para devolver foco al cerrar)
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
      // Al cerrar el drawer, devolver foco al botón que lo abrió
      retornarFocoRef?.current?.focus();
      return;
    }

    // Al abrir el drawer, mover foco al primer enlace de navegación
    const primerEnlace = asideRef.current?.querySelector("a");
    primerEnlace?.focus();

    // Focus trap básico: Tab y Shift+Tab quedan dentro del drawer
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
      className={`layout-sidebar border-r border-neutral-200 bg-neutral-50 p-5 ${className}`}
      // En tablet actúa como diálogo modal; en desktop es navegación estática
      role={sidebarAbierto ? "dialog" : undefined}
      aria-modal={sidebarAbierto ? "true" : undefined}
      aria-label="Menú de navegación"
    >
      {/* Logo + branding + cierre explícito en drawer mobile */}
      <div className="mb-6 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Logo size={28} />
          <span className="text-md font-semibold text-neutral-800">ManttoAI</span>
        </div>

        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar menú de navegación"
          className={`rounded-sm p-1 text-neutral-600 transition-all duration-150 ease-out-quart hover:bg-neutral-100 focus:outline-none focus:ring-2 focus:ring-primary-500 md:hidden ${
            sidebarAbierto ? "inline-flex" : "hidden"
          }`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <line x1="6" y1="6" x2="18" y2="18" />
            <line x1="18" y1="6" x2="6" y2="18" />
          </svg>
        </button>
      </div>

      {/* Navegación principal */}
      <nav className="flex flex-col gap-1">
        {filteredItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavClick}
            className={({ isActive }) =>
              `
                block rounded-sm px-3 py-2 text-base
                transition-all duration-150 ease-out-quart
                no-underline
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset
                ${
                  isActive
                    ? "bg-primary-50 font-semibold text-primary-600 border-l-2 border-primary-500 -ml-[2px] pl-[calc(0.75rem+2px)]"
                    : "font-normal text-neutral-600 hover:bg-neutral-100 hover:text-neutral-800 border-l-2 border-transparent"
                }
              `.trim()
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
