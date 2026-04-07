import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Tailwind v3: CSS procesado via PostCSS, no requiere plugin de Vite
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
  preview: {
    host: "0.0.0.0",
    port: 4173,
  },
});
