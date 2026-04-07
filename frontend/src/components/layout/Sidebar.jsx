import { NavLink } from "react-router-dom";

import Logo, { BRAND_COLOR } from "../ui/Logo";

const items = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/equipos", label: "Equipos" },
  { to: "/alertas", label: "Alertas" },
  { to: "/historial", label: "Historial" },
];

export default function Sidebar() {
  return (
    <aside style={{ borderRight: "1px solid #e5e7eb", padding: 20, background: "#f8fafc" }}>
      {/* Logo decorativo: el texto "ManttoAI" al lado hace redundante un title en el SVG */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24 }}>
        <Logo size={28} />
        <span style={{ fontWeight: 700, fontSize: 16, color: "#111827" }}>ManttoAI</span>
      </div>

      <nav style={{ display: "grid", gap: 4 }}>
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              textDecoration: "none",
              padding: "8px 12px",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: isActive ? 600 : 400,
              // Color de marca centralizado para el ítem activo
              color: isActive ? BRAND_COLOR : "#374151",
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
