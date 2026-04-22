import { formatProbability } from "../../utils/metrics";
import InfoTooltip from "../ui/InfoTooltip";

/**
 * Cards de resumen operativo — Estilo Apple.
 *
 * Características Apple:
 * - Cards sin borders, solo sombra sutil
 * - Fondo blanco limpio
 * - Colores semánticos sutiles (no agresivos)
 * - Tipografía con negative letter-spacing
 * - Espaciado generoso
 */

// Configuración de colores por severidad (Apple-style: más sutiles)
const SEVERITY_CONFIG = {
  success: {
    bg: "bg-success-50",
    text: "text-success-600",
    value: "text-success-600",
    icon: "✓",
  },
  warning: {
    bg: "bg-warning-50",
    text: "text-warning-600",
    value: "text-warning-600",
    icon: "!",
  },
  danger: {
    bg: "bg-danger-50",
    text: "text-danger-600",
    value: "text-danger-600",
    icon: "⚠",
  },
};

/**
 * Card individual de métrica.
 */
function MetricCard({ 
  label, 
  value, 
  description, 
  severity = null, 
  tooltip = null,
  className = "",
}) {
  const config = severity ? SEVERITY_CONFIG[severity] : null;
  
  return (
    <article 
      className={`
        rounded-2xl bg-white p-6 shadow-sm
        transition-shadow duration-200 hover:shadow-apple
        ${config?.bg || ""}
        ${className}
      `.replace(/\s+/g, " ").trim()}
    >
      {/* Label con tooltip opcional */}
      <div className="flex items-center gap-2 mb-3">
        <span className={`text-xs font-medium uppercase tracking-wide ${config?.text || "text-neutral-400"}`}>
          {label}
        </span>
        {tooltip && (
          <InfoTooltip label={`Ayuda: ${label}`} text={tooltip} />
        )}
      </div>
      
      {/* Valor principal */}
      <div className={`metric-value text-4xl font-semibold tracking-tight ${config?.value || "text-neutral-600"}`}>
        {value}
      </div>
      
      {/* Descripción */}
      {description && (
        <p className="mt-3 text-sm text-neutral-500">
          {description}
        </p>
      )}
    </article>
  );
}

/**
 * Grid de cards de resumen.
 */
export default function ResumenCards({ resumen }) {
  const alertasActivas = resumen.alertas_activas || 0;
  const equiposEnRiesgo = resumen.equipos_en_riesgo || 0;
  const totalEquipos = resumen.total_equipos || 0;
  const clasificacion = resumen.ultima_clasificacion || "normal";
  const probabilidad = formatProbability(resumen.probabilidad_falla, "—");

  // Determinar severidad
  const alertasSeveridad = alertasActivas === 0 ? "success" : alertasActivas >= 5 ? "danger" : "warning";
  const riesgoSeveridad = equiposEnRiesgo === 0 ? "success" : equiposEnRiesgo >= 3 ? "danger" : "warning";

  // Descripción contextual para alertas
  const alertasDesc = alertasActivas === 0
    ? "Sistema operando normalmente"
    : alertasActivas === 1
    ? "1 alerta requiere atención"
    : `${alertasActivas} alertas requieren atención`;

  // Descripción contextual para riesgo
  const riesgoDesc = equiposEnRiesgo === 0
    ? "Todos los equipos en condiciones óptimas"
    : totalEquipos > 0
    ? `${Math.round((equiposEnRiesgo / totalEquipos) * 100)}% del total monitoreado`
    : "Monitoreo activo";

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-12">
      {/* Alertas activas — Hero card */}
      <MetricCard
        label="Alertas activas"
        value={alertasActivas}
        description={alertasDesc}
        severity={alertasSeveridad}
        className="resumen-hero sm:col-span-2 lg:col-span-4"
      />

      {/* Equipos en riesgo — Hero card */}
      <MetricCard
        label="Equipos en riesgo"
        value={equiposEnRiesgo}
        description={riesgoDesc}
        severity={riesgoSeveridad}
        className="resumen-hero lg:col-span-4"
      />

      {/* Total equipos */}
      <MetricCard
        label="Total equipos"
        value={totalEquipos}
        tooltip="Cantidad de equipos registrados y monitoreados activamente."
        className="lg:col-span-4"
      />

      {/* Clasificación */}
      <MetricCard
        label="Clasificación"
        value={<span className="capitalize">{clasificacion}</span>}
        tooltip="Estado global estimado según telemetría reciente."
        className="lg:col-span-6"
      />

      {/* Probabilidad de falla */}
      <MetricCard
        label="Probabilidad de falla"
        value={probabilidad}
        tooltip="Probabilidad estimada de falla en el estado actual (0% a 100%)."
        className="lg:col-span-6"
      />
    </div>
  );
}
