export default function EquipoResumenCard({ equipo }) {
  if (!equipo) {
    return null;
  }

  return (
    <article style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2 style={{ marginTop: 0 }}>{equipo.nombre}</h2>
      <p>Estado: {equipo.estado}</p>
      <p>Ubicación: {equipo.ubicacion}</p>
      <p>Tipo: {equipo.tipo}</p>
    </article>
  );
}
