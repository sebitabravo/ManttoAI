import { useParams } from "react-router-dom";

import EmptyState from "../components/ui/EmptyState";

export default function EquipoDetallePage() {
  const { equipoId } = useParams();

  return (
    <section>
      <h1>Detalle del equipo {equipoId}</h1>
      <EmptyState title="Vista en construcción" description="Este detalle se completará cuando exista conexión real con lecturas, alertas e historial." />
    </section>
  );
}
