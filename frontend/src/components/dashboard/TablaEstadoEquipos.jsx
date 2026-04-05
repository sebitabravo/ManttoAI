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

  return `${(parsed * 100).toFixed(1)} %`;
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
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th align="left">ID</th>
              <th align="left">Equipo</th>
              <th align="left">Última temperatura</th>
              <th align="left">Última probabilidad</th>
              <th align="left">Alertas activas</th>
              <th align="left">Telemetría</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((equipo) => (
              <tr key={equipo.id}>
                <td>{equipo.id}</td>
                <td>{equipo.nombre}</td>
                <td>{formatTemperature(equipo.ultima_temperatura)}</td>
                <td>{formatProbability(equipo.ultima_probabilidad)}</td>
                <td>{Number(equipo.alertas_activas || 0)}</td>
                <td>{resolveTelemetryStatus(equipo)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
