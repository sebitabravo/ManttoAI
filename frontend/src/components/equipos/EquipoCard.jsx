import { Link } from "react-router-dom";
import { getConfigPrediccion, formatPorcentajeRiesgo } from "../../utils/prediccion";

/**
 * Badge visual que muestra el estado de predicción del equipo.
 * Usa colores semánticos según la clasificación del modelo ML.
 */
function PrediccionBadge({ clasificacion, probabilidad }) {
  const config = getConfigPrediccion(clasificacion);

  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold text-neutral-900"
      style={{
        background: config.bgColor,
        borderColor: config.borderColor,
      }}
      title={probabilidad != null ? `Probabilidad de falla: ${formatPorcentajeRiesgo(probabilidad)}` : undefined}
    >
      {/* El ícono mantiene el color semántico de riesgo */}
      <span aria-hidden="true" style={{ color: config.color }}>{config.emoji}</span>
      {config.label}
      {probabilidad != null && (
        <span className="font-normal opacity-75">
          {" "}· {formatPorcentajeRiesgo(probabilidad)}
        </span>
      )}
    </span>
  );
}

export default function EquipoCard({ equipo }) {
  const latestValueLabel = equipo.dato || "Sin lecturas registradas";

  // Datos de predicción enriquecidos desde EquiposPage
  const clasificacion = equipo.ultima_clasificacion ?? null;
  const probabilidad = equipo.ultima_probabilidad ?? null;

  return (
    <article className="flex flex-col gap-2 rounded-lg border border-neutral-200 bg-neutral-100 p-4 transition-shadow duration-150 ease-out-quart hover:shadow-md">
      <h2 className="mb-1 mt-0 text-base font-semibold text-neutral-900">{equipo.nombre}</h2>

      {/* Indicador visual de predicción */}
      <PrediccionBadge clasificacion={clasificacion} probabilidad={probabilidad} />

      <p className="m-0 text-sm text-neutral-700">Estado: {equipo.estado}</p>
      {equipo.tipo ? <p className="m-0 text-sm text-neutral-700">Tipo: {equipo.tipo}</p> : null}
      {equipo.ubicacion ? <p className="m-0 text-sm text-neutral-700">Ubicación: {equipo.ubicacion}</p> : null}
      <p className="m-0 text-sm text-neutral-700">Último dato: <span className="tabular-nums">{latestValueLabel}</span></p>
      {typeof equipo.alertas_activas === "number" ? (
        <p className="m-0 text-sm text-neutral-700">Alertas activas: <span className="tabular-nums font-semibold text-danger-600">{equipo.alertas_activas}</span></p>
      ) : null}

      <Link
        to={`/equipos/${equipo.id}`}
        aria-label={`Ver detalle ${equipo.nombre}`}
        className="mt-1 text-sm font-medium text-primary-600 transition-colors duration-150 hover:text-primary-700 hover:underline"
      >
        Ver detalle
      </Link>
    </article>
  );
}
