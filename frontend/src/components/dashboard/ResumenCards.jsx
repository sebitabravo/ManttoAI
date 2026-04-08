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
    <div className="grid gap-5 xl:grid-cols-12">
      {/* ALERTAS ACTIVAS — card hero primaria */}
      <article
        className={`resumen-hero rounded-lg border-2 p-6 md:p-7 xl:col-span-7 ${alertasClasses.card} transition-colors duration-150 ease-out-quart`}
      >
        <div className={`resumen-hero__label mb-2 text-xs font-semibold uppercase tracking-wide ${alertasClasses.label}`}>
          Alertas activas
        </div>
        <div className={`resumen-hero__value metric-value mb-2 text-5xl font-semibold ${alertasClasses.value}`}>
          {alertasActivas}
        </div>
        <div className="text-sm text-neutral-700">
          {alertasActivas === 0
            ? "Sistema operando dentro de parámetros normales"
            : alertasActivas === 1
            ? "1 alerta requiere atención"
            : `${alertasActivas} alertas requieren atención`}
        </div>
      </article>

      {/* EQUIPOS EN RIESGO — card hero secundaria */}
      <article
        className={`resumen-hero rounded-lg border-2 p-6 md:p-7 xl:col-span-5 ${riesgoClasses.card} transition-colors duration-150 ease-out-quart`}
      >
        <div className={`resumen-hero__label mb-2 text-xs font-semibold uppercase tracking-wide ${riesgoClasses.label}`}>
          Equipos en riesgo
        </div>
        <div className={`resumen-hero__value metric-value mb-2 text-5xl font-semibold ${riesgoClasses.value}`}>
          {equiposEnRiesgo}
        </div>
        <div className="text-sm text-neutral-700">
          {equiposEnRiesgo === 0
            ? "Todos los equipos en condiciones óptimas"
            : totalEquipos > 0
            ? `${Math.round((equiposEnRiesgo / totalEquipos) * 100)}% del total monitoreado`
            : "Monitoreo activo"}
        </div>
      </article>

      {/* Métricas secundarias compactas */}
      <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 xl:col-span-4">
        <div className="mb-1 text-xs font-medium uppercase tracking-wide text-neutral-500">
          Total equipos
        </div>
        <div className="metric-value text-2xl font-semibold text-neutral-700">
          {totalEquipos}
        </div>
      </article>

      <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 xl:col-span-4">
        <div className="mb-1 text-xs font-medium uppercase tracking-wide text-neutral-500">
          Clasificación
        </div>
        <div className="text-2xl font-semibold text-neutral-700 capitalize">
          {clasificacion}
        </div>
      </article>

      <article className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 xl:col-span-4">
        <div className="mb-1 text-xs font-medium uppercase tracking-wide text-neutral-500">
          Probabilidad de falla
        </div>
        <div className="metric-value text-2xl font-semibold text-neutral-700">
          {probabilidad}
        </div>
      </article>
    </div>
  );
}
