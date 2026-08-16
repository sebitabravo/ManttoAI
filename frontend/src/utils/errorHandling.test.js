import { describe, expect, it } from "vitest";

import { getApiErrorMessage, isApiUnavailableError } from "./errorHandling";

describe("errorHandling", () => {
  it("identifica timeout y red caída como indisponibilidad del backend", () => {
    expect(isApiUnavailableError({ code: "ECONNABORTED" })).toBe(true);
    expect(isApiUnavailableError({ code: "ERR_NETWORK", request: {} })).toBe(true);
    expect(isApiUnavailableError({ message: "Network Error", request: {} })).toBe(true);
  });

  it("no confunde un 401 con una caída del backend", () => {
    expect(
      isApiUnavailableError({ response: { status: 401, data: {} } })
    ).toBe(false);
    expect(
      getApiErrorMessage(
        { response: { data: { detail: "Credenciales inválidas" } } },
        "fallback"
      )
    ).toBe("Credenciales inválidas");
  });
});
