export default function EquipoResumenCard({ equipo }) {
  if (!equipo) {
    return null;
  }

  return (
    <article className="grid grid-cols-1 gap-3 rounded-lg border border-neutral-300 bg-neutral-100 p-4 shadow-sm">
      <h2 className="m-0 text-lg font-semibold text-neutral-900">{equipo.nombre}</h2>
      <dl className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">Estado</dt>
          <dd className="text-sm font-medium text-neutral-700">{equipo.estado}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">Ubicación</dt>
          <dd className="text-sm font-medium text-neutral-700">{equipo.ubicacion}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">Tipo</dt>
          <dd className="text-sm font-medium text-neutral-700">{equipo.tipo}</dd>
        </div>
      </dl>
    </article>
  );
}
