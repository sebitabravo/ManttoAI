/** Tests para el API client de administración. */

import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  createApiKey,
  createUser,
  deleteUser,
  getApiKeys,
  getAuditLogs,
  getUsers,
  revokeApiKey,
  updateUser,
} from "./admin";
import client from "./client";

vi.mock("./client", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe("admin API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("getUsers usa endpoint esperado sin filtros", async () => {
    client.get.mockResolvedValue({ data: { usuarios: [], total: 0 } });

    await getUsers();

    expect(client.get).toHaveBeenCalledWith("/usuarios?");
  });

  it("getUsers aplica filtros en query string", async () => {
    client.get.mockResolvedValue({ data: { usuarios: [], total: 0 } });

    await getUsers({ rol: "admin", page: 2, per_page: 25 });

    expect(client.get).toHaveBeenCalledWith(
      "/usuarios?rol=admin&page=2&per_page=25"
    );
  });

  it("createUser crea un usuario", async () => {
    const payload = {
      nombre: "Nuevo Usuario",
      email: "nuevo@test.com",
      password: "password123",
      rol: "visualizador",
    };
    client.post.mockResolvedValue({ data: { id: 3, ...payload } });

    const result = await createUser(payload);

    expect(client.post).toHaveBeenCalledWith("/usuarios", payload);
    expect(result.id).toBe(3);
  });

  it("updateUser actualiza usuario", async () => {
    const payload = { nombre: "Actualizado", rol: "admin" };
    client.put.mockResolvedValue({ data: { id: 1, ...payload } });

    await updateUser(1, payload);

    expect(client.put).toHaveBeenCalledWith("/usuarios/1", payload);
  });

  it("deleteUser elimina usuario", async () => {
    client.delete.mockResolvedValue({ data: { ok: true } });

    await deleteUser(1);

    expect(client.delete).toHaveBeenCalledWith("/usuarios/1");
  });

  it("getApiKeys consulta endpoint esperado", async () => {
    client.get.mockResolvedValue({ data: [] });

    await getApiKeys();

    expect(client.get).toHaveBeenCalledWith("/api-keys?");
  });

  it("getApiKeys permite incluir inactivas", async () => {
    client.get.mockResolvedValue({ data: [] });

    await getApiKeys({ include_inactive: true });

    expect(client.get).toHaveBeenCalledWith(
      "/api-keys?include_inactive=true"
    );
  });

  it("createApiKey crea key nueva", async () => {
    const payload = { device_id: "esp32_001" };
    client.post.mockResolvedValue({
      data: { id: 1, key: "mttk_demo", key_prefix: "_demo", ...payload },
    });

    const result = await createApiKey(payload);

    expect(client.post).toHaveBeenCalledWith("/api-keys", payload);
    expect(result.key).toBe("mttk_demo");
  });

  it("revokeApiKey revoca por id", async () => {
    client.delete.mockResolvedValue({ data: { ok: true } });

    await revokeApiKey(5);

    expect(client.delete).toHaveBeenCalledWith("/api-keys/5");
  });

  it("getAuditLogs consulta endpoint esperado", async () => {
    client.get.mockResolvedValue({ data: { logs: [], total: 0 } });

    await getAuditLogs();

    expect(client.get).toHaveBeenCalledWith("/audit-logs?");
  });

  it("getAuditLogs aplica filtros", async () => {
    client.get.mockResolvedValue({ data: { logs: [], total: 0 } });

    await getAuditLogs({
      usuario_id: 1,
      entity_type: "equipo",
      action: "create",
      page: 2,
    });

    expect(client.get).toHaveBeenCalledWith(
      "/audit-logs?usuario_id=1&entity_type=equipo&action=create&page=2"
    );
  });
});
