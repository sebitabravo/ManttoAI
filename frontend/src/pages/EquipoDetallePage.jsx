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
  } = useEquipoDetalle();

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

      <EquipoResumenCard equipo={equipo} />

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
