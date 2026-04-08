import GraficoLineaBase from "./GraficoLineaBase";
import { resolveMaxVibration } from "../../utils/metrics";
import { sortByTimestampAsc } from "../../utils/time";

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
      subtitle="Magnitud máxima por lectura (últimas 24 lecturas)"
      series={temporalSeries}
      unit="g"
      lineTone="primary"
      emptyMessage="Todavía no hay lecturas de vibración para graficar."
    />
  );
}
