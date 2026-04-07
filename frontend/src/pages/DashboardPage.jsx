import ResumenCards from "../components/dashboard/ResumenCards";
import GraficoTemperatura from "../components/dashboard/GraficoTemperatura";
import GraficoVibracion from "../components/dashboard/GraficoVibracion";
import TablaEstadoEquipos from "../components/dashboard/TablaEstadoEquipos";
import TablaUltimasLecturas from "../components/dashboard/TablaUltimasLecturas";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import { getDashboardData } from "../api/dashboard";
import usePolling from "../hooks/usePolling";
import { DASHBOARD_POLLING_INTERVAL_MS } from "../utils/constants";

const resumenInicial = {
  total_equipos: 0,
  alertas_activas: 0,
  equipos_en_riesgo: 0,
  ultima_clasificacion: "sin datos",
  probabilidad_falla: 0,
  equipos: [],
};

export default function DashboardPage() {
  const { data, loading, error } = usePolling(getDashboardData, DASHBOARD_POLLING_INTERVAL_MS, null);

  const resumen = data?.resumen || resumenInicial;
  const lecturas = Array.isArray(data?.lecturas) ? data.lecturas : [];

  const isInitialLoading = loading && !data;

  return (
    <section className="grid gap-8">
      {/* Header con jerarquía clara */}
      <div className="space-y-1">
        <h1 className="text-xl font-semibold text-neutral-800 tracking-tight">Dashboard</h1>
        <p className="text-sm text-neutral-500">Resumen operativo del prototipo de mantenimiento predictivo.</p>
      </div>

      {/* Resumen cards con jerarquía asimétrica */}
      {isInitialLoading ? (
        <LoadingSpinner label="Cargando resumen del dashboard..." />
      ) : (
        <ResumenCards resumen={resumen} />
      )}

      {/* Estado de equipos — tabla prominente */}
      <TablaEstadoEquipos equipos={resumen.equipos || []} />

      {/* Indicadores de estado de polling */}
      {loading && data ? (
        <div className="rounded-lg border border-neutral-300 bg-neutral-100 px-4 py-2.5 text-sm text-neutral-600">
          Actualizando datos del dashboard...
        </div>
      ) : null}

      {error ? (
        <div className="rounded-lg border border-warning-500 bg-warning-50 px-4 py-3 text-sm text-warning-700">
          No se pudo actualizar el backend. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      {/* Gráficos lado a lado — grid adaptativo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GraficoTemperatura lecturas={lecturas} />
        <GraficoVibracion lecturas={lecturas} />
      </div>

      {/* Últimas lecturas — tabla secundaria */}
      <TablaUltimasLecturas lecturas={lecturas} equipos={resumen.equipos || []} />
    </section>
  );
}
