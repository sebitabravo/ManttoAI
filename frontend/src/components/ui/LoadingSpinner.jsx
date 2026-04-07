/**
 * Indicador de carga del sistema de diseño ManttoAI.
 * 
 * Spinner visual animado + label semántico para lectores de pantalla.
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
      {/* Spinner visual animado */}
      <div 
        className="h-10 w-10 animate-spin rounded-full border-4 border-neutral-200 border-t-primary-600"
        aria-hidden="true"
      />
      
      {/* Label visible y para lectores de pantalla */}
      <span className="text-sm font-medium text-neutral-600">
        {label}
      </span>
    </div>
  );
}
