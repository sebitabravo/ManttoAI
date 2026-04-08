/**
 * Input del sistema de diseño ManttoAI.
 * 
 * Características:
 * - Label asociado semánticamente
 * - Estado de error con aria-invalid y aria-describedby
 * - Touch target mínimo 44px (WCAG 2.2)
 * - Border focus con ring
 * - Placeholder con contraste suficiente
 */
export default function Input({ label, error, className = "", ...props }) {
  const inputId = props.id || props.name;
  const errorId = error && inputId ? `${inputId}-error` : undefined;

  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm font-medium text-neutral-700">{label}</span>
      <input
        id={inputId}
        aria-invalid={Boolean(error)}
        aria-describedby={errorId}
        className={`
          px-3 py-2.5 min-h-[44px]
          rounded border
          bg-neutral-100
          text-base text-neutral-700 shadow-sm
          placeholder:text-neutral-400
          transition-all duration-150 ease-out-quart
          focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus:border-primary-500
          disabled:bg-neutral-100 disabled:cursor-not-allowed
          ${error ? "border-danger-500 focus-visible:ring-danger-500" : "border-neutral-300"}
          ${className}
        `.trim()}
        {...props}
      />
      {error ? (
        <small id={errorId} className="text-sm text-danger-600" role="alert">
          {error}
        </small>
      ) : null}
    </label>
  );
}
