import { useCallback, useEffect, useRef, useState } from "react";
import { Outlet } from "react-router-dom";

import Header from "./Header";
import Sidebar from "./Sidebar";
import { SPACING } from "../../styles/tokens";

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
        className={`layout-sidebar${sidebarAbierto ? " layout-sidebar--abierto" : ""}`}
        sidebarAbierto={sidebarAbierto}
        onNavClick={cerrarSidebar}
        retornarFocoRef={menuBtnRef}
      />

      <div>
        <Header
          onMenuToggle={toggleSidebar}
          sidebarAbierto={sidebarAbierto}
          menuBtnRef={menuBtnRef}
        />
        <main style={{ padding: SPACING.xxl }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
