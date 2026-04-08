import { useCallback, useEffect, useMemo, useState } from "react";

import { getEquipos } from "../api/equipos";
import { getLecturas } from "../api/lecturas";
import { getMantenciones, updateMantencion } from "../api/mantenciones";
import MantencionForm from "../components/mantenciones/MantencionForm";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import { SkeletonTable } from "../components/ui/Skeleton";
import { getApiErrorMessage } from "../utils/errorHandling";
import { formatDate } from "../utils/formatDate";
import { formatMetric, resolveMaxVibration } from "../utils/metrics";
import { sortByTimestampDesc } from "../utils/time";

export default function HistorialPage() {
  const [lecturas, setLecturas] = useState([]);
  const [mantenciones, setMantenciones] = useState([]);
  const [equiposById, setEquiposById] = useState(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingMantencionId, setEditingMantencionId] = useState(null);
  const [isSavingMantencion, setIsSavingMantencion] = useState(false);
  const [updateMantencionErrorMessage, setUpdateMantencionErrorMessage] = useState("");

  const loadHistorial = useCallback(async () => {
    setLoading(true);
    try {
      const [lecturasData, mantencionesData, equiposData] = await Promise.all([
        getLecturas(null, 25),
        getMantenciones({ limit: 25, order: "desc" }),
        getEquipos(),
      ]);

      setLecturas(Array.isArray(lecturasData) ? lecturasData : []);
      setMantenciones(Array.isArray(mantencionesData) ? mantencionesData : []);
      const nextEquiposById = new Map(
        (Array.isArray(equiposData) ? equiposData : []).map((equipo) => [
          Number(equipo.id),
          equipo.nombre,
        ])
      );
      setEquiposById(nextEquiposById);
      setError(null);
    } catch (fetchError) {
      setError(fetchError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistorial();
  }, [loadHistorial]);

  const lecturasRecientes = useMemo(() => {
    return sortByTimestampDesc(lecturas).slice(0, 25);
  }, [lecturas]);

  const mantencionesRecientes = useMemo(() => {
    return mantenciones.slice(0, 25);
  }, [mantenciones]);

  function resolveEquipoName(equipoId) {
    return equiposById.get(Number(equipoId)) || `Equipo #${equipoId}`;
  }

  const selectedMantencion = useMemo(() => {
    return mantencionesRecientes.find((mantencion) => Number(mantencion.id) === Number(editingMantencionId)) || null;
  }, [mantencionesRecientes, editingMantencionId]);

  function openMantencionEdit(mantencionId) {
    setEditingMantencionId(Number(mantencionId));
    setUpdateMantencionErrorMessage("");
  }

  function closeMantencionEdit() {
    setEditingMantencionId(null);
    setUpdateMantencionErrorMessage("");
  }

  async function handleUpdateMantencion(payload) {
    const resolvedMantencionId = Number(editingMantencionId);
    if (!Number.isFinite(resolvedMantencionId)) {
      setUpdateMantencionErrorMessage("No se puede actualizar esta mantención.");
      return;
    }

    setUpdateMantencionErrorMessage("");
    setIsSavingMantencion(true);

    try {
      await updateMantencion(resolvedMantencionId, payload);
      await loadHistorial();
      setEditingMantencionId(null);
    } catch (updateError) {
      setUpdateMantencionErrorMessage(
        getApiErrorMessage(updateError, "No pudimos actualizar la mantención. Revisá los datos ingresados.")
      );
    } finally {
      setIsSavingMantencion(false);
    }
  }

  return (
    <section className="grid grid-cols-1 gap-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="m-0 text-xl font-semibold text-neutral-900">Historial</h1>
          <p className="mb-0 mt-1.5 text-sm text-neutral-600">
            Lecturas y mantenciones persistidas para trazabilidad del prototipo.
          </p>
        </div>
        <Button type="button" variant="outline" onClick={loadHistorial} disabled={loading || isSavingMantencion}>
          {loading ? "Actualizando..." : "Actualizar"}
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4" aria-label="Cargando historial">
          <SkeletonTable rows={6} cols={5} />
          <SkeletonTable rows={5} cols={6} />
        </div>
      ) : null}

      {error ? (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-warning-300 bg-warning-50 px-3 py-2 text-sm text-warning-800">
          <p className="m-0">No se pudo cargar historial real de lecturas y mantenciones.</p>
          <Button type="button" variant="outline" onClick={loadHistorial} disabled={loading || isSavingMantencion}>
            {loading ? "Reintentando..." : "Reintentar"}
          </Button>
        </div>
      ) : null}

      {!loading && lecturasRecientes.length === 0 && mantencionesRecientes.length === 0 ? (
        <EmptyState
          title="Sin historial cargado"
          description="Acá conviven lecturas y mantenciones reales cuando ya existen datos en backend."
        >
          <Button type="button" variant="outline" onClick={loadHistorial} disabled={loading || isSavingMantencion}>
            {loading ? "Actualizando..." : "Actualizar historial"}
          </Button>
        </EmptyState>
      ) : null}

      <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
        <h2 className="mt-0 text-lg font-semibold text-neutral-900">Lecturas recientes</h2>
        {lecturasRecientes.length === 0 ? (
          <p className="mb-0 text-sm text-neutral-600">No hay lecturas históricas para mostrar.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <caption className="pb-2 text-left text-sm text-neutral-600">
                Historial cronológico de lecturas persistidas para auditoría del prototipo.
              </caption>
              <thead>
                <tr className="border-b border-neutral-200">
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Equipo</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Temperatura</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Humedad</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Vibración máx.</th>
                  <th scope="col" className="pb-2 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Fecha</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {lecturasRecientes.map((lectura) => (
                  <tr key={lectura.id || `${lectura.equipo_id}-${lectura.timestamp}`} className="hover:bg-neutral-50 transition-colors duration-150 ease-out-quart">
                    <td className="py-2 pr-4 text-sm text-neutral-900">{resolveEquipoName(lectura.equipo_id)}</td>
                    <td className="py-2 pr-4 text-sm tabular-nums text-neutral-900">{formatMetric(lectura.temperatura, "°C")}</td>
                    <td className="py-2 pr-4 text-sm tabular-nums text-neutral-900">{formatMetric(lectura.humedad, "%")}</td>
                    <td className="py-2 pr-4 text-sm tabular-nums text-neutral-900">{formatMetric(resolveMaxVibration(lectura), "g")}</td>
                    <td className="py-2 text-sm text-neutral-600">{formatDate(lectura.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="grid grid-cols-1 gap-3 rounded-lg border border-neutral-200 bg-neutral-100 p-4">
        <h2 className="mb-0 mt-0 text-lg font-semibold text-neutral-900">Mantenciones recientes</h2>
        {mantencionesRecientes.length === 0 ? (
          <p className="mb-0 text-sm text-neutral-600">
            No hay mantenciones registradas para este período.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <caption className="pb-2 text-left text-sm text-neutral-600">
                Mantenciones recientes con estado y acciones disponibles desde historial.
              </caption>
              <thead>
                <tr className="border-b border-neutral-200">
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">ID</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Equipo</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Tipo</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Descripción</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Estado</th>
                  <th scope="col" className="pb-2 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {mantencionesRecientes.map((mantencion) => {
                  const isEditing = Number(editingMantencionId) === Number(mantencion.id);

                  return (
                    <tr key={mantencion.id} className="hover:bg-neutral-50 transition-colors duration-150 ease-out-quart">
                      <td className="py-2 pr-4 text-sm tabular-nums text-neutral-900">{mantencion.id}</td>
                      <td className="py-2 pr-4 text-sm text-neutral-900">{resolveEquipoName(mantencion.equipo_id)}</td>
                      <td className="py-2 pr-4 text-sm text-neutral-900">{mantencion.tipo}</td>
                      <td className="py-2 pr-4 text-sm text-neutral-700">{mantencion.descripcion}</td>
                      <td className="py-2 pr-4 text-sm text-neutral-900">{mantencion.estado}</td>
                      <td className="py-2">
                        <Button
                          type="button"
                          variant={isEditing ? "primary" : "outline"}
                          onClick={() => (isEditing ? closeMantencionEdit() : openMantencionEdit(mantencion.id))}
                          disabled={isSavingMantencion}
                        >
                          {isEditing ? "Cancelar" : "Editar"}
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {selectedMantencion ? (
          <div className="border-t border-neutral-200 pt-3">
            <h3 className="mt-0 text-base font-semibold text-neutral-900">Actualizar mantención #{selectedMantencion.id}</h3>
            <MantencionForm
              initialValues={{
                tipo: selectedMantencion.tipo,
                descripcion: selectedMantencion.descripcion,
                estado: selectedMantencion.estado,
              }}
              onSubmit={handleUpdateMantencion}
              onCancel={closeMantencionEdit}
              submitLabel="Guardar cambios"
              isSubmitting={isSavingMantencion}
              errorMessage={updateMantencionErrorMessage}
            />
          </div>
        ) : null}
      </section>
    </section>
  );
}
