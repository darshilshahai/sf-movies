import axios from "axios";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.API_BASE_URL ||
  (import.meta.env.DEV ? "http://localhost:8000" : "");

if (!apiBaseUrl) {
  throw new Error(
    "VITE_API_BASE_URL is not configured. Please check your environment configuration."
  );
}

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});
