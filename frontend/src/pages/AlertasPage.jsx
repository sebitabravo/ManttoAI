import { useCallback, useMemo, useState } from "react";

import { getAlertas, marcarLeida } from "../api/alertas";
import AlertaBadge from "../components/alertas/AlertaBadge";
import AlertaItem from "../components/alertas/AlertaItem";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import usePolling from "../hooks/usePolling";
import { ALERTAS_POLLING_INTERVAL_MS } from "../utils/constants";

export default function AlertasPage() {
  const [markingId, setMarkingId] = useState(null);
  const [markError, setMarkError] = useState(null);

  // Fetcher estable para usePolling
  const fetchAlertas = useCallback(async () => {
    const alertasData = await getAlertas({ limite: 50 });
    return Array.isArray(alertasData) ? alertasData : [];
  }, []);

  const { data: alertas, loading, error, refresh } = usePolling(
    fetchAlertas,
    ALERTAS_POLLING_INTERVAL_MS,
    []
  );

  const alertasNoLeidas = useMemo(
    () => alertas.filter((alerta) => !alerta.leida),
    [alertas]
  );
  const alertasLeidas = useMemo(
    () => alertas.filter((alerta) => alerta.leida),
    [alertas]
  );

  async function handleMarkAsRead(alertaId) {
    setMarkingId(alertaId);
    setMarkError(null);
    try {
      await marcarLeida(alertaId);
      await refresh();
    } catch (err) {
      setMarkError(err);
    } finally {
      setMarkingId(null);
    }
  }

  const isInitialLoading = loading && alertas.length === 0;

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0 }}>Alertas</h1>
          <p style={{ marginTop: 6, marginBottom: 0, color: "#6b7280" }}>
            Monitoreo de alertas activas y trazabilidad de alertas leídas.
            <span style={{ marginLeft: 8, fontSize: "0.85em", color: "#9ca3af" }}>
              (actualización automática cada {ALERTAS_POLLING_INTERVAL_MS / 1000}s)
            </span>
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <AlertaBadge total={alertasNoLeidas.length} />
          <Button type="button" variant="outline" onClick={refresh} disabled={loading}>
            {loading ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
      </div>

      {/* Indicador de actualización en segundo plano */}
      {loading && alertas.length > 0 ? (
        <div className="rounded-xl border border-gray-300 bg-gray-50 p-2.5 text-gray-500">
          Actualizando alertas...
        </div>
      ) : null}

      {isInitialLoading ? <LoadingSpinner label="Cargando alertas desde backend..." /> : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudieron cargar o actualizar alertas. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      {markError ? (
        <div style={{ padding: 12, border: "1px solid #ef4444", borderRadius: 12, background: "#fef2f2" }}>
          Error al marcar alerta como leída. Intentá de nuevo.
        </div>
      ) : null}

      {!isInitialLoading && alertas.length === 0 ? (
        <EmptyState
          title="Sin alertas registradas"
          description="Cuando se detecten desvíos de umbrales o predicciones críticas aparecerán aquí."
        />
      ) : null}

      {alertasNoLeidas.length > 0 ? (
        <section style={{ display: "grid", gap: 12 }}>
          <h2 style={{ marginBottom: 0 }}>No leídas</h2>
          {alertasNoLeidas.map((alerta) => (
            <AlertaItem
              key={alerta.id}
              alerta={alerta}
              onMarkAsRead={handleMarkAsRead}
              marking={markingId === alerta.id}
            />
          ))}
        </section>
      ) : null}

      {alertasLeidas.length > 0 ? (
        <section style={{ display: "grid", gap: 12 }}>
          <h2 style={{ marginBottom: 0 }}>Leídas recientemente</h2>
          {alertasLeidas.slice(0, 20).map((alerta) => (
            <AlertaItem key={alerta.id} alerta={alerta} />
          ))}
        </section>
      ) : null}

      {!isInitialLoading && alertas.length > 0 && alertasNoLeidas.length === 0 ? (
        <p style={{ margin: 0, color: "#166534" }}>
          No quedan alertas pendientes por marcar como leídas.
        </p>
      ) : null}
    </section>
  );
}
