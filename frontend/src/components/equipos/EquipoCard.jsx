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
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "2px 10px",
        borderRadius: 9999,
        fontSize: 12,
        fontWeight: 600,
        // Texto oscuro fijo para garantizar contraste WCAG AA sobre cualquier bgColor
        color: "#1f2937",
        background: config.bgColor,
        border: `1px solid ${config.borderColor}`,
      }}
      title={probabilidad != null ? `Probabilidad de falla: ${formatPorcentajeRiesgo(probabilidad)}` : undefined}
    >
      {/* El ícono mantiene el color semántico de riesgo */}
      <span aria-hidden="true" style={{ color: config.color }}>{config.emoji}</span>
      {config.label}
      {probabilidad != null && (
        <span style={{ fontWeight: 400, opacity: 0.75 }}>
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
    <article
      style={{
        padding: 16,
        border: "1px solid #e5e7eb",
        borderRadius: 16,
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: 4 }}>{equipo.nombre}</h2>

      {/* Indicador visual de predicción */}
      <PrediccionBadge clasificacion={clasificacion} probabilidad={probabilidad} />

      <p style={{ margin: 0 }}>Estado: {equipo.estado}</p>
      {equipo.tipo ? <p style={{ margin: 0 }}>Tipo: {equipo.tipo}</p> : null}
      {equipo.ubicacion ? <p style={{ margin: 0 }}>Ubicación: {equipo.ubicacion}</p> : null}
      <p style={{ margin: 0 }}>Último dato: {latestValueLabel}</p>
      {typeof equipo.alertas_activas === "number" ? (
        <p style={{ margin: 0 }}>Alertas activas: {equipo.alertas_activas}</p>
      ) : null}

      <Link
        to={`/equipos/${equipo.id}`}
        aria-label={`Ver detalle ${equipo.nombre}`}
        style={{ marginTop: 4 }}
      >
        Ver detalle
      </Link>
    </article>
  );
}
