import { Link } from "react-router-dom";

import { formatProbability } from "../../utils/metrics";
import { getConfigPrediccion } from "../../utils/prediccion";

const GLOBAL_STATE_CLASSES = {
  success: {
    surface: "border-success-300 bg-success-50",
    title: "text-success-700",
    kicker: "text-success-700",
  },
  warning: {
    surface: "border-warning-300 bg-warning-50",
    title: "text-warning-700",
    kicker: "text-warning-700",
  },
  danger: {
    surface: "border-danger-300 bg-danger-50",
    title: "text-danger-700",
    kicker: "text-danger-700",
  },
};

const LINK_BUTTON_BASE_CLASSES =
  "inline-flex min-h-[44px] items-center justify-center gap-2 rounded px-4 py-2.5 text-base font-medium transition-all duration-150 ease-out-quart focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";

const LINK_BUTTON_PRIMARY_CLASSES =
  "border border-primary-600 bg-primary-600 text-neutral-50 shadow-sm hover:border-primary-700 hover:bg-primary-700 active:bg-primary-800 focus-visible:ring-primary-500";

const LINK_BUTTON_OUTLINE_CLASSES =
  "border border-neutral-300 bg-transparent text-neutral-700 hover:border-neutral-400 hover:bg-neutral-100 active:bg-neutral-200 focus-visible:ring-neutral-400";

function resolveProbabilidad(probabilidad) {
  const parsed = Number(probabilidad);
  if (!Number.isFinite(parsed)) {
    return null;
  }

  return Math.min(Math.max(parsed, 0), 1);
}

function resolveClasificacionNivel(clasificacion) {
  const normalized = String(clasificacion || "").toLowerCase().trim();

  if (normalized === "falla") return 2;
  if (normalized === "alerta") return 1;
  return 0;
}

function resolveEquipoScore(equipo) {
  const alertas = Number(equipo?.alertas_activas || 0);
  const probabilidad = resolveProbabilidad(equipo?.ultima_probabilidad);
  const nivelClasificacion = resolveClasificacionNivel(equipo?.ultima_clasificacion);

  return alertas * 100 + (probabilidad || 0) * 100 + nivelClasificacion * 25;
}

function resolveActionMessage(equipo) {
  const alertas = Number(equipo?.alertas_activas || 0);
  const probabilidad = resolveProbabilidad(equipo?.ultima_probabilidad);
  const clasificacion = String(equipo?.ultima_clasificacion || "").toLowerCase().trim();

  if (alertas >= 3 || clasificacion === "falla" || (probabilidad !== null && probabilidad >= 0.75)) {
    return "Programar inspección inmediata y revisar causa raíz en este turno.";
  }

  if (alertas > 0 || clasificacion === "alerta" || (probabilidad !== null && probabilidad >= 0.5)) {
    return "Planificar mantención preventiva y monitoreo reforzado en próximas 4 horas.";
  }

  return "Mantener seguimiento y validar tendencia en la próxima actualización.";
}

function resolveGlobalState(resumen) {
  const alertasActivas = Number(resumen?.alertas_activas || 0);
  const equiposEnRiesgo = Number(resumen?.equipos_en_riesgo || 0);

  if (alertasActivas >= 5 || equiposEnRiesgo >= 3) {
    return {
      severity: "danger",
      title: "Atención inmediata requerida",
      description:
        "Hay señales críticas en la operación. Priorizá intervención para evitar detenciones no planificadas.",
    };
  }

  if (alertasActivas > 0 || equiposEnRiesgo > 0) {
    return {
      severity: "warning",
      title: "Operación en observación",
      description:
        "Se detectaron desvíos que requieren seguimiento técnico para evitar escalamiento a falla.",
    };
  }

  return {
    severity: "success",
    title: "Operación estable",
    description:
      "No hay señales críticas activas. Mantené la rutina de monitoreo y validación de lecturas.",
  };
}

export default function PanelAccionOperativa({ resumen }) {
  const equipos = Array.isArray(resumen?.equipos) ? resumen.equipos : [];

  const prioridades = equipos
    .filter((equipo) => {
      const alertas = Number(equipo?.alertas_activas || 0);
      const probabilidad = resolveProbabilidad(equipo?.ultima_probabilidad);
      const clasificacion = String(equipo?.ultima_clasificacion || "").toLowerCase().trim();

      return (
        alertas > 0 ||
        (probabilidad !== null && probabilidad >= 0.45) ||
        clasificacion === "alerta" ||
        clasificacion === "falla"
      );
    })
    .sort((a, b) => resolveEquipoScore(b) - resolveEquipoScore(a))
    .slice(0, 4)
    .map((equipo) => {
      const config = getConfigPrediccion(equipo?.ultima_clasificacion);
      const rawId = equipo?.id;
      const idCandidate = rawId === null || rawId === undefined ? "" : String(rawId).trim();
      const id = idCandidate === "" || idCandidate.toLowerCase() === "nan" ? "" : idCandidate;

      return {
        id,
        nombre: equipo?.nombre || `Equipo ${id || "s/n"}`,
        alertasActivas: Number(equipo?.alertas_activas || 0),
        probabilidad: resolveProbabilidad(equipo?.ultima_probabilidad),
        config,
        accion: resolveActionMessage(equipo),
      };
    });

  const globalState = resolveGlobalState(resumen);
  const globalClasses = GLOBAL_STATE_CLASSES[globalState.severity];

  return (
    <section className={`rounded-lg border p-5 ${globalClasses.surface}`} aria-label="Acciones operativas recomendadas">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className={`mb-1 text-xs font-semibold uppercase tracking-wide ${globalClasses.kicker}`}>
            Estado operativo actual
          </p>
          <h2 className={`m-0 text-lg font-semibold ${globalClasses.title}`}>{globalState.title}</h2>
          <p className="mt-2 max-w-3xl text-sm text-neutral-700">{globalState.description}</p>
        </div>

        <nav aria-label="Acciones rápidas de operación" className="flex flex-wrap gap-2">
          <Link to="/alertas" className={`${LINK_BUTTON_BASE_CLASSES} ${LINK_BUTTON_PRIMARY_CLASSES}`}>
            Ver alertas activas
          </Link>
          <Link to="/equipos" className={`${LINK_BUTTON_BASE_CLASSES} ${LINK_BUTTON_OUTLINE_CLASSES}`}>
            Ver todos los equipos
          </Link>
        </nav>
      </div>

      <div className="mt-5 border-t border-neutral-200 pt-4">
        <h3 className="m-0 text-base font-semibold text-neutral-800">Acciones recomendadas ahora</h3>
        <p className="mt-1 text-sm text-neutral-600">
          Esta lista prioriza equipos con mayor combinación de alertas activas y probabilidad de falla.
        </p>

        {prioridades.length === 0 ? (
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3 py-2">
            <p className="m-0 text-sm text-neutral-600">No hay equipos con riesgo inmediato para intervención.</p>
            <Link to="/historial" className={`${LINK_BUTTON_BASE_CLASSES} ${LINK_BUTTON_OUTLINE_CLASSES}`}>
              Revisar historial
            </Link>
          </div>
        ) : (
          <ol className="mt-3 divide-y divide-neutral-200">
            {prioridades.map((prioridad, index) => (
              <li
                key={
                  prioridad.id ||
                  `prioridad-${String(prioridad.nombre || "s-n")
                    .toLowerCase()
                    .trim()
                    .replace(/\s+/g, "-")}-${prioridad.alertasActivas}-${Math.round(
                    (prioridad.probabilidad || 0) * 100
                  )}`
                }
                className="flex flex-col gap-3 py-3 lg:flex-row lg:items-start lg:justify-between"
              >
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span aria-hidden="true" className={`h-2.5 w-2.5 rounded-full ${prioridad.config.dotClass}`} />
                    <strong className="text-sm text-neutral-800">{index + 1}. {prioridad.nombre}</strong>
                    <span className={`rounded-sm border px-2 py-0.5 text-xs font-medium ${prioridad.config.chipClass}`}>
                      {prioridad.config.label}
                    </span>
                  </div>
                  <p className="mb-1 mt-1 text-sm text-neutral-700">{prioridad.accion}</p>
                  <p className="m-0 text-xs tabular-nums text-neutral-500">
                    Riesgo: {formatProbability(prioridad.probabilidad, "Sin predicción")} · Alertas activas: {prioridad.alertasActivas}
                  </p>
                </div>

                {prioridad.id ? (
                  <Link
                    to={`/equipos/${encodeURIComponent(prioridad.id)}`}
                    className={`${LINK_BUTTON_BASE_CLASSES} ${LINK_BUTTON_OUTLINE_CLASSES} self-start`}
                  >
                    Abrir detalle
                  </Link>
                ) : (
                  <span className="self-start text-xs text-neutral-500">ID no disponible</span>
                )}
              </li>
            ))}
          </ol>
        )}
      </div>
    </section>
  );
}
