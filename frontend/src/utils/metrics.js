export function resolveMaxVibration(lectura) {
  return Math.max(
    Math.abs(Number(lectura.vib_x) || 0),
    Math.abs(Number(lectura.vib_y) || 0),
    Math.abs(Number(lectura.vib_z) || 0)
  );
}

export function formatMetric(value, unit) {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return "—";
  }

  return `${numericValue.toFixed(2)} ${unit}`;
}
