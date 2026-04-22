import Logo from "../ui/Logo";
import TopbarNotifications from "./TopbarNotifications";
import UserMenu from "./UserMenu";

/**
 * Header principal de la aplicación — Estilo Apple Glass Navigation.
 * 
 * Características Apple:
 * - Efecto glass con backdrop-blur
 * - Altura compacta (48-56px)
 * - Tipografía limpia y espaciada
 * - Transiciones suaves
 * 
 * Props:
 *  - onMenuToggle: callback para alternar el sidebar en resolución tablet
 *  - sidebarAbierto: estado del drawer
 *  - menuBtnRef: ref al botón hamburguesa
 *  - onReplayTour: callback para lanzar el tour de producto
 */
export default function Header({ onMenuToggle, sidebarAbierto, menuBtnRef, onReplayTour }) {
  return (
    <header className="sticky top-0 z-50 flex h-14 items-center justify-between px-4 sm:px-6 glass-nav border-b border-neutral-200/50">
      <div className="flex items-center gap-4">
        {/* Botón hamburguesa: visible solo en tablet/mobile */}
        <button
          type="button"
          ref={menuBtnRef}
          className="btn-menu-tablet flex h-10 w-10 items-center justify-center rounded-lg text-neutral-500 transition-colors duration-200 hover:bg-neutral-100 hover:text-neutral-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
          onClick={onMenuToggle}
          aria-label={sidebarAbierto ? "Cerrar menú de navegación" : "Abrir menú de navegación"}
          aria-expanded={sidebarAbierto}
          aria-controls="nav-sidebar"
        >
          {sidebarAbierto ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          )}
        </button>

        {/* Logo + branding */}
        <div className="flex items-center gap-3">
          <Logo size={28} />
          <div className="flex items-baseline gap-2">
            <span className="text-base font-semibold text-neutral-600 tracking-tight">
              ManttoAI
            </span>
            <span className="hidden text-sm text-neutral-400 sm:inline">
              Mantenimiento Predictivo
            </span>
          </div>
        </div>
      </div>

      {/* Acciones: notificaciones + menú usuario */}
      <div className="flex items-center gap-2">
        <TopbarNotifications />
        <UserMenu onReplayTour={onReplayTour} />
      </div>
    </header>
  );
}
