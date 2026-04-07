export default function EquipoResumenCard({ equipo }) {
  if (!equipo) {
    return null;
  }

  return (
    <article className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
      <h2 className="mt-0 text-lg font-semibold text-neutral-900">{equipo.nombre}</h2>
      <p className="text-sm text-neutral-700">Estado: <span className="font-medium">{equipo.estado}</span></p>
      <p className="text-sm text-neutral-700">Ubicación: <span className="font-medium">{equipo.ubicacion}</span></p>
      <p className="text-sm text-neutral-700">Tipo: <span className="font-medium">{equipo.tipo}</span></p>
    </article>
  );
}
