import { useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";

import Logo, { BRAND_COLOR } from "../ui/Logo";
import { FONT_SIZE, RADIUS, SPACING, SURFACE, TEXT_COLOR } from "../../styles/tokens";

const items = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/equipos", label: "Equipos" },
  { to: "/alertas", label: "Alertas" },
  { to: "/historial", label: "Historial" },
];

/**
 * Sidebar de navegación.
 * Props:
 *  - className: clases CSS adicionales (usadas por Layout para el drawer en tablet)
 *  - sidebarAbierto: estado del drawer (para atributos ARIA y gestión de foco)
 *  - onNavClick: callback al hacer clic en un ítem de nav (cierra el drawer en tablet)
 *  - retornarFocoRef: ref al botón que abrió el drawer (para devolver foco al cerrar)
 */
export default function Sidebar({ className = "", sidebarAbierto = false, onNavClick, retornarFocoRef }) {
  const asideRef = useRef(null);

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
      className={className}
      // En tablet actúa como diálogo modal; en desktop es navegación estática
      role={sidebarAbierto ? "dialog" : undefined}
      aria-modal={sidebarAbierto ? "true" : undefined}
      aria-label="Menú de navegación"
      style={{ borderRight: `1px solid ${SURFACE.border}`, padding: SPACING.xl, background: SURFACE.bg }}
    >
      {/* Logo decorativo: el texto "ManttoAI" al lado hace redundante un title en el SVG */}
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.xxl }}>
        <Logo size={28} />
        <span style={{ fontWeight: 700, fontSize: FONT_SIZE.md, color: TEXT_COLOR.primary }}>ManttoAI</span>
      </div>

      <nav style={{ display: "grid", gap: SPACING.xs }}>
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavClick}
            style={({ isActive }) => ({
              textDecoration: "none",
              padding: `${SPACING.sm}px ${SPACING.md}px`,
              borderRadius: RADIUS.sm,
              fontSize: FONT_SIZE.base,
              fontWeight: isActive ? 600 : 400,
              // Color de marca centralizado para el ítem activo
              color: isActive ? BRAND_COLOR : TEXT_COLOR.secondary,
              background: isActive ? "#eff6ff" : "transparent",
            })}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
