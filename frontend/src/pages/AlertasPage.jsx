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
    <section className="grid gap-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="m-0 text-xl font-semibold text-neutral-900">Alertas</h1>
          <p className="mb-0 mt-1.5 text-sm text-neutral-600">
            Monitoreo de alertas activas y trazabilidad de alertas leídas.
            <span className="ml-2 text-xs text-neutral-500">
              (actualización automática cada {ALERTAS_POLLING_INTERVAL_MS / 1000}s)
            </span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <AlertaBadge total={alertasNoLeidas.length} />
          <Button type="button" variant="outline" onClick={refresh} disabled={loading}>
            {loading ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
      </div>

      {/* Indicador de actualización en segundo plano */}
      {loading && alertas.length > 0 ? (
        <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm text-neutral-600">
          Actualizando alertas...
        </div>
      ) : null}

      {isInitialLoading ? <LoadingSpinner label="Cargando alertas desde backend..." /> : null}

      {error ? (
        <div className="rounded-lg border border-warning-300 bg-warning-50 px-3 py-2 text-sm text-warning-800">
          No se pudieron cargar o actualizar alertas. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      {markError ? (
        <div className="rounded-lg border border-danger-300 bg-danger-50 px-3 py-2 text-sm text-danger-800">
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
        <section className="grid gap-3">
          <h2 className="mb-0 text-lg font-semibold text-neutral-900">No leídas</h2>
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
        <section className="grid gap-3">
          <h2 className="mb-0 text-lg font-semibold text-neutral-900">Leídas recientemente</h2>
          {alertasLeidas.slice(0, 20).map((alerta) => (
            <AlertaItem key={alerta.id} alerta={alerta} />
          ))}
        </section>
      ) : null}

      {!isInitialLoading && alertas.length > 0 && alertasNoLeidas.length === 0 ? (
        <p className="m-0 text-sm text-success-700">
          No quedan alertas pendientes por marcar como leídas.
        </p>
      ) : null}
    </section>
  );
}
