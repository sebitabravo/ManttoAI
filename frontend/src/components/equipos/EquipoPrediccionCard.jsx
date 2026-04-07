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
        className="h-full rounded-full transition-all duration-300"
        style={{
          width: `${porcentaje}%`,
          background: config.color,
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
      className="rounded-lg border p-4 transition-all duration-150 ease-out-quart"
      style={{
        borderColor: prediccion ? config.borderColor : 'oklch(92% 0.008 250)', // neutral-200
        background: prediccion ? config.bgColor : 'oklch(96% 0.005 250)', // neutral-100
      }}
    >
      <h2 className="mb-3 mt-0 text-lg font-semibold text-neutral-900">Última predicción</h2>

      {prediccion ? (
        <div className="flex flex-col gap-3">
          {/* Clasificación con ícono semántico */}
          <div className="flex items-center gap-2">
            <span className="text-2xl" aria-hidden="true">
              {config.emoji}
            </span>
            <span
              className="text-lg font-bold"
              style={{ color: config.color }}
            >
              {config.label}
            </span>
          </div>

          {/* Barra de riesgo */}
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-xs text-neutral-700">
              <span>Probabilidad de falla</span>
              <strong className="tabular-nums" style={{ color: config.color }}>
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
