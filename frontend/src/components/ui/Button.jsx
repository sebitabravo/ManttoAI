import { BRAND_COLOR } from "./Logo";

export default function Button({ children, type = "button", variant = "primary", ...props }) {
  // Colores por variante — primary usa BRAND_COLOR para consistencia con el logo y nav activo
  const colors = {
    primary: { background: BRAND_COLOR, color: "#ffffff", border: `1px solid ${BRAND_COLOR}` },
    outline: { background: "transparent", color: "#111827", border: "1px solid #d1d5db" },
    danger: { background: "#dc2626", color: "#ffffff", border: "1px solid #dc2626" },
  };

  return (
    <button
      type={type}
      style={{ borderRadius: 10, padding: "10px 14px", cursor: "pointer", ...colors[variant] }}
      {...props}
    >
      {children}
    </button>
  );
}
