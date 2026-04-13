/** Tests para el API client de umbrales. */

import { beforeEach, describe, expect, it, vi } from "vitest";

import client from "./client";
import { getUmbrales, updateUmbral } from "./umbrales";

vi.mock("./client", () => ({
  default: {
    get: vi.fn(),
    put: vi.fn(),
  },
}));

describe("umbrales API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("getUmbrales consulta endpoint base sin filtros", async () => {
    client.get.mockResolvedValue({ data: [] });

    await getUmbrales();

    expect(client.get).toHaveBeenCalledWith("/umbrales");
  });

  it("getUmbrales filtra por equipo cuando recibe equipoId", async () => {
    client.get.mockResolvedValue({ data: [] });

    await getUmbrales(7);

    expect(client.get).toHaveBeenCalledWith("/umbrales", {
      params: { equipo_id: 7 },
    });
  });

  it("updateUmbral actualiza el umbral indicado", async () => {
    const payload = { valor_min: 10, valor_max: 40 };
    client.put.mockResolvedValue({ data: { id: 3, ...payload } });

    await updateUmbral(3, payload);

    expect(client.put).toHaveBeenCalledWith("/umbrales/3", payload);
  });
});
