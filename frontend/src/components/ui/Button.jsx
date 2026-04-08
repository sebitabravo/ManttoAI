/**
 * Botón del sistema de diseño ManttoAI.
 * 
 * Variantes:
 * - primary: acción principal (bg azul petróleo, texto blanco)
 * - outline: acción secundaria (bg transparente, borde neutral)
 * - danger: acción destructiva (bg rojo, texto blanco)
 * 
 * Touch target: mínimo 44px altura (WCAG 2.2 Level AA)
 * Transiciones: 150ms ease-out-quart
 */
export default function Button({ children, type = "button", variant = "primary", className = "", ...props }) {
  const baseClasses = `
    inline-flex items-center justify-center gap-2
    px-4 py-2.5 min-h-[44px]
    rounded font-medium text-base
    transition-all duration-150 ease-out-quart
    focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  const variantClasses = {
    primary: `
      border border-primary-600 bg-primary-600 text-neutral-50 shadow-sm
      hover:bg-primary-700 hover:border-primary-700
      active:bg-primary-800
      focus-visible:ring-primary-500
    `,
    outline: `
      bg-transparent text-neutral-700 border border-neutral-300
      hover:bg-neutral-100 hover:border-neutral-400
      active:bg-neutral-200
      focus-visible:ring-neutral-400
    `,
    danger: `
      border border-danger-600 bg-danger-600 text-neutral-50 shadow-sm
      hover:bg-danger-700 hover:border-danger-700
      active:bg-danger-800
      focus-visible:ring-danger-500
    `,
  };

  return (
    <button
      type={type}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}
