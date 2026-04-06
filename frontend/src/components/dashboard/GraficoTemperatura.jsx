import { useMemo } from "react";

import GraficoLineaBase from "./GraficoLineaBase";

export default function GraficoTemperatura({ lecturas = [] }) {
  const temporalSeries = useMemo(() => {
    const recentLecturas = Array.isArray(lecturas) ? lecturas.slice(0, 24).reverse() : [];

    return recentLecturas
      .map((lectura) => ({
        timestamp: lectura.timestamp,
        value: Number(lectura.temperatura),
      }))
      .filter((point) => Number.isFinite(point.value));
  }, [lecturas]);

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
