import PropTypes from "prop-types";

import { formatDate } from "../../utils/formatDate";
import { formatMetric, resolveMaxVibration } from "../../utils/metrics";

function resolveEquipoName(equipoId, equiposById) {
  const resolvedName = equiposById.get(equipoId);
  if (resolvedName) {
    return resolvedName;
  }

  return `Equipo #${equipoId}`;
}

export default function TablaUltimasLecturas({ lecturas = [], equipos = [] }) {
  const equiposById = new Map(
    equipos.map((equipo) => [Number(equipo.id), equipo?.nombre ? String(equipo.nombre) : null])
  );

  const rows = lecturas.slice(0, 10);

  return (
    <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2>Últimas lecturas</h2>
      {rows.length === 0 ? (
        <p style={{ marginBottom: 0, color: "#6b7280" }}>
          Aún no hay lecturas registradas para mostrar.
        </p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th scope="col" align="left">Equipo</th>
              <th scope="col" align="left">Temperatura</th>
              <th scope="col" align="left">Vibración máx.</th>
              <th scope="col" align="left">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((lectura) => (
              <tr key={lectura.id || `${lectura.equipo_id}-${lectura.timestamp}`}>
                <td>{resolveEquipoName(Number(lectura.equipo_id), equiposById)}</td>
                <td>{formatMetric(Number(lectura.temperatura), "°C")}</td>
                <td>{formatMetric(resolveMaxVibration(lectura), "g")}</td>
                <td>{formatDate(lectura.timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

TablaUltimasLecturas.propTypes = {
  lecturas: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      equipo_id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      temperatura: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      vib_x: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      vib_y: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      vib_z: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      timestamp: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ),
  equipos: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
      nombre: PropTypes.string,
    })
  ),
};
