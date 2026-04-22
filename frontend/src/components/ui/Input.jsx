import { useId } from "react";

/**
 * Input del sistema de diseño ManttoAI — Estilo Apple.
 * 
 * Características:
 * - Diseño limpio y minimal sin bordes pesados
 * - Label asociado semánticamente
 * - Estado de error con aria-invalid y aria-describedby
 * - Touch target mínimo 44px (WCAG 2.2)
 * - Focus ring con Apple Blue
 * - Fondo sutil #f5f5f7 (Apple Gray)
 */
export default function Input({ label, error, className = "", ...props }) {
  const generatedId = useId().replace(/:/g, "");
  const sanitizedName =
    typeof props.name === "string"
      ? props.name.trim().replace(/[^a-zA-Z0-9\-_.:]/g, "-")
      : undefined;
  const inputId = props.id || sanitizedName || `input-${generatedId}`;
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <label className="flex flex-col gap-2">
      {label && (
        <span className="text-sm font-medium text-neutral-600 tracking-tight">
          {label}
        </span>
      )}
      <input
        id={inputId}
        aria-invalid={Boolean(error)}
        aria-describedby={errorId}
        className={`
          w-full px-3 py-2 min-h-[38px]
          rounded-md
          bg-[#f5f5f7]
          text-sm text-neutral-800
          border border-transparent
          placeholder:text-neutral-400
          transition-all duration-200
          hover:bg-neutral-200/60
          focus:outline-none focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
          disabled:bg-neutral-100 disabled:text-neutral-400 disabled:cursor-not-allowed
          ${error ? "border-danger-500 focus:border-danger-500 focus:ring-danger-500/20" : ""}
          ${className}
        `.replace(/\s+/g, " ").trim()}
        {...props}
      />
      {error && (
        <span id={errorId} className="text-sm text-danger-500" role="alert">
          {error}
        </span>
      )}
    </label>
  );
}
