import { formatDate } from "../../utils/formatDate";
import { formatMetric, resolveMaxVibration } from "../../utils/metrics";

export default function EquipoLecturasSection({ lecturas }) {
  return (
    <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2 style={{ marginTop: 0 }}>Últimas lecturas</h2>
      {lecturas.length === 0 ? (
        <p style={{ marginBottom: 0, color: "#6b7280" }}>
          No hay lecturas registradas para este equipo.
        </p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <caption style={{ textAlign: "left", paddingBottom: 8, color: "#6b7280" }}>
            Últimas lecturas registradas del equipo ordenadas desde la más reciente.
          </caption>
          <thead>
            <tr>
              <th scope="col" align="left">Fecha</th>
              <th scope="col" align="left">Temperatura</th>
              <th scope="col" align="left">Humedad</th>
              <th scope="col" align="left">Vibración máx.</th>
            </tr>
          </thead>
          <tbody>
            {lecturas.map((lectura) => (
              <tr key={lectura.id || lectura.timestamp}>
                <td>{formatDate(lectura.timestamp)}</td>
                <td>{formatMetric(lectura.temperatura, "°C")}</td>
                <td>{formatMetric(lectura.humedad, "%")}</td>
                <td>{formatMetric(resolveMaxVibration(lectura), "g")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
