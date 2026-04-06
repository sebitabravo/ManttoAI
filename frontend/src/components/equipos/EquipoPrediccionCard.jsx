import { formatProbability } from "../../utils/metrics";

export default function EquipoPrediccionCard({ prediccion }) {
  return (
    <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <h2 style={{ marginTop: 0 }}>Última predicción</h2>
      {prediccion ? (
        <div>
          <p style={{ marginBottom: 8 }}>Clasificación: {prediccion.clasificacion}</p>
          <strong>Probabilidad de falla: {formatProbability(prediccion.probabilidad)}</strong>
        </div>
      ) : (
        <p style={{ marginBottom: 0, color: "#6b7280" }}>
          Todavía no hay una predicción persistida para este equipo.
        </p>
      )}
    </section>
  );
}
