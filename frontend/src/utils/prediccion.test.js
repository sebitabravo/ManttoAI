import { describe, it, expect } from "vitest";
import { getConfigPrediccion, formatPorcentajeRiesgo } from "./prediccion";

describe("getConfigPrediccion", () => {
  it("devuelve CONFIG_DESCONOCIDA para null", () => {
    expect(getConfigPrediccion(null).label).toBe("Sin predicción");
  });

  it("devuelve CONFIG_DESCONOCIDA para undefined", () => {
    expect(getConfigPrediccion(undefined).label).toBe("Sin predicción");
  });

  it("devuelve CONFIG_DESCONOCIDA para clasificación desconocida", () => {
    expect(getConfigPrediccion("inexistente").label).toBe("Sin predicción");
  });

  it("reconoce 'normal' en minúsculas", () => {
    expect(getConfigPrediccion("normal").label).toBe("Normal");
  });

  it("reconoce 'NORMAL' en mayúsculas (case-insensitive)", () => {
    expect(getConfigPrediccion("NORMAL").label).toBe("Normal");
  });

  it("reconoce 'Advertencia' con capitalización mixta", () => {
    expect(getConfigPrediccion("Advertencia").label).toBe("Advertencia");
  });

  it("reconoce 'critico'", () => {
    expect(getConfigPrediccion("critico").label).toBe("Crítico");
  });

  it("convierte a string antes de procesar (no falla con número)", () => {
    // Un número no es null/undefined, debe caer en CONFIG_DESCONOCIDA
    expect(getConfigPrediccion(0).label).toBe("Sin predicción");
  });
});

describe("formatPorcentajeRiesgo", () => {
  it("formatea 0.5 como '50.0 %'", () => {
    expect(formatPorcentajeRiesgo(0.5)).toBe("50.0 %");
  });

  it("formatea 0 como '0.0 %'", () => {
    expect(formatPorcentajeRiesgo(0)).toBe("0.0 %");
  });

  it("formatea 1 como '100.0 %'", () => {
    expect(formatPorcentajeRiesgo(1)).toBe("100.0 %");
  });

  it("clampa valores mayores a 1 (ej: 1.5 → '100.0 %')", () => {
    expect(formatPorcentajeRiesgo(1.5)).toBe("100.0 %");
  });

  it("clampa valores negativos (ej: -0.2 → '0.0 %')", () => {
    expect(formatPorcentajeRiesgo(-0.2)).toBe("0.0 %");
  });

  it("devuelve '—' para null", () => {
    expect(formatPorcentajeRiesgo(null)).toBe("—");
  });

  it("devuelve '—' para undefined", () => {
    expect(formatPorcentajeRiesgo(undefined)).toBe("—");
  });

  it("devuelve '—' para string no numérico", () => {
    expect(formatPorcentajeRiesgo("abc")).toBe("—");
  });

  it("acepta string numérico válido (ej: '0.75')", () => {
    expect(formatPorcentajeRiesgo("0.75")).toBe("75.0 %");
  });
});
