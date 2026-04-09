/** Cliente API para endpoints de administración. */

import client from "./client";

/**
 * Lista todos los usuarios con filtros opcionales.
 */
export async function getUsers(filters = {}) {
  const params = new URLSearchParams();
  if (filters.rol) params.append("rol", filters.rol);
  if (filters.page) params.append("page", filters.page);
  if (filters.per_page) params.append("per_page", filters.per_page);

  const response = await client.get(`/usuarios?${params.toString()}`);
  return response.data;
}

/**
 * Crea un nuevo usuario.
 */
export async function createUser(data) {
  const response = await client.post("/usuarios", data);
  return response.data;
}

/**
 * Actualiza un usuario existente.
 */
export async function updateUser(userId, data) {
  const response = await client.put(`/usuarios/${userId}`, data);
  return response.data;
}

/**
 * Elimina un usuario.
 */
export async function deleteUser(userId) {
  const response = await client.delete(`/usuarios/${userId}`);
  return response.data;
}

/**
 * Lista todas las API keys.
 */
export async function getApiKeys(filters = {}) {
  const params = new URLSearchParams();
  if (filters.include_inactive) params.append("include_inactive", "true");
  if (filters.device_id) params.append("device_id", filters.device_id);

  const response = await client.get(`/api-keys?${params.toString()}`);
  return response.data;
}

/**
 * Crea una nueva API key.
 */
export async function createApiKey(data) {
  const response = await client.post("/api-keys", data);
  return response.data;
}

/**
 * Revoca una API key.
 */
export async function revokeApiKey(keyId) {
  const response = await client.delete(`/api-keys/${keyId}`);
  return response.data;
}

/**
 * Lista logs de auditoría.
 */
export async function getAuditLogs(filters = {}) {
  const params = new URLSearchParams();
  if (filters.usuario_id) params.append("usuario_id", filters.usuario_id);
  if (filters.entity_type) params.append("entity_type", filters.entity_type);
  if (filters.entity_id) params.append("entity_id", filters.entity_id);
  if (filters.action) params.append("action", filters.action);
  if (filters.page) params.append("page", filters.page);
  if (filters.per_page) params.append("per_page", filters.per_page);

  const response = await client.get(`/audit-logs?${params.toString()}`);
  return response.data;
}
