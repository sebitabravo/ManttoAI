import { Link } from "react-router-dom";

import Button from "../ui/Button";
import Logo from "../ui/Logo";
import useAuth from "../../hooks/useAuth";
import { FONT_SIZE, RADIUS, SPACING, SURFACE, TEXT_COLOR } from "../../styles/tokens";

/**
 * Header principal de la aplicación.
 * Props:
 *  - onMenuClick: callback para abrir el sidebar en resolución tablet
 */
export default function Header({ onMenuClick }) {
  const { user, logout } = useAuth();

  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: SPACING.xl, borderBottom: `1px solid ${SURFACE.border}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm }}>
        {/* Botón hamburguesa: solo visible en tablet via CSS (.btn-menu-tablet) */}
        <button
          type="button"
          className="btn-menu-tablet"
          onClick={onMenuClick}
          aria-label="Abrir menú de navegación"
          style={{ alignItems: "center", justifyContent: "center", background: "none", border: "none", cursor: "pointer", padding: SPACING.xs, borderRadius: RADIUS.sm, color: TEXT_COLOR.secondary }}
        >
          {/* Ícono hamburguesa SVG inline — sin dependencias externas */}
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

        {/* Logo decorativo: el texto "ManttoAI" al lado hace redundante un title en el SVG */}
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
