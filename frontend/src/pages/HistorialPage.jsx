import EmptyState from "../components/ui/EmptyState";

export default function HistorialPage() {
  return (
    <section>
      <h1>Historial</h1>
      <EmptyState title="Sin historial cargado" description="Acá van a convivir lecturas históricas y mantenciones registradas." />
    </section>
  );
}
