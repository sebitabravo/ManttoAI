import client from "./client";

/** Actualiza el perfil del usuario autenticado. */
export async function updateProfile(payload) {
  const { data } = await client.put("/auth/profile", payload);
  return data;
}
