import client from "./client";

export async function login(payload) {
  const { data } = await client.post("/auth/login", payload);
  return data;
}

export async function register(payload) {
  const { data } = await client.post("/auth/register", payload);
  return data;
}

export function logout() {
  window.localStorage.removeItem("manttoai_token");
  window.localStorage.removeItem("manttoai_user");
}
