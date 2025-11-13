/**
 * Types para el sistema de videollamadas con Jitsi Meet
 * 
 * @module types/videollamada
 * @description Definiciones de tipos TypeScript para videollamadas,
 * participantes, grabaciones y configuración de Jitsi.
 */

// ==================== ENUMS ====================

export enum TipoLlamada {
  VIDEO = 'video',
  VOZ = 'voz'
}

export enum EstadoVideollamada {
  PROGRAMADA = 'PROGRAMADA',
  ACTIVA = 'ACTIVA',
  FINALIZADA = 'FINALIZADA',
  CANCELADA = 'CANCELADA'
}

export enum CalidadConexion {
  EXCELENTE = 'excelente',
  BUENA = 'buena',
  REGULAR = 'regular',
  MALA = 'mala'
}

export enum FormatoGrabacion {
  MP4 = 'mp4',
  WEBM = 'webm',
  MKV = 'mkv',
  AVI = 'avi'
}

export enum CalidadGrabacion {
  SD = 'SD',
  HD = 'HD',
  FHD = 'FHD',
  UHD_4K = '4K'
}

export enum EstadoProcesamiento {
  PENDIENTE = 'pendiente',
  PROCESANDO = 'procesando',
  COMPLETADO = 'completado',
  ERROR = 'error'
}

// ==================== INTERFACES ====================

/**
 * Configuración de una videollamada
 */
export interface ConfiguracionVideollamada {
  max_participantes?: number;
  permitir_grabacion?: boolean;
  permitir_chat?: boolean;
  permitir_compartir_pantalla?: boolean;
  requerir_moderador?: boolean;
  calidad_video?: 'low' | 'standard' | 'high';
  [key: string]: any; // Permitir configuraciones adicionales
}

/**
 * Videollamada completa
 */
export interface Videollamada {
  id: string;
  jitsi_room_name: string;
  tipo_llamada: TipoLlamada;
  iniciador_id: string;
  sala_chat_id?: string;
  fecha_inicio: string;
  fecha_fin?: string;
  duracion_segundos?: number;
  estado: EstadoVideollamada;
  configuracion: ConfiguracionVideollamada;
  grabacion_url?: string;
  transcripcion?: string;
  resumen_ia?: string;
  participantes?: Participante[];
}

/**
 * Request para crear videollamada
 */
export interface VideollamadaCreateRequest {
  jitsi_room_name?: string;
  tipo_llamada: TipoLlamada;
  sala_chat_id?: string;
  configuracion?: ConfiguracionVideollamada;
}

/**
 * Response al listar videollamadas
 */
export interface VideollamadaListResponse {
  items: Videollamada[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

/**
 * Participante de videollamada
 */
export interface Participante {
  id: string;
  videollamada_id: string;
  usuario_id: string;
  fecha_union: string;
  fecha_salida?: string;
  duracion_segundos?: number;
  es_moderador: boolean;
  calidad_conexion?: CalidadConexion;
  estadisticas?: EstadisticasParticipante;
}

/**
 * Estadísticas de conexión de un participante
 */
export interface EstadisticasParticipante {
  latencia_ms?: number;
  perdida_paquetes_pct?: number;
  bitrate_audio?: number;
  bitrate_video?: number;
  resolucion_video?: string;
  fps?: number;
  actualizado_en?: string;
  [key: string]: any;
}

/**
 * Request para actualizar calidad de conexión
 */
export interface ActualizarCalidadRequest {
  calidad?: CalidadConexion;
  latencia_ms?: number;
  perdida_paquetes_pct?: number;
}

/**
 * Grabación de videollamada
 */
export interface Grabacion {
  id: string;
  videollamada_id: string;
  titulo: string;
  archivo_url: string;
  thumbnail_url?: string;
  formato: FormatoGrabacion;
  calidad: CalidadGrabacion;
  duracion_segundos: number;
  tamano_bytes: number;
  fecha_subida: string;
  estado_procesamiento: EstadoProcesamiento;
  error_mensaje?: string;
  metadatos?: Record<string, any>;
}

/**
 * Request para agregar grabación
 */
export interface GrabacionCreateRequest {
  titulo: string;
  archivo_url: string;
  thumbnail_url?: string;
  formato: FormatoGrabacion;
  calidad: CalidadGrabacion;
  duracion_segundos: number;
  tamano_bytes: number;
}

/**
 * Validación de acceso a videollamada
 */
export interface ValidacionAcceso {
  can_join: boolean;
  reason?: string;
  current_participants: number;
  max_participants: number;
}

/**
 * Response genérico
 */
export interface MessageResponse {
  success: boolean;
  message: string;
}

// ==================== JITSI CONFIG ====================

/**
 * Configuración de Jitsi Meet External API
 */
export interface JitsiMeetConfig {
  roomName: string;
  width?: string | number;
  height?: string | number;
  parentNode?: HTMLElement;
  configOverwrite?: JitsiConfigOverwrite;
  interfaceConfigOverwrite?: JitsiInterfaceConfig;
  jwt?: string;
  userInfo?: JitsiUserInfo;
  devices?: {
    audioInput?: string;
    audioOutput?: string;
    videoInput?: string;
  };
  onload?: () => void;
}

/**
 * Sobrescritura de configuración de Jitsi
 */
export interface JitsiConfigOverwrite {
  startWithAudioMuted?: boolean;
  startWithVideoMuted?: boolean;
  enableWelcomePage?: boolean;
  prejoinPageEnabled?: boolean;
  disableDeepLinking?: boolean;
  resolution?: number;
  constraints?: {
    video?: {
      height?: { ideal: number; max: number; min: number };
      width?: { ideal: number; max: number; min: number };
    };
  };
  enableLayerSuspension?: boolean;
  p2p?: {
    enabled?: boolean;
  };
  [key: string]: any;
}

/**
 * Configuración de interfaz de Jitsi
 */
export interface JitsiInterfaceConfig {
  TOOLBAR_BUTTONS?: string[];
  SHOW_JITSI_WATERMARK?: boolean;
  SHOW_WATERMARK_FOR_GUESTS?: boolean;
  SHOW_BRAND_WATERMARK?: boolean;
  DISABLE_VIDEO_BACKGROUND?: boolean;
  DEFAULT_BACKGROUND?: string;
  MOBILE_APP_PROMO?: boolean;
  [key: string]: any;
}

/**
 * Información del usuario para Jitsi
 */
export interface JitsiUserInfo {
  displayName?: string;
  email?: string;
  avatarURL?: string;
}

/**
 * Eventos de Jitsi Meet
 */
export enum JitsiEvent {
  VIDEO_CONFERENCE_JOINED = 'videoConferenceJoined',
  VIDEO_CONFERENCE_LEFT = 'videoConferenceLeft',
  PARTICIPANT_JOINED = 'participantJoined',
  PARTICIPANT_LEFT = 'participantLeft',
  AUDIO_MUTE_STATUS_CHANGED = 'audioMuteStatusChanged',
  VIDEO_MUTE_STATUS_CHANGED = 'videoMuteStatusChanged',
  SCREEN_SHARING_STATUS_CHANGED = 'screenSharingStatusChanged',
  READY_TO_CLOSE = 'readyToClose',
  ERROR_OCCURRED = 'errorOccurred',
  CONNECTION_QUALITY_CHANGED = 'connectionQualityChanged'
}

/**
 * Calidad de conexión de Jitsi (0-100)
 */
export interface JitsiConnectionQuality {
  participantId: string;
  connectionQuality: number; // 0-100
}

// ==================== UTILITY TYPES ====================

/**
 * Opciones para listar videollamadas
 */
export interface ListarVideollamadasOptions {
  sala_chat_id?: string;
  solo_activas?: boolean;
  skip?: number;
  limit?: number;
}

/**
 * Props comunes para componentes de videollamada
 */
export interface VideollamadaComponentProps {
  videollamadaId: string;
  className?: string;
  onClose?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Estado de la conexión de videollamada
 */
export interface ConnectionState {
  isConnected: boolean;
  isConnecting: boolean;
  error?: Error;
  quality?: CalidadConexion;
}

/**
 * Configuración de JWT para Jitsi
 */
export interface JitsiJWTPayload {
  context: {
    user: {
      id: string;
      name: string;
      avatar?: string;
      email?: string;
    };
    features?: {
      livestreaming?: boolean;
      recording?: boolean;
      transcription?: boolean;
    };
  };
  room: string;
  moderator?: boolean;
  aud?: string;
  iss?: string;
  sub?: string;
  exp?: number;
  nbf?: number;
}
