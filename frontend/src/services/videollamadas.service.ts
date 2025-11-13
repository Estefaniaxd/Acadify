/**
 * Servicio de Videollamadas - API Client
 * 
 * @module services/videollamadas
 * @description Cliente HTTP para interactuar con la API de videollamadas.
 * Maneja todas las operaciones CRUD y control de videollamadas con Jitsi Meet.
 */

import axios, { AxiosInstance } from 'axios';
import type {
  Videollamada,
  VideollamadaCreateRequest,
  VideollamadaListResponse,
  Participante,
  ActualizarCalidadRequest,
  Grabacion,
  GrabacionCreateRequest,
  ValidacionAcceso,
  MessageResponse,
  ListarVideollamadasOptions
} from '../types/videollamada.types';

// ==================== CONFIGURACIÓN ====================

const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const VIDEOLLAMADAS_PATH = '/api/communication/videollamadas';

/**
 * Cliente de API configurado
 */
class VideollamadasAPIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token JWT
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor para manejo de errores
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          // Error del servidor (4xx, 5xx)
          const message = error.response.data?.detail || error.response.data?.message || error.message;
          throw new Error(message);
        } else if (error.request) {
          // Error de red
          throw new Error('Error de conexión. Verifica tu conexión a internet.');
        } else {
          throw error;
        }
      }
    );
  }

  /**
   * Obtiene el token JWT del localStorage
   */
  private getAuthToken(): string | null {
    return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  }

  // ==================== ENDPOINTS PRINCIPALES ====================

  /**
   * Health check del módulo de videollamadas
   */
  async healthCheck(): Promise<MessageResponse> {
    const response = await this.client.get<MessageResponse>(`${VIDEOLLAMADAS_PATH}/health`);
    return response.data;
  }

  /**
   * Genera un nombre único para una sala Jitsi
   */
  async generarRoomName(baseName: string): Promise<{ room_name: string }> {
    const response = await this.client.get<{ room_name: string }>(
      `${VIDEOLLAMADAS_PATH}/room-name/generate`,
      { params: { base_name: baseName } }
    );
    return response.data;
  }

  /**
   * Crea una nueva videollamada
   */
  async crearVideollamada(data: VideollamadaCreateRequest): Promise<Videollamada> {
    const response = await this.client.post<Videollamada>(VIDEOLLAMADAS_PATH, data);
    return response.data;
  }

  /**
   * Obtiene información de una videollamada específica
   */
  async obtenerVideollamada(
    videollamadaId: string,
    incluirParticipantes: boolean = false
  ): Promise<Videollamada> {
    const response = await this.client.get<Videollamada>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}`,
      { params: { incluir_participantes: incluirParticipantes } }
    );
    return response.data;
  }

  /**
   * Lista videollamadas con filtros opcionales
   */
  async listarVideollamadas(
    options: ListarVideollamadasOptions = {}
  ): Promise<VideollamadaListResponse> {
    const params = {
      sala_chat_id: options.sala_chat_id,
      solo_activas: options.solo_activas ?? true,
      skip: options.skip ?? 0,
      limit: options.limit ?? 50,
    };

    const response = await this.client.get<VideollamadaListResponse>(
      VIDEOLLAMADAS_PATH,
      { params }
    );
    return response.data;
  }

  // ==================== PARTICIPANTES ====================

  /**
   * Se une a una videollamada existente
   */
  async unirseAVideollamada(
    videollamadaId: string,
    esModerador: boolean = false
  ): Promise<Participante> {
    const response = await this.client.post<Participante>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/join`,
      { es_moderador: esModerador }
    );
    return response.data;
  }

  /**
   * Sale de una videollamada
   */
  async salirDeVideollamada(videollamadaId: string): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/leave`
    );
    return response.data;
  }

  /**
   * Obtiene lista de participantes activos
   */
  async obtenerParticipantesActivos(videollamadaId: string): Promise<Participante[]> {
    const response = await this.client.get<Participante[]>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/participants`
    );
    return response.data;
  }

  /**
   * Actualiza la calidad de conexión de un participante
   */
  async actualizarCalidadConexion(
    participanteId: string,
    data: ActualizarCalidadRequest
  ): Promise<Participante> {
    const response = await this.client.patch<Participante>(
      `${VIDEOLLAMADAS_PATH}/participants/${participanteId}/quality`,
      data
    );
    return response.data;
  }

  // ==================== CONTROL ====================

  /**
   * Finaliza una videollamada activa (solo moderador)
   */
  async finalizarVideollamada(
    videollamadaId: string,
    resumenIA?: string
  ): Promise<Videollamada> {
    const response = await this.client.post<Videollamada>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/finalize`,
      { resumen_ia: resumenIA }
    );
    return response.data;
  }

  /**
   * Cancela una videollamada (solo moderador)
   */
  async cancelarVideollamada(videollamadaId: string): Promise<Videollamada> {
    const response = await this.client.post<Videollamada>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/cancel`
    );
    return response.data;
  }

  // ==================== GRABACIONES ====================

  /**
   * Agrega una grabación a una videollamada (solo moderador)
   */
  async agregarGrabacion(
    videollamadaId: string,
    data: GrabacionCreateRequest
  ): Promise<Grabacion> {
    const response = await this.client.post<Grabacion>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/recordings`,
      data
    );
    return response.data;
  }

  /**
   * Obtiene todas las grabaciones de una videollamada
   */
  async obtenerGrabaciones(videollamadaId: string): Promise<Grabacion[]> {
    const response = await this.client.get<Grabacion[]>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/recordings`
    );
    return response.data;
  }

  // ==================== TRANSCRIPCIÓN ====================

  /**
   * Actualiza la transcripción de una videollamada (solo moderador)
   */
  async actualizarTranscripcion(
    videollamadaId: string,
    transcripcion: string
  ): Promise<Videollamada> {
    const response = await this.client.patch<Videollamada>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/transcription`,
      { transcripcion }
    );
    return response.data;
  }

  // ==================== VALIDACIÓN ====================

  /**
   * Valida si un usuario puede unirse a una videollamada
   */
  async validarPuedeUnirse(videollamadaId: string): Promise<ValidacionAcceso> {
    const response = await this.client.post<ValidacionAcceso>(
      `${VIDEOLLAMADAS_PATH}/${videollamadaId}/validate-join`
    );
    return response.data;
  }

  // ==================== JWT PARA JITSI ====================

  /**
   * Genera un token JWT para autenticación con Jitsi Meet
   * Este endpoint debe ser implementado en el backend
   */
  async generarJitsiToken(
    videollamadaId: string,
    roomName: string,
    displayName: string,
    esModerador: boolean = false
  ): Promise<{ token: string; expires_at: string }> {
    const response = await this.client.post<{ token: string; expires_at: string }>(
      '/api/auth/jitsi-token',
      {
        videollamada_id: videollamadaId,
        room_name: roomName,
        display_name: displayName,
        is_moderator: esModerador,
      }
    );
    return response.data;
  }
}

// ==================== EXPORTAR INSTANCIA SINGLETON ====================

export const videollamadasAPI = new VideollamadasAPIClient();

// ==================== FUNCIONES DE UTILIDAD ====================

/**
 * Determina la calidad de conexión basada en métricas
 */
export function calcularCalidadConexion(
  latenciaMs: number,
  perdidaPaquetes: number
): 'excelente' | 'buena' | 'regular' | 'mala' {
  if (latenciaMs < 50 && perdidaPaquetes < 1) {
    return 'excelente';
  } else if (latenciaMs < 150 && perdidaPaquetes < 3) {
    return 'buena';
  } else if (latenciaMs < 300 && perdidaPaquetes < 5) {
    return 'regular';
  } else {
    return 'mala';
  }
}

/**
 * Formatea la duración en segundos a formato legible
 */
export function formatearDuracion(segundos: number): string {
  const horas = Math.floor(segundos / 3600);
  const minutos = Math.floor((segundos % 3600) / 60);
  const segs = segundos % 60;

  if (horas > 0) {
    return `${horas}h ${minutos}m ${segs}s`;
  } else if (minutos > 0) {
    return `${minutos}m ${segs}s`;
  } else {
    return `${segs}s`;
  }
}

/**
 * Formatea el tamaño de archivo en bytes a formato legible
 */
export function formatearTamanoArchivo(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Obtiene el color asociado a una calidad de conexión
 */
export function obtenerColorCalidad(
  calidad: 'excelente' | 'buena' | 'regular' | 'mala'
): string {
  const colores = {
    excelente: 'text-green-600',
    buena: 'text-blue-600',
    regular: 'text-yellow-600',
    mala: 'text-red-600',
  };
  return colores[calidad] || 'text-gray-600';
}

/**
 * Obtiene el ícono asociado a una calidad de conexión
 */
export function obtenerIconoCalidad(
  calidad: 'excelente' | 'buena' | 'regular' | 'mala'
): string {
  const iconos = {
    excelente: '📶',
    buena: '📡',
    regular: '⚠️',
    mala: '❌',
  };
  return iconos[calidad] || '❓';
}
