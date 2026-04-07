import { NavLink } from "react-router-dom";

const items = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/equipos", label: "Equipos" },
  { to: "/alertas", label: "Alertas" },
  { to: "/historial", label: "Historial" },
];

export default function Sidebar() {
  return (
    <aside style={{ borderRight: "1px solid #e5e7eb", padding: 20, background: "#f8fafc" }}>
      {/* Branding del sidebar: logo + nombre de producto */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24 }}>
        <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
          <circle cx="16" cy="16" r="16" fill="#1d4ed8" />
          <text x="16" y="22" fontSize="20" fontWeight="700" textAnchor="middle" fontFamily="system-ui, sans-serif" fill="white">M</text>
        </svg>
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
              // Color de marca azul para el ítem activo, gris neutro para el resto
              color: isActive ? "#1d4ed8" : "#374151",
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
