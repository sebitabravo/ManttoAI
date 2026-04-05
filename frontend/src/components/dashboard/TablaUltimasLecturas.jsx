import { formatDate } from "../../utils/formatDate";

const lecturas = [
  { equipo: "Compresor principal", temperatura: "42.5 °C", fecha: new Date().toISOString() },
  { equipo: "Motor bomba", temperatura: "39.8 °C", fecha: new Date().toISOString() },
];

export default function TablaUltimasLecturas() {
  return (
    <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2>Últimas lecturas</h2>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th align="left">Equipo</th>
            <th align="left">Temperatura</th>
            <th align="left">Fecha</th>
          </tr>
        </thead>
        <tbody>
          {lecturas.map((lectura) => (
            <tr key={`${lectura.equipo}-${lectura.fecha}`}>
              <td>{lectura.equipo}</td>
              <td>{lectura.temperatura}</td>
              <td>{formatDate(lectura.fecha)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
