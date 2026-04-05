import { useCallback, useEffect, useMemo, useState } from "react";

import { getAlertas, marcarLeida } from "../api/alertas";
import AlertaBadge from "../components/alertas/AlertaBadge";
import AlertaItem from "../components/alertas/AlertaItem";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";

export default function AlertasPage() {
  const [alertas, setAlertas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [markingId, setMarkingId] = useState(null);

  const loadAlertas = useCallback(async () => {
    setLoading(true);
    try {
      const alertasData = await getAlertas({ limite: 200 });
      setAlertas(Array.isArray(alertasData) ? alertasData : []);
      setError(null);
    } catch (fetchError) {
      setError(fetchError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlertas();
  }, [loadAlertas]);

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
    try {
      await marcarLeida(alertaId);
      await loadAlertas();
    } catch (markError) {
      setError(markError);
    } finally {
      setMarkingId(null);
    }
  }

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0 }}>Alertas</h1>
          <p style={{ marginTop: 6, marginBottom: 0, color: "#6b7280" }}>
            Monitoreo de alertas activas y trazabilidad de alertas leídas.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <AlertaBadge total={alertasNoLeidas.length} />
          <Button type="button" variant="outline" onClick={loadAlertas} disabled={loading}>
            {loading ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
      </div>

      {loading ? <LoadingSpinner label="Cargando alertas desde backend..." /> : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudieron cargar o actualizar alertas.
        </div>
      ) : null}

      {!loading && alertas.length === 0 ? (
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

      {!loading && alertas.length > 0 && alertasNoLeidas.length === 0 ? (
        <p style={{ margin: 0, color: "#166534" }}>
          No quedan alertas pendientes por marcar como leídas.
        </p>
      ) : null}
    </section>
  );
}
