import { formatDate } from "../../utils/formatDate";
import { formatMetric, resolveMaxVibration } from "../../utils/metrics";

export default function EquipoLecturasSection({ lecturas }) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4">
      <h2 className="mt-0 text-lg font-semibold text-neutral-900">Últimas lecturas</h2>
      {lecturas.length === 0 ? (
        <p className="mb-0 text-sm text-neutral-600">
          No hay lecturas registradas para este equipo.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <caption className="pb-2 text-left text-sm text-neutral-600">
              Últimas lecturas registradas del equipo ordenadas desde la más reciente.
            </caption>
            <thead>
              <tr className="border-b border-neutral-200">
                <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Fecha</th>
                <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Temperatura</th>
                <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Humedad</th>
                <th scope="col" className="pb-2 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Vibración máx.</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {lecturas.map((lectura) => (
                <tr key={lectura.id || lectura.timestamp} className="hover:bg-neutral-50 transition-colors duration-150">
                  <td className="py-2 pr-4 text-sm text-neutral-600">{formatDate(lectura.timestamp)}</td>
                  <td className="py-2 pr-4 text-sm tabular-nums text-neutral-900">{formatMetric(lectura.temperatura, "°C")}</td>
                  <td className="py-2 pr-4 text-sm tabular-nums text-neutral-900">{formatMetric(lectura.humedad, "%")}</td>
                  <td className="py-2 text-sm tabular-nums text-neutral-900">{formatMetric(resolveMaxVibration(lectura), "g")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
