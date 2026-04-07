export default function AlertaBadge({ total = 0 }) {
  const label = total === 1 ? "alerta" : "alertas";

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-danger-100 px-2.5 py-1 text-xs font-semibold tabular-nums text-danger-800">
      {total} {label}
    </span>
  );
}
