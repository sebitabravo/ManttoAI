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
    <section className="grid gap-3 rounded-lg border border-neutral-200 bg-neutral-100 p-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="mb-0 mt-0 text-lg font-semibold text-neutral-900">Mantenciones recientes</h2>
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
        <div className="border-t border-neutral-200 pt-3">
          <h3 className="mt-0 text-base font-semibold text-neutral-900">Registrar mantención</h3>
          <MantencionForm
            onSubmit={handleCreateMantencion}
            onCancel={closeCreateMantencionForm}
            submitLabel="Registrar mantención"
            isSubmitting={isCreatingMantencion}
            errorMessage={createMantencionErrorMessage}
          />
        </div>
      ) : null}

      {mantencionesRecientes.length === 0 ? (
        <p className="mb-0 text-sm text-neutral-600">
          No hay mantenciones registradas para este equipo.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <caption className="pb-2 text-left text-sm text-neutral-600">
              Mantenciones recientes del equipo y acciones de edición disponibles.
            </caption>
            <thead>
              <tr className="border-b border-neutral-200">
                <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">ID</th>
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
                  <tr key={mantencion.id} className="hover:bg-neutral-50 transition-colors duration-150">
                    <td className="py-2 pr-4 text-sm tabular-nums text-neutral-900">{mantencion.id}</td>
                    <td className="py-2 pr-4 text-sm text-neutral-900">{mantencion.tipo}</td>
                    <td className="py-2 pr-4 text-sm text-neutral-700">{mantencion.descripcion}</td>
                    <td className="py-2 pr-4 text-sm text-neutral-900">{mantencion.estado}</td>
                    <td className="py-2">
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
        </div>
      )}

      {selectedMantencion ? (
        <div className="border-t border-neutral-200 pt-3">
          <h3 className="mt-0 text-base font-semibold text-neutral-900">Editar mantención #{selectedMantencion.id}</h3>
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
        </div>
      ) : null}
    </section>
  );
}
