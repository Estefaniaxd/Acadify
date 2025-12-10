import axios, { AxiosInstance } from 'axios';

// ====================================
// TIPOS
// ====================================

export enum TipoNotificacion {
  TAREA_CALIFICADA = 'tarea_calificada',
  TAREA_CREADA = 'tarea_creada',
  RETROALIMENTACION_IA = 'retroalimentacion_ia',
  NUEVO_MENSAJE = 'nuevo_mensaje',
  ENTREGA_RECIBIDA = 'entrega_recibida',
  RECORDATORIO_VENCIMIENTO = 'recordatorio_vencimiento',
}

export interface Notificacion {
  id: string;
  usuario_id: string;
  tipo: TipoNotificacion;
  titulo: string;
  mensaje: string;
  tarea_id?: string;
  entrega_id?: string;
  leida: boolean;
  fecha_creacion: string;
  acciones?: {
    label: string;
    url: string;
    tipo: 'link' | 'button';
  }[];
}

// ====================================
// SERVICIO DE NOTIFICACIONES
// ====================================

export class NotificacionesService {
  private apiClient: AxiosInstance;
  private apiUrl: string;
  private eventSource?: EventSource;
  private listeners: Map<TipoNotificacion, Set<(notificacion: Notificacion) => void>> = new Map();

  constructor(apiUrl: string = 'http://localhost:8000') {
    this.apiUrl = apiUrl;
    this.apiClient = axios.create({
      baseURL: apiUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token JWT
    this.apiClient.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  /**
   * Obtener todas las notificaciones del usuario
   */
  async obtenerNotificaciones(
    limite: number = 20,
    offset: number = 0,
    soloNoLeidas: boolean = false
  ): Promise<{ notificaciones: Notificacion[]; total: number }> {
    try {
      console.log('🔔 Obteniendo notificaciones...');
      const response = await this.apiClient.get('/api/notificaciones', {
        params: {
          limit: limite,
          offset,
          solo_no_leidas: soloNoLeidas,
        },
      });
      console.log('✅ Notificaciones obtenidas:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error obteniendo notificaciones:', error);
      throw error;
    }
  }

  /**
   * Marcar notificación como leída
   */
  async marcarComoLeida(notificacionId: string): Promise<{ exito: boolean }> {
    try {
      console.log('🔔 Marcando notificación como leída:', notificacionId);
      const response = await this.apiClient.patch(
        `/api/notificaciones/${notificacionId}/leida`
      );
      console.log('✅ Notificación marcada como leída');
      return response.data;
    } catch (error) {
      console.error('❌ Error marcando notificación:', error);
      throw error;
    }
  }

  /**
   * Marcar todas las notificaciones como leídas
   */
  async marcarTodasComoLeidas(): Promise<{ exito: boolean }> {
    try {
      console.log('🔔 Marcando todas las notificaciones como leídas...');
      const response = await this.apiClient.post('/api/notificaciones/marcar-todas-leidas');
      console.log('✅ Todas marcadas como leídas');
      return response.data;
    } catch (error) {
      console.error('❌ Error marcando todas:', error);
      throw error;
    }
  }

  /**
   * Eliminar notificación
   */
  async eliminarNotificacion(notificacionId: string): Promise<{ exito: boolean }> {
    try {
      console.log('🔔 Eliminando notificación:', notificacionId);
      const response = await this.apiClient.delete(
        `/api/notificaciones/${notificacionId}`
      );
      console.log('✅ Notificación eliminada');
      return response.data;
    } catch (error) {
      console.error('❌ Error eliminando notificación:', error);
      throw error;
    }
  }

  /**
   * Enviar notificación (solo admin/profesor)
   */
  async enviarNotificacion(
    usuarioId: string,
    tipo: TipoNotificacion,
    titulo: string,
    mensaje: string,
    metadatos?: Record<string, any>
  ): Promise<{ notificacion_id: string }> {
    try {
      console.log('🔔 Enviando notificación a usuario:', usuarioId);
      const response = await this.apiClient.post('/api/notificaciones/enviar', {
        usuario_id: usuarioId,
        tipo,
        titulo,
        mensaje,
        metadatos,
      });
      console.log('✅ Notificación enviada');
      return response.data;
    } catch (error) {
      console.error('❌ Error enviando notificación:', error);
      throw error;
    }
  }

  /**
   * Conectar a SSE (Server-Sent Events) para recibir notificaciones en tiempo real
   */
  conectarSSE(usuarioId: string, onNotificacion?: (notif: Notificacion) => void): void {
    try {
      console.log('🔔 Conectando a SSE para notificaciones en tiempo real...');

      // Usar el endpoint correcto con el token JWT
      const token = localStorage.getItem('access_token');
      const url = `${this.apiUrl}/api/notificaciones/sse?usuario_id=${usuarioId}&token=${token}`;

      this.eventSource = new EventSource(url);

      this.eventSource.onmessage = (event) => {
        try {
          const notificacion: Notificacion = JSON.parse(event.data);
          console.log('📨 Nueva notificación recibida:', notificacion);

          // Llamar listeners registrados
          const listeners = this.listeners.get(notificacion.tipo);
          if (listeners) {
            listeners.forEach((callback) => callback(notificacion));
          }

          // Callback global
          if (onNotificacion) {
            onNotificacion(notificacion);
          }

          // Emitir evento global
          window.dispatchEvent(
            new CustomEvent('nueva-notificacion', { detail: notificacion })
          );
        } catch (error) {
          console.error('❌ Error procesando notificación SSE:', error);
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('❌ Error en SSE:', error);
        this.desconectarSSE();
        // Intentar reconectar en 5 segundos
        setTimeout(() => this.conectarSSE(usuarioId, onNotificacion), 5000);
      };

      console.log('✅ Conectado a SSE');
    } catch (error) {
      console.error('❌ Error conectando SSE:', error);
    }
  }

  /**
   * Desconectar SSE
   */
  desconectarSSE(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = undefined;
      console.log('🔌 Desconectado de SSE');
    }
  }

  /**
   * Registrar listener para tipo específico de notificación
   */
  on(tipo: TipoNotificacion, callback: (notif: Notificacion) => void): () => void {
    if (!this.listeners.has(tipo)) {
      this.listeners.set(tipo, new Set());
    }
    this.listeners.get(tipo)!.add(callback);

    // Retornar función para desuscribirse
    return () => {
      const set = this.listeners.get(tipo);
      if (set) {
        set.delete(callback);
      }
    };
  }

  /**
   * Obtener conteo de notificaciones no leídas
   */
  async obtenerConteoNoLeidas(): Promise<number> {
    try {
      const response = await this.apiClient.get('/api/notificaciones/conteo-no-leidas');
      return response.data.conteo;
    } catch (error) {
      console.error('❌ Error obteniendo conteo:', error);
      return 0;
    }
  }

  /**
   * Obtener notificaciones agrupadas por tipo
   */
  async obtenerNotificacionesAgrupadas(): Promise<
    Record<TipoNotificacion, Notificacion[]>
  > {
    try {
      console.log('🔔 Obteniendo notificaciones agrupadas...');
      const { notificaciones } = await this.obtenerNotificaciones(100);
      const agrupadas: Record<TipoNotificacion, Notificacion[]> = {} as any;

      notificaciones.forEach((notif) => {
        if (!agrupadas[notif.tipo]) {
          agrupadas[notif.tipo] = [];
        }
        agrupadas[notif.tipo].push(notif);
      });

      console.log('✅ Notificaciones agrupadas');
      return agrupadas;
    } catch (error) {
      console.error('❌ Error agrupando notificaciones:', error);
      throw error;
    }
  }
}

// Instancia global
export const notificacionesService = new NotificacionesService();
