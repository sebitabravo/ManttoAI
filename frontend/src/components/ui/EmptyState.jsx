/**
 * Estado vacío del sistema de diseño ManttoAI.
 * 
 * Usado cuando:
 * - No hay datos disponibles (tablas vacías, listas vacías)
 * - Filtros no retornan resultados
 * - Estado inicial antes de primera carga
 * 
 * Jerarquía visual:
 * - Título prominente
 * - Descripción secundaria con contexto
 * - Opcional: CTA para acción sugerida (pasarlo como children)
 */
export default function EmptyState({ title, description, children }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-neutral-300 bg-neutral-100 px-6 py-10 text-center shadow-sm">
      <h3 className="text-lg font-semibold text-neutral-700">
        {title}
      </h3>
      {description && (
        <p className="text-sm text-neutral-500 max-w-sm">
          {description}
        </p>
      )}
      {children && (
        <div className="mt-2">
          {children}
        </div>
      )}
    </div>
  );
}
