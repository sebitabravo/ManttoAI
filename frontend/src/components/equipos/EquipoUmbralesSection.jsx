import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";

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
    <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h2 style={{ marginTop: 0, marginBottom: 0 }}>Umbrales operativos</h2>
        <Button
          type="button"
          variant="outline"
          onClick={loadUmbrales}
          disabled={umbralesLoading || isSavingAnyUmbral}
        >
          {umbralesLoading ? "Cargando..." : "Recargar umbrales"}
        </Button>
      </div>
      <p style={{ marginTop: 8, color: "#6b7280" }}>
        Los cambios impactan en la evaluación de alertas para próximas lecturas de este equipo.
      </p>

      {umbralesLoading ? <LoadingSpinner label="Cargando umbrales del equipo..." /> : null}

      {umbralesErrorMessage ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          {umbralesErrorMessage}
        </div>
      ) : null}

      {!umbralesLoading && !umbralesErrorMessage && umbrales.length === 0 ? (
        <p style={{ marginBottom: 0, color: "#6b7280" }}>
          Este equipo no tiene umbrales configurados para editar desde la interfaz.
        </p>
      ) : null}

      {!umbralesLoading && umbrales.length > 0 ? (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <caption style={{ textAlign: "left", paddingBottom: 8, color: "#6b7280" }}>
            Umbrales operativos editables para las próximas evaluaciones del equipo.
          </caption>
          <thead>
            <tr>
              <th scope="col" align="left">Variable</th>
              <th scope="col" align="left">Valor mínimo</th>
              <th scope="col" align="left">Valor máximo</th>
              <th scope="col" align="left">Acciones</th>
            </tr>
          </thead>
          <tbody>
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
                <tr key={umbral.id}>
                  <td>{formatVariableLabel(umbral.variable)}</td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      value={draft.valor_min}
                      onChange={(event) =>
                        handleUmbralDraftChange(resolvedUmbralId, "valor_min", event.target.value)
                      }
                      disabled={isSaving}
                      aria-label={`Valor mínimo para ${umbral.variable}`}
                      style={{ padding: 8, borderRadius: 8, border: "1px solid #d1d5db", width: "100%" }}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      value={draft.valor_max}
                      onChange={(event) =>
                        handleUmbralDraftChange(resolvedUmbralId, "valor_max", event.target.value)
                      }
                      disabled={isSaving}
                      aria-label={`Valor máximo para ${umbral.variable}`}
                      style={{ padding: 8, borderRadius: 8, border: "1px solid #d1d5db", width: "100%" }}
                    />
                  </td>
                  <td>
                    <div style={{ display: "grid", gap: 6 }}>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => handleSaveUmbral(resolvedUmbralId)}
                        disabled={isSaving}
                      >
                        {isSaving ? "Guardando..." : "Guardar"}
                      </Button>
                      {umbralErrorMessageById ? (
                        <small style={{ color: "#dc2626" }} role="alert">
                          {umbralErrorMessageById}
                        </small>
                      ) : null}
                      {umbralSuccessMessage ? (
                        <small style={{ color: "#15803d" }} aria-live="polite">
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
      ) : null}
    </section>
  );
}
