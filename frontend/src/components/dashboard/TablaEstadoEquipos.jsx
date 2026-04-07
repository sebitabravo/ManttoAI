import { formatMetric, formatProbability } from "../../utils/metrics";

/**
 * Tabla de estado de equipos en el Dashboard.
 * 
 * Muestra:
 * - ID y nombre del equipo
 * - Última temperatura registrada
 * - Última probabilidad de falla
 * - Cantidad de alertas activas
 * - Estado de telemetría (Activa / Sin datos)
 * 
 * Responsive:
 * - Desktop: tabla completa
 * - Mobile: scroll horizontal (tabla densa con datos críticos)
 */
function resolveTelemetryStatus(equipo) {
  const hasTemperature = Number.isFinite(Number(equipo?.ultima_temperatura));
  return hasTemperature ? "Activa" : "Sin datos";
}

export default function TablaEstadoEquipos({ equipos = [] }) {
  const rows = Array.isArray(equipos) ? equipos : [];

  return (
    <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
      <h2 className="mb-4 mt-0 text-lg font-semibold text-neutral-800">Estado por equipo</h2>
      
      {rows.length === 0 ? (
        <p className="mb-0 text-sm text-neutral-500">
          Aún no hay equipos con telemetría para mostrar.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table aria-label="Estado de telemetría por equipo" className="w-full border-collapse">
            <caption className="sr-only">
              Estado de telemetría y alertas activas por equipo.
            </caption>
            <thead>
              <tr className="border-b border-neutral-300">
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  ID
                </th>
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Equipo
                </th>
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Última temperatura
                </th>
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Última probabilidad
                </th>
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Alertas activas
                </th>
                <th scope="col" className="pb-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Telemetría
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {rows.map((equipo) => {
                const telemetryStatus = resolveTelemetryStatus(equipo);
                const hasAlerts = Number(equipo.alertas_activas || 0) > 0;

                return (
                  <tr key={equipo.id} className="transition-colors duration-150 hover:bg-neutral-50">
                    <td className="py-3 pr-4 tabular-nums text-sm text-neutral-700">
                      {equipo.id}
                    </td>
                    <td className="py-3 pr-4 text-sm font-medium text-neutral-800">
                      {equipo.nombre || `Equipo ${equipo.id}`}
                    </td>
                    <td className="py-3 pr-4 tabular-nums text-sm text-neutral-700">
                      {formatMetric(equipo.ultima_temperatura, "°C", "Sin lecturas")}
                    </td>
                    <td className="py-3 pr-4 tabular-nums text-sm text-neutral-700">
                      {formatProbability(equipo.ultima_probabilidad, "Sin predicción")}
                    </td>
                    <td className={`py-3 pr-4 tabular-nums text-sm font-semibold ${hasAlerts ? "text-danger-600" : "text-neutral-600"}`}>
                      {Number(equipo.alertas_activas || 0)}
                    </td>
                    <td className="py-3 text-sm">
                      <span 
                        role="status" 
                        aria-live="polite" 
                        aria-label={`Telemetría ${telemetryStatus.toLowerCase()}`}
                        className={`rounded-sm px-2 py-1 text-xs font-medium ${
                          telemetryStatus === "Activa"
                            ? "bg-success-50 text-success-700"
                            : "bg-neutral-200 text-neutral-600"
                        }`}
                      >
                        {telemetryStatus}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
