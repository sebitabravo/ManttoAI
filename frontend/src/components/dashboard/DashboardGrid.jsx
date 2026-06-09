import WidgetContainer from "./WidgetContainer";
import KpiCard from "./KpiCard";

/**
 * Mapeo de tipo de widget a componente de renderizado.
 */
function renderWidgetContent(type, config) {
  switch (type) {
    case "kpi":
      return <KpiCard {...config} />;
    case "chart":
    case "table":
    case "alerts":
      // Placeholder para widgets futuros —
      // se renderiza un mensaje indicando que el tipo aun no tiene implementacion.
      return (
        <div className="flex h-full min-h-[100px] items-center justify-center rounded-xl bg-neutral-50">
          <span className="text-sm text-neutral-400">
            Widget &quot;{type}&quot; — pendiente de implementacion
          </span>
        </div>
      );
    default:
      return (
        <div className="flex h-full min-h-[100px] items-center justify-center rounded-xl bg-neutral-50">
          <span className="text-sm text-neutral-400">
            Tipo de widget desconocido: &quot;{type}&quot;
          </span>
        </div>
      );
  }
}

/**
 * Grid responsive de widgets del dashboard.
 *
 * Layout:
 * - 1 columna en mobile
 * - 2 columnas en tablet (md)
 * - 3 columnas en desktop (lg)
 *
 * Props:
 * @param {Array<{id: string, type: string, title: string, config: object}>} widgets
 * @param {Function} [onRemoveWidget] - Callback con (widgetId) al eliminar
 * @param {Object} [states] - Estados por widgetId: { [id]: { loading, error, emptyTitle } }
 * @param {Object} [handlers] - Handlers por widgetId: { [id]: { onRefresh, onExpand } }
 */
export default function DashboardGrid({
  widgets = [],
  onRemoveWidget = null,
  states = {},
  handlers = {},
}) {
  if (!Array.isArray(widgets) || widgets.length === 0) {
    return (
      <div className="flex min-h-[200px] items-center justify-center rounded-2xl bg-white p-8 shadow-sm">
        <div className="text-center">
          <p className="text-sm text-neutral-400">
            No hay widgets en el dashboard.
          </p>
          <p className="mt-1 text-xs text-neutral-300">
            Agrega widgets desde el panel de configuracion.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {widgets.map((widget) => {
        const widgetState = states[widget.id] || {};
        const widgetHandlers = handlers[widget.id] || {};

        return (
          <WidgetContainer
            key={widget.id}
            title={widget.title}
            loading={widgetState.loading || false}
            error={widgetState.error || null}
            emptyTitle={widgetState.emptyTitle || null}
            emptyDescription={widgetState.emptyDescription || null}
            onRefresh={widgetHandlers.onRefresh || null}
            onExpand={widgetHandlers.onExpand || null}
            onRemove={
              onRemoveWidget
                ? () => onRemoveWidget(widget.id)
                : null
            }
          >
            {renderWidgetContent(widget.type, widget.config)}
          </WidgetContainer>
        );
      })}
    </div>
  );
}
