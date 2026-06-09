import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { createMantencion, getMantenciones, updateMantencion } from "../api/mantenciones";
import { getApiErrorMessage } from "../utils/errorHandling";
import { sortByTimestampDesc } from "../utils/time";

/**
 * Hook que encapsula la logica de estado y operaciones de mantenciones
 * para la pagina de detalle de equipo.
 *
 * Maneja: carga de mantenciones, creacion, edicion, y estados de UI asociados.
 *
 * @param {number} resolvedEquipoId - ID del equipo (ya normalizado a numero)
 * @returns {Object} Estado y handlers de mantenciones
 */
export default function useMantenciones(resolvedEquipoId) {
  // === Estado de datos ===
  const [mantenciones, setMantenciones] = useState([]);

  // === Control de polling (evitar interferencia con operaciones de usuario) ===
  const isUserOperationInProgress = useRef(false);

  // === Estado de UI de creacion ===
  const [showCreateMantencionForm, setShowCreateMantencionForm] = useState(false);
  const [isCreatingMantencion, setIsCreatingMantencion] = useState(false);
  const [createMantencionErrorMessage, setCreateMantencionErrorMessage] = useState("");

  // === Estado de UI de edicion ===
  const [editingMantencionId, setEditingMantencionId] = useState(null);
  const [isSavingMantencion, setIsSavingMantencion] = useState(false);
  const [updateMantencionErrorMessage, setUpdateMantencionErrorMessage] = useState("");

  // === Valores computados ===
  const mantencionesRecientes = useMemo(() => {
    return sortByTimestampDesc(mantenciones).slice(0, 10);
  }, [mantenciones]);

  const selectedMantencion = useMemo(() => {
    return mantencionesRecientes.find(
      (mantencion) => Number(mantencion.id) === Number(editingMantencionId)
    ) || null;
  }, [mantencionesRecientes, editingMantencionId]);

  // === Carga de datos ===
  const loadMantenciones = useCallback(async (isPolling = false) => {
    if (!Number.isFinite(resolvedEquipoId)) return;

    if (isPolling && isUserOperationInProgress.current) {
      return;
    }

    try {
      const data = await getMantenciones({
        equipoId: resolvedEquipoId,
        limit: 10,
        order: "desc",
      });
      setMantenciones(Array.isArray(data) ? data : []);
    } catch (fetchError) {
      if (isPolling) {
        console.warn("Mantenciones polling failed, keeping previous data:", fetchError.message);
      }
    }
  }, [resolvedEquipoId]);

  // Carga inicial al montar
  useEffect(() => {
    if (Number.isFinite(resolvedEquipoId)) {
      loadMantenciones(false);
    }
  }, [loadMantenciones, resolvedEquipoId]);

  // === Handlers de UI de creacion ===
  function openCreateMantencionForm() {
    setCreateMantencionErrorMessage("");
    setEditingMantencionId(null);
    setShowCreateMantencionForm(true);
  }

  function closeCreateMantencionForm() {
    setCreateMantencionErrorMessage("");
    setShowCreateMantencionForm(false);
  }

  // === Handlers de UI de edicion ===
  function openMantencionEdit(mantencionId) {
    setShowCreateMantencionForm(false);
    setEditingMantencionId(Number(mantencionId));
    setUpdateMantencionErrorMessage("");
  }

  function closeMantencionEdit() {
    setEditingMantencionId(null);
    setUpdateMantencionErrorMessage("");
  }

  // === CRUD: Crear mantención ===
  async function handleCreateMantencion(payload) {
    if (!Number.isFinite(resolvedEquipoId)) {
      setCreateMantencionErrorMessage(
        "No se puede crear mantención: identificador de equipo inválido."
      );
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
      await loadMantenciones(false);
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

  // === CRUD: Actualizar mantención ===
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
      await loadMantenciones(false);
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
    loadMantenciones,
  };
}
