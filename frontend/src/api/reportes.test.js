/** Tests de cliente para endpoints de reportes. */

import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  downloadAlertasCsv,
  downloadInformeEjecutivoPdf,
  downloadLecturasCsv,
  downloadMantencionesCsv,
} from "./reportes";
import client from "./client";

vi.mock("./client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("reportes API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("descarga CSV de lecturas con query params", async () => {
    const blob = new Blob(["id,equipo_id\n1,1"], { type: "text/csv" });
    client.get.mockResolvedValue({
      data: blob,
      headers: {
        "content-disposition":
          'attachment; filename="manttoai_lecturas_20260408_180000.csv"',
      },
    });

    const result = await downloadLecturasCsv({ equipoId: 1, limit: 1000 });

    expect(client.get).toHaveBeenCalledWith("/api/v1/reportes/lecturas.csv", {
      params: { equipo_id: 1, limit: 1000 },
      responseType: "blob",
    });
    expect(result.filename).toContain("manttoai_lecturas");
    expect(result.blob).toBe(blob);
  });

  it("descarga CSV de alertas con fallback de nombre", async () => {
    const blob = new Blob(["id,equipo_id\n"], { type: "text/csv" });
    client.get.mockResolvedValue({ data: blob, headers: {} });

    const result = await downloadAlertasCsv({ soloNoLeidas: true, limit: 200 });

    expect(client.get).toHaveBeenCalledWith("/api/v1/reportes/alertas.csv", {
      params: { solo_no_leidas: true, limit: 200 },
      responseType: "blob",
    });
    expect(result.filename).toBe("manttoai_alertas.csv");
  });

  it("descarga CSV de mantenciones", async () => {
    const blob = new Blob(["id,equipo_id\n"], { type: "text/csv" });
    client.get.mockResolvedValue({ data: blob, headers: {} });

    await downloadMantencionesCsv({ equipoId: 2, order: "asc", limit: 300 });

    expect(client.get).toHaveBeenCalledWith("/api/v1/reportes/mantenciones.csv", {
      params: { equipo_id: 2, limit: 300, order: "asc" },
      responseType: "blob",
    });
  });

  it("descarga informe ejecutivo PDF", async () => {
    const blob = new Blob(["%PDF-1.4"], { type: "application/pdf" });
    client.get.mockResolvedValue({
      data: blob,
      headers: {
        "content-disposition":
          'attachment; filename="manttoai_informe_ejecutivo_20260408_180000.pdf"',
      },
    });

    const result = await downloadInformeEjecutivoPdf();

    expect(client.get).toHaveBeenCalledWith("/api/v1/reportes/ejecutivo.pdf", {
      params: {},
      responseType: "blob",
    });
    expect(result.filename).toContain("informe_ejecutivo");
    expect(result.blob).toBe(blob);
  });
});
