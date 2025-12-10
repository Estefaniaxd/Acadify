/**
 * API Configuration
 * ==================
 * Configuración centralizada para URLs de API y WebSocket
 * 
 * @author Acadify Team
 * @version 1.0.0
 */

/**
 * Normaliza y resuelve la URL base que debe usar el frontend para hablar con el backend.
 *
 * Prioriza variables de entorno pero cae automáticamente al backend local cuando
 * el frontend corre en Vite (puerto 5173/4173) para evitar llamadas al origen del navegador.
 */
const resolveApiBaseUrl = (): string => {
  // 1. Prioridad: Si estamos en Vite (desarrollo), usar path relativo para aprovechar el proxy
  // Esto evita problemas de CORS y asegura que las cookies/headers pasen correctamente
  if (typeof window !== "undefined") {
    const { port } = window.location;
    if (port === "5173" || port === "4173") {
      return "";
    }
  }

  // 2. Variables de entorno (para producción o si no es Vite)
  const candidates = [import.meta.env.VITE_API_URL, import.meta.env.VITE_API_BASE_URL];

  const normalize = (value?: string | null): string | null => {
    if (!value) {
      return null;
    }

    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }

    if (/^https?:\/\//i.test(trimmed)) {
      return trimmed.replace(/\/$/, "");
    }

    if (typeof window !== "undefined") {
      const base = trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
      return `${window.location.origin}${base}`.replace(/\/$/, "");
    }

    return `http://localhost:8000${trimmed.startsWith("/") ? trimmed : `/${trimmed}`}`.replace(/\/$/, "");
  };

  for (const candidate of candidates) {
    const normalized = normalize(candidate);
    if (normalized) {
      return normalized;
    }
  }

  // 3. Fallback
  if (typeof window !== "undefined") {
    const { protocol, hostname, port } = window.location;
    const fallbackPort = port;
    const portSegment = fallbackPort ? `:${fallbackPort}` : "";
    return `${protocol}//${hostname}${portSegment}`.replace(/\/$/, "");
  }

  return "http://localhost:8000";
};

/**
 * Base URL del backend API
 * En producción, cambiar a la URL real del servidor
 */
export const API_BASE_URL = resolveApiBaseUrl();

/**
 * Base URL para WebSocket
 * Automáticamente deriva de API_BASE_URL
 */
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

/**
 * Endpoints de la API
 */
export const API_ENDPOINTS = {
  // Autenticación
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    ME: '/api/auth/me',
  },

  // Chat/Comunicación
  CHAT: {
    SALAS: '/api/chat/salas',
    MIS_SALAS: '/api/chat/salas/mis-salas',
    SALA: (id: string) => `/api/chat/salas/${id}`,
    PARTICIPANTES: (id: string) => `/api/chat/salas/${id}/participantes`,
    MENSAJES: (id: string) => `/api/chat/salas/${id}/mensajes`,
    UPLOAD: '/api/chat/upload',
    BUSCAR: (id: string) => `/api/chat/salas/${id}/mensajes/buscar`,
  },

  // WebSocket
  WS: {
    CHAT: (salaId: string) => `/ws/chat/${salaId}`,
    NOTIFICACIONES: '/ws/notificaciones',
    VIDEOLLAMADAS: '/ws/videollamadas',
  },

  // Gamificación
  GAMIFICATION: {
    RACHAS: '/api/gamification/rachas/mi-racha',
    REGISTRAR: '/api/gamification/rachas/registrar',
    USAR_RECUPERACION: '/api/gamification/rachas/usar-recuperacion',
    HISTORIAL: '/api/gamification/rachas/historial',
  },

  // Instituciones
  INSTITUCIONES: {
    LIST: '/api/instituciones',
    CREATE: '/admin/instituciones',
    DETAIL: (id: string) => `/api/instituciones/${id}`,
    UPDATE: (id: string) => `/api/instituciones/${id}`,
    DELETE: (id: string) => `/api/instituciones/${id}`,
    INVITAR: (id: string) => `/admin/instituciones/${id}/invitar-coordinador`,
  },

  // Tienda
  TIENDA: {
    ITEMS: '/api/tienda/items',
    COMPRAR: '/api/tienda/comprar',
    INVENTARIO: '/api/tienda/inventario',
  },

  // Notificaciones
  NOTIFICACIONES: {
    LIST: '/api/communication/notificaciones',
    MARCAR_LEIDAS: '/api/communication/notificaciones/marcar-leidas',
    MARCAR_TODAS_LEIDAS: '/api/communication/notificaciones/marcar-todas-leidas',
    COUNT: '/api/communication/notificaciones/count',
    CONFIG: '/api/communication/notificaciones/configuracion',
    UPDATE_CONFIG: '/api/communication/notificaciones/configuracion',
    SSE: '/api/communication/notificaciones/sse',
  },

  // Invitaciones
  INVITACIONES: {
    LIST: '/invitaciones',
    ACEPTAR: (id: number | string) => `/invitaciones/${id}/aceptar`,
  },
} as const;

/**
 * Configuración de timeouts
 */
export const TIMEOUTS = {
  /** Timeout para requests HTTP normales (30 segundos) */
  HTTP_REQUEST: 30000,
  /** Timeout para uploads de archivos (2 minutos) */
  FILE_UPLOAD: 120000,
  /** Intervalo de heartbeat WebSocket (30 segundos) */
  WS_HEARTBEAT: 30000,
  /** Delay máximo para reconexión WebSocket (30 segundos) */
  WS_MAX_RECONNECT_DELAY: 30000,
  /** Máximo de intentos de reconexión */
  WS_MAX_RECONNECT_ATTEMPTS: 10,
} as const;

/**
 * Headers por defecto
 */
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
} as const;

/**
 * Obtiene el token de autenticación
 */
export const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

/**
 * Obtiene headers con autenticación
 */
export const getAuthHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    ...DEFAULT_HEADERS,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

/**
 * Construye URL completa para endpoint
 */
export const buildURL = (endpoint: string): string => {
  // Si ya tiene protocolo, devolver tal cual
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  // Si empieza con /, concatenar con base URL
  return `${API_BASE_URL}${endpoint}`;
};

/**
 * Construye URL de WebSocket
 */
export const buildWSURL = (endpoint: string): string => {
  // Si ya tiene protocolo, devolver tal cual
  if (endpoint.startsWith('ws://') || endpoint.startsWith('wss://')) {
    return endpoint;
  }
  // Si empieza con /, concatenar con base WS URL
  return `${WS_BASE_URL}${endpoint}`;
};

export default {
  API_BASE_URL,
  WS_BASE_URL,
  API_ENDPOINTS,
  TIMEOUTS,
  DEFAULT_HEADERS,
  getAuthToken,
  getAuthHeaders,
  buildURL,
  buildWSURL,
};
