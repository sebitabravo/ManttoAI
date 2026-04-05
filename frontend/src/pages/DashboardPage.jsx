import ResumenCards from "../components/dashboard/ResumenCards";
import GraficoTemperatura from "../components/dashboard/GraficoTemperatura";
import GraficoVibracion from "../components/dashboard/GraficoVibracion";
import TablaUltimasLecturas from "../components/dashboard/TablaUltimasLecturas";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import { getDashboardResumen } from "../api/dashboard";
import usePolling from "../hooks/usePolling";

const resumenInicial = {
  total_equipos: 0,
  alertas_activas: 0,
  equipos_en_riesgo: 0,
  ultima_clasificacion: "sin datos",
  probabilidad_falla: 0,
};

export default function DashboardPage() {
  const { data, loading, error } = usePolling(getDashboardResumen, 15000, resumenInicial);

  return (
    <section style={{ display: "grid", gap: 20 }}>
      <div>
        <h1 style={{ marginBottom: 4 }}>Dashboard</h1>
        <p style={{ marginTop: 0 }}>Resumen operativo del prototipo de mantenimiento predictivo.</p>
      </div>

      {loading ? <LoadingSpinner label="Cargando resumen del dashboard..." /> : <ResumenCards resumen={data || resumenInicial} />}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudo consultar el backend. Se muestra la vista base del scaffold.
        </div>
      ) : null}

      <div style={{ display: "grid", gap: 20, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
        <GraficoTemperatura />
        <GraficoVibracion />
      </div>

      <TablaUltimasLecturas />
    </section>
  );
}
