import { useEffect, useState } from "react";

import Button from "../ui/Button";
import Input from "../ui/Input";

const TIPOS_MANTENCION = [
  { value: "preventiva", label: "Preventiva" },
  { value: "correctiva", label: "Correctiva" },
  { value: "predictiva", label: "Predictiva" },
  { value: "emergencia", label: "Emergencia" },
];

const ESTADOS_MANTENCION = [
  { value: "programada", label: "Programada" },
  { value: "en_progreso", label: "En progreso" },
  { value: "ejecutada", label: "Ejecutada" },
  { value: "cancelada", label: "Cancelada" },
];

const selectClassName = "w-full min-h-[44px] rounded-md border border-neutral-300 bg-white px-3 py-2.5 text-sm text-neutral-900 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200 disabled:cursor-not-allowed disabled:opacity-60";

const DEFAULT_VALUES = {
  tipo: "preventiva",
  descripcion: "",
  estado: "programada",
};

function resolveInitialValues(initialValues) {
  return {
    tipo: typeof initialValues?.tipo === "string" ? initialValues.tipo : DEFAULT_VALUES.tipo,
    descripcion:
      typeof initialValues?.descripcion === "string" ? initialValues.descripcion : DEFAULT_VALUES.descripcion,
    estado: typeof initialValues?.estado === "string" ? initialValues.estado : DEFAULT_VALUES.estado,
  };
}

function validateForm(values) {
  const fieldErrors = {};

  if (!values.tipo.trim()) {
    fieldErrors.tipo = "El tipo de mantención es obligatorio.";
  }

  if (!values.descripcion.trim()) {
    fieldErrors.descripcion = "La descripción es obligatoria.";
  }

  if (!values.estado.trim()) {
    fieldErrors.estado = "El estado es obligatorio.";
  }

  return fieldErrors;
}

export default function MantencionForm({
  initialValues,
  onSubmit,
  onCancel,
  submitLabel = "Guardar mantención",
  isSubmitting = false,
  errorMessage = "",
}) {
  const [form, setForm] = useState(() => resolveInitialValues(initialValues));
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState("");

  useEffect(() => {
    setForm(resolveInitialValues(initialValues));
    setErrors({});
    setSubmitError("");
  }, [initialValues]);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: undefined }));
    setSubmitError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitError("");

    const fieldErrors = validateForm(form);
    if (Object.keys(fieldErrors).length > 0) {
      setErrors(fieldErrors);
      return;
    }

    const payload = {
      tipo: form.tipo.trim(),
      descripcion: form.descripcion.trim(),
      estado: form.estado.trim(),
    };

    try {
      await onSubmit(payload);
    } catch {
      setSubmitError("No pudimos guardar la mantención. Probá nuevamente.");
    }
  }

  const resolvedErrorMessage = errorMessage || submitError;

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-3">
      <div>
        <label htmlFor="mantencion-tipo" className="block mb-1 text-sm font-medium text-neutral-700">
          Tipo
        </label>
        <select
          id="mantencion-tipo"
          name="tipo"
          value={form.tipo}
          onChange={handleChange}
          disabled={isSubmitting}
          required
          className={selectClassName}
        >
          {TIPOS_MANTENCION.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        {errors.tipo ? <p className="mt-1 text-xs text-danger-600">{errors.tipo}</p> : null}
      </div>
      <Input
        label="Descripción"
        name="descripcion"
        value={form.descripcion}
        onChange={handleChange}
        error={errors.descripcion}
        disabled={isSubmitting}
        required
      />
      <div>
        <label htmlFor="mantencion-estado" className="block mb-1 text-sm font-medium text-neutral-700">
          Estado
        </label>
        <select
          id="mantencion-estado"
          name="estado"
          value={form.estado}
          onChange={handleChange}
          disabled={isSubmitting}
          required
          className={selectClassName}
        >
          {ESTADOS_MANTENCION.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        {errors.estado ? <p className="mt-1 text-xs text-danger-600">{errors.estado}</p> : null}
      </div>

      {resolvedErrorMessage ? (
        <div className="text-sm text-danger-600" role="alert">
          {resolvedErrorMessage}
        </div>
      ) : null}

      <div className="flex flex-wrap justify-end gap-2">
        {onCancel ? (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
            Cancelar
          </Button>
        ) : null}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Guardando..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}
