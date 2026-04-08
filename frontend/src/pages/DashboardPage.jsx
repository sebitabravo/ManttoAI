import ResumenCards from "../components/dashboard/ResumenCards";
import GraficoTemperatura from "../components/dashboard/GraficoTemperatura";
import GraficoVibracion from "../components/dashboard/GraficoVibracion";
import TablaEstadoEquipos from "../components/dashboard/TablaEstadoEquipos";
import TablaUltimasLecturas from "../components/dashboard/TablaUltimasLecturas";
import { SkeletonMetric, SkeletonTable, SkeletonChart } from "../components/ui/Skeleton";
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
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-semibold text-neutral-800 tracking-tight">Dashboard</h1>
          {loading && data ? (
            <span className="inline-flex items-center gap-1.5 text-xs text-neutral-500">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary-500 animate-pulse" aria-hidden="true" />
              Actualizando
            </span>
          ) : null}
        </div>
        <p className="text-sm text-neutral-500">Resumen operativo del prototipo de mantenimiento predictivo.</p>
      </div>

      {/* Bloque crítico: resumen operativo */}
      <section className="grid gap-5" aria-label="Resumen operativo crítico">
        {isInitialLoading ? (
          <div className="grid gap-4 xl:grid-cols-12">
            <SkeletonMetric className="xl:col-span-7" />
            <SkeletonMetric className="xl:col-span-5" />
            <SkeletonMetric className="xl:col-span-4" />
            <SkeletonMetric className="xl:col-span-4" />
            <SkeletonMetric className="xl:col-span-4" />
          </div>
        ) : (
          <ResumenCards resumen={resumen} />
        )}
      </section>

      {error ? (
        <div className="rounded-lg border border-warning-500 bg-warning-50 px-4 py-3 text-sm text-warning-700">
          No se pudo actualizar el backend. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      {/* Bloque analítico: estado + últimas lecturas */}
      <section className="grid gap-5 xl:grid-cols-12" aria-label="Estado y lecturas recientes">
        <div className="xl:col-span-7">
          {isInitialLoading ? <SkeletonTable rows={5} cols={6} /> : <TablaEstadoEquipos equipos={resumen.equipos || []} />}
        </div>

        <div className="xl:col-span-5">
          {isInitialLoading ? (
            <SkeletonTable rows={5} cols={4} />
          ) : (
            <TablaUltimasLecturas lecturas={lecturas} equipos={resumen.equipos || []} />
          )}
        </div>
      </section>

      {/* Gráficos lado a lado — grid adaptativo */}
      <section className="grid grid-cols-1 gap-5 lg:grid-cols-2" aria-label="Tendencias de sensores">
        {isInitialLoading ? (
          <>
            <SkeletonChart />
            <SkeletonChart />
          </>
        ) : (
          <>
            <GraficoTemperatura lecturas={lecturas} />
            <GraficoVibracion lecturas={lecturas} />
          </>
        )}
      </section>
    </section>
  );
}
