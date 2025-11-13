/**
 * Tipos del Módulo de Instituciones
 * Define todas las interfaces y tipos relacionados con instituciones educativas
 * 
 * IMPORTANTE: Estos tipos están sincronizados con el backend (snake_case)
 * Los servicios deben usar transformadores para convertir entre camelCase y snake_case
 */

// ============================================
// ENUMS (deben coincidir con backend)
// ============================================

export enum TipoInstitucion {
  COLEGIO = 'colegio',
  INSTITUTO = 'instituto',
  UNIVERSIDAD = 'universidad',
  INSTITUTO_TECNICO = 'instituto_tecnico',
  CENTRO_FORMACION = 'centro_formacion',
}

export enum NivelEducativo {
  PREESCOLAR = 'preescolar',
  PRIMARIA = 'primaria',
  BASICA = 'basica',
  MEDIA = 'media',
  TECNICA = 'tecnica',
  TECNOLOGICA = 'tecnologica',
  PROFESIONAL = 'profesional',
  POSTGRADO = 'postgrado',
}

export enum SectorInstitucion {
  PUBLICO = 'publico',
  PRIVADO = 'privado',
  MIXTO = 'mixto',
}

export enum ModalidadEnsenanza {
  PRESENCIAL = 'presencial',
  VIRTUAL = 'virtual',
  HIBRIDA = 'hibrida',
  DUAL = 'dual',
}

export enum TipoCalendario {
  SEMESTRAL = 'semestral',
  TRIMESTRAL = 'trimestral',
  BIMESTRAL = 'bimestral',
  ANUAL = 'anual',
}

export enum EstadoInstitucion {
  PENDIENTE = 'pendiente',
  ACTIVA = 'activa',
  SUSPENDIDA = 'suspendida',
  INACTIVA = 'inactiva',
}

// ============================================
// INTERFACES PRINCIPALES (snake_case - backend format)
// ============================================

export interface Institucion {
  // ID
  institucion_id: string;
  
  // Identificación básica
  nombre: string;
  sigla?: string;
  lema?: string;
  
  // Identidad visual
  logo_url: string;
  color_primario?: string;
  color_secundario?: string;
  
  // Clasificación académica
  tipo_institucion: TipoInstitucion;
  usa_programas: boolean;
  nivel_educativo: NivelEducativo;
  sector: SectorInstitucion;
  modalidad_ensenanza: ModalidadEnsenanza;
  
  // Calendario
  tipo_calendario?: TipoCalendario;
  jornadas?: string[];
  
  // Ubicación
  direccion?: string;
  ciudad?: string;
  pais: string;
  
  // Contacto
  correo_institucional: string;
  telefono: string;
  nit?: string;
  
  // Dominios
  dominio_principal?: string;
  dominios_adicionales?: string[];
  
  // Redes sociales
  redes_sociales?: Record<string, string>;
  
  // Estado y límites
  estado: EstadoInstitucion;
  numero_estudiantes_actual?: number;
  numero_docentes?: number;
  limite_estudiantes?: number;
  limite_docentes?: number;
  limite_cursos?: number;
  
  // Fechas
  fecha_creacion: string;
  fecha_activacion?: string;
  fecha_suspension?: string;
  fecha_actualizacion?: string;
  
  // Relaciones (opcional)
  coordinadores?: Coordinador[];
  programas?: ProgramaBasico[];
  
  // Estadísticas (opcional)
  estadisticas?: EstadisticasInstitucion;
}

export interface CrearInstitucionDTO {
  // Identificación básica (requeridos)
  nombre: string;
  tipo_institucion: TipoInstitucion;
  usa_programas: boolean;
  nivel_educativo: NivelEducativo;
  sector: SectorInstitucion;
  pais: string;
  correo_institucional: string;
  telefono: string;
  
  // Identidad visual (opcionales)
  sigla?: string;
  lema?: string;
  logo_url?: string;
  color_primario?: string;
  color_secundario?: string;
  
  // Ubicación (opcionales)
  direccion?: string;
  ciudad?: string;
  
  // Contacto adicional (opcionales)
  nit?: string;
  dominio_principal?: string;
  dominios_adicionales?: string[];
  
  // Configuración (opcionales)
  modalidad_ensenanza?: ModalidadEnsenanza;
  tipo_calendario?: TipoCalendario;
  jornadas?: string[];
  redes_sociales?: Record<string, string>;
  
  // Límites (opcionales)
  limite_estudiantes?: number;
  limite_docentes?: number;
  limite_cursos?: number;
}

export interface ActualizarInstitucionDTO {
  nombre?: string;
  sigla?: string;
  lema?: string;
  logo_url?: string;
  color_primario?: string;
  color_secundario?: string;
  tipo_institucion?: TipoInstitucion;
  nivel_educativo?: NivelEducativo;
  sector?: SectorInstitucion;
  modalidad_ensenanza?: ModalidadEnsenanza;
  tipo_calendario?: TipoCalendario;
  jornadas?: string[];
  direccion?: string;
  ciudad?: string;
  pais?: string;
  correo_institucional?: string;
  telefono?: string;
  nit?: string;
  dominio_principal?: string;
  dominios_adicionales?: string[];
  redes_sociales?: Record<string, string>;
  limite_estudiantes?: number;
  limite_docentes?: number;
  limite_cursos?: number;
}

export interface PersonalizacionInstitucion {
  logo_url?: string;
  color_primario: string;
  color_secundario: string;
}

export interface Coordinador {
  usuario_id: string;
  nombre: string;
  apellido: string;
  email: string;
  username: string;
  avatar_url?: string;
  fecha_asignacion: string;
}

export interface ProgramaBasico {
  programa_id: string;
  nombre: string;
  codigo: string;
  nivel_educativo: string;
  activo: boolean;
  cantidad_cursos?: number;
}

export interface EstadisticasInstitucion {
  total_programas: number;
  total_cursos: number;
  total_coordinadores: number;
  total_profesores: number;
  total_estudiantes: number;
  cursos_activos: number;
  estudiantes_activos: number;
}

export interface FiltrosInstitucion {
  busqueda?: string;
  estado?: EstadoInstitucion;
  tipo_institucion?: TipoInstitucion;
  sector?: SectorInstitucion;
  ordenar_por?: 'nombre' | 'fecha_creacion' | 'numero_estudiantes_actual';
  orden?: 'asc' | 'desc';
  pagina?: number;
  limite?: number;
}

export interface RespuestaPaginada<T> {
  items: T[];
  total: number;
  pagina: number;
  limite: number;
  total_paginas: number;
}

// ============================================
// TIPOS PARA INVITACIONES
// ============================================

export interface InvitacionInfo {
  valido: boolean;
  invitacion: {
    invitacion_id: string;
    codigo: string;
    email_destino: string;
    fecha_creacion: string;
    fecha_expiracion: string;
  };
  institucion: {
    institucion_id: string;
    nombre: string;
    sigla?: string;
    logo_url: string;
    tipo_institucion: string;
    nivel_educativo: string;
    ciudad?: string;
    pais: string;
  };
}

export interface InvitarCoordinadorRequest {
  email_destino: string;
}

export interface InvitarCoordinadorResponse {
  success: boolean;
  message: string;
  codigo: string;
  email_destino: string;
  fecha_expiracion: string;
}

export interface AceptarInvitacionRequest {
  codigo: string;
  nombre: string;
  apellido: string;
  password: string;
}

export interface AceptarInvitacionResponse {
  success: boolean;
  message: string;
  usuario: {
    usuario_id: string;
    email: string;
    username: string;
    nombre: string;
    apellido: string;
    rol: string;
  };
  institucion: {
    institucion_id: string;
    nombre: string;
    sigla?: string;
    estado: string;
    fecha_activacion?: string;
  };
}

// ============================================
// TIPOS PARA ESTADÍSTICAS Y REPORTES
// ============================================

export interface EstadisticasDetalladas extends EstadisticasInstitucion {
  programas_activos: number;
  promedio_estudiantes_por_curso: number;
  tasa_ocupacion: number; // Porcentaje de uso del límite
  crecimiento_mensual: number;
}

export interface OnboardingStatus {
  completado: boolean;
  pasos_completados: string[];
  pasos_pendientes: string[];
  porcentaje_completado: number;
}
