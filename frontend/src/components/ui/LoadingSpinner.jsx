/**
 * Indicador de carga del sistema de diseño ManttoAI.
 * 
 * Placeholder skeleton + label semántico para lectores de pantalla.
 * 
 * Uso:
 * - Estado de carga inicial (página completa)
 * - Carga inline (dentro de secciones)
 * 
 * Accesibilidad:
 * - role="status" + aria-live="polite" para anuncio no intrusivo
 * - aria-busy="true" para indicar proceso activo
 */
export default function LoadingSpinner({ label = "Cargando..." }) {
  return (
    <div 
      role="status" 
      aria-live="polite" 
      aria-busy="true"
      className="flex flex-col items-center justify-center gap-3 py-12"
    >
      {/* Skeleton visual: evita spinner genérico y mantiene jerarquía sobria */}
      <div className="w-full max-w-56 space-y-2" aria-hidden="true">
        <div className="h-2 w-full animate-pulse rounded bg-neutral-200" />
        <div className="h-2 w-4/5 animate-pulse rounded bg-neutral-200" />
      </div>
      
      {/* Label visible y para lectores de pantalla */}
      <span className="text-sm font-medium text-neutral-600">
        {label}
      </span>
    </div>
  );
}
