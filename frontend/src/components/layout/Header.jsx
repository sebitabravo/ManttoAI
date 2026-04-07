import { Link } from "react-router-dom";

import Button from "../ui/Button";
import Logo from "../ui/Logo";
import useAuth from "../../hooks/useAuth";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 20, borderBottom: "1px solid #e5e7eb" }}>
      {/* Logo decorativo: el texto "ManttoAI" al lado hace redundante un title en el SVG */}
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Logo size={24} />
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
