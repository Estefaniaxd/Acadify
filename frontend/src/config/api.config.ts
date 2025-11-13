/**
 * API Configuration
 * ==================
 * Configuración centralizada para URLs de API y WebSocket
 * 
 * @author Acadify Team
 * @version 1.0.0
 */

/**
 * Base URL del backend API
 * En producción, cambiar a la URL real del servidor
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    LIST: '/api/notificaciones',
    MARCAR_LEIDA: (id: string) => `/api/notificaciones/${id}/marcar-leida`,
    MARCAR_TODAS_LEIDAS: '/api/notificaciones/marcar-todas-leidas',
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
