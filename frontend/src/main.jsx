import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";

// Registrar Service Worker para PWA (solo en producción)
if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("SW registrado:", registration.scope);
      })
      .catch((error) => {
        console.error("Error al registrar SW:", error);
      });
  });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
