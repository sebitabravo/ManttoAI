import GraficoLineaBase from "./GraficoLineaBase";
import { sortByTimestampAsc } from "../../utils/time";

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
      subtitle="Serie temporal base (últimas 24 lecturas)"
      series={temporalSeries}
      unit="°C"
      color="oklch(0.61 0.20 27.33)" // danger-500 - warm red for temperature
      emptyMessage="Todavía no hay lecturas de temperatura para graficar."
    />
  );
}
