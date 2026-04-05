import { useEffect, useState } from "react";

import Button from "../ui/Button";
import Input from "../ui/Input";

const DEFAULT_VALUES = {
  nombre: "",
  ubicacion: "Laboratorio",
  tipo: "Motor",
  estado: "operativo",
};

function resolveInitialValues(initialValues) {
  return {
    nombre: typeof initialValues?.nombre === "string" ? initialValues.nombre : DEFAULT_VALUES.nombre,
    ubicacion:
      typeof initialValues?.ubicacion === "string" ? initialValues.ubicacion : DEFAULT_VALUES.ubicacion,
    tipo: typeof initialValues?.tipo === "string" ? initialValues.tipo : DEFAULT_VALUES.tipo,
    estado: typeof initialValues?.estado === "string" ? initialValues.estado : DEFAULT_VALUES.estado,
  };
}

function validateForm(values) {
  const fieldErrors = {};

  if (!values.nombre.trim()) {
    fieldErrors.nombre = "El nombre del equipo es obligatorio.";
  }

  if (!values.ubicacion.trim()) {
    fieldErrors.ubicacion = "La ubicación es obligatoria.";
  }

  if (!values.tipo.trim()) {
    fieldErrors.tipo = "El tipo es obligatorio.";
  }

  if (!values.estado.trim()) {
    fieldErrors.estado = "El estado es obligatorio.";
  }

  return fieldErrors;
}

export default function EquipoForm({
  initialValues,
  onSubmit,
  onCancel,
  submitLabel = "Guardar",
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
      nombre: form.nombre.trim(),
      ubicacion: form.ubicacion.trim(),
      tipo: form.tipo.trim(),
      estado: form.estado.trim(),
    };

    try {
      await onSubmit(payload);
    } catch {
      setSubmitError("No pudimos guardar los cambios. Probá nuevamente.");
    }
  }

  const resolvedErrorMessage = errorMessage || submitError;

  return (
    <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
      <Input
        label="Nombre del equipo"
        name="nombre"
        value={form.nombre}
        onChange={handleChange}
        error={errors.nombre}
        disabled={isSubmitting}
        required
      />
      <Input
        label="Ubicación"
        name="ubicacion"
        value={form.ubicacion}
        onChange={handleChange}
        error={errors.ubicacion}
        disabled={isSubmitting}
        required
      />
      <Input
        label="Tipo"
        name="tipo"
        value={form.tipo}
        onChange={handleChange}
        error={errors.tipo}
        disabled={isSubmitting}
        required
      />
      <Input
        label="Estado"
        name="estado"
        value={form.estado}
        onChange={handleChange}
        error={errors.estado}
        disabled={isSubmitting}
        required
      />

      {resolvedErrorMessage ? (
        <div style={{ color: "#dc2626", fontSize: 14 }} role="alert">
          {resolvedErrorMessage}
        </div>
      ) : null}

      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap" }}>
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
