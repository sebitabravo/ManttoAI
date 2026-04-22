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
    <article className="rounded-2xl bg-white p-4 shadow-sm transition-all duration-150 ease-out-quart hover:shadow-apple">
      <strong className="text-base font-semibold text-neutral-900">{formatTipoAlerta(alerta.tipo)}</strong>
      <p className="my-2 text-sm text-neutral-700">{alerta.mensaje}</p>
      <small className="text-xs text-neutral-600">
        Nivel: <span className="font-medium">{alerta.nivel}</span> · {timestamp ? formatDate(timestamp) : "Sin fecha"}
      </small>
      <div className="mt-3 flex items-center justify-between">
        <span className={`text-xs font-medium ${isLeida ? 'text-success-700' : 'text-danger-700'}`}>
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
