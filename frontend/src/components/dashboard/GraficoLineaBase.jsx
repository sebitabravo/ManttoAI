import { formatDate } from "../../utils/formatDate";
import { formatMetric } from "../../utils/metrics";

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
      <section className="rounded-2xl border border-gray-200 p-4">
        <h2 className="mt-0">{title}</h2>
        <p className="mt-0 text-gray-500">{subtitle}</p>
        <p className="mb-0">{emptyMessage}</p>
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
    <section className="rounded-2xl border border-gray-200 p-4">
      <h2 className="mt-0">{title}</h2>
      <p className="mt-0 text-gray-500">{subtitle}</p>

      <svg
        width="100%"
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
        role="img"
        aria-label={`Serie temporal de ${title.toLowerCase()}`}
      >
        <line
          x1={CHART_PADDING}
          y1={CHART_HEIGHT - CHART_PADDING}
          x2={CHART_WIDTH - CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke="#d1d5db"
          strokeWidth="1"
        />
        <line
          x1={CHART_PADDING}
          y1={CHART_PADDING}
          x2={CHART_PADDING}
          y2={CHART_HEIGHT - CHART_PADDING}
          stroke="#d1d5db"
          strokeWidth="1"
        />
        <polyline fill="none" stroke={color} strokeWidth="3" points={points} />
      </svg>

      <div className="mt-3 grid grid-cols-3 gap-2">
        <div>
          <div className="text-xs text-gray-500">Último</div>
          <strong>{formatMetric(latestValue, unit)}</strong>
        </div>
        <div>
          <div className="text-xs text-gray-500">Mínimo</div>
          <strong>{formatMetric(minValue, unit)}</strong>
        </div>
        <div>
          <div className="text-xs text-gray-500">Máximo</div>
          <strong>{formatMetric(maxValue, unit)}</strong>
        </div>
      </div>

      <div className="mt-2 flex justify-between text-xs text-gray-500">
        <span>{formatDate(firstTimestamp)}</span>
        <span>{formatDate(lastTimestamp)}</span>
      </div>
    </section>
  );
}
