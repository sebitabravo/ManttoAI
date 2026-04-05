export default function Button({ children, type = "button", variant = "primary", ...props }) {
  const colors = {
    primary: { background: "#2563eb", color: "#ffffff", border: "1px solid #2563eb" },
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
