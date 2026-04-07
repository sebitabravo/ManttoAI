import { Link } from "react-router-dom";

import Button from "../ui/Button";
import Logo from "../ui/Logo";
import useAuth from "../../hooks/useAuth";
import { FONT_SIZE, SPACING, SURFACE, TEXT_COLOR } from "../../styles/tokens";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: SPACING.xl, borderBottom: `1px solid ${SURFACE.border}` }}>
      {/* Logo decorativo: el texto "ManttoAI" al lado hace redundante un title en el SVG */}
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm }}>
        <Logo size={24} />
        <strong style={{ color: TEXT_COLOR.primary }}>ManttoAI</strong>
        <span style={{ color: TEXT_COLOR.muted, fontSize: FONT_SIZE.sm }}>Mantenimiento Predictivo</span>
      </div>
      <div style={{ display: "flex", gap: SPACING.md, alignItems: "center" }}>
        <span style={{ fontSize: FONT_SIZE.base, color: TEXT_COLOR.secondary }}>{user?.nombre || "Invitado"}</span>
        <Link to="/login" onClick={logout}>
          <Button variant="outline">Salir</Button>
        </Link>
      </div>
    </header>
  );
}
