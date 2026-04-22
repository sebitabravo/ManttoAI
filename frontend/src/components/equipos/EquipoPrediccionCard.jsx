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
      className="h-2.5 w-full overflow-hidden rounded-full bg-neutral-200"
    >
      <div
        className={`h-full rounded-full transition-all duration-300 ease-out-quart ${config.barClass}`}
        style={{
          width: `${porcentaje}%`,
        }}
      />
    </div>
  );
}

export default function EquipoPrediccionCard({ prediccion }) {
  // Configuración visual según clasificación del modelo
  const config = getConfigPrediccion(prediccion?.clasificacion);
  const cardToneClass = prediccion ? config.surfaceClass : "bg-white";

  return (
    // Comentario: Tarjeta de predicción al estilo Apple — sin borde exterior, fondo blanco y sombra sutil
    <section
      className={`rounded-2xl bg-white p-4 transition-all duration-150 ease-out-quart shadow-sm ${cardToneClass}`}
    >
      <h2 className="mb-3 mt-0 text-lg font-semibold text-neutral-900">Última predicción</h2>

      {prediccion ? (
        <div className="flex flex-col gap-3">
          {/* Clasificación semántica */}
          <div className="flex items-center gap-2">
            <span aria-hidden="true" className={`h-2.5 w-2.5 rounded-full ${config.dotClass}`} />
            <span className={`text-lg font-semibold ${config.textClass}`}>
              {config.label}
            </span>
          </div>

          {/* Barra de riesgo */}
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-xs text-neutral-700">
              <span>Probabilidad de falla</span>
              <strong className={`tabular-nums ${config.textClass}`}>
                {formatPorcentajeRiesgo(prediccion.probabilidad)}
              </strong>
            </div>
            <BarraRiesgo probabilidad={prediccion.probabilidad} config={config} />
          </div>

          {/* Clasificación raw del modelo (referencia técnica) */}
          <p className="m-0 text-xs text-neutral-600">
            Clasificación del modelo:{" "}
            <code className="font-mono">{prediccion.clasificacion}</code>
          </p>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-neutral-600">
          <span aria-hidden="true">—</span>
          <p className="m-0 text-sm">
            Todavía no hay una predicción persistida para este equipo.
          </p>
        </div>
      )}
    </section>
  );
}
