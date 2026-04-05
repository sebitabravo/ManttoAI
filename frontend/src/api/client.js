import axios from "axios";

const defaultBaseURL = window.location.port === "5173" ? "http://localhost:8000" : "/api";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || defaultBaseURL,
  timeout: 5000,
});

client.interceptors.request.use((config) => {
  const token = window.localStorage.getItem("manttoai_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;
