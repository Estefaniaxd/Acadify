import axios from "axios";

// Configuración base para APIs
export const API_BASE_URL = import.meta.env.PROD
  ? "https://your-api-domain.com" // URL de producción
  : "http://localhost:8000"; // Backend local durante desarrollo

export const AVATAR_ASSETS_BASE_URL = import.meta.env.PROD
  ? "https://your-api-domain.com/static/assets"
  : "http://localhost:8000/static/assets";

// Cliente axios configurado
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 5000, // Reducido de 10s a 5s para evitar bloqueos largos
});

// Interceptor para agregar el token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Función helper para manejar errores de API
export function formatApiError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  if (typeof error === "object" && error !== null && "detail" in error) {
    return String((error as { detail: unknown }).detail);
  }
  return "Error desconocido";
}
