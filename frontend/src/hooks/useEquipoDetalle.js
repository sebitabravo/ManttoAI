import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";

import { getEquipo, updateEquipo } from "../api/equipos";
import { getLecturas } from "../api/lecturas";
import { createMantencion, getMantenciones, updateMantencion } from "../api/mantenciones";
import { getPredicciones } from "../api/predicciones";
import useEquipoUmbrales from "./useEquipoUmbrales";
import { EQUIPO_DETALLE_POLLING_INTERVAL_MS } from "../utils/constants";
import { getApiErrorMessage } from "../utils/errorHandling";
import { sortByTimestampDesc } from "../utils/time";

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
 * Incluye polling automático para actualización en tiempo real.
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

  // === Control de polling ===
  // Usamos ref para trackear si hay operaciones de usuario en curso
  // y evitar que el polling interfiera con ellas
  const isUserOperationInProgress = useRef(false);

  // === Estados de edición de equipo ===
  const [showEditForm, setShowEditForm] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateErrorMessage, setUpdateErrorMessage] = useState("");

  const {
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
  } = useEquipoUmbrales(resolvedEquipoId);

  // === Estados de mantenciones ===
  const [showCreateMantencionForm, setShowCreateMantencionForm] = useState(false);
  const [isCreatingMantencion, setIsCreatingMantencion] = useState(false);
  const [createMantencionErrorMessage, setCreateMantencionErrorMessage] = useState("");
  const [editingMantencionId, setEditingMantencionId] = useState(null);
  const [isSavingMantencion, setIsSavingMantencion] = useState(false);
  const [updateMantencionErrorMessage, setUpdateMantencionErrorMessage] = useState("");

  // === Carga de datos del equipo ===
  const loadEquipoDetalle = useCallback(async (isPolling = false) => {
    if (!Number.isFinite(resolvedEquipoId)) {
      setError(new Error("Identificador de equipo inválido"));
      setLoading(false);
      return;
    }

    // Si es polling y hay operación de usuario en curso, saltear esta actualización
    if (isPolling && isUserOperationInProgress.current) {
      return;
    }

    // Solo mostrar loading en carga inicial, no en polling (stale-while-revalidate)
    if (!isPolling) {
      setLoading(true);
    }

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
      // En polling, no mostrar error si ya tenemos datos (stale-while-revalidate)
      // Keep showing old data instead of error
      if (isPolling && equipo) {
        console.warn("Polling failed, keeping previous data:", fetchError.message);
      } else {
        setError(fetchError);
      }
    } finally {
      setLoading(false);
    }
  }, [resolvedEquipoId, equipo]);

  // Carga inicial
  useEffect(() => {
    loadEquipoDetalle(false);
  }, [loadEquipoDetalle]);

  // Polling automático
  useEffect(() => {
    const timer = window.setInterval(() => {
      loadEquipoDetalle(true);
    }, EQUIPO_DETALLE_POLLING_INTERVAL_MS);

    return () => window.clearInterval(timer);
  }, [loadEquipoDetalle]);

  // === Valores computados ===
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
    loadEquipoDetalle(false);
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
    isUserOperationInProgress.current = true;

    try {
      await updateEquipo(resolvedEquipoId, payload);
      await loadEquipoDetalle(false);
      setShowEditForm(false);
    } catch (updateError) {
      setUpdateErrorMessage(
        getApiErrorMessage(updateError, "No pudimos actualizar el equipo. Revisá los datos ingresados.")
      );
    } finally {
      setIsUpdating(false);
      isUserOperationInProgress.current = false;
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
    isUserOperationInProgress.current = true;

    try {
      await createMantencion({
        equipo_id: resolvedEquipoId,
        ...payload,
      });
      await loadEquipoDetalle(false);
      setEditingMantencionId(null);
      setShowCreateMantencionForm(false);
    } catch (createError) {
      setCreateMantencionErrorMessage(
        getApiErrorMessage(createError, "No pudimos crear la mantención. Revisá los datos ingresados.")
      );
    } finally {
      setIsCreatingMantencion(false);
      isUserOperationInProgress.current = false;
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
    isUserOperationInProgress.current = true;

    try {
      await updateMantencion(resolvedMantencionId, payload);
      await loadEquipoDetalle(false);
      setEditingMantencionId(null);
    } catch (updateError) {
      setUpdateMantencionErrorMessage(
        getApiErrorMessage(updateError, "No pudimos actualizar la mantención. Revisá los datos ingresados.")
      );
    } finally {
      setIsSavingMantencion(false);
      isUserOperationInProgress.current = false;
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

    // Polling info (para mostrar en UI)
    pollingIntervalMs: EQUIPO_DETALLE_POLLING_INTERVAL_MS,
  };
}
