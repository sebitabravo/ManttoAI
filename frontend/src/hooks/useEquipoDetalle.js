import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { getEquipo, updateEquipo } from "../api/equipos";
import { getLecturas } from "../api/lecturas";
import { createMantencion, getMantenciones, updateMantencion } from "../api/mantenciones";
import { getPredicciones } from "../api/predicciones";
import { getUmbrales, updateUmbral } from "../api/umbrales";
import { getApiErrorMessage } from "../utils/errorHandling";
import { sortByTimestampDesc } from "../utils/time";

/**
 * Normaliza entrada decimal: remueve espacios y reemplaza coma por punto.
 * @param {string|number|null} value - Valor a normalizar
 * @returns {string} Valor normalizado como string
 */
function normalizeDecimalInput(value) {
  return String(value ?? "").trim().replace(",", ".");
}

/**
 * Construye objeto de drafts para edición de umbrales.
 * @param {Array} umbrales - Lista de umbrales del equipo
 * @returns {Object} Objeto con umbralId como key y {valor_min, valor_max} como value
 */
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

/**
 * Formatea nombre de variable para mostrar en UI.
 * @param {string} variable - Nombre de variable (ej: "temperatura", "vib_x")
 * @returns {string} Label formateado (ej: "Temperatura", "Vib x")
 */
export function formatVariableLabel(variable) {
  if (typeof variable !== "string" || !variable.trim()) {
    return "Variable";
  }

  const normalizedVariable = variable.trim().replaceAll("_", " ").toLowerCase();
  return normalizedVariable.charAt(0).toUpperCase() + normalizedVariable.slice(1);
}

/**
 * Hook que encapsula toda la lógica de estado y operaciones para la página de detalle de equipo.
 * Maneja: datos del equipo, lecturas, predicciones, mantenciones y umbrales.
 *
 * @returns {Object} Estado y handlers para el componente EquipoDetallePage
 */
export default function useEquipoDetalle() {
  const { equipoId } = useParams();
  const resolvedEquipoId = Number(equipoId);

  // === Estados principales del equipo ===
  const [equipo, setEquipo] = useState(null);
  const [lecturas, setLecturas] = useState([]);
  const [prediccion, setPrediccion] = useState(null);
  const [mantenciones, setMantenciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // === Estados de edición de equipo ===
  const [showEditForm, setShowEditForm] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateErrorMessage, setUpdateErrorMessage] = useState("");

  // === Estados de umbrales ===
  const [umbrales, setUmbrales] = useState([]);
  const [umbralDrafts, setUmbralDrafts] = useState({});
  const [umbralesLoading, setUmbralesLoading] = useState(true);
  const [umbralesErrorMessage, setUmbralesErrorMessage] = useState("");
  const [savingUmbralById, setSavingUmbralById] = useState({});
  const [umbralErrorById, setUmbralErrorById] = useState({});
  const [umbralSuccessById, setUmbralSuccessById] = useState({});

  // === Estados de mantenciones ===
  const [showCreateMantencionForm, setShowCreateMantencionForm] = useState(false);
  const [isCreatingMantencion, setIsCreatingMantencion] = useState(false);
  const [createMantencionErrorMessage, setCreateMantencionErrorMessage] = useState("");
  const [editingMantencionId, setEditingMantencionId] = useState(null);
  const [isSavingMantencion, setIsSavingMantencion] = useState(false);
  const [updateMantencionErrorMessage, setUpdateMantencionErrorMessage] = useState("");

  // === Carga de datos del equipo ===
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
        getLecturas(resolvedEquipoId, 10),
        getPredicciones(resolvedEquipoId).catch((fetchError) => {
          if (fetchError?.response?.status === 404) {
            return null;
          }

          throw fetchError;
        }),
        getMantenciones({ equipoId: resolvedEquipoId, limit: 10, order: "desc" }),
      ]);

      setEquipo(equipoData);
      setLecturas(Array.isArray(lecturasData) ? lecturasData : []);
      setPrediccion(prediccionData);
      setMantenciones(Array.isArray(mantencionesData) ? mantencionesData : []);
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

  // === Carga de umbrales ===
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
      const umbralesEquipo = (Array.isArray(umbralesData) ? umbralesData : []).filter(
        (umbral) => Number(umbral.equipo_id) === resolvedEquipoId
      );

      setUmbrales(umbralesEquipo);
      setUmbralDrafts(buildUmbralDrafts(umbralesEquipo));
      setSavingUmbralById({});
      setUmbralErrorById({});
      setUmbralSuccessById({});
    } catch (fetchError) {
      setUmbralesErrorMessage(
        getApiErrorMessage(
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

  // === Valores computados ===
  const isSavingAnyUmbral = useMemo(() => {
    return Object.values(savingUmbralById).some(Boolean);
  }, [savingUmbralById]);

  const lecturasOrdenadas = useMemo(() => {
    return sortByTimestampDesc(lecturas).slice(0, 10);
  }, [lecturas]);

  const mantencionesRecientes = useMemo(() => {
    return sortByTimestampDesc(mantenciones).slice(0, 10);
  }, [mantenciones]);

  const selectedMantencion = useMemo(() => {
    return mantencionesRecientes.find((mantencion) => Number(mantencion.id) === Number(editingMantencionId)) || null;
  }, [mantencionesRecientes, editingMantencionId]);

  // === Handlers de refresh ===
  function handleRefresh() {
    loadEquipoDetalle();
    loadUmbrales();
  }

  // === Handlers de equipo ===
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
      setShowEditForm(false);
    } catch (updateError) {
      setUpdateErrorMessage(
        getApiErrorMessage(updateError, "No pudimos actualizar el equipo. Revisá los datos ingresados.")
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

  // === Handlers de mantenciones ===
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
      setEditingMantencionId(null);
      setShowCreateMantencionForm(false);
    } catch (createError) {
      setCreateMantencionErrorMessage(
        getApiErrorMessage(createError, "No pudimos crear la mantención. Revisá los datos ingresados.")
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
      setEditingMantencionId(null);
    } catch (updateError) {
      setUpdateMantencionErrorMessage(
        getApiErrorMessage(updateError, "No pudimos actualizar la mantención. Revisá los datos ingresados.")
      );
    } finally {
      setIsSavingMantencion(false);
    }
  }

  // === Handlers de umbrales ===
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

    const valorMin = Number.parseFloat(normalizeDecimalInput(draft.valor_min));
    const valorMax = Number.parseFloat(normalizeDecimalInput(draft.valor_max));

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
        [resolvedUmbralId]: getApiErrorMessage(saveError, "No pudimos guardar este umbral."),
      }));
    } finally {
      setSavingUmbralById((current) => ({ ...current, [resolvedUmbralId]: false }));
    }
  }

  // === Retorno del hook ===
  return {
    // Identificador
    equipoId,

    // Estado principal
    equipo,
    loading,
    error,

    // Lecturas
    lecturasOrdenadas,

    // Predicción
    prediccion,

    // Edición de equipo
    showEditForm,
    isUpdating,
    updateErrorMessage,
    openEditForm,
    closeEditForm,
    handleUpdateEquipo,

    // Umbrales
    umbrales,
    umbralDrafts,
    umbralesLoading,
    umbralesErrorMessage,
    savingUmbralById,
    umbralErrorById,
    umbralSuccessById,
    isSavingAnyUmbral,
    loadUmbrales,
    handleUmbralDraftChange,
    handleSaveUmbral,

    // Mantenciones
    mantencionesRecientes,
    showCreateMantencionForm,
    isCreatingMantencion,
    createMantencionErrorMessage,
    editingMantencionId,
    selectedMantencion,
    isSavingMantencion,
    updateMantencionErrorMessage,
    openCreateMantencionForm,
    closeCreateMantencionForm,
    openMantencionEdit,
    closeMantencionEdit,
    handleCreateMantencion,
    handleUpdateMantencion,

    // Refresh
    handleRefresh,
  };
}
