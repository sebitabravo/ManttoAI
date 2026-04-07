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
 * - Desktop: 2 grandes (alertas, riesgo) + row de métricas compactas
 * - Tablet: 2 columnas
 * - Mobile: 1 columna
 *
 * NOTA: Las clases de color se resuelven con un mapa explícito porque Tailwind JIT
 * no detecta clases construidas con interpolación dinámica (ej. `bg-${variable}-50`).
 */

// Mapa explícito de clases por severidad — Tailwind JIT necesita ver las clases completas
const SEVERITY_CLASSES = {
  success: {
    card: "bg-success-50 border-success-500",
    label: "text-success-700",
    value: "text-success-700",
  },
  warning: {
    card: "bg-warning-50 border-warning-500",
    label: "text-warning-700",
    value: "text-warning-700",
  },
  danger: {
    card: "bg-danger-50 border-danger-500",
    label: "text-danger-700",
    value: "text-danger-700",
  },
};

export default function ResumenCards({ resumen }) {
  const alertasActivas = resumen.alertas_activas || 0;
  const equiposEnRiesgo = resumen.equipos_en_riesgo || 0;
  const totalEquipos = resumen.total_equipos || 0;
  const clasificacion = resumen.ultima_clasificacion || "normal";
  const probabilidad = formatProbability(resumen.probabilidad_falla, "Sin datos");

  // Determinar severidad visual para alertas (color semántico)
  const alertasSeveridad = alertasActivas === 0 ? "success" : alertasActivas >= 5 ? "danger" : "warning";
  const riesgoSeveridad = equiposEnRiesgo === 0 ? "success" : equiposEnRiesgo >= 3 ? "danger" : "warning";

  const alertasClasses = SEVERITY_CLASSES[alertasSeveridad];
  const riesgoClasses = SEVERITY_CLASSES[riesgoSeveridad];

  return (
    <div className="grid gap-4">
      {/* Fila superior: cards hero de alertas y riesgo */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* ALERTAS ACTIVAS — card hero prominente */}
        <article
          className={`rounded-lg border-2 p-6 ${alertasClasses.card} transition-all duration-200 ease-out-quart hover:shadow-md`}
        >
          <div className={`text-sm font-medium uppercase tracking-wide ${alertasClasses.label} mb-2`}>
            Alertas activas
          </div>
          <div className={`metric-value text-5xl font-semibold ${alertasClasses.value} mb-3`}>
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

        {/* EQUIPOS EN RIESGO — card hero prominente */}
        <article
          className={`rounded-lg border-2 p-6 ${riesgoClasses.card} transition-all duration-200 ease-out-quart hover:shadow-md`}
        >
          <div className={`text-sm font-medium uppercase tracking-wide ${riesgoClasses.label} mb-2`}>
            Equipos en riesgo
          </div>
          <div className={`metric-value text-5xl font-semibold ${riesgoClasses.value} mb-3`}>
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
      </div>

      {/* Fila inferior: métricas secundarias compactas */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* TOTAL EQUIPOS */}
        <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 transition-all duration-200 ease-out-quart hover:shadow">
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500 mb-1">
            Total equipos
          </div>
          <div className="metric-value text-2xl font-semibold text-neutral-700">
            {totalEquipos}
          </div>
        </article>

        {/* CLASIFICACIÓN */}
        <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 transition-all duration-200 ease-out-quart hover:shadow">
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500 mb-1">
            Clasificación
          </div>
          <div className="text-2xl font-semibold text-neutral-700 capitalize">
            {clasificacion}
          </div>
        </article>

        {/* PROBABILIDAD FALLA */}
        <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 transition-all duration-200 ease-out-quart hover:shadow">
          <div className="text-xs font-medium uppercase tracking-wide text-neutral-500 mb-1">
            Probabilidad de falla
          </div>
          <div className="metric-value text-2xl font-semibold text-neutral-700">
            {probabilidad}
          </div>
        </article>
      </div>
    </div>
  );
}
