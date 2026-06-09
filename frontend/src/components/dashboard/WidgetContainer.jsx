import { RotateCw, Expand, X } from "lucide-react";

import { SkeletonCard } from "../ui/Skeleton";
import EmptyState from "../ui/EmptyState";

/**
 * Contenedor de widget del dashboard — Estilo Apple.
 *
 * Estados:
 * - loading: muestra un SkeletonCard
 * - error: muestra un mensaje de error estilizado
 * - empty: muestra EmptyState
 * - normal: muestra children
 *
 * Props:
 * @param {string} title - Titulo del widget
 * @param {React.ReactNode} [icon] - Icono lucide-react al lado del titulo
 * @param {boolean} [loading] - Estado de carga
 * @param {string|null} [error] - Mensaje de error (truthy = estado error)
 * @param {string|null} [emptyTitle] - Titulo para EmptyState
 * @param {string|null} [emptyDescription] - Descripcion para EmptyState
 * @param {Function} [onRefresh] - Handler para boton refresh
 * @param {Function} [onExpand] - Handler para boton expandir
 * @param {Function} [onRemove] - Handler para boton remover
 * @param {React.ReactNode} children - Contenido del widget en estado normal
 */
export default function WidgetContainer({
  title,
  icon = null,
  loading = false,
  error = null,
  emptyTitle = null,
  emptyDescription = null,
  onRefresh = null,
  onExpand = null,
  onRemove = null,
  children,
}) {
  const hasControls = onRefresh || onExpand || onRemove;

  return (
    <section className="flex h-full flex-col rounded-2xl bg-white p-6 shadow-sm transition-shadow duration-200 hover:shadow-apple">
      {/* Header */}
      <header className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon && (
            <span className="text-neutral-400" aria-hidden="true">
              {icon}
            </span>
          )}
          <h3 className="text-base font-semibold text-neutral-700 tracking-tight">
            {title}
          </h3>
        </div>

        {hasControls && (
          <div className="flex items-center gap-1">
            {onRefresh && (
              <button
                type="button"
                onClick={onRefresh}
                disabled={loading}
                aria-label="Actualizar widget"
                className="rounded-lg p-1.5 text-neutral-400 transition-colors duration-200 hover:bg-neutral-100 hover:text-neutral-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RotateCw
                  size={16}
                  className={loading ? "animate-spin" : ""}
                />
              </button>
            )}
            {onExpand && (
              <button
                type="button"
                onClick={onExpand}
                aria-label="Expandir widget"
                className="rounded-lg p-1.5 text-neutral-400 transition-colors duration-200 hover:bg-neutral-100 hover:text-neutral-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
              >
                <Expand size={16} />
              </button>
            )}
            {onRemove && (
              <button
                type="button"
                onClick={onRemove}
                aria-label="Eliminar widget"
                className="rounded-lg p-1.5 text-neutral-400 transition-colors duration-200 hover:bg-danger-50 hover:text-danger-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-danger-500 focus-visible:ring-offset-2"
              >
                <X size={16} />
              </button>
            )}
          </div>
        )}
      </header>

      {/* Cuerpo segun estado */}
      <div className="flex-1">
        {loading && <SkeletonCard />}

        {!loading && error && (
          <div className="flex h-full min-h-[120px] flex-col items-center justify-center gap-2 rounded-xl bg-danger-50/50 px-4 py-8 text-center">
            <p className="text-sm font-medium text-danger-600">
              {error}
            </p>
            {onRefresh && (
              <button
                type="button"
                onClick={onRefresh}
                className="mt-2 text-xs font-medium text-primary-600 underline underline-offset-2 hover:text-primary-700 transition-colors"
              >
                Intentar de nuevo
              </button>
            )}
          </div>
        )}

        {!loading && !error && emptyTitle && (
          <EmptyState title={emptyTitle} description={emptyDescription} />
        )}

        {!loading && !error && !emptyTitle && children}
      </div>
    </section>
  );
}
