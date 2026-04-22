import { useEffect, useState } from "react";

import ResumenCards from "../components/dashboard/ResumenCards";
import GraficoTemperatura from "../components/dashboard/GraficoTemperatura";
import GraficoVibracion from "../components/dashboard/GraficoVibracion";
import TablaEstadoEquipos from "../components/dashboard/TablaEstadoEquipos";
import { SkeletonMetric, SkeletonTable, SkeletonChart } from "../components/ui/Skeleton";
import Button from "../components/ui/Button";
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

/**
 * Dashboard principal — Estilo Apple.
 * 
 * Características:
 * - Cards limpias sin bordes
 * - Tipografía con negative letter-spacing
 * - Espaciado generoso
 * - Jerarquía visual clara
 */
export default function DashboardPage() {
  const { data, loading, error, refresh } = usePolling(getDashboardData, DASHBOARD_POLLING_INTERVAL_MS, null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);

  const resumen = data?.resumen || resumenInicial;
  const lecturas = Array.isArray(data?.lecturas) ? data.lecturas : [];

  const isInitialLoading = loading && !data;

  useEffect(() => {
    if (data) {
      setLastUpdatedAt(new Date());
    }
  }, [data]);

  const lastUpdatedLabel = lastUpdatedAt
    ? lastUpdatedAt.toLocaleTimeString("es-CL", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "—";

  return (
    <div className="space-y-10">
      {/* Header del dashboard */}
      <header className="space-y-2">
        <div className="flex items-center gap-3">
          <h1 className="text-display-md font-semibold text-neutral-600 tracking-tight">
            Centro de control
          </h1>
          {loading && data && (
            <span className="inline-flex items-center gap-2 text-xs text-neutral-400">
              <span className="h-1.5 w-1.5 rounded-full bg-primary-500 animate-pulse" aria-hidden="true" />
              Actualizando
            </span>
          )}
        </div>
        <p className="text-base text-neutral-400">
          Monitoreá el estado de tus equipos y anticipá fallas antes de que ocurran.
          <span className="ml-3 text-sm">
            Última actualización: {lastUpdatedLabel}
          </span>
        </p>
      </header>

      {/* Live region para screen readers */}
      {lastUpdatedAt && (
        <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
          Dashboard actualizado a las {lastUpdatedLabel}.
        </div>
      )}

      {/* Resumen operativo */}
      <section data-tour="dashboard-resumen" aria-label="Resumen operativo">
        {isInitialLoading ? (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
            <SkeletonMetric className="lg:col-span-4" />
            <SkeletonMetric className="lg:col-span-4" />
            <SkeletonMetric className="lg:col-span-4" />
            <SkeletonMetric className="lg:col-span-6" />
            <SkeletonMetric className="lg:col-span-6" />
          </div>
        ) : (
          <ResumenCards resumen={resumen} />
        )}
      </section>

      {/* Error banner */}
      {error && (
        <div className="flex items-center justify-between gap-4 rounded-xl bg-warning-50 px-5 py-4">
          <p className="text-sm text-warning-700">
            No se pudo conectar con el backend. Se muestran los últimos datos válidos.
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={refresh} 
            disabled={loading}
          >
            {loading ? "Reintentando..." : "Reintentar"}
          </Button>
        </div>
      )}

      {/* Gráficos de tendencias */}
      <section data-tour="dashboard-graficos" aria-label="Tendencias de sensores">
        <h2 className="mb-6 text-xl font-semibold text-neutral-600 tracking-tight">
          Tendencias
        </h2>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
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
        </div>
      </section>

      {/* Estado de equipos */}
      <section aria-label="Estado de equipos">
        <h2 className="mb-6 text-xl font-semibold text-neutral-600 tracking-tight">
          Estado de equipos
        </h2>
        {isInitialLoading ? (
          <SkeletonTable rows={5} cols={6} />
        ) : (
          <TablaEstadoEquipos equipos={resumen.equipos || []} />
        )}
      </section>
    </div>
  );
}
