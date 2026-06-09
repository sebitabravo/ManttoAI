import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Registrar Service Worker para PWA (solo en producción)
if (
  import.meta.env.PROD &&
  "serviceWorker" in navigator
) {
  navigator.serviceWorker.register("/sw.js").catch(() => {
    // Fallo silencioso: la app funciona sin offline
  });
}
