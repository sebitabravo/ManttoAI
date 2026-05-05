import { formatMetric, formatProbability } from "../../utils/metrics";
import { getRubroBadgeClass, getRubroLabel } from "../../utils/rubro";

/**
 * Tabla de estado de equipos — Estilo Apple.
 * 
 * Características Apple:
 * - Card blanca sin bordes pesados
 * - Tipografía limpia
 * - Hover sutil en filas
 * - Badges minimalistas
 */

function resolveTelemetryStatus(equipo) {
  const hasTemperature = Number.isFinite(Number(equipo?.ultima_temperatura));
  return hasTemperature ? "Activa" : "Sin datos";
}

export default function TablaEstadoEquipos({ equipos = [] }) {
  const rows = Array.isArray(equipos) ? equipos : [];

  return (
    <section className="rounded-2xl bg-white p-6 shadow-sm">
      {rows.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-neutral-400">
            Aún no hay equipos con telemetría para mostrar.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto -mx-6 px-6 pb-1">
          <table aria-label="Estado de telemetría por equipo" className="w-full min-w-[560px]">
            <caption className="sr-only">
              Estado de telemetría y alertas activas por equipo.
            </caption>
            <thead>
              <tr className="border-b border-neutral-100">
                <th scope="col" className="whitespace-nowrap pb-4 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  ID
                </th>
                <th scope="col" className="whitespace-nowrap pb-4 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  Equipo
                </th>
                <th scope="col" className="whitespace-nowrap pb-4 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  Rubro
                </th>
                <th scope="col" className="whitespace-nowrap pb-4 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  Temp.
                </th>
                <th scope="col" className="whitespace-nowrap pb-4 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  Prob.
                </th>
                <th scope="col" className="whitespace-nowrap pb-4 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  Alertas
                </th>
                <th scope="col" className="whitespace-nowrap pb-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  Estado
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {rows.map((equipo) => {
                const telemetryStatus = resolveTelemetryStatus(equipo);
                const alertCount = Number(equipo.alertas_activas || 0);
                const hasAlerts = alertCount > 0;

                return (
                  <tr 
                    key={equipo.id} 
                    className="transition-colors duration-200 hover:bg-neutral-50"
                  >
                    <td className="py-4 pr-6 tabular-nums text-sm text-neutral-500">
                      {equipo.id}
                    </td>
                    <td className="py-4 pr-6 text-sm font-medium text-neutral-600">
                      {equipo.nombre || `Equipo ${equipo.id}`}
                    </td>
                    <td className="py-4 pr-6 text-sm text-neutral-600">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getRubroBadgeClass(equipo.rubro)}`}>
                        {getRubroLabel(equipo.rubro)}
                      </span>
                    </td>
                    <td className="py-4 pr-6 tabular-nums text-sm text-neutral-600">
                      {formatMetric(equipo.ultima_temperatura, "°C", "—")}
                    </td>
                    <td className="py-4 pr-6 tabular-nums text-sm text-neutral-600">
                      {formatProbability(equipo.ultima_probabilidad, "—")}
                    </td>
                    <td className="py-4 pr-6">
                      <span 
                        className={`
                          inline-flex items-center justify-center
                          min-w-[28px] h-7 px-2.5
                          rounded-full text-xs font-semibold tabular-nums
                          ${hasAlerts 
                            ? "bg-danger-50 text-danger-600" 
                            : "bg-neutral-100 text-neutral-500"
                          }
                        `.replace(/\s+/g, " ").trim()}
                      >
                        {alertCount}
                      </span>
                    </td>
                    <td className="py-4">
                      <span 
                        aria-label={`Estado: ${telemetryStatus.toLowerCase()}`}
                        className={`
                          inline-flex items-center gap-1.5
                          px-2.5 py-1 rounded-full
                          text-xs font-medium
                          ${telemetryStatus === "Activa"
                            ? "bg-success-50 text-success-600"
                            : "bg-neutral-100 text-neutral-500"
                          }
                        `.replace(/\s+/g, " ").trim()}
                      >
                        {telemetryStatus === "Activa" && (
                          <span className="h-1.5 w-1.5 rounded-full bg-success-500" aria-hidden="true" />
                        )}
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
