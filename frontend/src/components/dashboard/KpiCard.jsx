import { ArrowUp, ArrowDown, Minus } from "lucide-react";

/**
 * Colores semánticos para cada dirección de tendencia.
 */
const TREND_COLORS = {
  up: {
    text: "text-success-600",
    bg: "bg-success-50",
    dot: "bg-success-500",
  },
  down: {
    text: "text-danger-600",
    bg: "bg-danger-50",
    dot: "bg-danger-500",
  },
  stable: {
    text: "text-neutral-600",
    bg: "bg-neutral-100",
    dot: "bg-neutral-500",
  },
};

/**
 * Mapeo de colores semánticos a clases Tailwind (evita clases dinámicas).
 */
const COLOR_MAP = {
  success: "text-success-600",
  danger: "text-danger-600",
  warning: "text-warning-600",
  primary: "text-primary-600",
};

/**
 * Icono según dirección de tendencia.
 */
function TrendIcon({ direction }) {
  switch (direction) {
    case "up":
      return <ArrowUp size={14} className="text-success-600" aria-hidden="true" />;
    case "down":
      return <ArrowDown size={14} className="text-danger-600" aria-hidden="true" />;
    default:
      return <Minus size={14} className="text-neutral-600" aria-hidden="true" />;
  }
}

/**
 * Widget KPI del dashboard — Estilo Apple.
 *
 * Muestra un valor numérico grande con su label y tendencia.
 *
 * Props:
 * @param {string} label - Etiqueta del KPI
 * @param {string|number} value - Valor a mostrar
 * @param {string} [unit] - Unidad de medida (ej: "°C", "%", "rpm")
 * @param {"up"|"down"|"stable"} [trend] - Dirección de tendencia
 * @param {string} [trendValue] - Texto descriptivo de la tendencia (ej: "+12% vs ayer")
 * @param {"success"|"danger"|"warning"|"primary"} [color] - Color semántico opcional
 */
export default function KpiCard({
  label,
  value,
  unit = null,
  trend = null,
  trendValue = null,
  color = null,
}) {
  const trendStyle = trend ? TREND_COLORS[trend] : null;

  return (
    <article className="rounded-2xl bg-white p-6 shadow-sm transition-shadow duration-200 hover:shadow-apple">
      {/* Label */}
      <div className="mb-2 flex items-center gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-neutral-500">
          {label}
        </span>
      </div>

      {/* Valor principal */}
      <div className="flex items-baseline gap-1.5">
        <span
          className={`metric-value text-4xl font-semibold tracking-tight ${
            color ? COLOR_MAP[color] : "text-neutral-700"
          }`}
        >
          {value}
        </span>
        {unit && (
          <span className="text-sm font-medium text-neutral-500">
            {unit}
          </span>
        )}
      </div>

      {/* Tendencia */}
      {trend && (
        <div className="mt-3 flex items-center gap-1.5">
          <span
            className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium ${
              trendStyle?.bg || ""
            } ${trendStyle?.text || ""}`}
          >
            <TrendIcon direction={trend} />
            {trendValue ?? null}
          </span>
        </div>
      )}
    </article>
  );
}
