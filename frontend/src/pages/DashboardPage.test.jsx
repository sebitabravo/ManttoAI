import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import usePolling from "../hooks/usePolling";
import DashboardPage from "./DashboardPage";

vi.mock("../api/dashboard", () => ({
  getDashboardData: vi.fn(),
}));

vi.mock("../hooks/usePolling", () => ({
  default: vi.fn(),
}));

vi.mock("../components/dashboard/ResumenCards", () => ({
  default: () => <div data-testid="dashboard-summary" />,
}));

vi.mock("../components/dashboard/GraficoTemperatura", () => ({
  default: () => null,
}));

vi.mock("../components/dashboard/GraficoVibracion", () => ({
  default: () => null,
}));

vi.mock("../components/dashboard/TablaEstadoEquipos", () => ({
  default: () => null,
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("no muestra métricas en cero cuando falla la carga inicial", () => {
    const refresh = vi.fn();
    usePolling.mockReturnValue({
      data: null,
      loading: false,
      error: { code: "ECONNABORTED" },
      refresh,
    });

    render(<DashboardPage />);

    expect(screen.getByRole("alert").textContent).toContain(
      "El backend puede estar despertando"
    );
    expect(screen.queryByTestId("dashboard-summary")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));
    expect(refresh).toHaveBeenCalledTimes(1);
  });

  it("conserva los datos visibles mientras un polling posterior falla", () => {
    usePolling.mockReturnValue({
      data: {
        resumen: {
          total_equipos: 1,
          alertas_activas: 0,
          equipos_en_riesgo: 0,
          equipos: [],
        },
        lecturas: [],
      },
      loading: false,
      error: new Error("backend no disponible"),
      refresh: vi.fn(),
    });

    render(<DashboardPage />);

    expect(screen.getByTestId("dashboard-summary")).toBeTruthy();
    expect(screen.getByText(/Se muestran los últimos datos válidos/)).toBeTruthy();
  });
});
