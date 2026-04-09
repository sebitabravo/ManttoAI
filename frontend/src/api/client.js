import axios from "axios";

// En desarrollo (Vite dev server) VITE_API_URL puede apuntar al backend directo.
// En producción el contenedor frontend (nginx interno) proxea /api/v1/ al backend.
// La detección por puerto era frágil; ahora depende exclusivamente de VITE_API_URL.
const defaultBaseURL = "/api/v1";

function getCookieValue(cookieName) {
  const cookies = document.cookie.split(";").map((cookie) => cookie.trim());
  const match = cookies.find((cookie) => cookie.startsWith(`${cookieName}=`));
  return match ? decodeURIComponent(match.split("=").slice(1).join("=")) : "";
}

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || defaultBaseURL,
  timeout: 5000,
  withCredentials: true,
});

client.interceptors.request.use((config) => {
  const method = String(config.method || "get").toLowerCase();
  if (["post", "put", "patch", "delete"].includes(method)) {
    const csrfToken = getCookieValue("manttoai_csrf");
    if (csrfToken) {
      config.headers = config.headers || {};
      config.headers["X-CSRF-Token"] = csrfToken;
    }
  }

  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401 && window.location.pathname !== "/login") {
      window.sessionStorage.removeItem("manttoai_user");
      window.location.assign("/login");
    }

    return Promise.reject(error);
  }
);

export default client;
