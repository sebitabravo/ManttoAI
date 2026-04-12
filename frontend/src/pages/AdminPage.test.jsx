/** Tests básicos para AdminPage (Vitest + RTL). */

import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as adminApi from "../api/admin";
import AdminPage from "./AdminPage";

vi.mock("../hooks/useAuth", () => ({
  default: () => ({
    user: { id: 1, nombre: "Admin", email: "admin@test.com", rol: "admin" },
    isAuthenticated: true,
    isAuthResolved: true,
  }),
}));

vi.mock("../api/admin", () => ({
  getUsers: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  deleteUser: vi.fn(),
  getApiKeys: vi.fn(),
  createApiKey: vi.fn(),
  revokeApiKey: vi.fn(),
  getAuditLogs: vi.fn(),
}));

describe("AdminPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    adminApi.getUsers.mockResolvedValue({
      usuarios: [
        {
          id: 1,
          nombre: "Admin",
          email: "admin@test.com",
          rol: "admin",
          created_at: "2026-04-08T00:00:00Z",
        },
      ],
      total: 1,
    });

    adminApi.getApiKeys.mockResolvedValue([
      {
        id: 1,
        key_prefix: "xxxxxx01",
        device_id: "esp32_001",
        is_active: true,
        created_at: "2026-04-08T00:00:00Z",
      },
    ]);

    adminApi.getAuditLogs.mockResolvedValue({
      logs: [
        {
          id: 1,
          action: "create",
          entity_type: "equipo",
          entity_id: 1,
          usuario_id: 1,
          ip_address: "127.0.0.1",
          created_at: "2026-04-08T00:00:00Z",
        },
      ],
      total: 1,
    });
  });

  it("renderiza el panel y carga usuarios", async () => {
    render(<AdminPage />);

    await waitFor(() => {
      expect(adminApi.getUsers).toHaveBeenCalledTimes(1);
      expect(screen.queryByText("Cargando...")).toBeNull();
      expect(screen.getByText("Panel de Administración")).toBeTruthy();
      expect(screen.getByText("admin@test.com")).toBeTruthy();
    });
  });

  it("cambia de tab y carga API keys + audit logs", async () => {
    render(<AdminPage />);

    await waitFor(() => {
      expect(adminApi.getUsers).toHaveBeenCalledTimes(1);
      expect(screen.queryByText("Cargando...")).toBeNull();
      expect(screen.getByRole("button", { name: "API Keys" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "API Keys" }));
    await waitFor(() => {
      expect(adminApi.getApiKeys).toHaveBeenCalledTimes(1);
      expect(screen.getByText("esp32_001")).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Audit Logs" }));
    await waitFor(() => {
      expect(adminApi.getAuditLogs).toHaveBeenCalledTimes(1);
      expect(screen.getByText("equipo #1")).toBeTruthy();
    });
  });

  it("permite crear un usuario desde el modal", async () => {
    adminApi.createUser.mockResolvedValue({
      id: 2,
      nombre: "Test User",
      email: "test@test.com",
      rol: "visualizador",
    });

    render(<AdminPage />);

    await waitFor(() => expect(adminApi.getUsers).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Nuevo Usuario" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Nuevo Usuario" })).toBeTruthy();
    });

    const inputs = document.querySelectorAll("input");
    fireEvent.change(inputs[0], { target: { value: "Test User" } });
    fireEvent.change(inputs[1], { target: { value: "test@test.com" } });
    fireEvent.change(inputs[2], { target: { value: "password123" } });

    fireEvent.click(screen.getByRole("button", { name: "Crear Usuario" }));

    await waitFor(() => {
      expect(adminApi.createUser).toHaveBeenCalledWith({
        nombre: "Test User",
        email: "test@test.com",
        password: "password123",
        rol: "visualizador",
      });
    });
  });

  it("permite revocar API key activa", async () => {
    adminApi.revokeApiKey.mockResolvedValue({ ok: true });

    render(<AdminPage />);

    await waitFor(() => {
      expect(adminApi.getUsers).toHaveBeenCalledTimes(1);
      expect(screen.queryByText("Cargando...")).toBeNull();
      expect(screen.getByRole("button", { name: "API Keys" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "API Keys" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Revocar" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Revocar" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Revocar API Key" })).toBeTruthy();
    });

    const dialog = screen.getByRole("dialog");
    fireEvent.click(within(dialog).getByRole("button", { name: "Revocar" }));

    await waitFor(() => {
      expect(adminApi.revokeApiKey).toHaveBeenCalledWith(1);
    });
  });
});
