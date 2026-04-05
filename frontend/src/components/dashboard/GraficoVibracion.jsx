import GraficoLineaBase from "./GraficoLineaBase";

function sortByTimestampAsc(lecturas) {
  return [...lecturas].sort((current, next) => {
    return new Date(current.timestamp).getTime() - new Date(next.timestamp).getTime();
  });
}

function resolveVibrationMagnitude(lectura) {
  return Math.max(
    Math.abs(Number(lectura.vib_x) || 0),
    Math.abs(Number(lectura.vib_y) || 0),
    Math.abs(Number(lectura.vib_z) || 0)
  );
}

export default function GraficoVibracion({ lecturas = [] }) {
  const temporalSeries = sortByTimestampAsc(lecturas)
    .slice(-24)
    .map((lectura) => ({
      timestamp: lectura.timestamp,
      value: resolveVibrationMagnitude(lectura),
    }))
    .filter((point) => Number.isFinite(point.value));

  return (
    <GraficoLineaBase
      title="Vibración"
      subtitle="Magnitud máxima por lectura (últimas 24 lecturas)"
      series={temporalSeries}
      unit="g"
      color="#2563eb"
      emptyMessage="Todavía no hay lecturas de vibración para graficar."
    />
  );
}
