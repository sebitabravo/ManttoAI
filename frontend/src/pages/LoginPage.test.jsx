import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { login as loginRequest } from "../api/auth";
import useAuth from "../hooks/useAuth";
import LoginPage from "./LoginPage";

vi.mock("../api/auth", () => ({
  getCurrentUser: vi.fn(),
  login: vi.fn(),
}));

vi.mock("../hooks/useAuth", () => ({
  default: vi.fn(),
}));

vi.mock("react-router-dom", () => ({
  useNavigate: () => vi.fn(),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
    useAuth.mockReturnValue({ login: vi.fn() });
    loginRequest.mockImplementation(() => new Promise(() => {}));
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.useRealTimers();
  });

  it("informa cuando el backend lleva varios segundos despertando", async () => {
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "admin@manttoai.local" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "una-clave-segura" },
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Continuar" }));
    });
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });

    expect(screen.getByRole("status").textContent).toContain(
      "El backend gratuito se está iniciando"
    );
  });

  it("rellena la cuenta demo cuando el despliegue la configura", () => {
    vi.stubEnv("VITE_DEMO_EMAIL", "demo@manttoai.local");
    vi.stubEnv("VITE_DEMO_PASSWORD", "DemoPublica123!");

    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Usar cuenta demo" }));

    expect(screen.getByLabelText("Email").value).toBe("demo@manttoai.local");
    expect(screen.getByLabelText("Contraseña").value).toBe("DemoPublica123!");
  });
});
