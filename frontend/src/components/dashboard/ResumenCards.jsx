import { formatProbability } from "../../utils/metrics";

/**
 * Cards de resumen con jerarquía visual asimétrica.
 * 
 * Principio de diseño: Data is the Hero
 * - Alertas activas y Equipos en riesgo son PROMINENTES (críticas para decisiones)
 * - Métricas secundarias (total equipos, clasificación, probabilidad) son compactas
 * - Layout asimétrico con variación de tamaño según importancia operativa
 * 
 * Grid adaptativo:
 * - Desktop: 2 grandes (alertas, riesgo) + 3 pequeñas apiladas
 * - Tablet: 2 columnas
 * - Mobile: 1 columna
 */
export default function ResumenCards({ resumen }) {
  const alertasActivas = resumen.alertas_activas || 0;
  const equiposEnRiesgo = resumen.equipos_en_riesgo || 0;
  const totalEquipos = resumen.total_equipos || 0;
  const clasificacion = resumen.ultima_clasificacion || "normal";
  const probabilidad = formatProbability(resumen.probabilidad_falla, "Sin datos");

  // Determinar severidad visual para alertas (color semántico)
  const alertasSeveridad = alertasActivas === 0 ? "success" : alertasActivas >= 5 ? "danger" : "warning";
  const riesgoSeveridad = equiposEnRiesgo === 0 ? "success" : equiposEnRiesgo >= 3 ? "danger" : "warning";

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* ALERTA ACTIVAS — card GRANDE prominente */}
      <article
        className={`
          lg:col-span-2 lg:row-span-2
          rounded-lg border-2 p-6
          bg-${alertasSeveridad}-50
          border-${alertasSeveridad}-500
          transition-all duration-200 ease-out-quart
          hover:shadow-md
        `}
      >
        <div className={`text-sm font-medium uppercase tracking-wide text-${alertasSeveridad}-700 mb-2`}>
          Alertas activas
        </div>
        <div className={`metric-value text-6xl font-semibold text-${alertasSeveridad}-700 mb-3`}>
          {alertasActivas}
        </div>
        <div className="text-sm text-neutral-600">
          {alertasActivas === 0
            ? "Sistema operando dentro de parámetros normales"
            : alertasActivas === 1
            ? "1 alerta requiere atención"
            : `${alertasActivas} alertas requieren atención`}
        </div>
      </article>

      {/* EQUIPOS EN RIESGO — card GRANDE prominente */}
      <article
        className={`
          lg:col-span-2 lg:row-span-2
          rounded-lg border-2 p-6
          bg-${riesgoSeveridad}-50
          border-${riesgoSeveridad}-500
          transition-all duration-200 ease-out-quart
          hover:shadow-md
        `}
      >
        <div className={`text-sm font-medium uppercase tracking-wide text-${riesgoSeveridad}-700 mb-2`}>
          Equipos en riesgo
        </div>
        <div className={`metric-value text-6xl font-semibold text-${riesgoSeveridad}-700 mb-3`}>
          {equiposEnRiesgo}
        </div>
        <div className="text-sm text-neutral-600">
          {equiposEnRiesgo === 0
            ? "Todos los equipos en condiciones óptimas"
            : totalEquipos > 0
            ? `${Math.round((equiposEnRiesgo / totalEquipos) * 100)}% del total monitoreado`
            : "Monitoreo activo"}
        </div>
      </article>

      {/* TOTAL EQUIPOS — card pequeña secundaria */}
      <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 transition-all duration-200 ease-out-quart hover:shadow">
        <div className="text-xs font-medium uppercase tracking-wide text-neutral-500 mb-1">
          Total equipos
        </div>
        <div className="metric-value text-3xl font-semibold text-neutral-700">
          {totalEquipos}
        </div>
      </article>

      {/* CLASIFICACIÓN — card pequeña secundaria */}
      <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 transition-all duration-200 ease-out-quart hover:shadow">
        <div className="text-xs font-medium uppercase tracking-wide text-neutral-500 mb-1">
          Clasificación
        </div>
        <div className="text-2xl font-semibold text-neutral-700 capitalize">
          {clasificacion}
        </div>
      </article>

      {/* PROBABILIDAD FALLA — card pequeña secundaria */}
      <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 transition-all duration-200 ease-out-quart hover:shadow md:col-span-2 lg:col-span-1">
        <div className="text-xs font-medium uppercase tracking-wide text-neutral-500 mb-1">
          Probabilidad de falla
        </div>
        <div className="metric-value text-2xl font-semibold text-neutral-700">
          {probabilidad}
        </div>
      </article>
    </div>
  );
}
