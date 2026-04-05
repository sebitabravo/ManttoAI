import { formatDate } from "../../utils/formatDate";

function resolveEquipoName(equipoId, equiposById) {
  const resolvedName = equiposById.get(equipoId);
  if (resolvedName) {
    return resolvedName;
  }

  return `Equipo #${equipoId}`;
}

function resolveMaxVibration(lectura) {
  return Math.max(
    Math.abs(Number(lectura.vib_x) || 0),
    Math.abs(Number(lectura.vib_y) || 0),
    Math.abs(Number(lectura.vib_z) || 0)
  );
}

function formatMetric(value, unit) {
  if (!Number.isFinite(value)) {
    return "—";
  }

  return `${value.toFixed(2)} ${unit}`;
}

export default function TablaUltimasLecturas({ lecturas = [], equipos = [] }) {
  const equiposById = new Map(
    equipos.map((equipo) => [
      Number(equipo.id),
      String(equipo.nombre),
    ])
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
              <th align="left">Equipo</th>
              <th align="left">Temperatura</th>
              <th align="left">Vibración máx.</th>
              <th align="left">Fecha</th>
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
