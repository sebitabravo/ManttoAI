export default function Input({ label, error, ...props }) {
  const inputId = props.id || props.name;
  const errorId = error && inputId ? `${inputId}-error` : undefined;

  return (
    <label style={{ display: "grid", gap: 6 }}>
      <span>{label}</span>
      <input
        id={inputId}
        aria-invalid={Boolean(error)}
        aria-describedby={errorId}
        style={{
          padding: 10,
          borderRadius: 10,
          border: `1px solid ${error ? "#dc2626" : "#d1d5db"}`,
        }}
        {...props}
      />
      {error ? (
        <small id={errorId} style={{ color: "#dc2626" }} role="alert">
          {error}
        </small>
      ) : null}
    </label>
  );
}
