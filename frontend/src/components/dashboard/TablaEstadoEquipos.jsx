import { formatMetric, formatProbability } from "../../utils/metrics";

function resolveTelemetryStatus(equipo) {
  const hasTemperature = Number.isFinite(Number(equipo?.ultima_temperatura));
  return hasTemperature ? "Activa" : "Sin datos";
}

export default function TablaEstadoEquipos({ equipos = [] }) {
  const rows = Array.isArray(equipos) ? equipos : [];

  return (
    <section className="rounded-2xl border border-gray-200 p-4">
      <h2 className="mt-0">Estado por equipo</h2>
      {rows.length === 0 ? (
        <p className="mb-0 text-gray-500">
          Aún no hay equipos con telemetría para mostrar.
        </p>
      ) : (
        <table aria-label="Estado de telemetría por equipo" className="w-full border-collapse">
          <caption className="caption-top pb-2 text-left text-gray-500">
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
                  <td>{formatMetric(equipo.ultima_temperatura, "°C", "Sin lecturas")}</td>
                  <td>{formatProbability(equipo.ultima_probabilidad, "Sin predicción")}</td>
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
