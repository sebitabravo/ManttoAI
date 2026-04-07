import { formatDate } from "../../utils/formatDate";
import Button from "../ui/Button";

/** Capitaliza la primera letra del tipo de alerta para la UI */
function formatTipoAlerta(tipo) {
  if (!tipo) return "—";
  return String(tipo).charAt(0).toUpperCase() + String(tipo).slice(1);
}

export default function AlertaItem({ alerta, onMarkAsRead, marking = false }) {
  const timestamp = alerta.created_at || alerta.fecha;
  const isLeida = Boolean(alerta.leida);

  return (
    <article style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <strong>{formatTipoAlerta(alerta.tipo)}</strong>
      <p style={{ margin: "8px 0" }}>{alerta.mensaje}</p>
      <small>
        Nivel: {alerta.nivel} · {timestamp ? formatDate(timestamp) : "Sin fecha"}
      </small>
      <div style={{ marginTop: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 12, color: isLeida ? "#166534" : "#991b1b" }}>
          {isLeida ? "Leída" : "No leída"}
        </span>
        {onMarkAsRead && !isLeida ? (
          <Button type="button" variant="outline" onClick={() => onMarkAsRead(alerta.id)} disabled={marking}>
            {marking ? "Marcando..." : "Marcar como leída"}
          </Button>
        ) : null}
      </div>
    </article>
  );
}
