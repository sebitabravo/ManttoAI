export function formatDate(value) {
  if (value == null) {
    return "—";
  }

  const parsedDate = new Date(value);
  if (!Number.isFinite(parsedDate.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat("es-CL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parsedDate);
}
