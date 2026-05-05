/**
 * Botón del sistema de diseño ManttoAI — Estilo Apple.
 * 
 * Variantes:
 * - primary: Apple Blue (#0071e3), texto blanco
 * - secondary: Near Black (#1d1d1f), texto blanco
 * - outline: Transparente con borde, texto Apple Blue
 * - ghost: Sin borde, texto Apple Blue
 * - danger: Apple Red (#ff3b30), texto blanco
 * - pill: Link estilo Apple "Learn more" con borde redondeado 980px
 * 
 * Touch target: mínimo 44px altura (WCAG 2.2 Level AA)
 * Transiciones: 200ms ease Apple
 */
export default function Button({ 
  children, 
  type = "button", 
  variant = "primary", 
  size = "default",
  className = "", 
  ...props 
}) {
  // Clases base compartidas
  const baseClasses = `
    inline-flex items-center justify-center gap-2
    font-medium
    transition-all duration-200
    focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none
  `;

  // Tamaños adaptados para dashboard B2B (más compactos)
  // min-h-[44px] asegura touch target WCAG 2.2 Level AA
  const sizeClasses = {
    sm: "px-3 py-1.5 text-xs rounded-md min-h-[36px]",
    default: "px-4 py-2 text-sm rounded-md min-h-[44px]",
    lg: "px-6 py-2.5 text-base rounded-md min-h-[44px]",
  };

  // Variantes de estilo Apple
  const variantClasses = {
    // Primary: Apple Blue
    primary: `
      bg-primary-500 text-white
      hover:bg-primary-600
      active:bg-primary-700
    `,
    // Secondary: Near Black
    secondary: `
      bg-neutral-600 text-white
      hover:bg-neutral-700
      active:bg-neutral-800
    `,
    // Outline: Borde con texto azul
    outline: `
      bg-transparent text-primary-500 
      border border-primary-500
      hover:bg-primary-50
      active:bg-primary-100
    `,
    // Ghost: Sin borde, solo texto
    ghost: `
      bg-transparent text-primary-500
      hover:bg-neutral-100
      active:bg-neutral-200
    `,
    // Danger: Apple Red
    danger: `
      bg-danger-500 text-white
      hover:bg-danger-600
      active:bg-danger-700
    `,
    // Pill: Estilo "Learn more" de Apple — borde pill 980px
    pill: `
      bg-transparent text-primary-600
      border border-primary-500
      rounded-pill
      hover:bg-primary-50 hover:text-primary-700
      active:bg-primary-100
    `,
    // Pill filled: "Buy" / "Shop" style
    "pill-filled": `
      bg-primary-500 text-white
      rounded-pill
      hover:bg-primary-600
      active:bg-primary-700
    `,
  };

  // Para pill variant, override el border-radius del size
  const radiusOverride = variant.includes("pill") ? "rounded-pill" : "";

  return (
    <button
      type={type}
      className={`
        ${baseClasses} 
        ${sizeClasses[size]} 
        ${variantClasses[variant]} 
        ${radiusOverride}
        ${className}
      `.replace(/\s+/g, " ").trim()}
      {...props}
    >
      {children}
    </button>
  );
}
