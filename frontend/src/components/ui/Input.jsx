export default function Input({ label, error, ...props }) {
  return (
    <label style={{ display: "grid", gap: 6 }}>
      <span>{label}</span>
      <input style={{ padding: 10, borderRadius: 10, border: "1px solid #d1d5db" }} {...props} />
      {error ? <small style={{ color: "#dc2626" }}>{error}</small> : null}
    </label>
  );
}
