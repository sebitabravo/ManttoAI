/**
 * Componentes Skeleton para estados de carga — Estilo Apple.
 *
 * Características Apple:
 * - Cards con fondo blanco y sombra sutil
 * - Sin bordes pesados
 * - Animación pulse suave
 * - Esquinas redondeadas consistentes
 */

/**
 * Bloque animado base para skeletons.
 */
function PulseBlock({ className = "", style }) {
  return (
    <div 
      className={`animate-pulse rounded-lg bg-neutral-200 ${className}`} 
      style={style}
      aria-hidden="true" 
    />
  );
}

/**
 * Skeleton para bloques de texto.
 */
export function SkeletonText({ lines = 3, className = "" }) {
  const widths = ["w-full", "w-5/6", "w-4/5", "w-3/4", "w-2/3"];

  return (
    <div className={`grid gap-3 ${className}`} role="status" aria-busy="true" aria-label="Cargando contenido">
      {Array.from({ length: lines }, (_, i) => (
        <PulseBlock key={i} className={`h-4 ${widths[i % widths.length]}`} />
      ))}
    </div>
  );
}

/**
 * Skeleton para una card.
 */
export function SkeletonCard({ className = "" }) {
  return (
    <div 
      className={`rounded-2xl bg-white p-6 shadow-sm ${className}`} 
      role="status" 
      aria-busy="true" 
      aria-label="Cargando card"
    >
      <PulseBlock className="mb-4 h-5 w-2/3" />
      <PulseBlock className="mb-3 h-4 w-full" />
      <PulseBlock className="mb-3 h-4 w-5/6" />
      <PulseBlock className="h-4 w-1/2" />
    </div>
  );
}

/**
 * Skeleton para una métrica grande.
 */
export function SkeletonMetric({ className = "" }) {
  return (
    <div 
      className={`rounded-2xl bg-white p-6 shadow-sm ${className}`} 
      role="status" 
      aria-busy="true" 
      aria-label="Cargando métrica"
    >
      <PulseBlock className="mb-3 h-3 w-24" />
      <PulseBlock className="mb-3 h-12 w-24" />
      <PulseBlock className="h-4 w-3/4" />
    </div>
  );
}

/**
 * Skeleton para una tabla.
 */
export function SkeletonTable({ rows = 5, cols = 4, className = "" }) {
  return (
    <div 
      className={`rounded-2xl bg-white p-6 shadow-sm ${className}`} 
      role="status" 
      aria-busy="true" 
      aria-label="Cargando tabla"
    >
      {/* Título */}
      <PulseBlock className="mb-6 h-6 w-48" />

      {/* Header */}
      <div className="mb-4 flex gap-4 border-b border-neutral-100 pb-4">
        {Array.from({ length: cols }, (_, i) => (
          <PulseBlock key={i} className="h-3 flex-1" />
        ))}
      </div>

      {/* Filas */}
      {Array.from({ length: rows }, (_, rowIdx) => (
        <div key={rowIdx} className="flex gap-4 border-b border-neutral-100 py-4">
          {Array.from({ length: cols }, (_, colIdx) => (
            <PulseBlock key={colIdx} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton para un gráfico.
 */
export function SkeletonChart({ className = "" }) {
  return (
    <div 
      className={`rounded-2xl bg-white p-6 shadow-sm ${className}`} 
      role="status" 
      aria-busy="true" 
      aria-label="Cargando gráfico"
    >
      <PulseBlock className="mb-2 h-5 w-40" />
      <PulseBlock className="mb-6 h-4 w-64" />

      {/* Área del gráfico */}
      <div className="mb-6 flex h-48 items-end gap-1.5">
        {Array.from({ length: 12 }, (_, i) => (
          <PulseBlock
            key={i}
            className="flex-1 rounded-t-lg"
            style={{ height: `${30 + Math.sin(i * 0.5) * 25 + 20}%` }}
          />
        ))}
      </div>

      {/* Métricas resumen */}
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 3 }, (_, i) => (
          <div key={i}>
            <PulseBlock className="mb-2 h-3 w-16" />
            <PulseBlock className="h-6 w-20" />
          </div>
        ))}
      </div>
    </div>
  );
}
