import { NavLink } from "react-router-dom";

import Logo, { BRAND_COLOR } from "../ui/Logo";
import { FONT_SIZE, RADIUS, SPACING, SURFACE, TEXT_COLOR } from "../../styles/tokens";

const items = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/equipos", label: "Equipos" },
  { to: "/alertas", label: "Alertas" },
  { to: "/historial", label: "Historial" },
];

export default function Sidebar() {
  return (
    <aside style={{ borderRight: `1px solid ${SURFACE.border}`, padding: SPACING.xl, background: SURFACE.bg }}>
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
