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

export function parseTimestamp(value) {
  if (value == null) {
    return null;
  }

  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }

  if (value instanceof Date) {
    const timestamp = value.getTime();
    return Number.isFinite(timestamp) ? timestamp : null;
  }

  const parsed = Date.parse(String(value).trim());
  return Number.isFinite(parsed) ? parsed : null;
}

export function compareByTimestampAsc(current, next) {
  const currentTimestamp = parseTimestamp(current?.timestamp);
  const nextTimestamp = parseTimestamp(next?.timestamp);

  if (currentTimestamp === null && nextTimestamp === null) {
    return 0;
  }
  if (currentTimestamp === null) {
    return 1;
  }
  if (nextTimestamp === null) {
    return -1;
  }

  return currentTimestamp - nextTimestamp;
}

export function compareByTimestampDesc(current, next) {
  const currentTimestamp = parseTimestamp(current?.timestamp);
  const nextTimestamp = parseTimestamp(next?.timestamp);

  if (currentTimestamp === null && nextTimestamp === null) {
    return 0;
  }
  if (currentTimestamp === null) {
    return 1;
  }
  if (nextTimestamp === null) {
    return -1;
  }

  return nextTimestamp - currentTimestamp;
}
