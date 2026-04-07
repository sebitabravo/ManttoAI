import { Link } from "react-router-dom";

import Button from "../ui/Button";
import useAuth from "../../hooks/useAuth";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 20, borderBottom: "1px solid #e5e7eb" }}>
      {/* Nombre de producto consistente con el branding del login */}
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <svg width="24" height="24" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
          <circle cx="16" cy="16" r="16" fill="#1d4ed8" />
          <text x="16" y="22" fontSize="20" fontWeight="700" textAnchor="middle" fontFamily="system-ui, sans-serif" fill="white">M</text>
        </svg>
        <strong style={{ color: "#111827" }}>ManttoAI</strong>
        <span style={{ color: "#6b7280", fontSize: 13 }}>Mantenimiento Predictivo</span>
      </div>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <span style={{ fontSize: 14, color: "#374151" }}>{user?.nombre || "Invitado"}</span>
        <Link to="/login" onClick={logout}>
          <Button variant="outline">Salir</Button>
        </Link>
      </div>
    </header>
  );
}
