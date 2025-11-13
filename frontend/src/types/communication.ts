/**
 * Communication Types
 * ===================
 * Definiciones de tipos TypeScript para el sistema de comunicación.
 * 
 * Incluye:
 * - Salas de chat
 * - Mensajes
 * - Usuarios
 * - Eventos WebSocket
 * - Estados y configuraciones
 * 
 * @author Acadify Team
 * @version 1.0.0
 */

// ==================== ENUMS ====================

/**
 * Tipos de salas de chat
 */
export enum TipoSala {
  /** Chat 1:1 entre dos usuarios */
  INDIVIDUAL = 'individual',
  /** Grupo de chat con múltiples usuarios */
  GRUPO = 'grupo',
  /** Chat de una clase académica */
  CLASE = 'clase',
  /** Chat de un curso completo */
  CURSO = 'curso'
}

/**
 * Tipos de mensajes
 */
export enum TipoMensaje {
  /** Mensaje de texto plano o con markdown */
  TEXTO = 'texto',
  /** Imagen compartida */
  IMAGEN = 'imagen',
  /** Video compartido */
  VIDEO = 'video',
  /** Audio/nota de voz */
  AUDIO = 'audio',
  /** Archivo genérico */
  ARCHIVO = 'archivo',
  /** Mensaje del sistema (join, leave, etc.) */
  SISTEMA = 'sistema',
  /** Mensaje generado por IA (Rutilio) */
  IA = 'ia'
}

/**
 * Estado de usuarios
 */
export enum EstadoUsuario {
  /** Usuario activo y disponible */
  ONLINE = 'online',
  /** Usuario desconectado */
  OFFLINE = 'offline',
  /** Usuario ausente (AFK) */
  AUSENTE = 'ausente',
  /** No molestar */
  NO_MOLESTAR = 'no_molestar'
}

/**
 * Estado de conexión WebSocket
 */
export enum WebSocketState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTING = 'disconnecting',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

// ==================== INTERFACES BASE ====================

/**
 * Usuario del sistema
 */
export interface Usuario {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  avatar_url?: string;
  estado?: EstadoUsuario;
  ultimo_visto?: string;
  esta_escribiendo?: boolean;
}

/**
 * Sala de chat
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
  
  // Computed fields (calculados en cliente)
  no_leidos?: number;
  ultimo_mensaje?: Mensaje;
  participantes?: Participante[];
  usuarios_online?: number;
  usuarios_escribiendo?: string[];
}

/**
 * Mensaje en una sala
 */
export interface Mensaje {
  id: string;
  sala_id: string;
  usuario_id: string;
  
  // Información del usuario (denormalized para performance)
  usuario_nombre?: string;
  usuario_apellido?: string;
  usuario_avatar?: string;
  
  // Contenido
  contenido: string;
  contenido_html?: string;
  tipo_mensaje: TipoMensaje;
  
  // Archivos adjuntos
  archivos_urls?: string[];
  metadatos_archivos?: Record<string, any>;
  
  // Threading (hilos de conversación)
  mensaje_padre_id?: string;
  mensaje_padre?: Mensaje;
  respuestas?: Mensaje[];
  
  // Menciones
  menciones_usuarios?: string[];
  menciones_ia?: boolean;
  menciones_todos?: boolean;
  
  // Flags
  es_importante?: boolean;
  es_anuncio?: boolean;
  editado: boolean;
  eliminado: boolean;
  
  // Timestamps
  fecha_creacion: string;
  fecha_edicion?: string;
  fecha_eliminacion?: string;
  
  // Reacciones: { emoji: [usuario_ids] }
  reacciones?: Record<string, string[]>;
  
  // Computed
  es_propio?: boolean;
  esta_siendo_editado?: boolean;
}

/**
 * Participante de una sala
 */
export interface Participante {
  usuario_id: string;
  sala_id: string;
  
  // Permisos
  puede_escribir: boolean;
  puede_eliminar_mensajes: boolean;
  es_administrador: boolean;
  
  // Estado
  fecha_union: string;
  silenciado: boolean;
  ultima_lectura?: string;
  
  // Usuario relacionado (denormalized)
  usuario?: Usuario;
  usuario_nombre?: string;
  usuario_apellido?: string;
  usuario_avatar?: string;
  usuario_estado?: EstadoUsuario;
}

/**
 * Notificación
 */
export interface Notificacion {
  id: string;
  usuario_id: string;
  tipo_notificacion: string;
  titulo: string;
  mensaje: string;
  leida: boolean;
  fecha_creacion: string;
  fecha_lectura?: string;
  
  // Metadata
  sala_id?: string;
  mensaje_id?: string;
  url_accion?: string;
  icono?: string;
  color?: string;
}

// ==================== EVENTOS WEBSOCKET ====================

/**
 * Tipos de eventos WebSocket
 */
export enum WebSocketEventType {
  // Conexión
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
  RECONNECTING = 'reconnecting',
  
  // Mensajes
  MESSAGE_NEW = 'message.new',
  MESSAGE_EDIT = 'message.edit',
  MESSAGE_DELETE = 'message.delete',
  MESSAGE_REACTION = 'message.reaction',
  MESSAGE_SENT = 'message.sent',
  MESSAGE_EDITED = 'message.edited',
  MESSAGE_DELETED = 'message.deleted',
  
  // Typing indicators
  TYPING_UPDATE = 'typing.update',
  TYPING_STOP = 'typing.stop',
  TYPING_USERS = 'typing.users',
  
  // Read receipts
  READ_RECEIPT = 'read.receipt',
  MESSAGES_READ = 'messages.read',
  
  // Usuarios
  USER_CONNECTED = 'user.connected',
  USER_DISCONNECTED = 'user.disconnected',
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  ONLINE_USERS = 'online.users',
  
  // Reacciones
  REACTION_ADDED = 'reaction.added'
}

/**
 * Evento WebSocket base
 */
export interface WebSocketEvent<T = any> {
  type: WebSocketEventType | string;
  data?: T;
  timestamp?: string;
  [key: string]: any;
}

/**
 * Evento: Nuevo mensaje
 */
export interface MessageNewEvent extends WebSocketEvent {
  type: WebSocketEventType.MESSAGE_NEW;
  sala_id: string;
  mensaje: Mensaje;
}

/**
 * Evento: Mensaje editado
 */
export interface MessageEditEvent extends WebSocketEvent {
  type: WebSocketEventType.MESSAGE_EDIT;
  sala_id: string;
  mensaje_id: string;
  contenido: string;
  contenido_html?: string;
  fecha_edicion: string;
  editado: true;
}

/**
 * Evento: Mensaje eliminado
 */
export interface MessageDeleteEvent extends WebSocketEvent {
  type: WebSocketEventType.MESSAGE_DELETE;
  sala_id: string;
  mensaje_id: string;
  eliminado_por: string;
  es_administrador: boolean;
}

/**
 * Evento: Reacción añadida
 */
export interface MessageReactionEvent extends WebSocketEvent {
  type: WebSocketEventType.MESSAGE_REACTION;
  sala_id: string;
  mensaje_id: string;
  emoji: string;
  usuario_id: string;
  reacciones: Record<string, string[]>;
}

/**
 * Evento: Usuario escribiendo
 */
export interface TypingUpdateEvent extends WebSocketEvent {
  type: WebSocketEventType.TYPING_UPDATE;
  usuario_id: string;
  usuario_nombre?: string;
  is_typing: boolean;
}

/**
 * Evento: Usuarios online
 */
export interface OnlineUsersEvent extends WebSocketEvent {
  type: WebSocketEventType.ONLINE_USERS;
  usuarios: string[];
  count: number;
}

// ==================== REQUESTS ====================

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
 * Request para añadir reacción
 */
export interface AñadirReaccionRequest {
  emoji: string;
}

/**
 * Request para marcar como leído
 */
export interface MarcarLeidoRequest {
  mensajes_ids: string[];
}

// ==================== RESPONSES ====================

/**
 * Response paginada genérica
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Response de estadísticas de sala
 */
export interface EstadisticasSala {
  total_mensajes: number;
  total_participantes: number;
  participantes_online: number;
  mensajes_no_leidos: number;
  ultimo_mensaje?: Mensaje;
  usuarios_activos_24h: number;
}

// ==================== UI STATE ====================

/**
 * Estado de UI para componente de chat
 */
export interface ChatUIState {
  salaActiva: string | null;
  mensajeEnEdicion: string | null;
  mensajeRespondiendo: Mensaje | null;
  mostrarEmojiPicker: boolean;
  mostrarParticipantes: boolean;
  filtroMensajes: string;
  cargandoMensajes: boolean;
  hayMasMensajes: boolean;
}

/**
 * Estado de typing indicator
 */
export interface TypingState {
  [salaId: string]: {
    usuarios: string[];
    timeout?: NodeJS.Timeout;
  };
}

/**
 * Configuración de notificaciones
 */
export interface NotificacionConfig {
  habilitadas: boolean;
  sonido: boolean;
  escritorio: boolean;
  menciones: boolean;
  todos_mensajes: boolean;
  solo_importantes: boolean;
}

// ==================== UTILIDADES ====================

/**
 * Filtros para búsqueda de mensajes
 */
export interface FiltrosMensajes {
  tipo?: TipoMensaje;
  usuario_id?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  solo_importantes?: boolean;
  solo_con_archivos?: boolean;
  query?: string;
}

/**
 * Opciones para cargar mensajes
 */
export interface CargarMensajesOptions {
  page?: number;
  size?: number;
  antes_de?: string; // mensaje_id
  despues_de?: string; // mensaje_id
  filtros?: FiltrosMensajes;
}

/**
 * Metadata de archivo adjunto
 */
export interface ArchivoMetadata {
  nombre: string;
  tipo: string;
  tamaño: number;
  url: string;
  thumbnail?: string;
  width?: number;
  height?: number;
  duracion?: number; // para audio/video en segundos
}

/**
 * Error de API
 */
export interface APIError {
  message: string;
  code?: string;
  status?: number;
  details?: any;
}

// ==================== GUARDS & VALIDATORS ====================

/**
 * Type guard para verificar si es un mensaje válido
 */
export const esMensajeValido = (obj: any): obj is Mensaje => {
  return (
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.sala_id === 'string' &&
    typeof obj.usuario_id === 'string' &&
    typeof obj.contenido === 'string' &&
    typeof obj.tipo_mensaje === 'string'
  );
};

/**
 * Type guard para verificar si es una sala válida
 */
export const esSalaValida = (obj: any): obj is SalaChat => {
  return (
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.nombre === 'string' &&
    typeof obj.tipo === 'string'
  );
};

// ==================== EXPORTS ====================

export type {
  WebSocketEvent,
  MessageNewEvent,
  MessageEditEvent,
  MessageDeleteEvent,
  MessageReactionEvent,
  TypingUpdateEvent,
  OnlineUsersEvent
};
