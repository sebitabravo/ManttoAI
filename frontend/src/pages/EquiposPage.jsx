import { useCallback, useState } from "react";

import { getDashboardResumen } from "../api/dashboard";
import { createEquipo, getEquipos } from "../api/equipos";
import EquipoCard from "../components/equipos/EquipoCard";
import EquipoForm from "../components/equipos/EquipoForm";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import Button from "../components/ui/Button";
import usePolling from "../hooks/usePolling";
import { getApiErrorMessage } from "../utils/errorHandling";
import { formatMetric, formatProbability } from "../utils/metrics";
import { EQUIPOS_POLLING_INTERVAL_MS } from "../utils/constants";

function resolveLatestDataLabel(equipoResumen) {
  if (!equipoResumen) {
    return "Sin lecturas registradas";
  }

  if (equipoResumen.ultima_temperatura !== null && equipoResumen.ultima_temperatura !== undefined) {
    return formatMetric(equipoResumen.ultima_temperatura, "°C", "Sin lecturas registradas");
  }

  if (equipoResumen.ultima_probabilidad !== null && equipoResumen.ultima_probabilidad !== undefined) {
    return `${formatProbability(equipoResumen.ultima_probabilidad, "Sin lecturas registradas")} riesgo`;
  }

  return "Sin lecturas registradas";
}

export default function EquiposPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createErrorMessage, setCreateErrorMessage] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  // Fetcher estable para usePolling - obtiene equipos enriquecidos con datos del dashboard
  const fetchEquipos = useCallback(async () => {
    const [equiposData, resumen] = await Promise.all([
      getEquipos(),
      getDashboardResumen().catch(() => null),
    ]);

    const equiposResumen = Array.isArray(resumen?.equipos) ? resumen.equipos : [];
    const resumenById = new Map(
      equiposResumen.map((equipoResumen) => [Number(equipoResumen.id), equipoResumen])
    );

    return equiposData.map((equipo) => {
      const equipoResumen = resumenById.get(Number(equipo.id));

      return {
        ...equipo,
        dato: resolveLatestDataLabel(equipoResumen),
        alertas_activas: Number(equipoResumen?.alertas_activas || 0),
        // Datos de predicción para el indicador visual en la card
        ultima_clasificacion: equipoResumen?.ultima_clasificacion ?? null,
        ultima_probabilidad: equipoResumen?.ultima_probabilidad ?? null,
      };
    });
  }, []);

  const { data: equipos, loading, error, refresh } = usePolling(
    fetchEquipos,
    EQUIPOS_POLLING_INTERVAL_MS,
    []
  );

  async function handleCreateEquipo(payload) {
    setCreateErrorMessage("");
    setIsCreating(true);

    try {
      await createEquipo(payload);
      await refresh();
      setShowCreateForm(false);
    } catch (createError) {
      setCreateErrorMessage(
        getApiErrorMessage(createError, "No pudimos crear el equipo. Revisá los datos ingresados.")
      );
    } finally {
      setIsCreating(false);
    }
  }

  function openCreateForm() {
    setCreateErrorMessage("");
    setShowCreateForm(true);
  }

  function closeCreateForm() {
    setCreateErrorMessage("");
    setShowCreateForm(false);
  }

  const isInitialLoading = loading && equipos.length === 0;

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0 }}>Equipos</h1>
          <p style={{ marginTop: 6, marginBottom: 0, color: "#6b7280" }}>
            Activos registrados en el sistema de monitoreo.
            <span style={{ marginLeft: 8, fontSize: "0.85em", color: "#9ca3af" }}>
              (actualización automática cada {EQUIPOS_POLLING_INTERVAL_MS / 1000}s)
            </span>
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
          <Button
            type="button"
            variant={showCreateForm ? "primary" : "outline"}
            onClick={showCreateForm ? closeCreateForm : openCreateForm}
            disabled={isCreating}
          >
            {showCreateForm ? "Cerrar formulario" : "Nuevo equipo"}
          </Button>
          <Button type="button" variant="outline" onClick={refresh} disabled={loading || isCreating}>
            {loading ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
      </div>

      {showCreateForm ? (
        <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
          <h2 style={{ marginTop: 0 }}>Alta de equipo</h2>
          <EquipoForm
            submitLabel="Crear equipo"
            onSubmit={handleCreateEquipo}
            onCancel={closeCreateForm}
            isSubmitting={isCreating}
            errorMessage={createErrorMessage}
          />
        </section>
      ) : null}

      {/* Indicador de actualización en segundo plano */}
      {loading && equipos.length > 0 ? (
        <div className="rounded-xl border border-gray-300 bg-gray-50 p-2.5 text-gray-500">
          Actualizando equipos...
        </div>
      ) : null}

      {isInitialLoading ? <LoadingSpinner label="Cargando equipos desde backend..." /> : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudieron cargar equipos. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      {!isInitialLoading && equipos.length === 0 ? (
        <EmptyState
          title="No hay equipos cargados"
          description="Usá el botón 'Nuevo equipo' para cargar activos y habilitar monitoreo en la interfaz."
        />
      ) : null}

      <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        {equipos.map((equipo) => (
          <EquipoCard key={equipo.id} equipo={equipo} />
        ))}
      </div>
    </section>
  );
}
