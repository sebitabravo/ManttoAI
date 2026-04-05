export default function Modal({ open = false, title = "Modal", children }) {
  if (!open) {
    return null;
  }

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(15, 23, 42, 0.35)", display: "grid", placeItems: "center" }}>
      <div style={{ background: "#ffffff", padding: 24, borderRadius: 16, minWidth: 320 }}>
        <h2>{title}</h2>
        <div>{children}</div>
      </div>
    </div>
  );
}
