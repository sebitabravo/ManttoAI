export const RUBRO_OPTIONS = [
  { value: "industrial", label: "Industrial" },
  { value: "agricola", label: "Agrícola" },
  { value: "comercial", label: "Comercial" },
];

const RUBRO_LABEL_BY_VALUE = {
  industrial: "Industrial",
  agricola: "Agrícola",
  comercial: "Comercial",
};

const RUBRO_BADGE_CLASS_BY_VALUE = {
  industrial: "bg-primary-50 text-primary-700",
  agricola: "bg-success-50 text-success-700",
  comercial: "bg-warning-50 text-warning-700",
};

export function normalizeRubro(value) {
  const normalized = String(value || "").trim().toLowerCase();
  if (normalized === "agricola" || normalized === "comercial" || normalized === "industrial") {
    return normalized;
  }
  return "industrial";
}

export function getRubroLabel(value) {
  return RUBRO_LABEL_BY_VALUE[normalizeRubro(value)] || "Industrial";
}

export function getRubroBadgeClass(value) {
  return RUBRO_BADGE_CLASS_BY_VALUE[normalizeRubro(value)] || RUBRO_BADGE_CLASS_BY_VALUE.industrial;
}
