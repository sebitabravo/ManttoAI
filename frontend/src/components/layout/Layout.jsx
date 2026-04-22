import { useCallback, useEffect, useRef, useState } from "react";
import { Outlet } from "react-router-dom";

import Header from "./Header";
import OnboardingTour from "../onboarding/OnboardingTour";
import { isOnboardingDone } from "../../utils/onboardingStorage";
import Sidebar from "./Sidebar";
import ChatBot from "../chat/ChatBot";

/**
 * Layout principal de la aplicación — Estilo Apple.
 * 
 * Estructura:
 * - Desktop (>768px): sidebar fijo 260px + header glass + main
 * - Tablet/Mobile (<=768px): header + main, sidebar como drawer superpuesto
 * 
 * Características Apple:
 * - Fondo gris Apple (#f5f5f7)
 * - Header con efecto glass
 * - Espaciado generoso
 * - Transiciones suaves
 */
export default function Layout() {
  const [sidebarAbierto, setSidebarAbierto] = useState(false);
  const [mostrarOnboarding, setMostrarOnboarding] = useState(() => !isOnboardingDone());
  const menuBtnRef = useRef(null);

  const toggleSidebar = useCallback(() => setSidebarAbierto((s) => !s), []);
  const cerrarSidebar = useCallback(() => setSidebarAbierto(false), []);

  // Cerrar el drawer con Escape
  useEffect(() => {
    if (!sidebarAbierto) return;

    function onKeyDown(e) {
      if (e.key === "Escape") cerrarSidebar();
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [sidebarAbierto, cerrarSidebar]);

  return (
    <div className="layout-root min-h-screen bg-neutral-100">
      {/* Skip link para accesibilidad */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[120] focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-500 focus:shadow-lg focus:ring-2 focus:ring-primary-500"
      >
        Saltar al contenido principal
      </a>

      {/* Overlay para cerrar sidebar en mobile */}
      {sidebarAbierto && (
        <div
          className="layout-overlay"
          onClick={cerrarSidebar}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <Sidebar
        className={sidebarAbierto ? "layout-sidebar--abierto" : ""}
        sidebarAbierto={sidebarAbierto}
        onClose={cerrarSidebar}
        onNavClick={cerrarSidebar}
        retornarFocoRef={menuBtnRef}
      />

      {/* Contenido principal */}
      <div className="flex min-w-0 flex-col">
        <Header
          onMenuToggle={toggleSidebar}
          sidebarAbierto={sidebarAbierto}
          menuBtnRef={menuBtnRef}
          onReplayTour={() => setMostrarOnboarding(true)}
        />
        
        <main 
          id="main-content" 
          tabIndex={-1} 
          className="flex-1 bg-neutral-100 px-6 py-8 md:px-8 md:py-10 xl:px-12"
        >
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Tour de onboarding */}
      {mostrarOnboarding && (
        <OnboardingTour onComplete={() => setMostrarOnboarding(false)} />
      )}

      {/* Asistente de IA */}
      <ChatBot />
    </div>
  );
}
