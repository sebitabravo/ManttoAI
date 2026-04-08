import { describe, expect, it } from "vitest";

import { formatProbability } from "./metrics";

describe("formatProbability", () => {
  it("usa fallback cuando la probabilidad es null", () => {
    expect(formatProbability(null)).toBe("Sin predicción");
  });

  it("usa fallback cuando la probabilidad es undefined", () => {
    expect(formatProbability(undefined)).toBe("Sin predicción");
  });

  it("formatea probabilidad válida", () => {
    expect(formatProbability(0.58)).toBe("58.0 %");
  });

  it("clampa valores sobre 1", () => {
    expect(formatProbability(1.4)).toBe("100.0 %");
  });

  it("clampa valores bajo 0", () => {
    expect(formatProbability(-0.2)).toBe("0.0 %");
  });
});
