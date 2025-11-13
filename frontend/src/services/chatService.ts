/**
 * Chat Service
 * =============
 * Servicio para interactuar con la API REST de chat.
 * 
 * Responsabilidades:
 * - Operaciones CRUD sobre salas y mensajes
 * - Gestión de participantes
 * - Subida de archivos
 * - Manejo de errores y retry logic
 * 
 * Principios SOLID:
 * - Single Responsibility: Solo maneja llamadas HTTP de chat
 * - Dependency Inversion: Usa axios (abstracción)
 * 
 * @author Acadify Team
 * @version 1.0.0
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

/**
 * Tipo de sala de chat
 */
export enum TipoSala {
  INDIVIDUAL = 'individual',
  GRUPO = 'grupo',
  CLASE = 'clase',
  CURSO = 'curso'
}

/**
 * Tipo de mensaje
 */
export enum TipoMensaje {
  TEXTO = 'texto',
  IMAGEN = 'imagen',
  VIDEO = 'video',
  AUDIO = 'audio',
  ARCHIVO = 'archivo',
  SISTEMA = 'sistema',
  IA = 'ia'
}

/**
 * Interfaz de sala de chat
 */
export interface SalaChat {
  id: string;
  nombre: string;
  tipo: TipoSala;
  descripcion?: string;
  imagen_sala?: string;
  creado_por: string;
  fecha_creacion: string;
  ultima_actividad: string;
  esta_activa: boolean;
  curso_id?: string;
  // Computed
  no_leidos?: number;
  ultimo_mensaje?: Mensaje;
}

/**
 * Interfaz de mensaje
 */
export interface Mensaje {
  id: string;
  sala_id: string;
  usuario_id: string;
  usuario_nombre?: string;
  usuario_apellido?: string;
  usuario_avatar?: string;
  contenido: string;
  contenido_html?: string;
  tipo_mensaje: TipoMensaje;
  archivos_urls?: string[];
  metadatos_archivos?: Record<string, any>;
  mensaje_padre_id?: string;
  menciones_usuarios?: string[];
  menciones_ia?: boolean;
  menciones_todos?: boolean;
  es_importante?: boolean;
  es_anuncio?: boolean;
  fecha_creacion: string;
  fecha_edicion?: string;
  fecha_eliminacion?: string;
  editado: boolean;
  eliminado: boolean;
  reacciones?: Record<string, string[]>; // emoji -> [usuario_ids]
  es_propio?: boolean; // Computed en el cliente
}

/**
 * Interfaz de participante
 */
export interface Participante {
  usuario_id: string;
  sala_id: string;
  puede_escribir: boolean;
  puede_eliminar_mensajes: boolean;
  es_administrador: boolean;
  fecha_union: string;
  silenciado: boolean;
  // Usuario relacionado
  usuario_nombre?: string;
  usuario_apellido?: string;
  usuario_avatar?: string;
}

/**
 * Request para crear sala
 */
export interface CrearSalaRequest {
  nombre: string;
  tipo: TipoSala;
  descripcion?: string;
  imagen_sala?: string;
  curso_id?: string;
  participantes_ids?: string[];
}

/**
 * Request para crear mensaje
 */
export interface CrearMensajeRequest {
  contenido: string;
  tipo_mensaje?: TipoMensaje;
  mensaje_padre_id?: string;
  archivos_urls?: string[];
  metadatos_archivos?: Record<string, any>;
  menciones_usuarios?: string[];
  menciones_ia?: boolean;
  menciones_todos?: boolean;
  es_importante?: boolean;
  es_anuncio?: boolean;
}

/**
 * Request para actualizar mensaje
 */
export interface ActualizarMensajeRequest {
  contenido: string;
}

/**
 * Response paginada
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Opciones de configuración del servicio
 */
export interface ChatServiceOptions {
  baseURL: string;
  timeout?: number;
}

/**
 * Clase ChatService
 */
export class ChatService {
  private axiosInstance: AxiosInstance;
  private token: string | null = null;
  
  constructor(options: ChatServiceOptions) {
    this.axiosInstance = axios.create({
      baseURL: options.baseURL,
      timeout: options.timeout ?? 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Interceptor para añadir token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Interceptor para manejo de errores
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Establece el token de autenticación
   */
  public setToken(token: string): void {
    this.token = token;
  }
  
  /**
   * Limpia el token de autenticación
   */
  public clearToken(): void {
    this.token = null;
  }
  
  // ==================== SALAS ====================
  
  /**
   * Obtiene todas las salas del usuario
   */
  public async getSalas(): Promise<SalaChat[]> {
    const response = await this.axiosInstance.get<SalaChat[]>('/salas');
    return response.data;
  }
  
  /**
   * Obtiene una sala específica por ID
   */
  public async getSala(salaId: string): Promise<SalaChat> {
    const response = await this.axiosInstance.get<SalaChat>(`/salas/${salaId}`);
    return response.data;
  }
  
  /**
   * Crea una nueva sala
   */
  public async crearSala(data: CrearSalaRequest): Promise<SalaChat> {
    const response = await this.axiosInstance.post<SalaChat>('/salas', data);
    return response.data;
  }
  
  /**
   * Actualiza una sala existente
   */
  public async actualizarSala(
    salaId: string,
    data: Partial<CrearSalaRequest>
  ): Promise<SalaChat> {
    const response = await this.axiosInstance.put<SalaChat>(`/salas/${salaId}`, data);
    return response.data;
  }
  
  /**
   * Elimina una sala
   */
  public async eliminarSala(salaId: string): Promise<void> {
    await this.axiosInstance.delete(`/salas/${salaId}`);
  }
  
  /**
   * Une al usuario a una sala
   */
  public async unirseSala(salaId: string): Promise<Participante> {
    const response = await this.axiosInstance.post<Participante>(`/salas/${salaId}/unirse`);
    return response.data;
  }
  
  /**
   * Sale de una sala
   */
  public async salirSala(salaId: string): Promise<void> {
    await this.axiosInstance.post(`/salas/${salaId}/salir`);
  }
  
  // ==================== MENSAJES ====================
  
  /**
   * Obtiene mensajes de una sala (paginados)
   */
  public async getMensajes(
    salaId: string,
    page: number = 1,
    size: number = 50
  ): Promise<PaginatedResponse<Mensaje>> {
    const response = await this.axiosInstance.get<PaginatedResponse<Mensaje>>(
      `/salas/${salaId}/mensajes`,
      {
        params: { page, size }
      }
    );
    return response.data;
  }
  
  /**
   * Envía un mensaje (vía REST - alternativa a WebSocket)
   */
  public async enviarMensaje(
    salaId: string,
    data: CrearMensajeRequest
  ): Promise<Mensaje> {
    const response = await this.axiosInstance.post<Mensaje>(
      `/salas/${salaId}/mensajes`,
      data
    );
    return response.data;
  }
  
  /**
   * Edita un mensaje existente
   */
  public async editarMensaje(
    mensajeId: string,
    data: ActualizarMensajeRequest
  ): Promise<Mensaje> {
    const response = await this.axiosInstance.put<Mensaje>(
      `/mensajes/${mensajeId}`,
      data
    );
    return response.data;
  }
  
  /**
   * Elimina un mensaje
   */
  public async eliminarMensaje(mensajeId: string): Promise<void> {
    await this.axiosInstance.delete(`/mensajes/${mensajeId}`);
  }
  
  /**
   * Añade una reacción a un mensaje
   */
  public async añadirReaccion(mensajeId: string, emoji: string): Promise<Mensaje> {
    const response = await this.axiosInstance.post<Mensaje>(
      `/mensajes/${mensajeId}/reacciones`,
      { emoji }
    );
    return response.data;
  }
  
  /**
   * Marca mensajes como leídos
   */
  public async marcarComoLeido(mensajesIds: string[]): Promise<void> {
    await this.axiosInstance.post('/mensajes/marcar-leido', {
      mensajes_ids: mensajesIds
    });
  }
  
  /**
   * Marca toda una sala como leída
   */
  public async marcarSalaLeida(salaId: string): Promise<void> {
    await this.axiosInstance.post(`/salas/${salaId}/marcar-leida`);
  }
  
  // ==================== PARTICIPANTES ====================
  
  /**
   * Obtiene participantes de una sala
   */
  public async getParticipantes(salaId: string): Promise<Participante[]> {
    const response = await this.axiosInstance.get<Participante[]>(
      `/salas/${salaId}/participantes`
    );
    return response.data;
  }
  
  /**
   * Añade participantes a una sala
   */
  public async añadirParticipantes(
    salaId: string,
    usuariosIds: string[]
  ): Promise<Participante[]> {
    const response = await this.axiosInstance.post<Participante[]>(
      `/salas/${salaId}/participantes`,
      { usuarios_ids: usuariosIds }
    );
    return response.data;
  }
  
  /**
   * Actualiza permisos de un participante
   */
  public async actualizarParticipante(
    salaId: string,
    usuarioId: string,
    permisos: Partial<Participante>
  ): Promise<Participante> {
    const response = await this.axiosInstance.put<Participante>(
      `/salas/${salaId}/participantes/${usuarioId}`,
      permisos
    );
    return response.data;
  }
  
  /**
   * Elimina un participante de una sala
   */
  public async eliminarParticipante(salaId: string, usuarioId: string): Promise<void> {
    await this.axiosInstance.delete(`/salas/${salaId}/participantes/${usuarioId}`);
  }
  
  // ==================== ARCHIVOS ====================
  
  /**
   * Sube un archivo al chat
   */
  public async subirArchivo(file: File, salaId: string): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sala_id', salaId);
    
    const response = await this.axiosInstance.post<{ url: string }>(
      '/archivos/subir',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    return response.data.url;
  }
  
  /**
   * Sube múltiples archivos
   */
  public async subirArchivos(files: File[], salaId: string): Promise<string[]> {
    const uploadPromises = files.map(file => this.subirArchivo(file, salaId));
    return Promise.all(uploadPromises);
  }
  
  // ==================== BÚSQUEDA ====================
  
  /**
   * Busca mensajes en una sala
   */
  public async buscarMensajes(
    salaId: string,
    query: string,
    page: number = 1,
    size: number = 20
  ): Promise<PaginatedResponse<Mensaje>> {
    const response = await this.axiosInstance.get<PaginatedResponse<Mensaje>>(
      `/salas/${salaId}/mensajes/buscar`,
      {
        params: { q: query, page, size }
      }
    );
    return response.data;
  }
  
  // ==================== UTILIDADES ====================
  
  /**
   * Maneja errores de la API
   */
  private handleError(error: AxiosError): void {
    if (error.response) {
      // Error del servidor
      console.error('Chat API Error:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url
      });
      
      // Casos específicos
      if (error.response.status === 401) {
        console.error('❌ No autorizado - token inválido o expirado');
        // Aquí podrías emitir un evento para logout
      } else if (error.response.status === 403) {
        console.error('❌ Prohibido - sin permisos');
      } else if (error.response.status === 404) {
        console.error('❌ No encontrado');
      }
    } else if (error.request) {
      // Error de red
      console.error('❌ Error de red - sin respuesta del servidor');
    } else {
      // Otro error
      console.error('❌ Error:', error.message);
    }
  }
}

// ==================== Singleton Instance ====================

let chatServiceInstance: ChatService | null = null;

/**
 * Crea o devuelve la instancia del servicio
 */
export const getChatService = (options?: ChatServiceOptions): ChatService => {
  if (!chatServiceInstance) {
    if (!options) {
      throw new Error('ChatService: options requeridas en la primera llamada');
    }
    chatServiceInstance = new ChatService(options);
  }
  return chatServiceInstance;
};

/**
 * Resetea la instancia (útil para tests)
 */
export const resetChatService = (): void => {
  chatServiceInstance = null;
};

export default ChatService;
