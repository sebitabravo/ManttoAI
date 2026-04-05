import { useMemo } from "react";
import PropTypes from "prop-types";

import GraficoLineaBase from "./GraficoLineaBase";
import { compareByTimestampAsc } from "../../utils/formatDate";
import { resolveMaxVibration } from "../../utils/metrics";

export default function GraficoVibracion({ lecturas = [] }) {
  const temporalSeries = useMemo(() => {
    return [...lecturas]
      .sort(compareByTimestampAsc)
      .slice(-24)
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

GraficoVibracion.propTypes = {
  lecturas: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      vib_x: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      vib_y: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      vib_z: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ),
};
