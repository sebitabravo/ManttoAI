import { useCallback, useEffect, useRef, useState } from "react";
import { Outlet } from "react-router-dom";

import Header from "./Header";
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
        onNavClick={cerrarSidebar}
        retornarFocoRef={menuBtnRef}
      />

      <div className="flex flex-col">
        <Header
          onMenuToggle={toggleSidebar}
          sidebarAbierto={sidebarAbierto}
          menuBtnRef={menuBtnRef}
        />
        <main className="bg-neutral-50 px-4 py-5 md:px-6 md:py-6 xl:px-8 xl:py-7">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
