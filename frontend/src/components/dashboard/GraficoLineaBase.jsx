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
      <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
        <h2 style={{ marginTop: 0 }}>{title}</h2>
        <p style={{ marginTop: 0, color: "#6b7280" }}>{subtitle}</p>
        <p style={{ marginBottom: 0 }}>{emptyMessage}</p>
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
    <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <p style={{ marginTop: 0, color: "#6b7280" }}>{subtitle}</p>

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

      <div
        style={{
          marginTop: 12,
          display: "grid",
          gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
          gap: 8,
        }}
      >
        <div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>Último</div>
          <strong>{formatMetric(latestValue, unit)}</strong>
        </div>
        <div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>Mínimo</div>
          <strong>{formatMetric(minValue, unit)}</strong>
        </div>
        <div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>Máximo</div>
          <strong>{formatMetric(maxValue, unit)}</strong>
        </div>
      </div>

      <div
        style={{
          marginTop: 8,
          display: "flex",
          justifyContent: "space-between",
          color: "#6b7280",
          fontSize: 12,
        }}
      >
        <span>{formatDate(firstTimestamp)}</span>
        <span>{formatDate(lastTimestamp)}</span>
      </div>
    </section>
  );
}
