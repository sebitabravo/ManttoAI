import GraficoLineaBase from "./GraficoLineaBase";
import { sortByTimestampAsc } from "../../utils/time";

const TEMPERATURA_ZONES = [
  { label: "Óptima", min: -Infinity, max: 40, color: "#22c55e" },
  { label: "Atención", min: 40, max: 55, color: "#f59e0b" },
  { label: "Crítica", min: 55, max: Infinity, color: "#ef4444" },
];

export default function GraficoTemperatura({ lecturas = [] }) {
  const temporalSeries = sortByTimestampAsc(Array.isArray(lecturas) ? lecturas : [])
    .slice(-24)
    .map((lectura) => ({
      timestamp: lectura.timestamp,
      value: Number(lectura.temperatura),
    }))
    .filter((point) => Number.isFinite(point.value));

  return (
    <GraficoLineaBase
      title="Temperatura"
      subtitle="Tendencia térmica operativa (últimas 24 lecturas)"
      series={temporalSeries}
      unit="°C"
      lineTone="danger"
      zones={TEMPERATURA_ZONES}
      emptyMessage="Todavía no hay lecturas de temperatura para graficar."
    />
  );
}
