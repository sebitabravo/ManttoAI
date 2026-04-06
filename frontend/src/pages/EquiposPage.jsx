import { useCallback, useEffect, useState } from "react";

import { getDashboardResumen } from "../api/dashboard";
import { createEquipo, getEquipos } from "../api/equipos";
import EquipoCard from "../components/equipos/EquipoCard";
import EquipoForm from "../components/equipos/EquipoForm";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import Button from "../components/ui/Button";
import { subscribeEquiposRefresh } from "../utils/equiposEvents";
import { formatMetric, formatProbability } from "../utils/metrics";

function resolveRequestErrorMessage(error, fallbackMessage) {
  const backendDetail = error?.response?.data?.detail;

  if (typeof backendDetail === "string" && backendDetail.trim()) {
    return backendDetail;
  }

  if (typeof error?.message === "string" && error.message.trim()) {
    return error.message;
  }

  return fallbackMessage;
}

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
  const [equipos, setEquipos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createErrorMessage, setCreateErrorMessage] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const loadEquipos = useCallback(async () => {
    setLoading(true);
    try {
      const [equiposData, resumen] = await Promise.all([
        getEquipos(),
        getDashboardResumen().catch(() => null),
      ]);

      const equiposResumen = Array.isArray(resumen?.equipos) ? resumen.equipos : [];
      const resumenById = new Map(
        equiposResumen.map((equipoResumen) => [Number(equipoResumen.id), equipoResumen])
      );

      const enrichedEquipos = equiposData.map((equipo) => {
        const equipoResumen = resumenById.get(Number(equipo.id));

        return {
          ...equipo,
          dato: resolveLatestDataLabel(equipoResumen),
          alertas_activas: Number(equipoResumen?.alertas_activas || 0),
        };
      });

      setEquipos(enrichedEquipos);
      setError(null);
    } catch (fetchError) {
      setError(fetchError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEquipos();

    const unsubscribe = subscribeEquiposRefresh(() => {
      loadEquipos();
    });

    return unsubscribe;
  }, [loadEquipos]);

  async function handleCreateEquipo(payload) {
    setCreateErrorMessage("");
    setIsCreating(true);

    try {
      await createEquipo(payload);
      await loadEquipos();
      setShowCreateForm(false);
    } catch (createError) {
      setCreateErrorMessage(
        resolveRequestErrorMessage(createError, "No pudimos crear el equipo. Revisá los datos ingresados.")
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

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Equipos</h1>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
          <Button
            type="button"
            variant={showCreateForm ? "primary" : "outline"}
            onClick={showCreateForm ? closeCreateForm : openCreateForm}
            disabled={isCreating}
          >
            {showCreateForm ? "Cerrar formulario" : "Nuevo equipo"}
          </Button>
          <Button type="button" variant="outline" onClick={loadEquipos} disabled={loading || isCreating}>
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

      {loading ? <LoadingSpinner label="Cargando equipos desde backend..." /> : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudieron cargar equipos. Verificá la conexión con el backend.
        </div>
      ) : null}

      {!loading && equipos.length === 0 ? (
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
