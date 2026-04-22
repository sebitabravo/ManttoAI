import { useId, useMemo, useState } from "react";

import { formatDate, formatAxisTime } from "../../utils/formatDate";
import { formatMetric } from "../../utils/metrics";

/**
 * Gráfico de línea enriquecido para series temporales.
 *
 * Inspirado en dashboards enterprise:
 * - Línea suavizada + área degradada
 * - Bandas de contexto por rangos operacionales
 * - Tooltip contextual y crosshair
 * - Métricas clave + estado actual
 *
 * Mantiene SVG nativo para evitar dependencias pesadas.
 */
const CHART_WIDTH = 620;
const CHART_HEIGHT = 270;
const CHART_PADDING = {
  top: 26,
  right: 24,
  bottom: 34,
  left: 68,
};

const LINE_THEMES = {
  primary: {
    lineStart: "#2563eb",
    lineEnd: "#06b6d4",
    areaStart: "#60a5fa",
    areaEnd: "#dbeafe",
    accent: "#1d4ed8",
  },
  success: {
    lineStart: "#059669",
    lineEnd: "#10b981",
    areaStart: "#34d399",
    areaEnd: "#d1fae5",
    accent: "#047857",
  },
  warning: {
    lineStart: "#d97706",
    lineEnd: "#f59e0b",
    areaStart: "#fbbf24",
    areaEnd: "#fef3c7",
    accent: "#b45309",
  },
  danger: {
    lineStart: "#dc2626",
    lineEnd: "#f97316",
    areaStart: "#fb7185",
    areaEnd: "#fee2e2",
    accent: "#b91c1c",
  },
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

  const toY =
    range === 0
      ? () => CHART_PADDING.top + innerHeight / 2
      : (value) => CHART_PADDING.top + ((maxValue - value) / range) * innerHeight;

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

function toSmoothLinePath(points, tension = 0.2) {
  if (!Array.isArray(points) || points.length === 0) return "";
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;

  let d = `M ${points[0].x} ${points[0].y}`;

  for (let index = 0; index < points.length - 1; index += 1) {
    const p0 = points[index - 1] || points[index];
    const p1 = points[index];
    const p2 = points[index + 1];
    const p3 = points[index + 2] || p2;

    const cp1x = p1.x + (p2.x - p0.x) * tension;
    const cp1y = p1.y + (p2.y - p0.y) * tension;
    const cp2x = p2.x - (p3.x - p1.x) * tension;
    const cp2y = p2.y - (p3.y - p1.y) * tension;

    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }

  return d;
}

function toSmoothAreaPath(points, tension = 0.2) {
  if (!Array.isArray(points) || points.length === 0) return "";

  const baselineY = CHART_HEIGHT - CHART_PADDING.bottom;
  const topPath = toSmoothLinePath(points, tension);
  const last = points[points.length - 1];
  const first = points[0];

  return `${topPath} L ${last.x} ${baselineY} L ${first.x} ${baselineY} Z`;
}

function formatDelta(value, unit) {
  if (!Number.isFinite(value)) {
    return "—";
  }

  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)} ${unit}`;
}

function formatCompact(value) {
  if (!Number.isFinite(value)) return "—";
  return Number(value).toFixed(1);
}

function formatZoneRange(zone, unit) {
  const min = zone.min;
  const max = zone.max;

  if (max === Infinity) {
    return `> ${formatCompact(min)} ${unit}`;
  }
  if (min === -Infinity) {
    return `< ${formatCompact(max)} ${unit}`;
  }
  return `${formatCompact(min)} – ${formatCompact(max)} ${unit}`;
}

function sanitizeColor(input, fallback = "#cbd5e1") {
  if (typeof input !== "string") {
    return fallback;
  }

  const value = input.trim();
  if (/^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$/i.test(value)) {
    return value;
  }

  if (/^var\(--[a-z0-9-]+\)$/i.test(value)) {
    return value;
  }

  const safeKeywords = new Set(["transparent", "currentColor"]);
  if (safeKeywords.has(value.toLowerCase())) {
    return value;
  }

  return fallback;
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

function resolveXTicks(series) {
  if (!Array.isArray(series) || series.length === 0) {
    return [];
  }

  if (series.length <= 2) {
    return [0, series.length - 1].filter(
      (index, idx, arr) => index >= 0 && arr.indexOf(index) === idx
    );
  }

  const last = series.length - 1;
  const ticks = [0, Math.round(last * 0.25), Math.round(last * 0.5), Math.round(last * 0.75), last];
  return ticks.filter((index, idx, arr) => arr.indexOf(index) === idx);
}

function resolveZoneForValue(zones, value) {
  if (!Array.isArray(zones) || !Number.isFinite(value)) {
    return null;
  }

  return (
    zones.find((zone) => {
      const min = Number.isFinite(zone.min) ? zone.min : -Infinity;
      const max = Number.isFinite(zone.max) ? zone.max : Infinity;
      return value >= min && value < max;
    }) || null
  );
}

function resolveVisibleZones(zones, minValue, maxValue, toY) {
  if (!Array.isArray(zones) || zones.length === 0) {
    return [];
  }

  return zones
    .map((zone, index) => {
      const zoneMin = Number.isFinite(zone.min) ? zone.min : -Infinity;
      const zoneMax = Number.isFinite(zone.max) ? zone.max : Infinity;

      const clippedMin = Math.max(zoneMin, minValue);
      const clippedMax = Math.min(zoneMax, maxValue);

      if (!Number.isFinite(clippedMin) || !Number.isFinite(clippedMax) || clippedMax <= clippedMin) {
        return null;
      }

      const yTop = toY(clippedMax);
      const yBottom = toY(clippedMin);

      return {
        id: `${zone.label}-${index}`,
        label: zone.label,
        color: zone.color,
        y: yTop,
        height: yBottom - yTop,
      };
    })
    .filter(Boolean);
}

export default function GraficoLineaBase({
  title,
  subtitle,
  series,
  unit,
  lineTone = "primary",
  emptyMessage,
  zones = [],
}) {
  const [activeIndex, setActiveIndex] = useState(null);

  const chartId = useId().replace(/:/g, "");
  const descId = `chart-desc-${chartId}`;
  const gradientId = `chart-line-gradient-${chartId}`;
  const areaGradientId = `chart-area-gradient-${chartId}`;
  const glowId = `chart-glow-${chartId}`;

  const safeTitle = String(title || "Serie");
  const theme = LINE_THEMES[lineTone] || LINE_THEMES.primary;

  const normalizedSeries = useMemo(
    () =>
      (Array.isArray(series) ? series : [])
        .map((point) => ({
          timestamp: point?.timestamp,
          value: Number(point?.value),
        }))
        .filter((point) => Number.isFinite(point.value)),
    [series]
  );

  const normalizedZones = useMemo(
    () =>
      (Array.isArray(zones) ? zones : [])
        .map((zone) => ({
          label: String(zone?.label || "Rango"),
          min: Number.isFinite(zone?.min) ? Number(zone.min) : -Infinity,
          max: Number.isFinite(zone?.max) ? Number(zone.max) : Infinity,
          color: sanitizeColor(zone?.color, "#cbd5e1"),
        }))
        .filter((zone) => zone.max > zone.min),
    [zones]
  );

  // Todos los useMemo deben declararse antes de cualquier return condicional
  // para cumplir con las reglas de hooks de React
  const values = useMemo(
    () => normalizedSeries.map((point) => point.value),
    [normalizedSeries]
  );
  const geometry = useMemo(() => buildChartGeometry(values), [values]);
  const points = geometry.points;
  const linePath = useMemo(() => toSmoothLinePath(points, 0.05), [points]);
  const areaPath = useMemo(() => toSmoothAreaPath(points, 0.05), [points]);

  const latestValue = values[values.length - 1];
  const minValue = geometry.minValue;
  const maxValue = geometry.maxValue;
  const previousValue = values.length > 1 ? values[values.length - 2] : NaN;
  const deltaValue = Number.isFinite(previousValue) ? latestValue - previousValue : NaN;

  const yTicks = useMemo(
    () => [maxValue, minValue + geometry.range * 0.66, minValue + geometry.range * 0.33, minValue],
    [geometry.range, maxValue, minValue]
  );
  const xTickIndexes = useMemo(() => resolveXTicks(normalizedSeries), [normalizedSeries]);
  const visibleZones = useMemo(
    () => resolveVisibleZones(normalizedZones, minValue, maxValue, geometry.toY),
    [normalizedZones, minValue, maxValue, geometry]
  );
  const currentZone = useMemo(
    () => resolveZoneForValue(normalizedZones, latestValue),
    [latestValue, normalizedZones]
  );

  const keyIndexes = useMemo(
    () =>
      new Set([
        values.indexOf(minValue),
        values.indexOf(maxValue),
        Math.max(values.length - 1, 0),
      ]),
    [maxValue, minValue, values]
  );

  const isEmpty = normalizedSeries.length === 0;

  if (isEmpty) {
    return (
      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <h3 className="mb-1 mt-0 text-lg font-semibold text-neutral-600 tracking-tight">{title}</h3>
        <p className="mb-6 mt-0 text-sm text-neutral-400">{subtitle}</p>
        <div className="my-4 flex h-40 items-center justify-center rounded-xl bg-neutral-100">
          <span className="text-sm text-neutral-400">{emptyMessage}</span>
        </div>
      </section>
    );
  }

  const firstTimestamp = normalizedSeries[0].timestamp;
  const lastTimestamp = normalizedSeries[normalizedSeries.length - 1].timestamp;

  const description = `Último ${formatMetric(latestValue, unit)}. Mínimo ${formatMetric(
    minValue,
    unit
  )}. Máximo ${formatMetric(maxValue, unit)}.`;

  const resolvedActiveIndex =
    activeIndex === null ? null : clamp(activeIndex, 0, Math.max(points.length - 1, 0));

  const activePoint = resolvedActiveIndex === null ? null : points[resolvedActiveIndex];
  const activeSeriesPoint =
    resolvedActiveIndex === null ? null : normalizedSeries[resolvedActiveIndex];
  const latestPoint = points[points.length - 1] || null;

  let activeTooltip = null;
  if (activePoint && activeSeriesPoint) {
    const tooltipWidth = 190;
    const tooltipHeight = 58;
    const desiredX = activePoint.x + 10;
    const desiredY = activePoint.y - tooltipHeight - 10;

    const zone = resolveZoneForValue(normalizedZones, activeSeriesPoint.value);

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
      zoneLabel: zone?.label || "Sin rango",
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
      setActiveIndex((previousIndex) =>
        previousIndex === nextIndex ? previousIndex : nextIndex
      );
    }
  }

  function handleKeyDown(event) {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
      return;
    }

    event.preventDefault();

    if (event.key === "ArrowRight") {
      const next =
        resolvedActiveIndex === null
          ? 0
          : clamp(resolvedActiveIndex + 1, 0, points.length - 1);
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
    <section className="rounded-2xl bg-white p-6 shadow-sm">
      <h3 className="mb-1 mt-0 text-lg font-semibold text-neutral-600 tracking-tight">{title}</h3>
      <p className="mb-4 mt-0 text-sm text-neutral-400">{subtitle}</p>

      {normalizedZones.length > 0 ? (
        <div className="mb-5 flex flex-wrap gap-2">
          {normalizedZones.map((zone) => (
            <span
              key={`${zone.label}-${zone.min}-${zone.max}`}
              className="inline-flex items-center gap-1.5 rounded-full bg-neutral-100 px-3 py-1.5 text-xs text-neutral-500"
            >
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ backgroundColor: zone.color }}
                aria-hidden="true"
              />
              {zone.label}
              <span className="text-neutral-400">· {formatZoneRange(zone, unit)}</span>
            </span>
          ))}
        </div>
      ) : null}

      <svg
        width="100%"
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
        role="img"
        aria-label={`Serie temporal de ${safeTitle.toLowerCase()}`}
        aria-describedby={descId}
        className="mb-4 overflow-hidden"
      >
        <desc id={descId}>{description}</desc>

        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={theme.lineStart} />
            <stop offset="100%" stopColor={theme.lineEnd} />
          </linearGradient>

          <linearGradient id={areaGradientId} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={theme.areaStart} stopOpacity="0.35" />
            <stop offset="100%" stopColor={theme.areaEnd} stopOpacity="0.05" />
          </linearGradient>

          <filter id={glowId} x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Bandas de referencia por zona */}
        {visibleZones.map((zone) => (
          <rect
            key={zone.id}
            x={CHART_PADDING.left}
            y={zone.y}
            width={geometry.innerWidth}
            height={zone.height}
            fill={zone.color}
            opacity="0.08"
          />
        ))}

        {/* Grilla horizontal */}
        {yTicks.map((tick, index) => {
          const y = geometry.toY(tick);

          return (
            <g key={`y-tick-${index}`}>
              <line
                x1={CHART_PADDING.left}
                y1={y}
                x2={CHART_WIDTH - CHART_PADDING.right}
                y2={y}
                stroke="#d4d4d8"
                strokeDasharray="4 4"
                strokeWidth="1"
              />
              <text
                x={CHART_PADDING.left - 10}
                y={y + 4}
                fill="#737373"
                textAnchor="end"
                fontSize="11"
                className="tabular-nums"
              >
                {formatMetric(tick, unit)}
              </text>
            </g>
          );
        })}

        {/* Grilla vertical (tick temporal) */}
        {xTickIndexes.map((index) => {
          const point = points[index];
          if (!point) return null;

          return (
            <line
              key={`x-grid-${index}`}
              x1={point.x}
              y1={CHART_PADDING.top}
              x2={point.x}
              y2={CHART_HEIGHT - CHART_PADDING.bottom}
              stroke="#e5e7eb"
              strokeDasharray="3 6"
              strokeWidth="0.9"
              opacity="0.55"
            />
          );
        })}

        {/* Ejes */}
        <line
          x1={CHART_PADDING.left}
          y1={CHART_HEIGHT - CHART_PADDING.bottom}
          x2={CHART_WIDTH - CHART_PADDING.right}
          y2={CHART_HEIGHT - CHART_PADDING.bottom}
          stroke="#a3a3a3"
          strokeWidth="1"
        />
        <line
          x1={CHART_PADDING.left}
          y1={CHART_PADDING.top}
          x2={CHART_PADDING.left}
          y2={CHART_HEIGHT - CHART_PADDING.bottom}
          stroke="#a3a3a3"
          strokeWidth="1"
        />

        {/* Área + línea principal */}
        <path d={areaPath} fill={`url(#${areaGradientId})`} />
        <path
          d={linePath}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter={`url(#${glowId})`}
        />

        {/* Marcadores clave */}
        {points.map((point, index) => {
          if (!keyIndexes.has(index)) {
            return null;
          }

          return (
            <circle
              key={`key-point-${index}`}
              cx={point.x}
              cy={point.y}
              r="3.2"
              fill="#ffffff"
              stroke={theme.accent}
              strokeWidth="2"
            />
          );
        })}

        {/* Punto actual con halo */}
        {latestPoint ? (
          <g pointerEvents="none">
            <circle cx={latestPoint.x} cy={latestPoint.y} r="7" fill={theme.lineEnd} opacity="0.18" />
            <circle cx={latestPoint.x} cy={latestPoint.y} r="4" fill={theme.lineEnd} stroke="#fff" strokeWidth="2" />
          </g>
        ) : null}

        {/* Capa de interacción */}
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

        {/* Crosshair */}
        {activePoint ? (
          <g pointerEvents="none">
            <line
              x1={activePoint.x}
              y1={CHART_PADDING.top}
              x2={activePoint.x}
              y2={CHART_HEIGHT - CHART_PADDING.bottom}
              stroke="#9ca3af"
              strokeWidth="1"
              strokeDasharray="4 3"
            />
            <circle cx={activePoint.x} cy={activePoint.y} r="4" fill={theme.accent} stroke="#ffffff" strokeWidth="2" />
          </g>
        ) : null}

        {/* Tooltip */}
        {activeTooltip ? (
          <g transform={`translate(${activeTooltip.x}, ${activeTooltip.y})`} pointerEvents="none">
            <rect width="190" height="58" rx="8" fill="#fafafa" stroke="#d4d4d8" strokeWidth="1" />
            <text x="10" y="17" fill="#525252" fontSize="11" className="tabular-nums">
              {activeTooltip.dateLabel}
            </text>
            <text x="10" y="35" fill={theme.accent} fontSize="13" fontWeight="700">
              {activeTooltip.valueLabel}
            </text>
            <text x="10" y="50" fill="#6b7280" fontSize="11">
              Estado: {activeTooltip.zoneLabel}
            </text>
          </g>
        ) : null}

        {/* Etiquetas de eje X */}
        {xTickIndexes.map((index) => {
          const point = points[index];
          const raw = normalizedSeries[index]?.timestamp;
          if (!point) return null;

          return (
            <text
              key={`x-label-${index}`}
              x={point.x}
              y={CHART_HEIGHT - CHART_PADDING.bottom + 18}
              fill="#737373"
              textAnchor="middle"
              fontSize="11"
              className="tabular-nums"
            >
              {raw ? formatAxisTime(raw) : ""}
            </text>
          );
        })}
      </svg>

      {/* Live region para lectores de pantalla */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {activeTooltip
          ? `${activeTooltip.dateLabel} — ${activeTooltip.valueLabel} — Estado: ${activeTooltip.zoneLabel}`
          : ""}
      </div>

      {/* Métricas resumen — layout flexible que no fuerza 5 columnas */}
      <div className="mb-4 flex flex-wrap gap-2">
        <div className="flex items-baseline gap-1.5 rounded-lg bg-neutral-100 px-3 py-2">
          <span className="text-[11px] font-medium uppercase text-neutral-400">Último</span>
          <strong className="metric-value text-sm font-semibold text-neutral-600">{formatMetric(latestValue, unit)}</strong>
        </div>

        <div className="flex items-baseline gap-1.5 rounded-lg bg-neutral-100 px-3 py-2">
          <span className="text-[11px] font-medium uppercase text-neutral-400">Δ</span>
          <strong className="metric-value text-sm font-semibold" style={{ color: theme.accent }}>
            {formatDelta(deltaValue, unit)}
          </strong>
        </div>

        <div className="flex items-baseline gap-1.5 rounded-lg bg-neutral-100 px-3 py-2">
          <span className="text-[11px] font-medium uppercase text-neutral-400">Mín</span>
          <strong className="metric-value text-sm font-semibold text-neutral-600">{formatMetric(minValue, unit)}</strong>
        </div>

        <div className="flex items-baseline gap-1.5 rounded-lg bg-neutral-100 px-3 py-2">
          <span className="text-[11px] font-medium uppercase text-neutral-400">Máx</span>
          <strong className="metric-value text-sm font-semibold text-neutral-600">{formatMetric(maxValue, unit)}</strong>
        </div>

        <div className="flex items-center gap-1.5 rounded-lg bg-neutral-100 px-3 py-2">
          <span
            className="inline-block h-2 w-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: currentZone?.color || theme.accent }}
            aria-hidden="true"
          />
          <span className="text-[11px] font-medium uppercase text-neutral-400">Estado</span>
          <strong className="text-sm font-semibold text-neutral-600">
            {currentZone?.label || "—"}
          </strong>
        </div>
      </div>

      {/* Rango temporal */}
      <div className="flex justify-between gap-2 border-t border-neutral-100 pt-3 text-xs tabular-nums text-neutral-400">
        <span className="truncate">{formatDate(firstTimestamp)}</span>
        <span className="truncate text-right">{formatDate(lastTimestamp)}</span>
      </div>
    </section>
  );
}
