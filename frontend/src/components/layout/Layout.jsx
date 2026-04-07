import { useState } from "react";
import { Outlet } from "react-router-dom";

import Header from "./Header";
import Sidebar from "./Sidebar";

export default function Layout() {
  // Estado del drawer de navegación en resolución tablet
  const [sidebarAbierto, setSidebarAbierto] = useState(false);

  function abrirSidebar() {
    setSidebarAbierto(true);
  }

  function cerrarSidebar() {
    setSidebarAbierto(false);
  }

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
        onNavClick={cerrarSidebar}
      />

      <div>
        <Header onMenuClick={abrirSidebar} />
        <main style={{ padding: 24 }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
