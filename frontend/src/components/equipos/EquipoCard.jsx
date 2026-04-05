import { Link } from "react-router-dom";

export default function EquipoCard({ equipo }) {
  const latestValueLabel = equipo.dato || "Sin lecturas registradas";

  return (
    <article style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2 style={{ marginTop: 0 }}>{equipo.nombre}</h2>
      <p>Estado: {equipo.estado}</p>
      {equipo.tipo ? <p>Tipo: {equipo.tipo}</p> : null}
      {equipo.ubicacion ? <p>Ubicación: {equipo.ubicacion}</p> : null}
      <p>Último dato: {latestValueLabel}</p>
      {typeof equipo.alertas_activas === "number" ? <p>Alertas activas: {equipo.alertas_activas}</p> : null}
      <Link to={`/equipos/${equipo.id}`} aria-label={`Ver detalle ${equipo.nombre}`}>
        Ver detalle
      </Link>
    </article>
  );
}
