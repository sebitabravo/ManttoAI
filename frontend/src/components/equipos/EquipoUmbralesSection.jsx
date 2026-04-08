import Button from "../ui/Button";
import { SkeletonTable } from "../ui/Skeleton";

export default function EquipoUmbralesSection({
  loadUmbrales,
  umbralesLoading,
  isSavingAnyUmbral,
  umbralesErrorMessage,
  umbrales,
  umbralDrafts,
  savingUmbralById,
  umbralErrorById,
  umbralSuccessById,
  handleUmbralDraftChange,
  handleSaveUmbral,
  formatVariableLabel,
}) {
  return (
    <section className="rounded-lg border border-neutral-300 bg-neutral-100 p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h2 className="mb-0 mt-0 text-lg font-semibold text-neutral-900">Umbrales operativos</h2>
        <Button
          type="button"
          variant="outline"
          onClick={loadUmbrales}
          disabled={umbralesLoading || isSavingAnyUmbral}
        >
          {umbralesLoading ? "Cargando..." : "Recargar umbrales"}
        </Button>
      </div>
      <p className="mt-2 text-sm text-neutral-600">
        Los cambios impactan en la evaluación de alertas para próximas lecturas de este equipo.
      </p>

      {umbralesLoading ? <SkeletonTable rows={3} cols={4} className="mt-2" /> : null}

      {umbralesErrorMessage ? (
        <div className="rounded-lg border border-warning-300 bg-warning-50 px-3 py-2 text-sm text-warning-800">
          {umbralesErrorMessage}
        </div>
      ) : null}

      {!umbralesLoading && !umbralesErrorMessage && umbrales.length === 0 ? (
        <p className="mb-0 text-sm text-neutral-600">
          Este equipo no tiene umbrales configurados para editar desde la interfaz.
        </p>
      ) : null}

      {!umbralesLoading && umbrales.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <caption className="pb-2 text-left text-sm text-neutral-600">
              Umbrales operativos editables para las próximas evaluaciones del equipo.
            </caption>
            <thead>
              <tr className="border-b border-neutral-200">
                <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Variable</th>
                <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Valor mínimo</th>
                <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Valor máximo</th>
                <th scope="col" className="pb-2 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {umbrales.map((umbral) => {
                const resolvedUmbralId = Number(umbral.id);
                const draft = umbralDrafts[resolvedUmbralId] || {
                  valor_min: String(umbral.valor_min),
                  valor_max: String(umbral.valor_max),
                };
                const isSaving = Boolean(savingUmbralById[resolvedUmbralId]);
                const umbralErrorMessageById = umbralErrorById[resolvedUmbralId];
                const umbralSuccessMessage = umbralSuccessById[resolvedUmbralId];

                return (
                  <tr key={umbral.id} className="hover:bg-neutral-50 transition-colors duration-150 ease-out-quart">
                    <td className="py-2 pr-4 text-sm font-medium text-neutral-900">{formatVariableLabel(umbral.variable)}</td>
                    <td className="py-2 pr-4">
                      <input
                        type="number"
                        step="0.01"
                        value={draft.valor_min}
                        onChange={(event) =>
                          handleUmbralDraftChange(resolvedUmbralId, "valor_min", event.target.value)
                        }
                        disabled={isSaving}
                        aria-label={`Valor mínimo para ${umbral.variable}`}
                        className="w-full min-h-[44px] rounded border border-neutral-300 bg-neutral-100 px-3 py-2.5 text-sm tabular-nums shadow-sm transition-all duration-150 ease-out-quart focus:border-primary-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:cursor-not-allowed disabled:bg-neutral-100 disabled:text-neutral-500"
                      />
                    </td>
                    <td className="py-2 pr-4">
                      <input
                        type="number"
                        step="0.01"
                        value={draft.valor_max}
                        onChange={(event) =>
                          handleUmbralDraftChange(resolvedUmbralId, "valor_max", event.target.value)
                        }
                        disabled={isSaving}
                        aria-label={`Valor máximo para ${umbral.variable}`}
                        className="w-full min-h-[44px] rounded border border-neutral-300 bg-neutral-100 px-3 py-2.5 text-sm tabular-nums shadow-sm transition-all duration-150 ease-out-quart focus:border-primary-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:cursor-not-allowed disabled:bg-neutral-100 disabled:text-neutral-500"
                      />
                    </td>
                    <td className="py-2">
                      <div className="grid gap-1.5">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => handleSaveUmbral(resolvedUmbralId)}
                          disabled={isSaving}
                        >
                          {isSaving ? "Guardando..." : "Guardar"}
                        </Button>
                        {umbralErrorMessageById ? (
                          <small className="text-xs text-danger-600" role="alert">
                            {umbralErrorMessageById}
                          </small>
                        ) : null}
                        {umbralSuccessMessage ? (
                          <small className="text-xs text-success-700" aria-live="polite">
                            {umbralSuccessMessage}
                          </small>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
