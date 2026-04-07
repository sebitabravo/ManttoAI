import { Link } from "react-router-dom";

/**
 * Página 404 — ruta no encontrada.
 * Diseño limpio con CTA claro para volver al dashboard.
 */
export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-neutral-50 p-8">
      <div className="metric-value text-6xl font-semibold text-neutral-300">404</div>
      <h1 className="text-xl font-semibold text-neutral-800">Página no encontrada</h1>
      <p className="text-sm text-neutral-600">La ruta solicitada no existe en el sistema.</p>
      <Link
        to="/dashboard"
        className="mt-2 text-sm font-medium text-primary-600 transition-colors duration-150 ease-out-quart hover:text-primary-700 hover:underline"
      >
        Volver al dashboard
      </Link>
    </main>
  );
}
