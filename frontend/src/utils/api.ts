// Configuración base para APIs
export const API_BASE_URL = import.meta.env.PROD 
  ? 'https://your-api-domain.com'  // URL de producción
  : 'http://localhost:8000';  // Backend local durante desarrollo

export const AVATAR_ASSETS_BASE_URL = import.meta.env.PROD
  ? 'https://your-api-domain.com/static/assets'
  : 'http://localhost:8000/static/assets';

// Función helper para manejar errores de API
export function formatApiError(error: any): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  if (error?.detail) {
    return error.detail;
  }
  return 'Error desconocido';
}