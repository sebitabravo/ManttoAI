import PropTypes from "prop-types";

function formatTemperature(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return "Sin lecturas";
  }

  return `${parsed.toFixed(2)} °C`;
}

function formatProbability(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return "Sin predicción";
  }

  const normalized = parsed > 1 ? Math.min(parsed / 100, 1) : parsed;
  const clamped = Math.min(Math.max(normalized, 0), 1);
  return `${(clamped * 100).toFixed(1)} %`;
}

function resolveTelemetryStatus(equipo) {
  const hasTemperature = Number.isFinite(Number(equipo?.ultima_temperatura));
  return hasTemperature ? "Activa" : "Sin datos";
}

export default function TablaEstadoEquipos({ equipos = [] }) {
  const rows = Array.isArray(equipos) ? equipos : [];

  return (
    <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2 style={{ marginTop: 0 }}>Estado por equipo</h2>
      {rows.length === 0 ? (
        <p style={{ marginBottom: 0, color: "#6b7280" }}>
          Aún no hay equipos con telemetría para mostrar.
        </p>
      ) : (
        <table aria-label="Estado de telemetría por equipo" style={{ width: "100%", borderCollapse: "collapse" }}>
          <caption style={{ captionSide: "top", textAlign: "left", paddingBottom: 8, color: "#6b7280" }}>
            Estado de telemetría y alertas activas por equipo.
          </caption>
          <thead>
            <tr>
              <th scope="col" align="left">ID</th>
              <th scope="col" align="left">Equipo</th>
              <th scope="col" align="left">Última temperatura</th>
              <th scope="col" align="left">Última probabilidad</th>
              <th scope="col" align="left">Alertas activas</th>
              <th scope="col" align="left">Telemetría</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((equipo) => {
              const telemetryStatus = resolveTelemetryStatus(equipo);

              return (
                <tr key={equipo.id}>
                  <td>{equipo.id}</td>
                  <td>{equipo.nombre || `Equipo ${equipo.id}`}</td>
                  <td>{formatTemperature(equipo.ultima_temperatura)}</td>
                  <td>{formatProbability(equipo.ultima_probabilidad)}</td>
                  <td>{Number(equipo.alertas_activas || 0)}</td>
                  <td>
                    <span role="status" aria-live="polite" aria-label={`Telemetría ${telemetryStatus.toLowerCase()}`}>
                      {telemetryStatus}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}

TablaEstadoEquipos.propTypes = {
  equipos: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
      nombre: PropTypes.string,
      ultima_temperatura: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      ultima_probabilidad: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      alertas_activas: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    })
  ),
};
