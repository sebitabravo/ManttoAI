/**
 * Componentes Skeleton para estados de carga del sistema de diseño ManttoAI.
 *
 * Reemplazan al spinner genérico con placeholders que imitan la estructura
 * del contenido que se va a cargar. Reducen la percepción de espera y dan
 * contexto visual sobre lo que está por aparecer.
 *
 * Variantes:
 * - SkeletonText: líneas de texto con ancho variable
 * - SkeletonCard: card rectangular con título y líneas
 * - SkeletonTable: tabla con filas skeleton
 * - SkeletonMetric: métrica grande con label
 *
 * Accesibilidad:
 * - role="status" + aria-busy="true" en el contenedor
 * - aria-label descriptivo para lectores de pantalla
 */

/**
 * Pulso animado base para todos los skeletons.
 * Usa animate-pulse de Tailwind con fondo neutral sutil.
 */
function PulseBlock({ className = "" }) {
  return <div className={`animate-pulse rounded bg-neutral-200 ${className}`} aria-hidden="true" />;
}

/**
 * Skeleton para bloques de texto.
 * Genera `lines` líneas con ancho variado para simular texto real.
 */
export function SkeletonText({ lines = 3, className = "" }) {
  // Anchos variados para que no se vea como una grilla repetitiva
  const widths = ["w-full", "w-5/6", "w-4/5", "w-3/4", "w-2/3"];

  return (
    <div className={`grid gap-2 ${className}`} role="status" aria-busy="true" aria-label="Cargando contenido">
      {Array.from({ length: lines }, (_, i) => (
        <PulseBlock key={i} className={`h-4 ${widths[i % widths.length]}`} />
      ))}
    </div>
  );
}

/**
 * Skeleton para una card con título y contenido.
 * Imita la estructura de EquipoCard, EquipoResumenCard, etc.
 */
export function SkeletonCard({ className = "" }) {
  return (
    <div className={`rounded-lg border border-neutral-200 bg-neutral-100 p-4 ${className}`} role="status" aria-busy="true" aria-label="Cargando card">
      <PulseBlock className="mb-3 h-5 w-2/3" />
      <PulseBlock className="mb-2 h-4 w-full" />
      <PulseBlock className="mb-2 h-4 w-5/6" />
      <PulseBlock className="h-4 w-1/2" />
    </div>
  );
}

/**
 * Skeleton para una métrica grande (como las de ResumenCards).
 * Título chico + número grande + subtítulo.
 */
export function SkeletonMetric({ className = "" }) {
  return (
    <div className={`rounded-lg border border-neutral-200 bg-neutral-100 p-4 ${className}`} role="status" aria-busy="true" aria-label="Cargando métrica">
      <PulseBlock className="mb-2 h-3 w-24" />
      <PulseBlock className="mb-2 h-10 w-20" />
      <PulseBlock className="h-4 w-3/4" />
    </div>
  );
}

/**
 * Skeleton para una tabla con encabezados y filas.
 * Imita la estructura de TablaEstadoEquipos, TablaUltimasLecturas, etc.
 */
export function SkeletonTable({ rows = 5, cols = 4, className = "" }) {
  return (
    <div className={`rounded-lg border border-neutral-200 bg-neutral-100 p-4 ${className}`} role="status" aria-busy="true" aria-label="Cargando tabla de datos">
      {/* Título */}
      <PulseBlock className="mb-4 h-5 w-40" />

      {/* Header */}
      <div className="mb-3 flex gap-4 border-b border-neutral-200 pb-3">
        {Array.from({ length: cols }, (_, i) => (
          <PulseBlock key={i} className="h-3 flex-1" />
        ))}
      </div>

      {/* Filas */}
      {Array.from({ length: rows }, (_, rowIdx) => (
        <div key={rowIdx} className="flex gap-4 border-b border-neutral-100 py-2.5">
          {Array.from({ length: cols }, (_, colIdx) => (
            <PulseBlock key={colIdx} className={`h-4 flex-1 ${colIdx === 0 ? "w-20" : ""}`} />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton para el gráfico de línea base.
 * Imita el área del gráfico SVG con métricas resumen debajo.
 */
export function SkeletonChart({ className = "" }) {
  return (
    <div className={`rounded-lg border border-neutral-200 bg-neutral-100 p-4 ${className}`} role="status" aria-busy="true" aria-label="Cargando gráfico">
      <PulseBlock className="mb-2 h-5 w-32" />
      <PulseBlock className="mb-4 h-4 w-56" />

      {/* Área del gráfico */}
      <div className="mb-4 flex h-44 items-end gap-1">
        {Array.from({ length: 12 }, (_, i) => (
          <PulseBlock
            key={i}
            className="flex-1"
            // Alturas variadas para simular una curva
            style={{ height: `${30 + Math.sin(i * 0.5) * 25 + 20}%` }}
          />
        ))}
      </div>

      {/* Métricas resumen */}
      <div className="grid grid-cols-3 gap-3">
        <div>
          <PulseBlock className="mb-1 h-3 w-12" />
          <PulseBlock className="h-5 w-16" />
        </div>
        <div>
          <PulseBlock className="mb-1 h-3 w-12" />
          <PulseBlock className="h-5 w-16" />
        </div>
        <div>
          <PulseBlock className="mb-1 h-3 w-12" />
          <PulseBlock className="h-5 w-16" />
        </div>
      </div>
    </div>
  );
}
