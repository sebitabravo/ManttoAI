import ResumenCards from "../components/dashboard/ResumenCards";
import GraficoTemperatura from "../components/dashboard/GraficoTemperatura";
import GraficoVibracion from "../components/dashboard/GraficoVibracion";
import TablaEstadoEquipos from "../components/dashboard/TablaEstadoEquipos";
import TablaUltimasLecturas from "../components/dashboard/TablaUltimasLecturas";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import { getDashboardData } from "../api/dashboard";
import usePolling from "../hooks/usePolling";

const resumenInicial = {
  total_equipos: 0,
  alertas_activas: 0,
  equipos_en_riesgo: 0,
  ultima_clasificacion: "sin datos",
  probabilidad_falla: 0,
  equipos: [],
};

function resolveTimestamp(value) {
  const parsed = Date.parse(value ?? "");
  return Number.isFinite(parsed) ? parsed : 0;
}

export default function DashboardPage() {
  const { data, loading, error } = usePolling(getDashboardData, 15000, null);

  const resumen = data?.resumen || resumenInicial;
  const fetchedLecturas = Array.isArray(data?.lecturas) ? data.lecturas : [];
  const lecturas = [...fetchedLecturas].sort((current, next) => {
    return resolveTimestamp(next?.timestamp) - resolveTimestamp(current?.timestamp);
  });

  const isInitialLoading = loading && !data;

  return (
    <section style={{ display: "grid", gap: 20 }}>
      <div>
        <h1 style={{ marginBottom: 4 }}>Dashboard</h1>
        <p style={{ marginTop: 0 }}>Resumen operativo del prototipo de mantenimiento predictivo.</p>
      </div>

      {isInitialLoading ? <LoadingSpinner label="Cargando resumen del dashboard..." /> : <ResumenCards resumen={resumen} />}

      <TablaEstadoEquipos equipos={resumen.equipos || []} />

      {loading && data ? (
        <div
          style={{
            padding: 10,
            border: "1px solid #d1d5db",
            borderRadius: 12,
            background: "#f9fafb",
            color: "#6b7280",
          }}
        >
          Actualizando datos del dashboard...
        </div>
      ) : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudo actualizar el backend. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      <div style={{ display: "grid", gap: 20, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
        <GraficoTemperatura lecturas={lecturas} />
        <GraficoVibracion lecturas={lecturas} />
      </div>

      <TablaUltimasLecturas lecturas={lecturas} equipos={resumen.equipos || []} />
    </section>
  );
}
