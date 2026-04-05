import { useMemo } from "react";
import PropTypes from "prop-types";

import GraficoLineaBase from "./GraficoLineaBase";
import { compareByTimestampAsc } from "../../utils/formatDate";

export default function GraficoTemperatura({ lecturas = [] }) {
  const temporalSeries = useMemo(() => {
    return [...lecturas]
      .sort(compareByTimestampAsc)
      .slice(-24)
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

GraficoTemperatura.propTypes = {
  lecturas: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      temperatura: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ),
};
