import { useCallback, useState } from "react";
import { Link } from "react-router-dom";

import { getDashboardResumen } from "../api/dashboard";
import { createEquipo, getEquipos } from "../api/equipos";
import EquipoCard from "../components/equipos/EquipoCard";
import EquipoForm from "../components/equipos/EquipoForm";
import SmartProvisioningModal from "../components/equipos/SmartProvisioningModal";
import EmptyState from "../components/ui/EmptyState";
import Button from "../components/ui/Button";
import { SkeletonCard } from "../components/ui/Skeleton";
import usePolling from "../hooks/usePolling";
import { getApiErrorMessage } from "../utils/errorHandling";
import { formatMetric, formatProbability } from "../utils/metrics";
import { EQUIPOS_POLLING_INTERVAL_MS } from "../utils/constants";
import { getRubroBadgeClass, getRubroLabel } from "../utils/rubro";

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
  const [showProvisioning, setShowProvisioning] = useState(false);

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
    <section data-tour="equipos-contenido" className="grid grid-cols-1 gap-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="m-0 text-xl font-semibold text-neutral-900">Equipos</h1>
            {loading && equipos.length > 0 ? (
              <span className="inline-flex items-center gap-1.5 text-xs text-neutral-500">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary-500 animate-pulse" aria-hidden="true" />
                Actualizando
              </span>
            ) : null}
          </div>
          <p className="mb-0 mt-1.5 text-sm text-neutral-600">
            Activos registrados en el sistema de monitoreo.
            <span className="ml-2 text-xs text-neutral-500">
              (actualización automática cada {EQUIPOS_POLLING_INTERVAL_MS / 1000}s)
            </span>
          </p>
        </div>
        <div className="flex flex-wrap justify-end gap-2">
          <Button
            type="button"
            variant={showCreateForm ? "primary" : "outline"}
            onClick={showCreateForm ? closeCreateForm : openCreateForm}
            disabled={isCreating}
          >
            {showCreateForm ? "Cerrar formulario" : "Nuevo equipo"}
          </Button>
          <Button type="button" variant="outline" onClick={() => setShowProvisioning(true)}>
            Smart Provisioning
          </Button>
          <Button type="button" variant="outline" onClick={refresh} disabled={loading || isCreating}>
            {loading ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
      </div>

      {showCreateForm ? (
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="mt-0 text-lg font-semibold text-neutral-900">Alta de equipo</h2>
          <EquipoForm
            submitLabel="Crear equipo"
            onSubmit={handleCreateEquipo}
            onCancel={closeCreateForm}
            isSubmitting={isCreating}
            errorMessage={createErrorMessage}
          />
        </section>
      ) : null}

      {isInitialLoading ? (
        <div className="grid gap-4 grid-cols-[repeat(auto-fit,minmax(240px,1fr))]" aria-label="Cargando equipos">
          {Array.from({ length: 6 }, (_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
      ) : null}

      {error ? (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-warning-300 bg-warning-50 px-3 py-2 text-sm text-warning-800">
          <p className="m-0">No se pudieron cargar equipos. Se mantienen los últimos datos disponibles.</p>
          <Button type="button" variant="outline" onClick={refresh} disabled={loading || isCreating}>
            {loading ? "Reintentando..." : "Reintentar"}
          </Button>
        </div>
      ) : null}

      {!isInitialLoading && equipos.length === 0 ? (
        <EmptyState
          title="No hay equipos cargados"
          description="Usá el botón 'Nuevo equipo' para cargar activos y habilitar monitoreo en la interfaz."
        >
          <Button type="button" variant="outline" onClick={openCreateForm}>
            Registrar primer equipo
          </Button>
        </EmptyState>
      ) : null}

      <div className="hidden overflow-x-auto rounded-2xl bg-white shadow-sm md:block">
        <table className="w-full min-w-[980px]" aria-label="Tabla de equipos">
          <thead>
            <tr className="border-b border-neutral-100">
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Equipo</th>
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Rubro</th>
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Tipo</th>
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Estado</th>
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Ubicación</th>
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Último dato</th>
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Alertas</th>
              <th scope="col" className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {equipos.map((equipo) => (
              <tr key={equipo.id} className="transition-colors duration-200 hover:bg-neutral-50">
                <td className="px-5 py-4 text-sm font-medium text-neutral-700">{equipo.nombre}</td>
                <td className="px-5 py-4 text-sm text-neutral-600">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getRubroBadgeClass(equipo.rubro)}`}>
                    {getRubroLabel(equipo.rubro)}
                  </span>
                </td>
                <td className="px-5 py-4 text-sm text-neutral-600">{equipo.tipo || "—"}</td>
                <td className="px-5 py-4 text-sm text-neutral-600">{equipo.estado || "—"}</td>
                <td className="px-5 py-4 text-sm text-neutral-600">{equipo.ubicacion || "—"}</td>
                <td className="px-5 py-4 text-sm text-neutral-600 tabular-nums">
                  {equipo.dato || formatMetric(null, "°C", "Sin lecturas registradas")}
                </td>
                <td className="px-5 py-4 text-sm text-neutral-600 tabular-nums">{Number(equipo.alertas_activas || 0)}</td>
                <td className="px-5 py-4 text-sm">
                  <Link
                    to={`/equipos/${equipo.id}`}
                    className="font-medium text-primary-500 transition-colors duration-150 ease-out-quart hover:text-primary-600 hover:underline focus:outline-none focus-visible:rounded-sm focus-visible:ring-2 focus-visible:ring-primary-500"
                  >
                    Ver detalle
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-4 grid-cols-[repeat(auto-fit,minmax(240px,1fr))] md:hidden">
        {equipos.map((equipo) => (
          <EquipoCard key={equipo.id} equipo={equipo} onDeleted={refresh} />
        ))}
      </div>

      <SmartProvisioningModal open={showProvisioning} onClose={() => setShowProvisioning(false)} />
    </section>
  );
}
