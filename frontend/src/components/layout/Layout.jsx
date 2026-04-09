import { useCallback, useEffect, useRef, useState } from "react";
import { Outlet } from "react-router-dom";

import Header from "./Header";
import OnboardingTour, { isOnboardingDone } from "../onboarding/OnboardingTour";
import Sidebar from "./Sidebar";

/**
 * Layout principal de la aplicación.
 * 
 * Estructura:
 * - Desktop (>768px): sidebar fijo 240px + header + main
 * - Tablet/Mobile (<=768px): header + main, sidebar como drawer superpuesto
 * 
 * Accesibilidad:
 * - Cierre del drawer con Escape
 * - Cierre del drawer al hacer clic en overlay
 * - Cierre del drawer al navegar (onNavClick)
 * - Restauración de foco al cerrar
 */
export default function Layout() {
  // Estado del drawer de navegación en resolución tablet
  const [sidebarAbierto, setSidebarAbierto] = useState(false);

  // Onboarding: se muestra solo la primera vez que el usuario ingresa
  const [mostrarOnboarding, setMostrarOnboarding] = useState(() => !isOnboardingDone());

  // Ref al botón hamburguesa para devolver el foco al cerrarlo
  const menuBtnRef = useRef(null);

  const toggleSidebar = useCallback(() => setSidebarAbierto((s) => !s), []);
  const cerrarSidebar = useCallback(() => setSidebarAbierto(false), []);

  // Cerrar el drawer con la tecla Escape (accesibilidad)
  useEffect(() => {
    if (!sidebarAbierto) return;

    function onKeyDown(e) {
      if (e.key === "Escape") cerrarSidebar();
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [sidebarAbierto, cerrarSidebar]);

  return (
    <div className="layout-root">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-3 focus:z-[120] focus:rounded-sm focus:bg-neutral-100 focus:px-3 focus:py-2 focus:text-sm focus:text-neutral-800 focus:ring-2 focus:ring-primary-500"
      >
        Saltar al contenido principal
      </a>

      {/* Overlay semitransparente: cierra el sidebar al hacer clic fuera en tablet */}
      {sidebarAbierto && (
        <div
          className="layout-overlay"
          onClick={cerrarSidebar}
          aria-hidden="true"
        />
      )}

      <Sidebar
        className={sidebarAbierto ? "layout-sidebar--abierto" : ""}
        sidebarAbierto={sidebarAbierto}
        onClose={cerrarSidebar}
        onNavClick={cerrarSidebar}
        retornarFocoRef={menuBtnRef}
      />

      <div className="flex min-w-0 flex-col">
        <Header
          onMenuToggle={toggleSidebar}
          sidebarAbierto={sidebarAbierto}
          menuBtnRef={menuBtnRef}
        />
        <main id="main-content" tabIndex={-1} className="bg-neutral-50 px-4 py-5 md:px-6 md:py-6 xl:px-8 xl:py-7">
          <Outlet />
        </main>
      </div>

      {/* Tour de onboarding para nuevos usuarios */}
      {mostrarOnboarding && (
        <OnboardingTour onComplete={() => setMostrarOnboarding(false)} />
      )}
    </div>
  );
}
