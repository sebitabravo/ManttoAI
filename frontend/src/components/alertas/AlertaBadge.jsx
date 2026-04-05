export default function AlertaBadge({ total = 0 }) {
  return (
    <span style={{ padding: "4px 10px", borderRadius: 999, background: "#fee2e2", color: "#991b1b", fontSize: 12 }}>
      {total} alertas
    </span>
  );
}
