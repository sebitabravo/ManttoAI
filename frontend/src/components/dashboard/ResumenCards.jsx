import { formatProbability } from "../../utils/metrics";

export default function ResumenCards({ resumen }) {
  const cards = [
    { label: "Equipos", value: resumen.total_equipos || 0 },
    { label: "Alertas activas", value: resumen.alertas_activas || 0 },
    { label: "Equipos en riesgo", value: resumen.equipos_en_riesgo || 0 },
    { label: "Clasificación", value: resumen.ultima_clasificacion || "normal" },
    { label: "Probabilidad de falla", value: formatProbability(resumen.probabilidad_falla, "Sin datos") },
  ];

  return (
    <div className="grid gap-4" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
      {cards.map((card) => (
        <article key={card.label} className="rounded-2xl border border-gray-200 p-4">
          <div className="text-sm text-gray-500">{card.label}</div>
          <strong className="text-3xl">{card.value}</strong>
        </article>
      ))}
    </div>
  );
}
