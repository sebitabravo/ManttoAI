import { useMemo } from "react";

import GraficoLineaBase from "./GraficoLineaBase";
import { resolveMaxVibration } from "../../utils/metrics";

export default function GraficoVibracion({ lecturas = [] }) {
  const temporalSeries = useMemo(() => {
    const recentLecturas = Array.isArray(lecturas) ? lecturas.slice(0, 24).reverse() : [];

    return recentLecturas
      .map((lectura) => ({
        timestamp: lectura.timestamp,
        value: resolveMaxVibration(lectura),
      }))
      .filter((point) => Number.isFinite(point.value));
  }, [lecturas]);

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
