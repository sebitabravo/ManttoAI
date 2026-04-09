import GraficoLineaBase from "./GraficoLineaBase";
import { resolveMaxVibration } from "../../utils/metrics";
import { sortByTimestampAsc } from "../../utils/time";

const VIBRACION_ZONES = [
  { label: "Estable", min: -Infinity, max: 3, color: "#22c55e" },
  { label: "Sensibilidad", min: 3, max: 6, color: "#f59e0b" },
  { label: "Riesgo mecánico", min: 6, max: Infinity, color: "#ef4444" },
];

export default function GraficoVibracion({ lecturas = [] }) {
  const temporalSeries = sortByTimestampAsc(Array.isArray(lecturas) ? lecturas : [])
    .slice(-24)
    .map((lectura) => ({
      timestamp: lectura.timestamp,
      value: resolveMaxVibration(lectura),
    }))
    .filter((point) => Number.isFinite(point.value));

  return (
    <GraficoLineaBase
      title="Vibración"
      subtitle="Magnitud vibracional máxima por lectura (últimas 24 lecturas)"
      series={temporalSeries}
      unit="g"
      lineTone="primary"
      zones={VIBRACION_ZONES}
      emptyMessage="Todavía no hay lecturas de vibración para graficar."
    />
  );
}
