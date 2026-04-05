import { Link } from "react-router-dom";

export default function EquipoCard({ equipo }) {
  return (
    <article style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2 style={{ marginTop: 0 }}>{equipo.nombre}</h2>
      <p>Estado: {equipo.estado}</p>
      <p>Último dato: {equipo.dato}</p>
      <Link to={`/equipos/${equipo.id}`}>Ver detalle</Link>
    </article>
  );
}
