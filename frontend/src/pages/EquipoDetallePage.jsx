import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { getEquipo, updateEquipo } from "../api/equipos";
import EquipoForm from "../components/equipos/EquipoForm";
import MantencionForm from "../components/mantenciones/MantencionForm";
import { getLecturas } from "../api/lecturas";
import { createMantencion, getMantenciones, updateMantencion } from "../api/mantenciones";
import { getPredicciones } from "../api/predicciones";
import { getUmbrales, updateUmbral } from "../api/umbrales";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import Button from "../components/ui/Button";
import { notifyEquiposRefresh } from "../utils/equiposEvents";
import { notifyMantencionesRefresh } from "../utils/mantencionesEvents";
import { compareByTimestampDesc, formatDate } from "../utils/formatDate";
import { formatMetric, resolveMaxVibration } from "../utils/metrics";

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

function buildUmbralDrafts(umbrales) {
  return (Array.isArray(umbrales) ? umbrales : []).reduce((accumulator, umbral) => {
    const umbralId = Number(umbral.id);

    return {
      ...accumulator,
      [umbralId]: {
        valor_min: String(umbral.valor_min),
        valor_max: String(umbral.valor_max),
      },
    };
  }, {});
}

function formatVariableLabel(variable) {
  if (typeof variable !== "string" || !variable.trim()) {
    return "Variable";
  }

  const normalizedVariable = variable.trim().replaceAll("_", " ").toLowerCase();
  return normalizedVariable.charAt(0).toUpperCase() + normalizedVariable.slice(1);
}

export default function EquipoDetallePage() {
  const { equipoId } = useParams();
  const resolvedEquipoId = Number(equipoId);

  const [equipo, setEquipo] = useState(null);
  const [lecturas, setLecturas] = useState([]);
  const [prediccion, setPrediccion] = useState(null);
  const [mantenciones, setMantenciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateErrorMessage, setUpdateErrorMessage] = useState("");
  const [umbrales, setUmbrales] = useState([]);
  const [umbralDrafts, setUmbralDrafts] = useState({});
  const [umbralesLoading, setUmbralesLoading] = useState(true);
  const [umbralesErrorMessage, setUmbralesErrorMessage] = useState("");
  const [savingUmbralById, setSavingUmbralById] = useState({});
  const [umbralErrorById, setUmbralErrorById] = useState({});
  const [umbralSuccessById, setUmbralSuccessById] = useState({});
  const [showCreateMantencionForm, setShowCreateMantencionForm] = useState(false);
  const [isCreatingMantencion, setIsCreatingMantencion] = useState(false);
  const [createMantencionErrorMessage, setCreateMantencionErrorMessage] = useState("");
  const [editingMantencionId, setEditingMantencionId] = useState(null);
  const [isSavingMantencion, setIsSavingMantencion] = useState(false);
  const [updateMantencionErrorMessage, setUpdateMantencionErrorMessage] = useState("");

  const loadEquipoDetalle = useCallback(async () => {
    if (!Number.isFinite(resolvedEquipoId)) {
      setError(new Error("Identificador de equipo inválido"));
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const [equipoData, lecturasData, prediccionData, mantencionesData] = await Promise.all([
        getEquipo(resolvedEquipoId),
        getLecturas(resolvedEquipoId),
        getPredicciones(resolvedEquipoId).catch((fetchError) => {
          if (fetchError?.response?.status === 404) {
            return null;
          }

          throw fetchError;
        }),
        getMantenciones(),
      ]);

      setEquipo(equipoData);
      setLecturas(Array.isArray(lecturasData) ? lecturasData : []);
      setPrediccion(prediccionData);
      const mantencionesEquipo = Array.isArray(mantencionesData)
        ? mantencionesData.filter((mantencion) => Number(mantencion.equipo_id) === resolvedEquipoId)
        : [];
      setMantenciones(mantencionesEquipo);
      setError(null);
    } catch (fetchError) {
      setError(fetchError);
    } finally {
      setLoading(false);
    }
  }, [resolvedEquipoId]);

  useEffect(() => {
    loadEquipoDetalle();
  }, [loadEquipoDetalle]);

  const loadUmbrales = useCallback(async () => {
    if (!Number.isFinite(resolvedEquipoId)) {
      setUmbralesErrorMessage("No se pueden cargar umbrales: identificador de equipo inválido.");
      setUmbralesLoading(false);
      return;
    }

    setUmbralesLoading(true);
    setUmbralesErrorMessage("");

    try {
      const umbralesData = await getUmbrales();
      const umbralesEquipo = (Array.isArray(umbralesData) ? umbralesData : [])
        .filter((umbral) => Number(umbral.equipo_id) === resolvedEquipoId)
        .sort((current, next) => String(current.variable).localeCompare(String(next.variable)));

      setUmbrales(umbralesEquipo);
      setUmbralDrafts(buildUmbralDrafts(umbralesEquipo));
      setSavingUmbralById({});
      setUmbralErrorById({});
      setUmbralSuccessById({});
    } catch (fetchError) {
      setUmbralesErrorMessage(
        resolveRequestErrorMessage(
          fetchError,
          "No pudimos cargar umbrales del equipo. Revisá conexión y permisos de acceso."
        )
      );
    } finally {
      setUmbralesLoading(false);
    }
  }, [resolvedEquipoId]);

  useEffect(() => {
    loadUmbrales();
  }, [loadUmbrales]);

  const isSavingAnyUmbral = useMemo(() => {
    return Object.values(savingUmbralById).some(Boolean);
  }, [savingUmbralById]);

  function handleRefresh() {
    loadEquipoDetalle();
    loadUmbrales();
  }

  async function handleUpdateEquipo(payload) {
    if (!Number.isFinite(resolvedEquipoId)) {
      setUpdateErrorMessage("No se puede actualizar: identificador de equipo inválido.");
      return;
    }

    setUpdateErrorMessage("");
    setIsUpdating(true);

    try {
      await updateEquipo(resolvedEquipoId, payload);
      await loadEquipoDetalle();
      notifyEquiposRefresh();
      setShowEditForm(false);
    } catch (updateError) {
      setUpdateErrorMessage(
        resolveRequestErrorMessage(updateError, "No pudimos actualizar el equipo. Revisá los datos ingresados.")
      );
    } finally {
      setIsUpdating(false);
    }
  }

  function openEditForm() {
    setUpdateErrorMessage("");
    setShowEditForm(true);
  }

  function closeEditForm() {
    setUpdateErrorMessage("");
    setShowEditForm(false);
  }

  function openCreateMantencionForm() {
    setCreateMantencionErrorMessage("");
    setEditingMantencionId(null);
    setShowCreateMantencionForm(true);
  }

  function closeCreateMantencionForm() {
    setCreateMantencionErrorMessage("");
    setShowCreateMantencionForm(false);
  }

  function openMantencionEdit(mantencionId) {
    setShowCreateMantencionForm(false);
    setEditingMantencionId(Number(mantencionId));
    setUpdateMantencionErrorMessage("");
  }

  function closeMantencionEdit() {
    setEditingMantencionId(null);
    setUpdateMantencionErrorMessage("");
  }

  async function handleCreateMantencion(payload) {
    if (!Number.isFinite(resolvedEquipoId)) {
      setCreateMantencionErrorMessage("No se puede crear mantención: identificador de equipo inválido.");
      return;
    }

    setCreateMantencionErrorMessage("");
    setIsCreatingMantencion(true);

    try {
      await createMantencion({
        equipo_id: resolvedEquipoId,
        ...payload,
      });
      await loadEquipoDetalle();
      notifyMantencionesRefresh();
      setEditingMantencionId(null);
      setShowCreateMantencionForm(false);
    } catch (createError) {
      setCreateMantencionErrorMessage(
        resolveRequestErrorMessage(createError, "No pudimos crear la mantención. Revisá los datos ingresados.")
      );
    } finally {
      setIsCreatingMantencion(false);
    }
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
      await loadEquipoDetalle();
      notifyMantencionesRefresh();
      setEditingMantencionId(null);
    } catch (updateError) {
      setUpdateMantencionErrorMessage(
        resolveRequestErrorMessage(updateError, "No pudimos actualizar la mantención. Revisá los datos ingresados.")
      );
    } finally {
      setIsSavingMantencion(false);
    }
  }

  function handleUmbralDraftChange(umbralId, field, value) {
    const resolvedUmbralId = Number(umbralId);

    setUmbralDrafts((current) => ({
      ...current,
      [resolvedUmbralId]: {
        ...current[resolvedUmbralId],
        [field]: value,
      },
    }));

    setUmbralErrorById((current) => ({ ...current, [resolvedUmbralId]: "" }));
    setUmbralSuccessById((current) => ({ ...current, [resolvedUmbralId]: "" }));
  }

  async function handleSaveUmbral(umbralId) {
    const resolvedUmbralId = Number(umbralId);
    const draft = umbralDrafts[resolvedUmbralId];

    if (!draft) {
      return;
    }

    const valorMin = Number.parseFloat(draft.valor_min);
    const valorMax = Number.parseFloat(draft.valor_max);

    if (!Number.isFinite(valorMin) || !Number.isFinite(valorMax)) {
      setUmbralErrorById((current) => ({
        ...current,
        [resolvedUmbralId]: "Ingresá números válidos para mínimo y máximo.",
      }));
      setUmbralSuccessById((current) => ({ ...current, [resolvedUmbralId]: "" }));
      return;
    }

    if (valorMin > valorMax) {
      setUmbralErrorById((current) => ({
        ...current,
        [resolvedUmbralId]: "El valor mínimo no puede ser mayor que el máximo.",
      }));
      setUmbralSuccessById((current) => ({ ...current, [resolvedUmbralId]: "" }));
      return;
    }

    setSavingUmbralById((current) => ({ ...current, [resolvedUmbralId]: true }));
    setUmbralErrorById((current) => ({ ...current, [resolvedUmbralId]: "" }));
    setUmbralSuccessById((current) => ({ ...current, [resolvedUmbralId]: "" }));

    try {
      const updatedUmbral = await updateUmbral(resolvedUmbralId, {
        valor_min: valorMin,
        valor_max: valorMax,
      });

      setUmbrales((current) =>
        current.map((umbral) => (Number(umbral.id) === resolvedUmbralId ? updatedUmbral : umbral))
      );
      setUmbralDrafts((current) => ({
        ...current,
        [resolvedUmbralId]: {
          valor_min: String(updatedUmbral.valor_min),
          valor_max: String(updatedUmbral.valor_max),
        },
      }));
      setUmbralSuccessById((current) => ({
        ...current,
        [resolvedUmbralId]: "Umbral actualizado correctamente.",
      }));
    } catch (saveError) {
      setUmbralErrorById((current) => ({
        ...current,
        [resolvedUmbralId]: resolveRequestErrorMessage(saveError, "No pudimos guardar este umbral."),
      }));
    } finally {
      setSavingUmbralById((current) => ({ ...current, [resolvedUmbralId]: false }));
    }
  }

  const lecturasOrdenadas = useMemo(() => {
    return [...lecturas].sort(compareByTimestampDesc).slice(0, 10);
  }, [lecturas]);

  const mantencionesRecientes = useMemo(() => {
    return [...mantenciones]
      .sort((current, next) => Number(next.id) - Number(current.id))
      .slice(0, 10);
  }, [mantenciones]);

  const selectedMantencion = useMemo(() => {
    return mantencionesRecientes.find((mantencion) => Number(mantencion.id) === Number(editingMantencionId)) || null;
  }, [mantencionesRecientes, editingMantencionId]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Detalle del equipo {equipoId}</h1>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
          <Button
            type="button"
            variant={showEditForm ? "primary" : "outline"}
            onClick={showEditForm ? closeEditForm : openEditForm}
            disabled={!equipo || isUpdating}
          >
            {showEditForm ? "Cerrar edición" : "Editar equipo"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleRefresh}
            disabled={
              loading ||
              isUpdating ||
              umbralesLoading ||
              isSavingAnyUmbral ||
              isCreatingMantencion ||
              isSavingMantencion
            }
          >
            {loading ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
      </div>

      {loading ? <LoadingSpinner label="Cargando detalle de equipo..." /> : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No pudimos obtener datos reales del equipo solicitado.
        </div>
      ) : null}

      {!loading && !equipo ? (
        <EmptyState
          title="Equipo no disponible"
          description="El backend no devolvió información para este equipo o todavía no existe."
        />
      ) : null}

      {equipo ? (
        <article style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
          <h2 style={{ marginTop: 0 }}>{equipo.nombre}</h2>
          <p>Estado: {equipo.estado}</p>
          <p>Ubicación: {equipo.ubicacion}</p>
          <p>Tipo: {equipo.tipo}</p>
        </article>
      ) : null}

      {equipo && showEditForm ? (
        <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
          <h2 style={{ marginTop: 0 }}>Editar equipo</h2>
          <EquipoForm
            initialValues={{
              nombre: equipo.nombre,
              ubicacion: equipo.ubicacion,
              tipo: equipo.tipo,
              estado: equipo.estado,
            }}
            submitLabel="Guardar cambios"
            onSubmit={handleUpdateEquipo}
            onCancel={closeEditForm}
            isSubmitting={isUpdating}
            errorMessage={updateErrorMessage}
          />
        </section>
      ) : null}

      <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
          <h2 style={{ marginTop: 0, marginBottom: 0 }}>Umbrales operativos</h2>
          <Button
            type="button"
            variant="outline"
            onClick={loadUmbrales}
            disabled={umbralesLoading || isSavingAnyUmbral}
          >
            {umbralesLoading ? "Cargando..." : "Recargar umbrales"}
          </Button>
        </div>
        <p style={{ marginTop: 8, color: "#6b7280" }}>
          Los cambios impactan en la evaluación de alertas para próximas lecturas de este equipo.
        </p>

        {umbralesLoading ? <LoadingSpinner label="Cargando umbrales del equipo..." /> : null}

        {umbralesErrorMessage ? (
          <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
            {umbralesErrorMessage}
          </div>
        ) : null}

        {!umbralesLoading && !umbralesErrorMessage && umbrales.length === 0 ? (
          <p style={{ marginBottom: 0, color: "#6b7280" }}>
            Este equipo no tiene umbrales configurados para editar desde la interfaz.
          </p>
        ) : null}

        {!umbralesLoading && umbrales.length > 0 ? (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">Variable</th>
                <th align="left">Valor mínimo</th>
                <th align="left">Valor máximo</th>
                <th align="left">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {umbrales.map((umbral) => {
                const resolvedUmbralId = Number(umbral.id);
                const draft = umbralDrafts[resolvedUmbralId] || {
                  valor_min: String(umbral.valor_min),
                  valor_max: String(umbral.valor_max),
                };
                const isSaving = Boolean(savingUmbralById[resolvedUmbralId]);
                const umbralErrorMessage = umbralErrorById[resolvedUmbralId];
                const umbralSuccessMessage = umbralSuccessById[resolvedUmbralId];

                return (
                  <tr key={umbral.id}>
                    <td>{formatVariableLabel(umbral.variable)}</td>
                    <td>
                      <input
                        type="number"
                        step="0.01"
                        value={draft.valor_min}
                        onChange={(event) =>
                          handleUmbralDraftChange(resolvedUmbralId, "valor_min", event.target.value)
                        }
                        disabled={isSaving}
                        aria-label={`Valor mínimo para ${umbral.variable}`}
                        style={{ padding: 8, borderRadius: 8, border: "1px solid #d1d5db", width: "100%" }}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        step="0.01"
                        value={draft.valor_max}
                        onChange={(event) =>
                          handleUmbralDraftChange(resolvedUmbralId, "valor_max", event.target.value)
                        }
                        disabled={isSaving}
                        aria-label={`Valor máximo para ${umbral.variable}`}
                        style={{ padding: 8, borderRadius: 8, border: "1px solid #d1d5db", width: "100%" }}
                      />
                    </td>
                    <td>
                      <div style={{ display: "grid", gap: 6 }}>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => handleSaveUmbral(resolvedUmbralId)}
                          disabled={isSaving}
                        >
                          {isSaving ? "Guardando..." : "Guardar"}
                        </Button>
                        {umbralErrorMessage ? (
                          <small style={{ color: "#dc2626" }} role="alert">
                            {umbralErrorMessage}
                          </small>
                        ) : null}
                        {umbralSuccessMessage ? (
                          <small style={{ color: "#15803d" }}>{umbralSuccessMessage}</small>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : null}
      </section>

      <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
        <h2 style={{ marginTop: 0 }}>Última predicción</h2>
        {prediccion ? (
          <div>
            <p style={{ marginBottom: 8 }}>Clasificación: {prediccion.clasificacion}</p>
            <strong>Probabilidad de falla: {(Number(prediccion.probabilidad || 0) * 100).toFixed(1)} %</strong>
          </div>
        ) : (
          <p style={{ marginBottom: 0, color: "#6b7280" }}>
            Todavía no hay una predicción persistida para este equipo.
          </p>
        )}
      </section>

      <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
        <h2 style={{ marginTop: 0 }}>Últimas lecturas</h2>
        {lecturasOrdenadas.length === 0 ? (
          <p style={{ marginBottom: 0, color: "#6b7280" }}>
            No hay lecturas registradas para este equipo.
          </p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">Fecha</th>
                <th align="left">Temperatura</th>
                <th align="left">Humedad</th>
                <th align="left">Vibración máx.</th>
              </tr>
            </thead>
            <tbody>
              {lecturasOrdenadas.map((lectura) => (
                <tr key={lectura.id || lectura.timestamp}>
                  <td>{formatDate(lectura.timestamp)}</td>
                  <td>{formatMetric(lectura.temperatura, "°C")}</td>
                  <td>{formatMetric(lectura.humedad, "%")}</td>
                  <td>{formatMetric(resolveMaxVibration(lectura), "g")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16, display: "grid", gap: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
          <h2 style={{ marginTop: 0, marginBottom: 0 }}>Mantenciones recientes</h2>
          <Button
            type="button"
            variant={showCreateMantencionForm ? "primary" : "outline"}
            onClick={showCreateMantencionForm ? closeCreateMantencionForm : openCreateMantencionForm}
            disabled={isCreatingMantencion || isSavingMantencion}
          >
            {showCreateMantencionForm ? "Cerrar formulario" : "Nueva mantención"}
          </Button>
        </div>

        {showCreateMantencionForm ? (
          <section style={{ padding: 12, border: "1px solid #e5e7eb", borderRadius: 12 }}>
            <h3 style={{ marginTop: 0 }}>Registrar mantención</h3>
            <MantencionForm
              onSubmit={handleCreateMantencion}
              onCancel={closeCreateMantencionForm}
              submitLabel="Registrar mantención"
              isSubmitting={isCreatingMantencion}
              errorMessage={createMantencionErrorMessage}
            />
          </section>
        ) : null}

        {mantencionesRecientes.length === 0 ? (
          <p style={{ marginBottom: 0, color: "#6b7280" }}>
            No hay mantenciones registradas para este equipo.
          </p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">ID</th>
                <th align="left">Tipo</th>
                <th align="left">Descripción</th>
                <th align="left">Estado</th>
                <th align="left">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {mantencionesRecientes.map((mantencion) => {
                const isEditing = Number(editingMantencionId) === Number(mantencion.id);

                return (
                  <tr key={mantencion.id}>
                    <td>{mantencion.id}</td>
                    <td>{mantencion.tipo}</td>
                    <td>{mantencion.descripcion}</td>
                    <td>{mantencion.estado}</td>
                    <td>
                      <Button
                        type="button"
                        variant={isEditing ? "primary" : "outline"}
                        onClick={() => (isEditing ? closeMantencionEdit() : openMantencionEdit(mantencion.id))}
                        disabled={isCreatingMantencion || isSavingMantencion}
                      >
                        {isEditing ? "Cancelar" : "Editar"}
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {selectedMantencion ? (
          <section style={{ padding: 12, border: "1px solid #e5e7eb", borderRadius: 12 }}>
            <h3 style={{ marginTop: 0 }}>Editar mantención #{selectedMantencion.id}</h3>
            <MantencionForm
              initialValues={{
                tipo: selectedMantencion.tipo,
                descripcion: selectedMantencion.descripcion,
                estado: selectedMantencion.estado,
              }}
              onSubmit={handleUpdateMantencion}
              onCancel={closeMantencionEdit}
              submitLabel="Guardar actualización"
              isSubmitting={isSavingMantencion}
              errorMessage={updateMantencionErrorMessage}
            />
          </section>
        ) : null}
      </section>
    </section>
  );
}
