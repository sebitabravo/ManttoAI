import { useId, useState } from "react";

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
  let minValue = Infinity;
  let maxValue = -Infinity;

  for (const value of values) {
    if (value < minValue) minValue = value;
    if (value > maxValue) maxValue = value;
  }

  if (minValue === Infinity) minValue = 0;
  if (maxValue === -Infinity) maxValue = 0;

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

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function resolveClosestPointIndex(points, targetX) {
  if (!Array.isArray(points) || points.length === 0) {
    return null;
  }

  let closestIndex = 0;
  let closestDistance = Math.abs(points[0].x - targetX);

  for (let index = 1; index < points.length; index += 1) {
    const distance = Math.abs(points[index].x - targetX);
    if (distance < closestDistance) {
      closestDistance = distance;
      closestIndex = index;
    }
  }

  return closestIndex;
}

export default function GraficoLineaBase({
  title,
  subtitle,
  series,
  unit,
  lineTone = "primary",
  emptyMessage,
}) {
  const [activeIndex, setActiveIndex] = useState(null);
  const chartId = useId().replace(/:/g, "");
  const titleId = `chart-title-${chartId}`;
  const descId = `chart-desc-${chartId}`;
  const safeTitle = String(title || "Serie");

  const normalizedSeries = (Array.isArray(series) ? series : [])
    .map((point) => ({
      timestamp: point?.timestamp,
      value: Number(point?.value),
    }))
    .filter((point) => Number.isFinite(point.value));

  const isEmpty = normalizedSeries.length === 0;
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

  const values = normalizedSeries.map((point) => point.value);
  const geometry = buildChartGeometry(values);
  const points = geometry.points;
  const linePoints = toPolylinePoints(points);
  const areaPath = toAreaPath(points);

  const latestValue = values[values.length - 1];
  const minValue = geometry.minValue;
  const maxValue = geometry.maxValue;
  const previousValue = values.length > 1 ? values[values.length - 2] : NaN;
  const deltaValue = Number.isFinite(previousValue) ? latestValue - previousValue : NaN;

  const yTicks = [maxValue, minValue + geometry.range / 2, minValue];

  const firstTimestamp = normalizedSeries[0].timestamp;
  const lastTimestamp = normalizedSeries[normalizedSeries.length - 1].timestamp;
  const description = `Último ${formatMetric(latestValue, unit)}. Mínimo ${formatMetric(
    minValue,
    unit
  )}. Máximo ${formatMetric(maxValue, unit)}.`;

  const resolvedActiveIndex =
    activeIndex === null ? null : clamp(activeIndex, 0, Math.max(points.length - 1, 0));

  const activePoint =
    resolvedActiveIndex === null ? null : points[resolvedActiveIndex];

  const activeSeriesPoint =
    resolvedActiveIndex === null ? null : normalizedSeries[resolvedActiveIndex];

  let activeTooltip = null;
  if (activePoint && activeSeriesPoint) {
    const tooltipWidth = 168;
    const tooltipHeight = 46;
    const desiredX = activePoint.x + 10;
    const desiredY = activePoint.y - tooltipHeight - 8;

    activeTooltip = {
      x: clamp(
        desiredX,
        CHART_PADDING.left + 4,
        CHART_WIDTH - CHART_PADDING.right - tooltipWidth
      ),
      y: clamp(
        desiredY,
        CHART_PADDING.top + 2,
        CHART_HEIGHT - CHART_PADDING.bottom - tooltipHeight - 2
      ),
      valueLabel: formatMetric(activeSeriesPoint.value, unit),
      dateLabel: formatDate(activeSeriesPoint.timestamp),
    };
  }

  function handlePointerMove(event) {
    if (!event?.currentTarget) {
      return;
    }

    const bounds = event.currentTarget.getBoundingClientRect();
    if (!Number.isFinite(bounds.width) || bounds.width <= 0) {
      return;
    }

    const rawX = ((event.clientX - bounds.left) / bounds.width) * CHART_WIDTH;
    const chartX = clamp(rawX, CHART_PADDING.left, CHART_WIDTH - CHART_PADDING.right);
    const nextIndex = resolveClosestPointIndex(points, chartX);

    if (nextIndex !== null) {
      setActiveIndex(nextIndex);
    }
  }

  function handleKeyDown(event) {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
      return;
    }

    event.preventDefault();

    if (event.key === "ArrowRight") {
      const next = resolvedActiveIndex === null ? 0 : clamp(resolvedActiveIndex + 1, 0, points.length - 1);
      setActiveIndex(next);
      return;
    }

    const prev =
      resolvedActiveIndex === null
        ? Math.max(points.length - 1, 0)
        : clamp(resolvedActiveIndex - 1, 0, points.length - 1);
    setActiveIndex(prev);
  }

  return (
    <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
      <h3 className="mb-2 mt-0 text-md font-semibold text-neutral-800">{title}</h3>
      <p className="mt-0 mb-4 text-sm text-neutral-500">{subtitle}</p>

      <svg
        width="100%"
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
        role="img"
        aria-labelledby={titleId}
        aria-describedby={descId}
        className="mb-4"
      >
        <title id={titleId}>{`Serie temporal de ${safeTitle.toLowerCase()}`}</title>
        <desc id={descId}>{description}</desc>

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

        {/* Capa de interacción (hover/focus/teclado) */}
        <rect
          x={CHART_PADDING.left}
          y={CHART_PADDING.top}
          width={geometry.innerWidth}
          height={geometry.innerHeight}
          fill="transparent"
          className="cursor-crosshair"
          aria-label="Explorar datos: mover el cursor o usar las teclas izquierda/derecha para ver detalles"
          tabIndex={0}
          onPointerDown={handlePointerMove}
          onPointerMove={handlePointerMove}
          onPointerEnter={handlePointerMove}
          onPointerLeave={() => setActiveIndex(null)}
          onFocus={() => setActiveIndex(points.length - 1)}
          onBlur={() => setActiveIndex(null)}
          onKeyDown={handleKeyDown}
        />

        {/* Línea vertical + punto activo */}
        {activePoint ? (
          <g pointerEvents="none">
            <line
              x1={activePoint.x}
              y1={CHART_PADDING.top}
              x2={activePoint.x}
              y2={CHART_HEIGHT - CHART_PADDING.bottom}
              className="text-neutral-300"
              stroke="currentColor"
              strokeWidth="1"
              strokeDasharray="4 3"
            />
            <circle
              cx={activePoint.x}
              cy={activePoint.y}
              r={4}
              className={lineClass}
              fill="currentColor"
              stroke="white"
              strokeWidth="2"
            />
          </g>
        ) : null}

        {/* Tooltip contextual del punto activo */}
        {activeTooltip ? (
          <g transform={`translate(${activeTooltip.x}, ${activeTooltip.y})`} pointerEvents="none">
            <rect
              width="168"
              height="46"
              rx="6"
              className="fill-neutral-50 stroke-neutral-300"
              strokeWidth="1"
            />
            <text x="8" y="17" className="fill-neutral-600 tabular-nums" fontSize="11">
              {activeTooltip.dateLabel}
            </text>
            <text x="8" y="34" className={`fill-current text-sm font-semibold ${lineClass}`}>
              {activeTooltip.valueLabel}
            </text>
          </g>
        ) : null}
  </svg>

      {/* Live region para que lectores de pantalla reciban actualizaciones del tooltip activo */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {activeTooltip ? `${activeTooltip.dateLabel} — ${activeTooltip.valueLabel}` : ""}
      </div>

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
