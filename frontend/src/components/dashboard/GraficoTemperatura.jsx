import GraficoLineaBase from "./GraficoLineaBase";

function sortByTimestampAsc(lecturas) {
  return [...lecturas].sort((current, next) => {
    return new Date(current.timestamp).getTime() - new Date(next.timestamp).getTime();
  });
}

export default function GraficoTemperatura({ lecturas = [] }) {
  const temporalSeries = sortByTimestampAsc(lecturas)
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
      color="#ef4444"
      emptyMessage="Todavía no hay lecturas de temperatura para graficar."
    />
  );
}
