import axios from "axios";

// En desarrollo (Vite dev server) VITE_API_URL puede apuntar al backend directo.
// En produccion el contenedor frontend (nginx interno) proxea /api/v1 al backend.
// La deteccion por puerto era fragil; ahora depende exclusivamente de VITE_API_URL.
const defaultBaseURL = "/api/v1";

function getCookieValue(cookieName) {
  const cookies = document.cookie.split(";").map((cookie) => cookie.trim());
  const match = cookies.find((cookie) => cookie.startsWith(`${cookieName}=`));
  return match ? decodeURIComponent(match.split("=").slice(1).join("=")) : "";
}

// Retry config for rate limiting (429 errors)
const RETRY_CONFIG = {
  maxRetries: 3,
  initialDelayMs: 2000,  // 2 seconds first retry
  maxDelayMs: 10000,   // 10 seconds max
};

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

/**
 * Retry handler for 429 Too Many Requests.
 * Uses exponential backoff: 2s, 4s, 8s...
 */
async function retryRequest(error, config) {
  const retries = (config.__retryCount || 0) + 1;

  // Only retry on 429
  if (error.response?.status !== 429 || retries > RETRY_CONFIG.maxRetries) {
    return Promise.reject(error);
  }

  // Calculate delay with exponential backoff
  const delay = Math.min(
    RETRY_CONFIG.initialDelayMs * Math.pow(2, retries - 1),
    RETRY_CONFIG.maxDelayMs
  );

  console.warn(`Rate limited (429). Retrying in ${delay}ms (attempt ${retries}/${RETRY_CONFIG.maxRetries})`);

  // Wait and retry
  await new Promise((resolve) => setTimeout(resolve, delay));

  // Update retry count
  config.__retryCount = retries;
  config.__retryRequest = true;

  return client(config);
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    // Skip retry for non-429 errors or if already retried
    if (config && !config.__retryRequest) {
      try {
        return await retryRequest(error, config);
      } catch {
        // Retry failed, fall through to reject
      }
    }

    // Handle 401 - redirect to login
    if (error?.response?.status === 401 && window.location.pathname !== "/login") {
      window.sessionStorage.removeItem("manttoai_user");
      window.location.assign("/login");
    }

    return Promise.reject(error);
  }
);

export default client;
