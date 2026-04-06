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
    <section className="grid gap-5">
      <div>
        <h1 className="mb-1">Dashboard</h1>
        <p className="mt-0">Resumen operativo del prototipo de mantenimiento predictivo.</p>
      </div>

      {isInitialLoading ? <LoadingSpinner label="Cargando resumen del dashboard..." /> : <ResumenCards resumen={resumen} />}

      <TablaEstadoEquipos equipos={resumen.equipos || []} />

      {loading && data ? (
        <div className="rounded-xl border border-gray-300 bg-gray-50 p-2.5 text-gray-500">
          Actualizando datos del dashboard...
        </div>
      ) : null}

      {error ? (
        <div className="rounded-xl border border-amber-500 bg-amber-50 p-3">
          No se pudo actualizar el backend. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      {/* Nota: auto-fit + minmax no tiene utilitario nativo exacto en Tailwind. */}
      <div className="grid gap-5" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
        <GraficoTemperatura lecturas={lecturas} />
        <GraficoVibracion lecturas={lecturas} />
      </div>

      <TablaUltimasLecturas lecturas={lecturas} equipos={resumen.equipos || []} />
    </section>
  );
}
