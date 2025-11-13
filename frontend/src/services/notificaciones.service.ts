/**
 * Servicio de Notificaciones - API Client
 * 
 * @module services/notificaciones
 * @description Cliente HTTP para interactuar con la API de notificaciones.
 * Maneja notificaciones, configuración y preferencias del usuario.
 */

import axios, { AxiosInstance } from 'axios';

// ==================== TIPOS ====================

export interface Notificacion {
  id: string;
  usuario_id: string;
  titulo: string;
  mensaje?: string;
  tipo_notificacion: TipoNotificacion;
  url_accion?: string;
  icono?: string;
  color?: string;
  sala_id?: string;
  mensaje_id?: string;
  tarea_id?: string;
  curso_id?: string;
  leida: boolean;
  enviada_email: boolean;
  enviada_push: boolean;
  fecha_creacion: string;
  fecha_lectura?: string;
  datos_adicionales?: Record<string, any>;
}

export type TipoNotificacion =
  | 'mensaje_directo'
  | 'mencion'
  | 'respuesta_hilo'
  | 'mensaje_importante'
  | 'tarea_nueva'
  | 'tarea_vencimiento'
  | 'tarea_calificada'
  | 'tarea_comentario'
  | 'curso_nuevo'
  | 'clase_cancelada'
  | 'evaluacion_disponible'
  | 'logro_desbloqueado'
  | 'sistema';

export interface ConfiguracionNotificaciones {
  id: string;
  usuario_id: string;
  notificaciones_activas: boolean;
  sonido_activo: boolean;
  
  // Notificaciones de tareas
  tareas_nuevas: boolean;
  tareas_vencimiento_24h: boolean;
  tareas_vencimiento_1h: boolean;
  tareas_calificadas: boolean;
  tareas_comentarios: boolean;
  
  // Notificaciones de chat
  mensajes_directos: boolean;
  menciones: boolean;
  respuestas_hilos: boolean;
  mensajes_importantes: boolean;
  
  // Notificaciones por email
  resumen_diario_email: boolean;
  urgentes_email: boolean;
  menciones_email: boolean;
  
  // Configuración de horarios
  horario_inicio: string;
  horario_fin: string;
  dias_activos: number[];
  
  fecha_actualizacion?: string;
}

export interface FiltrosNotificaciones {
  tipo_notificacion?: TipoNotificacion;
  solo_no_leidas?: boolean;
  ordenar_por?: 'fecha_creacion' | 'fecha_lectura';
  orden_desc?: boolean;
  limite?: number;
  offset?: number;
}

export interface ContadorNotificaciones {
  count: number;
}

// ==================== CONFIGURACIÓN ====================

const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const NOTIFICACIONES_PATH = '/api/communication';

/**
 * Cliente de API configurado para notificaciones
 */
class NotificacionesAPIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${NOTIFICACIONES_PATH}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token JWT
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para manejar errores
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Silenciar errores 405 (endpoints deshabilitados temporalmente)
        if (error.response?.status !== 405) {
          console.error('Error en API de notificaciones:', error.response?.data || error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // ==================== NOTIFICACIONES ====================

  /**
   * Obtiene notificaciones con filtros opcionales
   */
  async obtenerNotificaciones(filtros?: FiltrosNotificaciones): Promise<Notificacion[]> {
    try {
      const { data } = await this.client.get<Notificacion[]>('/notificaciones', {
        params: {
          tipo_notificacion: filtros?.tipo_notificacion,
          solo_no_leidas: filtros?.solo_no_leidas,
          ordenar_por: filtros?.ordenar_por || 'fecha_creacion',
          orden_desc: filtros?.orden_desc !== false,
          limite: filtros?.limite || 20,
          offset: filtros?.offset || 0,
        },
      });
      return data;
    } catch (error) {
      // Silenciar errores 405
      if (axios.isAxiosError(error) && error.response?.status !== 405) {
        console.error('Error al obtener notificaciones:', error);
      }
      throw error;
    }
  }

  /**
   * Marca notificaciones específicas como leídas
   */
  async marcarComoLeidas(notificacionesIds: string[]): Promise<{ message: string }> {
    const { data } = await this.client.post('/notificaciones/marcar-leidas', {
      notificaciones_ids: notificacionesIds,
    });
    return data;
  }

  /**
   * Marca todas las notificaciones como leídas
   */
  async marcarTodasLeidas(tipoNotificacion?: TipoNotificacion): Promise<{ message: string }> {
    const { data } = await this.client.post('/notificaciones/marcar-todas-leidas', null, {
      params: {
        tipo_notificacion: tipoNotificacion,
      },
    });
    return data;
  }

  /**
   * Obtiene el contador de notificaciones no leídas
   */
  async obtenerContadorNoLeidas(): Promise<number> {
    try {
      const { data } = await this.client.get<ContadorNotificaciones>('/notificaciones/count');
      return data.count ?? 0;
    } catch (error) {
      // Silenciar errores 405 (endpoint deshabilitado)
      if (axios.isAxiosError(error) && error.response?.status !== 405) {
        console.warn('Error al obtener contador de notificaciones:', error);
      }
      return 0;
    }
  }

  // ==================== CONFIGURACIÓN ====================

  /**
   * Obtiene la configuración de notificaciones del usuario
   */
  async obtenerConfiguracion(): Promise<ConfiguracionNotificaciones> {
    try {
      const { data } = await this.client.get('/configuracion/notificaciones');
      return data;
    } catch (error) {
      console.warn('Error al obtener configuración de notificaciones:', error);
      // Retornar configuración por defecto
      return {
        id: '',
        usuario_id: '',
        notificaciones_activas: true,
        sonido_activo: false,
        tareas_nuevas: true,
        tareas_vencimiento_24h: true,
        tareas_vencimiento_1h: true,
        tareas_calificadas: true,
        tareas_comentarios: true,
        mensajes_directos: true,
        menciones: true,
        respuestas_hilos: true,
        mensajes_importantes: true,
        resumen_diario_email: false,
        urgentes_email: true,
        menciones_email: true,
        horario_inicio: '08:00',
        horario_fin: '20:00',
        dias_activos: [1, 2, 3, 4, 5]
      };
    }
  }

  /**
   * Actualiza la configuración de notificaciones
   */
  async actualizarConfiguracion(
    config: Partial<ConfiguracionNotificaciones>
  ): Promise<ConfiguracionNotificaciones> {
    const { data } = await this.client.put('/configuracion/notificaciones', config);
    return data;
  }
}

// ==================== EXPORTAR INSTANCIA ÚNICA ====================

export const notificacionesService = new NotificacionesAPIClient();
export default notificacionesService;

// ==================== UTILIDADES ====================

/**
 * Obtiene el icono asociado a un tipo de notificación
 */
export function obtenerIconoNotificacion(tipo: TipoNotificacion): string {
  const iconos: Record<TipoNotificacion, string> = {
    mensaje_directo: '💬',
    mencion: '@',
    respuesta_hilo: '↩️',
    mensaje_importante: '⭐',
    tarea_nueva: '📝',
    tarea_vencimiento: '⏰',
    tarea_calificada: '✅',
    tarea_comentario: '💭',
    curso_nuevo: '📚',
    clase_cancelada: '❌',
    evaluacion_disponible: '📊',
    logro_desbloqueado: '🏆',
    sistema: '🔔',
  };
  return iconos[tipo] || '🔔';
}

/**
 * Obtiene el color asociado a un tipo de notificación
 */
export function obtenerColorNotificacion(tipo: TipoNotificacion): string {
  const colores: Record<TipoNotificacion, string> = {
    mensaje_directo: 'from-blue-500 to-indigo-600',
    mencion: 'from-purple-500 to-pink-600',
    respuesta_hilo: 'from-cyan-500 to-blue-600',
    mensaje_importante: 'from-yellow-500 to-orange-600',
    tarea_nueva: 'from-green-500 to-emerald-600',
    tarea_vencimiento: 'from-red-500 to-rose-600',
    tarea_calificada: 'from-violet-500 to-purple-600',
    tarea_comentario: 'from-indigo-500 to-blue-600',
    curso_nuevo: 'from-teal-500 to-cyan-600',
    clase_cancelada: 'from-gray-500 to-gray-700',
    evaluacion_disponible: 'from-amber-500 to-yellow-600',
    logro_desbloqueado: 'from-yellow-400 to-orange-500',
    sistema: 'from-gray-400 to-gray-600',
  };
  return colores[tipo] || 'from-gray-500 to-gray-700';
}

/**
 * Obtiene el título legible de un tipo de notificación
 */
export function obtenerTituloTipo(tipo: TipoNotificacion): string {
  const titulos: Record<TipoNotificacion, string> = {
    mensaje_directo: 'Mensaje Directo',
    mencion: 'Mención',
    respuesta_hilo: 'Respuesta en Hilo',
    mensaje_importante: 'Mensaje Importante',
    tarea_nueva: 'Nueva Tarea',
    tarea_vencimiento: 'Tarea por Vencer',
    tarea_calificada: 'Tarea Calificada',
    tarea_comentario: 'Comentario en Tarea',
    curso_nuevo: 'Nuevo Curso',
    clase_cancelada: 'Clase Cancelada',
    evaluacion_disponible: 'Evaluación Disponible',
    logro_desbloqueado: 'Logro Desbloqueado',
    sistema: 'Sistema',
  };
  return titulos[tipo] || 'Notificación';
}

/**
 * Formatea tiempo relativo (hace X minutos/horas/días)
 */
export function formatearTiempoRelativo(fecha: string): string {
  const ahora = new Date();
  const fechaNotif = new Date(fecha);
  const diffMs = ahora.getTime() - fechaNotif.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHoras = Math.floor(diffMs / 3600000);
  const diffDias = Math.floor(diffMs / 86400000);

  if (diffMin < 1) return 'Ahora mismo';
  if (diffMin < 60) return `Hace ${diffMin} min`;
  if (diffHoras < 24) return `Hace ${diffHoras} h`;
  if (diffDias < 7) return `Hace ${diffDias} d`;
  
  return fechaNotif.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
}

/**
 * Nombres de días de la semana
 */
export const DIAS_SEMANA = [
  { value: 1, label: 'Lunes' },
  { value: 2, label: 'Martes' },
  { value: 3, label: 'Miércoles' },
  { value: 4, label: 'Jueves' },
  { value: 5, label: 'Viernes' },
  { value: 6, label: 'Sábado' },
  { value: 7, label: 'Domingo' },
];
