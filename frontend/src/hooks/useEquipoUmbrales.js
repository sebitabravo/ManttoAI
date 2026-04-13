import { useCallback, useEffect, useMemo, useState } from "react";

import { getUmbrales, updateUmbral } from "../api/umbrales";
import { getApiErrorMessage } from "../utils/errorHandling";

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
 * Maneja estado, carga y edición de umbrales asociados a un equipo.
 * @param {number} resolvedEquipoId - Identificador numérico del equipo
 * @returns {Object} Estado y acciones para la gestión de umbrales
 */
export default function useEquipoUmbrales(resolvedEquipoId) {
  const [umbrales, setUmbrales] = useState([]);
  const [umbralDrafts, setUmbralDrafts] = useState({});
  const [umbralesLoading, setUmbralesLoading] = useState(true);
  const [umbralesErrorMessage, setUmbralesErrorMessage] = useState("");
  const [savingUmbralById, setSavingUmbralById] = useState({});
  const [umbralErrorById, setUmbralErrorById] = useState({});
  const [umbralSuccessById, setUmbralSuccessById] = useState({});

  const loadUmbrales = useCallback(async () => {
    if (!Number.isFinite(resolvedEquipoId)) {
      setUmbralesErrorMessage("No se pueden cargar umbrales: identificador de equipo inválido.");
      setUmbralesLoading(false);
      return;
    }

    setUmbralesLoading(true);
    setUmbralesErrorMessage("");

    try {
      const umbralesData = await getUmbrales(resolvedEquipoId);
      const umbralesEquipo = Array.isArray(umbralesData) ? umbralesData : [];

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

  const isSavingAnyUmbral = useMemo(() => {
    return Object.values(savingUmbralById).some(Boolean);
  }, [savingUmbralById]);

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

  return {
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
  };
}
