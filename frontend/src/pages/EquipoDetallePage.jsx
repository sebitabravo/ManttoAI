import EquipoLecturasSection from "../components/equipos/EquipoLecturasSection";
import EquipoForm from "../components/equipos/EquipoForm";
import EquipoMantencionesSection from "../components/equipos/EquipoMantencionesSection";
import EquipoPrediccionCard from "../components/equipos/EquipoPrediccionCard";
import EquipoResumenCard from "../components/equipos/EquipoResumenCard";
import EquipoUmbralesSection from "../components/equipos/EquipoUmbralesSection";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import Button from "../components/ui/Button";
import useEquipoDetalle, { formatVariableLabel } from "../hooks/useEquipoDetalle";

export default function EquipoDetallePage() {
  const {
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

    // Polling
    pollingIntervalMs,
  } = useEquipoDetalle();

  // Solo mostrar loading spinner en carga inicial
  const isInitialLoading = loading && !equipo;

  return (
    <section className="grid gap-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="m-0 text-xl font-semibold text-neutral-900">Detalle del equipo {equipoId}</h1>
            {loading && equipo ? (
              <span className="inline-flex items-center gap-1.5 text-xs text-neutral-500">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary-500 animate-pulse" aria-hidden="true" />
                Actualizando
              </span>
            ) : null}
          </div>
          <p className="mb-0 mt-1.5 text-sm text-neutral-600">
            Lecturas, predicciones y mantenciones en tiempo real.
            <span className="ml-2 text-xs text-neutral-500">
              (actualización automática cada {pollingIntervalMs / 1000}s)
            </span>
          </p>
        </div>
        <div className="flex flex-wrap justify-end gap-2">
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

      {isInitialLoading ? <LoadingSpinner label="Cargando detalle de equipo..." /> : null}

      {error ? (
        <div className="rounded-lg border border-warning-300 bg-warning-50 px-3 py-2 text-sm text-warning-800">
          No pudimos obtener datos reales del equipo solicitado. Se mantienen los últimos datos disponibles.
        </div>
      ) : null}

      {!isInitialLoading && !equipo ? (
        <EmptyState
          title="Equipo no disponible"
          description="El backend no devolvió información para este equipo o todavía no existe."
        />
      ) : null}

      <EquipoResumenCard equipo={equipo} />

      {equipo && showEditForm ? (
        <section className="rounded-lg border border-neutral-200 bg-neutral-100 p-4">
          <h2 className="mt-0 text-lg font-semibold text-neutral-900">Editar equipo</h2>
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

      <EquipoUmbralesSection
        loadUmbrales={loadUmbrales}
        umbralesLoading={umbralesLoading}
        isSavingAnyUmbral={isSavingAnyUmbral}
        umbralesErrorMessage={umbralesErrorMessage}
        umbrales={umbrales}
        umbralDrafts={umbralDrafts}
        savingUmbralById={savingUmbralById}
        umbralErrorById={umbralErrorById}
        umbralSuccessById={umbralSuccessById}
        handleUmbralDraftChange={handleUmbralDraftChange}
        handleSaveUmbral={handleSaveUmbral}
        formatVariableLabel={formatVariableLabel}
      />

      <EquipoPrediccionCard prediccion={prediccion} />

      <EquipoLecturasSection lecturas={lecturasOrdenadas} />

      <EquipoMantencionesSection
        showCreateMantencionForm={showCreateMantencionForm}
        isCreatingMantencion={isCreatingMantencion}
        isSavingMantencion={isSavingMantencion}
        openCreateMantencionForm={openCreateMantencionForm}
        closeCreateMantencionForm={closeCreateMantencionForm}
        handleCreateMantencion={handleCreateMantencion}
        createMantencionErrorMessage={createMantencionErrorMessage}
        mantencionesRecientes={mantencionesRecientes}
        editingMantencionId={editingMantencionId}
        openMantencionEdit={openMantencionEdit}
        closeMantencionEdit={closeMantencionEdit}
        selectedMantencion={selectedMantencion}
        handleUpdateMantencion={handleUpdateMantencion}
        updateMantencionErrorMessage={updateMantencionErrorMessage}
      />
    </section>
  );
}
