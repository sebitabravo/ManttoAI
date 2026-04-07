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
const CHART_HEIGHT = 220;
const CHART_PADDING = 28;

function buildLinePoints(values) {
  if (values.length === 0) {
    return "";
  }

  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = maxValue - minValue || 1;
  const innerWidth = CHART_WIDTH - CHART_PADDING * 2;
  const innerHeight = CHART_HEIGHT - CHART_PADDING * 2;

  return values
    .map((value, index) => {
      const denominator = values.length > 1 ? values.length - 1 : 1;
      const x = CHART_PADDING + (index / denominator) * innerWidth;
      const normalizedValue = (value - minValue) / range;
      const y = CHART_HEIGHT - CHART_PADDING - normalizedValue * innerHeight;
      return `${x},${y}`;
    })
    .join(" ");
}

export default function GraficoLineaBase({
  title,
  subtitle,
  series,
  unit,
  color,
  emptyMessage,
}) {
  const isEmpty = series.length === 0;

  if (isEmpty) {
    return (
      <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-6">
        <h3 className="mb-2 mt-0 text-md font-semibold text-neutral-800">{title}</h3>
        <p className="mt-0 text-sm text-neutral-500">{subtitle}</p>
        <p className="mb-0 text-sm text-neutral-600">{emptyMessage}</p>
      </section>
    );
  }

  const values = series.map((point) => point.value);
  const points = buildLinePoints(values);
  const latestValue = values[values.length - 1];
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const firstTimestamp = series[0].timestamp;
  const lastTimestamp = series[series.length - 1].timestamp;

  return (
    <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-6">
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
        
        {/* Ejes del gráfico */}
        <line
          x1={CHART_PADDING}
          y1={CHART_HEIGHT - CHART_PADDING}
          x2={CHART_WIDTH - CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke="oklch(85% 0.012 250)"
          strokeWidth="1"
        />
        <line
          x1={CHART_PADDING}
          y1={CHART_PADDING}
          x2={CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke="oklch(85% 0.012 250)"
          strokeWidth="1"
        />
        
        {/* Línea de datos */}
        <polyline fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={points} />
      </svg>

      {/* Métricas resumen */}
      <div className="mb-3 grid grid-cols-3 gap-3">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">Último</div>
          <strong className="metric-value text-lg text-neutral-800">{formatMetric(latestValue, unit)}</strong>
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
