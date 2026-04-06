import client from "./client";

export async function login(payload) {
  const { data } = await client.post("/auth/login", payload);
  return data;
}

export async function getCurrentUser() {
  const { data } = await client.get("/auth/me");
  return data;
}

export async function register(payload) {
  const { data } = await client.post("/auth/register", payload);
  return data;
}

export async function logout() {
  await client.post("/auth/logout");
}
