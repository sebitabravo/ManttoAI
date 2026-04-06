import { getConfigPrediccion, formatPorcentajeRiesgo } from "../../utils/prediccion";

/**
 * Barra de progreso que representa visualmente la probabilidad de falla.
 * El color cambia según la severidad de la clasificación.
 */
function BarraRiesgo({ probabilidad, config }) {
  const porcentaje = Number.isFinite(Number(probabilidad))
    ? Math.min(Math.max(Number(probabilidad) * 100, 0), 100)
    : 0;

  // aria-valuetext combina porcentaje y clasificación para lectores de pantalla
  const textoAccesible = `${formatPorcentajeRiesgo(probabilidad)} — ${config.label}`;

  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(porcentaje)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="Probabilidad de falla"
      aria-valuetext={textoAccesible}
      style={{
        width: "100%",
        height: 10,
        borderRadius: 9999,
        background: "#e5e7eb",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${porcentaje}%`,
          height: "100%",
          background: config.color,
          borderRadius: 9999,
          transition: "width 0.4s ease",
        }}
      />
    </div>
  );
}

export default function EquipoPrediccionCard({ prediccion }) {
  // Configuración visual según clasificación del modelo
  const config = getConfigPrediccion(prediccion?.clasificacion);

  return (
    <section
      style={{
        padding: 16,
        border: `1px solid ${prediccion ? config.borderColor : "#e5e7eb"}`,
        borderRadius: 16,
        background: prediccion ? config.bgColor : "#ffffff",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: 12 }}>Última predicción</h2>

      {prediccion ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {/* Clasificación con ícono semántico */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 24 }} aria-hidden="true">
              {config.emoji}
            </span>
            <span
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: config.color,
              }}
            >
              {config.label}
            </span>
          </div>

          {/* Barra de riesgo */}
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, color: "#374151" }}>
              <span>Probabilidad de falla</span>
              <strong style={{ color: config.color }}>
                {formatPorcentajeRiesgo(prediccion.probabilidad)}
              </strong>
            </div>
            <BarraRiesgo probabilidad={prediccion.probabilidad} config={config} />
          </div>

          {/* Clasificación raw del modelo (referencia técnica) */}
          <p style={{ margin: 0, fontSize: 12, color: "#6b7280" }}>
            Clasificación del modelo:{" "}
            <code style={{ fontFamily: "monospace" }}>{prediccion.clasificacion}</code>
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#6b7280" }}>
          <span aria-hidden="true">—</span>
          <p style={{ margin: 0 }}>
            Todavía no hay una predicción persistida para este equipo.
          </p>
        </div>
      )}
    </section>
  );
}
