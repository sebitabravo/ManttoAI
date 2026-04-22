import { useEffect, useState } from "react";

import Button from "../ui/Button";
import Input from "../ui/Input";
import { selectClassName } from "../../utils/formStyles";

const ESTADOS_EQUIPO = [
  { value: "operativo", label: "Operativo" },
  { value: "monitoreo", label: "En monitoreo" },
  { value: "detenido", label: "Detenido" },
  { value: "mantenimiento", label: "En mantenimiento" },
  { value: "fuera_servicio", label: "Fuera de servicio" },
];

const TIPOS_EQUIPO = [
  { value: "Motor", label: "Motor" },
  { value: "Compresor", label: "Compresor" },
  { value: "Bomba", label: "Bomba" },
  { value: "Ventilador", label: "Ventilador" },
  { value: "Otro", label: "Otro" },
];

const DEFAULT_VALUES = {
  nombre: "",
  ubicacion: "Laboratorio",
  tipo: "Motor",
  estado: "operativo",
  mac_address: "",
};

function resolveInitialValues(initialValues) {
  return {
    nombre: typeof initialValues?.nombre === "string" ? initialValues.nombre : DEFAULT_VALUES.nombre,
    ubicacion:
      typeof initialValues?.ubicacion === "string" ? initialValues.ubicacion : DEFAULT_VALUES.ubicacion,
    tipo: typeof initialValues?.tipo === "string" ? initialValues.tipo : DEFAULT_VALUES.tipo,
    estado: typeof initialValues?.estado === "string" ? initialValues.estado : DEFAULT_VALUES.estado,
    mac_address: typeof initialValues?.mac_address === "string" ? initialValues.mac_address : DEFAULT_VALUES.mac_address,
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

  if (values.mac_address.trim() && !/^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/.test(values.mac_address.trim())) {
    fieldErrors.mac_address = "La dirección MAC no tiene un formato válido (ej: 00:1A:2B:3C:4D:5E).";
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
      mac_address: form.mac_address.trim() || undefined,
    };

    try {
      await onSubmit(payload);
    } catch {
      setSubmitError("No pudimos guardar los cambios. Probá nuevamente.");
    }
  }

  const resolvedErrorMessage = errorMessage || submitError;

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-3">
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
        label="Dirección MAC (Opcional)"
        name="mac_address"
        value={form.mac_address}
        onChange={handleChange}
        error={errors.mac_address}
        disabled={isSubmitting}
        placeholder="ej: 00:1A:2B:3C:4D:5E"
      />
      <div>
        <label htmlFor="equipo-tipo" className="block mb-1 text-sm font-medium text-neutral-700">
          Tipo
        </label>
        <select
          id="equipo-tipo"
          name="tipo"
          value={form.tipo}
          onChange={handleChange}
          disabled={isSubmitting}
          required
          className={selectClassName}
        >
          {TIPOS_EQUIPO.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        {errors.tipo ? <p className="mt-1 text-xs text-danger-600">{errors.tipo}</p> : null}
      </div>
      <div>
        <label htmlFor="equipo-estado" className="block mb-1 text-sm font-medium text-neutral-700">
          Estado
        </label>
        <select
          id="equipo-estado"
          name="estado"
          value={form.estado}
          onChange={handleChange}
          disabled={isSubmitting}
          required
          className={selectClassName}
        >
          {ESTADOS_EQUIPO.map((opt) => (
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
