import AlertaItem from "../components/alertas/AlertaItem";

const alertas = [
  { id: 1, tipo: "temperatura", nivel: "alto", mensaje: "Temperatura fuera de rango", fecha: new Date().toISOString() },
];

export default function AlertasPage() {
  return (
    <section>
      <h1>Alertas activas</h1>
      <div style={{ display: "grid", gap: 12 }}>
        {alertas.map((alerta) => (
          <AlertaItem key={alerta.id} alerta={alerta} />
        ))}
      </div>
    </section>
  );
}
