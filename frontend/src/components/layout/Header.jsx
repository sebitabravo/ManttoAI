import { useNavigate } from "react-router-dom";

import Button from "../ui/Button";
import Logo from "../ui/Logo";
import useAuth from "../../hooks/useAuth";

/**
 * Header principal de la aplicación.
 * 
 * Funcionalidad:
 * - Logo + branding
 * - Botón hamburguesa para sidebar responsive (visible solo en tablet/mobile)
 * - Usuario actual + botón salir
 * 
 * Props:
 *  - onMenuToggle: callback para alternar el sidebar en resolución tablet
 *  - sidebarAbierto: estado del drawer (para aria-expanded y aria-label dinámico)
 *  - menuBtnRef: ref al botón hamburguesa (para devolver foco al cerrar el drawer)
 */
export default function Header({ onMenuToggle, sidebarAbierto, menuBtnRef }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="flex items-center justify-between border-b border-neutral-200 bg-neutral-100 px-5 py-4">
      <div className="flex items-center gap-3">
        {/* Botón hamburguesa: visible solo en tablet/mobile via CSS (.btn-menu-tablet) */}
        <button
          type="button"
          ref={menuBtnRef}
          className="btn-menu-tablet flex items-center justify-center rounded-sm bg-transparent p-1 text-neutral-600 transition-all duration-150 ease-out-quart hover:bg-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
          onClick={onMenuToggle}
          aria-label={sidebarAbierto ? "Cerrar menú de navegación" : "Abrir menú de navegación"}
          aria-expanded={sidebarAbierto}
          aria-controls="nav-sidebar"
        >
          {/* Ícono hamburguesa SVG inline */}
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

        {/* Logo + branding */}
        <Logo size={24} />
        <strong className="text-base font-semibold text-neutral-800">ManttoAI</strong>
        <span className="hidden text-sm text-neutral-500 sm:inline">Mantenimiento Predictivo</span>
      </div>

      {/* Usuario + botón salir */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-neutral-600">{user?.nombre || "Invitado"}</span>
        <Button type="button" variant="outline" onClick={handleLogout}>
          Salir
        </Button>
      </div>
    </header>
  );
}
