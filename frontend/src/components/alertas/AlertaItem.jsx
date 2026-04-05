import { formatDate } from "../../utils/formatDate";

export default function AlertaItem({ alerta }) {
  return (
    <article style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
      <strong>{alerta.tipo}</strong>
      <p style={{ margin: "8px 0" }}>{alerta.mensaje}</p>
      <small>
        Nivel: {alerta.nivel} · {formatDate(alerta.fecha)}
      </small>
    </article>
  );
}
