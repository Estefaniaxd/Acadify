/**
 * Types y DTOs para el módulo de Invitaciones
 * Gestiona las invitaciones de admin a coordinadores para administrar instituciones
 */

/**
 * Estado de una invitación
 */
export enum EstadoInvitacion {
  PENDIENTE = 'PENDIENTE',
  ACEPTADA = 'ACEPTADA',
  RECHAZADA = 'RECHAZADA',
  EXPIRADA = 'EXPIRADA',
  CANCELADA = 'CANCELADA',
}

/**
 * Rol al que se invita
 */
export enum RolInvitacion {
  COORDINADOR = 'COORDINADOR',
  PROFESOR = 'PROFESOR',
  ESTUDIANTE = 'ESTUDIANTE',
}

/**
 * Interface principal de Invitación
 */
export interface Invitacion {
  id: number;
  
  // Datos del invitado
  email: string;
  nombreInvitado: string;
  rol: RolInvitacion;
  
  // Relaciones
  institucionId: number;
  institucion?: {
    id: number;
    nombre: string;
    codigo: string;
  };
  programaId?: number; // Opcional, para profesores/estudiantes
  programa?: {
    id: number;
    nombre: string;
    codigo: string;
  };
  
  // Datos del invitador (admin)
  creadoPorId: number;
  creadoPor?: {
    id: number;
    nombre: string;
    email: string;
  };
  
  // Control de invitación
  codigo: string; // Código de 6 dígitos
  token: string; // Token único para URL
  estado: EstadoInvitacion;
  
  // Fechas
  fechaCreacion: string;
  fechaExpiracion: string;
  fechaAceptacion?: string;
  fechaRechazo?: string;
  
  // Metadata
  mensaje?: string; // Mensaje personalizado del admin
  intentosReenvio: number;
  ultimoReenvio?: string;
  
  // Usuario creado tras aceptar
  usuarioCreado?: {
    id: number;
    nombre: string;
    email: string;
  };
}

/**
 * DTO para crear una invitación
 */
export interface CrearInvitacionDTO {
  email: string;
  nombreInvitado: string;
  rol: RolInvitacion;
  institucionId: number;
  programaId?: number;
  mensaje?: string;
  diasExpiracion?: number; // Default: 7 días
}

/**
 * DTO para aceptar una invitación
 */
export interface AceptarInvitacionDTO {
  token: string;
  codigo: string;
  
  // Datos del usuario a crear
  nombre: string;
  apellido: string;
  password: string;
  passwordConfirm: string;
  
  // Datos adicionales opcionales
  telefono?: string;
  documento?: string;
  fechaNacimiento?: string;
}

/**
 * DTO para rechazar una invitación
 */
export interface RechazarInvitacionDTO {
  token: string;
  motivo?: string;
}

/**
 * Filtros para listar invitaciones
 */
export interface FiltrosInvitaciones {
  estado?: EstadoInvitacion;
  rol?: RolInvitacion;
  institucionId?: number;
  programaId?: number;
  email?: string;
  busqueda?: string;
  fechaDesde?: string;
  fechaHasta?: string;
  pagina?: number;
  limite?: number;
  ordenarPor?: 'reciente' | 'antiguo' | 'expiracion';
}

/**
 * Estadísticas de invitaciones
 */
export interface EstadisticasInvitaciones {
  total: number;
  pendientes: number;
  aceptadas: number;
  rechazadas: number;
  expiradas: number;
  canceladas: number;
  
  // Por rol
  coordinadores: number;
  profesores: number;
  estudiantes: number;
  
  // Métricas
  tasaAceptacion: number; // Porcentaje
  tiempoPromedioAceptacion: number; // En horas
  invitacionesHoy: number;
  invitacionesEstaSemana: number;
}

/**
 * Respuesta al validar un token
 */
export interface ValidacionInvitacion {
  valida: boolean;
  invitacion?: Invitacion;
  error?: string;
  razon?: 'EXPIRADA' | 'NO_ENCONTRADA' | 'YA_ACEPTADA' | 'CANCELADA';
}

/**
 * Notificación de invitación
 */
export interface NotificacionInvitacion {
  id: number;
  tipo: 'INVITACION_RECIBIDA' | 'INVITACION_ACEPTADA' | 'INVITACION_RECHAZADA' | 'INVITACION_EXPIRADA';
  invitacionId: number;
  invitacion: Invitacion;
  leida: boolean;
  fechaCreacion: string;
}

/**
 * Respuesta paginada genérica
 */
export interface RespuestaPaginada<T> {
  items: T[];
  total: number;
  pagina: number;
  tamanoPagina: number;
  totalPaginas: number;
}

/**
 * Historial de una invitación
 */
export interface HistorialInvitacion {
  id: number;
  invitacionId: number;
  accion: 'CREADA' | 'ENVIADA' | 'REENVIADA' | 'ACEPTADA' | 'RECHAZADA' | 'EXPIRADA' | 'CANCELADA';
  descripcion: string;
  realizadoPorId?: number;
  realizadoPor?: {
    id: number;
    nombre: string;
  };
  fecha: string;
  metadata?: Record<string, any>;
}

/**
 * Email template data
 */
export interface DatosEmailInvitacion {
  nombreInvitado: string;
  nombreInstitucion: string;
  nombreAdmin: string;
  emailAdmin: string;
  codigo: string;
  urlAceptar: string;
  mensaje?: string;
  fechaExpiracion: string;
  rol: RolInvitacion;
}

/**
 * Response al enviar invitación
 */
export interface RespuestaEnvioInvitacion {
  invitacion: Invitacion;
  emailEnviado: boolean;
  error?: string;
}
