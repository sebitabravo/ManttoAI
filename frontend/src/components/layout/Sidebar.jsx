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
      <h2>ManttoAI</h2>
      <nav style={{ display: "grid", gap: 10 }}>
        {items.map((item) => (
          <NavLink key={item.to} to={item.to} style={{ textDecoration: "none", color: "#111827" }}>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
