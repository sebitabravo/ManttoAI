import { formatDate } from "../../utils/formatDate";
import { formatMetric } from "../../utils/metrics";

/**
 * Gráfico de línea base para series temporales.
 * 
 * Usado por GraficoTemperatura y GraficoVibracion.
 * SVG nativo sin dependencias externas (Chart.js pesado para MVP).
 * 
 * Features:
 * - Escalado automático según min/max de valores
 * - Responsive con viewBox
 * - Métricas resumen: último, mínimo, máximo
 * - Range temporal visible (primer y último timestamp)
 */
const CHART_WIDTH = 560;
const CHART_HEIGHT = 240;
const CHART_PADDING = {
  top: 20,
  right: 20,
  bottom: 26,
  left: 54,
};

const LINE_TONE_CLASS = {
  primary: "text-primary-600",
  success: "text-success-600",
  warning: "text-warning-600",
  danger: "text-danger-600",
};

function buildChartGeometry(values) {
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = maxValue - minValue || 1;

  const innerWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right;
  const innerHeight = CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom;

  const toY = (value) =>
    CHART_PADDING.top + ((maxValue - value) / range) * innerHeight;

  const points = values.map((value, index) => {
    const denominator = values.length > 1 ? values.length - 1 : 1;
    const x = CHART_PADDING.left + (index / denominator) * innerWidth;
    return {
      value,
      x,
      y: toY(value),
    };
  });

  return {
    minValue,
    maxValue,
    range,
    innerWidth,
    innerHeight,
    points,
    toY,
  };
}

function toPolylinePoints(points) {
  return points.map((point) => `${point.x},${point.y}`).join(" ");
}

function toAreaPath(points) {
  if (points.length === 0) return "";

  const first = points[0];
  const last = points[points.length - 1];
  const baselineY = CHART_HEIGHT - CHART_PADDING.bottom;
  const line = points.map((point) => `L ${point.x} ${point.y}`).join(" ");

  return `M ${first.x} ${baselineY} ${line} L ${last.x} ${baselineY} Z`;
}

function formatDelta(value, unit) {
  if (!Number.isFinite(value)) {
    return "—";
  }

  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)} ${unit}`;
}

export default function GraficoLineaBase({
  title,
  subtitle,
  series,
  unit,
  lineTone = "primary",
  emptyMessage,
}) {
  const isEmpty = series.length === 0;
  const lineClass = LINE_TONE_CLASS[lineTone] || LINE_TONE_CLASS.primary;

  if (isEmpty) {
    return (
      <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
        <h3 className="mb-2 mt-0 text-md font-semibold text-neutral-800">{title}</h3>
        <p className="mt-0 text-sm text-neutral-500">{subtitle}</p>
        {/* Placeholder visual — área del gráfico vacía */}
        <div className="my-4 flex h-32 items-center justify-center rounded border border-dashed border-neutral-300 bg-neutral-50">
          <span className="text-sm text-neutral-400">{emptyMessage}</span>
        </div>
      </section>
    );
  }

  const values = series.map((point) => point.value);
  const geometry = buildChartGeometry(values);
  const points = geometry.points;
  const linePoints = toPolylinePoints(points);
  const areaPath = toAreaPath(points);

  const latestValue = values[values.length - 1];
  const minValue = geometry.minValue;
  const maxValue = geometry.maxValue;
  const previousValue = values.length > 1 ? values[values.length - 2] : NaN;
  const deltaValue = Number.isFinite(previousValue) ? latestValue - previousValue : NaN;
  const lastPoint = points[points.length - 1];

  const yTicks = [maxValue, minValue + geometry.range / 2, minValue];

  const firstTimestamp = series[0].timestamp;
  const lastTimestamp = series[series.length - 1].timestamp;

  return (
    <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
      <h3 className="mb-2 mt-0 text-md font-semibold text-neutral-800">{title}</h3>
      <p className="mt-0 mb-4 text-sm text-neutral-500">{subtitle}</p>

      <svg
        width="100%"
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
        role="img"
        aria-label={`Serie temporal de ${title.toLowerCase()}`}
        className="mb-4"
      >
        <title>{`Serie temporal de ${title.toLowerCase()}`}</title>

        {/* Grilla horizontal + etiquetas de referencia */}
        {yTicks.map((tick, index) => {
          const y = geometry.toY(tick);

          return (
            <g key={index}>
              <line
                x1={CHART_PADDING.left}
                y1={y}
                x2={CHART_WIDTH - CHART_PADDING.right}
                y2={y}
                className="text-neutral-200"
                stroke="currentColor"
                strokeWidth="1"
              />
              <text
                x={CHART_PADDING.left - 8}
                y={y + 4}
                className="fill-neutral-500 tabular-nums"
                textAnchor="end"
                fontSize="11"
              >
                {formatMetric(tick, unit)}
              </text>
            </g>
          );
        })}

        {/* Ejes del gráfico */}
        <line
          x1={CHART_PADDING.left}
          y1={CHART_HEIGHT - CHART_PADDING.bottom}
          x2={CHART_WIDTH - CHART_PADDING.right}
          y2={CHART_HEIGHT - CHART_PADDING.bottom}
          className="text-neutral-300"
          stroke="currentColor"
          strokeWidth="1"
        />
        <line
          x1={CHART_PADDING.left}
          y1={CHART_PADDING.top}
          x2={CHART_PADDING.left}
          y2={CHART_HEIGHT - CHART_PADDING.bottom}
          className="text-neutral-300"
          stroke="currentColor"
          strokeWidth="1"
        />

        {/* Área de tendencia */}
        <path className={`${lineClass} opacity-10`} d={areaPath} fill="currentColor" />

        {/* Línea de datos */}
        <polyline
          className={lineClass}
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={linePoints}
        />

        {/* Puntos de muestra */}
        {points.map((point, index) => {
          const isLatest = index === points.length - 1;
          return (
            <circle
              key={`${point.x}-${point.y}`}
              cx={point.x}
              cy={point.y}
              r={isLatest ? 4 : 2}
              className={isLatest ? lineClass : "text-neutral-400"}
              fill="currentColor"
            />
          );
        })}

        {/* Marcador de valor actual */}
        {lastPoint ? (
          <text
            x={Math.min(lastPoint.x + 8, CHART_WIDTH - CHART_PADDING.right - 4)}
            y={Math.max(lastPoint.y - 8, CHART_PADDING.top + 10)}
            className={`fill-current text-xs font-medium ${lineClass}`}
          >
            {formatMetric(latestValue, unit)}
          </text>
        ) : null}
      </svg>

      {/* Métricas resumen */}
      <div className="mb-3 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">Último</div>
          <strong className="metric-value text-lg text-neutral-800">{formatMetric(latestValue, unit)}</strong>
        </div>
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">Variación</div>
          <strong className="metric-value text-lg text-primary-700">{formatDelta(deltaValue, unit)}</strong>
        </div>
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">Mínimo</div>
          <strong className="metric-value text-lg text-neutral-800">{formatMetric(minValue, unit)}</strong>
        </div>
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">Máximo</div>
          <strong className="metric-value text-lg text-neutral-800">{formatMetric(maxValue, unit)}</strong>
        </div>
      </div>

      {/* Range temporal */}
      <div className="flex justify-between border-t border-neutral-200 pt-3 text-xs tabular-nums text-neutral-500">
        <span>{formatDate(firstTimestamp)}</span>
        <span>{formatDate(lastTimestamp)}</span>
      </div>
    </section>
  );
}
