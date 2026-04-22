import { useState } from "react";
import { Link } from "react-router-dom";
import { getConfigPrediccion, formatPorcentajeRiesgo } from "../../utils/prediccion";
import { deleteEquipo } from "../../api/equipos";
import Modal from "../ui/Modal";
import Button from "../ui/Button";

/**
 * Badge visual que muestra el estado de predicción del equipo.
 * Usa colores semánticos según la clasificación del modelo ML.
 */
function PrediccionBadge({ clasificacion, probabilidad }) {
  const config = getConfigPrediccion(clasificacion);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${config.chipClass}`}
      title={probabilidad != null ? `Probabilidad de falla: ${formatPorcentajeRiesgo(probabilidad)}` : undefined}
    >
      <span aria-hidden="true" className={`h-2 w-2 rounded-full ${config.dotClass}`} />
      {config.label}
      {probabilidad != null && (
        <span className="font-normal opacity-75">
          {" "}· {formatPorcentajeRiesgo(probabilidad)}
        </span>
      )}
    </span>
  );
}

export default function EquipoCard({ equipo, onDeleted }) {
  const latestValueLabel = equipo.dato || "Sin lecturas registradas";
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  async function handleDelete() {
    setIsDeleting(true);
    setDeleteError("");
    try {
      await deleteEquipo(equipo.id);
      setShowDeleteModal(false);
      onDeleted?.();
    } catch {
      setDeleteError("No se pudo eliminar el equipo. Probá nuevamente.");
    } finally {
      setIsDeleting(false);
    }
  }

  // Datos de predicción enriquecidos desde EquiposPage
  const clasificacion = equipo.ultima_clasificacion ?? null;
  const probabilidad = equipo.ultima_probabilidad ?? null;

  return (
    <>
      {/* Comentario: Aplicando estilo Apple — eliminar borde exterior, usar fondo blanco y sombra sutil */}
      <article className="flex flex-col gap-2 rounded-2xl bg-white p-4 shadow-sm transition-all duration-150 ease-out-quart hover:shadow-[rgba(0,0,0,0.22)_3px_5px_30px_0px]">
        <div className="flex items-start justify-between gap-2">
          <h2 className="mb-1 mt-0 text-base font-semibold text-neutral-900">{equipo.nombre}</h2>
          <button
            type="button"
            onClick={() => setShowDeleteModal(true)}
            className="shrink-0 rounded px-2 py-1 text-xs text-neutral-400 transition-colors hover:bg-danger-50 hover:text-danger-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-danger-500"
            aria-label={`Eliminar ${equipo.nombre}`}
          >
            ✕
          </button>
        </div>

        {/* Indicador visual de predicción */}
        <PrediccionBadge clasificacion={clasificacion} probabilidad={probabilidad} />

        <p className="m-0 text-sm text-neutral-700">Estado: {equipo.estado}</p>
        {equipo.tipo ? <p className="m-0 text-sm text-neutral-700">Tipo: {equipo.tipo}</p> : null}
        {equipo.ubicacion ? <p className="m-0 text-sm text-neutral-700">Ubicación: {equipo.ubicacion}</p> : null}
        <p className="m-0 text-sm text-neutral-700">Último dato: <span className="tabular-nums">{latestValueLabel}</span></p>
        {typeof equipo.alertas_activas === "number" ? (
          <p className="m-0 text-sm text-neutral-700">Alertas activas: <span className="tabular-nums font-semibold text-danger-600">{equipo.alertas_activas}</span></p>
        ) : null}

        <Link
          to={`/equipos/${equipo.id}`}
          aria-label={`Ver detalle ${equipo.nombre}`}
          className="mt-1 text-sm font-medium text-primary-500 transition-colors duration-150 ease-out-quart hover:text-primary-600 hover:underline focus:outline-none focus-visible:rounded-sm focus-visible:ring-2 focus-visible:ring-primary-500"
        >
          Ver detalle
        </Link>
      </article>

      <Modal open={showDeleteModal} onClose={() => setShowDeleteModal(false)} title="Eliminar equipo">
        <div className="space-y-4">
          <p className="text-sm text-neutral-600">
            ¿Estás seguro de que querés eliminar <strong>{equipo.nombre}</strong>? Esta acción eliminará todas las lecturas, alertas y mantenciones asociadas.
          </p>
          {deleteError ? (
            <p className="text-sm text-danger-600" role="alert">{deleteError}</p>
          ) : null}
          <div className="flex justify-end space-x-3">
            <Button type="button" variant="outline" onClick={() => setShowDeleteModal(false)} disabled={isDeleting}>
              Cancelar
            </Button>
            <Button type="button" variant="danger" onClick={handleDelete} disabled={isDeleting}>
              {isDeleting ? "Eliminando..." : "Eliminar"}
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
