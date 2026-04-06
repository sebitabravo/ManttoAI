import MantencionForm from "../mantenciones/MantencionForm";
import Button from "../ui/Button";

export default function EquipoMantencionesSection({
  showCreateMantencionForm,
  isCreatingMantencion,
  isSavingMantencion,
  openCreateMantencionForm,
  closeCreateMantencionForm,
  handleCreateMantencion,
  createMantencionErrorMessage,
  mantencionesRecientes,
  editingMantencionId,
  openMantencionEdit,
  closeMantencionEdit,
  selectedMantencion,
  handleUpdateMantencion,
  updateMantencionErrorMessage,
}) {
  return (
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
          <caption style={{ textAlign: "left", paddingBottom: 8, color: "#6b7280" }}>
            Mantenciones recientes del equipo y acciones de edición disponibles.
          </caption>
          <thead>
            <tr>
              <th scope="col" align="left">ID</th>
              <th scope="col" align="left">Tipo</th>
              <th scope="col" align="left">Descripción</th>
              <th scope="col" align="left">Estado</th>
              <th scope="col" align="left">Acciones</th>
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
  );
}
