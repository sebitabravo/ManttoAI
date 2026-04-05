export default function ResumenCards({ resumen }) {
  const probabilidadFalla = Number(resumen.probabilidad_falla || 0);

  const cards = [
    { label: "Equipos", value: resumen.total_equipos || 0 },
    { label: "Alertas activas", value: resumen.alertas_activas || 0 },
    { label: "Equipos en riesgo", value: resumen.equipos_en_riesgo || 0 },
    { label: "Clasificación", value: resumen.ultima_clasificacion || "normal" },
    { label: "Probabilidad de falla", value: `${(probabilidadFalla * 100).toFixed(1)} %` },
  ];

  return (
    <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
      {cards.map((card) => (
        <article key={card.label} style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
          <div style={{ fontSize: 14, color: "#6b7280" }}>{card.label}</div>
          <strong style={{ fontSize: 28 }}>{card.value}</strong>
        </article>
      ))}
    </div>
  );
}
