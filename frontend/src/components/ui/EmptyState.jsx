export default function EmptyState({ title, description }) {
  return (
    <div style={{ padding: 20, border: "1px dashed #cbd5e1", borderRadius: 16 }}>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
