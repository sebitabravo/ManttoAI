import { formatDate } from "../../utils/formatDate";
import { formatMetric, resolveMaxVibration } from "../../utils/metrics";

/**
 * Tabla de últimas lecturas en el Dashboard.
 * 
 * Muestra las 10 lecturas más recientes con:
 * - Nombre del equipo
 * - Temperatura registrada
 * - Vibración máxima (max de x, y, z)
 * - Timestamp
 * 
 * Responsive: scroll horizontal en mobile
 */
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
    <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
      <h2 className="mb-4 mt-0 text-lg font-semibold text-neutral-800">Últimas lecturas</h2>
      
      {rows.length === 0 ? (
        <p className="mb-0 text-sm text-neutral-500">
          Aún no hay lecturas registradas para mostrar.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <caption className="sr-only">
              Lecturas más recientes recibidas desde los equipos monitoreados.
            </caption>
            <thead>
              <tr className="border-b border-neutral-300">
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Equipo
                </th>
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Temperatura
                </th>
                <th scope="col" className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Vibración máx.
                </th>
                <th scope="col" className="pb-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-600">
                  Fecha
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {rows.map((lectura) => (
                <tr key={lectura.id || `${lectura.equipo_id}-${lectura.timestamp}`} className="transition-colors duration-150 ease-out-quart hover:bg-neutral-50">
                  <td className="py-3 pr-4 text-sm font-medium text-neutral-800">
                    {resolveEquipoName(Number(lectura.equipo_id), equiposById)}
                  </td>
                  <td className="py-3 pr-4 tabular-nums text-sm text-neutral-700">
                    {formatMetric(Number(lectura.temperatura), "°C")}
                  </td>
                  <td className="py-3 pr-4 tabular-nums text-sm text-neutral-700">
                    {formatMetric(resolveMaxVibration(lectura), "g")}
                  </td>
                  <td className="py-3 tabular-nums text-sm text-neutral-600">
                    {formatDate(lectura.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
