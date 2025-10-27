// Enums
export enum EstadoCurso {
  ACTIVO = 'activo',
  INACTIVO = 'inactivo',
  ARCHIVADO = 'archivado',
  BORRADOR = 'borrador',
}

export enum EstadoGrupo {
  ACTIVO = 'activo',
  INACTIVO = 'inactivo',
  ARCHIVADO = 'archivado',
}

export enum EstadoClase {
  PROGRAMADA = 'programada',
  EN_PROGRESO = 'en_progreso',
  FINALIZADA = 'finalizada',
  CANCELADA = 'cancelada',
}

export enum TipoClase {
  TEORICA = "teorica",
  PRACTICA = "practica",
  LABORATORIO = "laboratorio",
  TALLER = "taller",
  SEMINARIO = "seminario",
  CONFERENCIA = "conferencia",
  EXAMEN = "examen",
  OTRO = "otro"
}

export enum EstadoCodigoAcceso {
  ACTIVO = "activo",
  VENCIDO = "vencido",
  DESHABILITADO = "deshabilitado"
}

export enum ModalidadCurso {
  ANUAL = "anual",
  SEMESTRAL = "semestral", 
  TRIMESTRAL = "trimestral",
  CUATRIMESTRAL = "cuatrimestral",
  BIMESTRAL = "bimestral",
  MENSUAL = "mensual",
  MODULAR = "modular",
  FLEXIBLE = "flexible",
  OTRO = "otro"
}

export enum TipoMaterialEducativo {
  PDF = "pdf",
  VIDEO = "video",
  AUDIO = "audio",
  IMAGEN = "imagen",
  PRESENTACION = "presentacion",
  DOCUMENTO = "documento",
  HOJA_DE_CALCULO = "hoja_de_calculo",
  ENLACE = "enlace",
  INTERACTIVO = "interactivo",
  CODIGO_FUENTE = "codigo_fuente",
  OTRO = "otro"
}

export enum CarpetaMaterial {
  LECTURAS = "lecturas",
  GUIAS = "guias", 
  TAREAS = "tareas",
  EXAMENES = "examenes",
  RECURSOS = "recursos",
  MULTIMEDIA = "multimedia",
  EJERCICIOS = "ejercicios",
  BIBLIOGRAFIAS = "bibliografias",
  OTROS = "otros"
}

export enum EstadoMaterial {
  ACTIVO = "activo",
  ARCHIVADO = "archivado",
  BORRADOR = "borrador",
  REVISION = "revision"
}

export enum JornadaGrupo {
  MANANA = "manana",
  TARDE = "tarde", 
  NOCTURNA = "nocturna"
}

export enum NivelPrograma {
  BASICO = "basico",
  INTERMEDIO = "intermedio",
  AVANZADO = "avanzado"
}

export enum TipoPrograma {
  ACADEMICO = "academico",
  TECNICO = "tecnico",
  PROFESIONAL = "profesional"
}

// Interfaces de configuración
export interface ConfiguracionCurso {
  permite_auto_inscripcion: boolean;
  requiere_aprobacion: boolean;
  es_publico: boolean;
  permite_invitados: boolean;
  notificar_nuevos_materiales: boolean;
  notificar_nuevas_clases: boolean;
  integrar_con_drive?: boolean;
  carpeta_drive_id?: string;
}

// Interfaces para Cursos
export interface Curso {
  curso_id: string;
  institucion_id: string;
  coordinador_id?: string;
  programa_id: string;
  nombre: string;
  descripcion?: string;
  objetivos?: string;
  codigo_curso?: string;
  codigo?: string; // Alias para compatibilidad
  creditos: number;
  horas_academicas: number;
  duracion_estimada?: number; // Para compatibilidad
  modalidad: ModalidadCurso;
  categoria?: string;
  nivel?: string;
  idioma?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  activo: boolean;
  estado?: EstadoCurso;
  permite_inscripcion: boolean;
  maximo_estudiantes?: number;
  minimo_estudiantes: number;
  estudiantes_actuales?: number;
  permite_material_estudiantes: boolean;
  requiere_aprobacion_material: boolean;
  carpeta_drive_id?: string;
  carpeta_drive_url?: string;
  configuracion?: ConfiguracionCurso;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface CursoDetallado extends Curso {
  institucion_nombre?: string;
  coordinador_nombre?: string;
  coordinador_apellido?: string;
  programa_nombre?: string;
  total_estudiantes: number;
  total_docentes: number;
  total_grupos: number;
  total_material: number;
  total_clases: number;
}

export interface CursoCreate {
  institucion_id: string;
  coordinador_id?: string;
  programa_id: string;
  nombre: string;
  descripcion?: string;
  objetivos?: string;
  codigo_curso?: string;
  creditos: number;
  horas_academicas: number;
  modalidad: ModalidadCurso;
  fecha_inicio?: string;
  fecha_fin?: string;
  maximo_estudiantes?: number;
  minimo_estudiantes: number;
  permite_inscripcion: boolean;
  permite_material_estudiantes: boolean;
  requiere_aprobacion_material: boolean;
}

export interface CursoUpdate {
  nombre?: string;
  descripcion?: string;
  objetivos?: string;
  codigo_curso?: string;
  creditos?: number;
  horas_academicas?: number;
  modalidad?: ModalidadCurso;
  fecha_inicio?: string;
  fecha_fin?: string;
  maximo_estudiantes?: number;
  minimo_estudiantes?: number;
  activo?: boolean;
  permite_inscripcion?: boolean;
  permite_material_estudiantes?: boolean;
  requiere_aprobacion_material?: boolean;
}

// Interfaces para Clases
export interface Clase {
  clase_id: string;
  grupo_id: string;
  docente_id: string;
  titulo: string;
  descripcion?: string;
  tipo_clase: TipoClase;
  estado: EstadoClase;
  fecha_inicio: string;
  fecha_fin?: string;
  duracion_estimada?: number;
  codigo_acceso: string;
  estado_codigo: EstadoCodigoAcceso;
  fecha_vencimiento_codigo?: string;
  max_estudiantes?: number;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface ClaseDetallada extends Clase {
  grupo_nombre?: string;
  docente_nombre?: string;
  docente_apellido?: string;
  total_estudiantes_unidos: number;
  total_material_subido: number;
}

export interface ClaseCreate {
  grupo_id: string;
  docente_id: string;
  titulo: string;
  descripcion?: string;
  tipo_clase: TipoClase;
  fecha_inicio: string;
  fecha_fin?: string;
  duracion_estimada?: number;
  max_estudiantes?: number;
  fecha_vencimiento_codigo?: string;
}

export interface ClaseUpdate {
  titulo?: string;
  descripcion?: string;
  tipo_clase?: TipoClase;
  estado?: EstadoClase;
  fecha_inicio?: string;
  fecha_fin?: string;
  duracion_estimada?: number;
  max_estudiantes?: number;
  fecha_vencimiento_codigo?: string;
}

export interface EstudianteUnirse {
  codigo_acceso: string;
  ip_acceso?: string;
  user_agent?: string;
}

export interface RespuestaUnirse {
  success: boolean;
  message: string;
  clase?: Clase;
}

// Interfaces para Material Educativo
export interface MaterialEducativo {
  material_id: string;
  titulo: string;
  descripcion?: string;
  tipo_material: TipoMaterialEducativo;
  carpeta: CarpetaMaterial;
  url_archivo: string;
  formato_archivo?: string;
  tamano_archivo?: number;
  version: number;
  es_version_actual: boolean;
  material_original_id?: string;
  estado: EstadoMaterial;
  numero_descargas: number;
  tags?: string;
  url_drive?: string;
  es_publico?: boolean;
  requiere_autenticacion?: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
}

export interface MaterialEducativoDetallado extends MaterialEducativo {
  autor_nombre?: string;
  autor_apellido?: string;
  tamano_legible: string;
  total_versiones: number;
}

export interface MaterialEducativoCreate {
  titulo: string;
  descripcion?: string;
  tipo_material: TipoMaterialEducativo;
  carpeta: CarpetaMaterial;
  url_archivo: string;
  formato_archivo: string;
  tags?: string;
  tamano_archivo?: number;
  hash_archivo?: string;
}

export interface MaterialEducativoUpdate {
  titulo?: string;
  descripcion?: string;
  tipo_material?: TipoMaterialEducativo;
  carpeta?: CarpetaMaterial;
  estado?: EstadoMaterial;
  url_archivo?: string;
  formato_archivo?: string;
  tags?: string;
}

// Interfaces para grupos y programas
export interface Grupo {
  grupo_id: string;
  programa_id: string;
  docente_tutor_id?: string;
  nombre: string;
  jornada: JornadaGrupo;
}

export interface Programa {
  programa_id: string;
  institucion_id: string;
  nombre: string;
  descripcion?: string;
  nivel: NivelPrograma;
  tipo: TipoPrograma;
}

// Interfaces para estadísticas
export interface EstadisticasCurso {
  curso_id: string;
  total_estudiantes_inscritos: number;
  total_docentes_asignados: number;
  total_grupos_vinculados: number;
  total_material_subido: number;
  total_clases_programadas: number;
  promedio_asistencia: number;
  ultima_actividad?: string;
}

export interface EstadisticasMaterial {
  total_materiales: number;
  por_carpeta: Record<string, number>;
  por_tipo: Record<string, number>;
  total_descargas: number;
  material_mas_popular?: MaterialEducativo;
}

// Filtros
export interface FiltrosCurso {
  institucion_id?: string;
  programa_id?: string;
  modalidad?: ModalidadCurso;
  activo_solo?: boolean;
  skip?: number;
  limit?: number;
}

export interface FiltrosMaterial {
  carpeta?: CarpetaMaterial;
  tipo_material?: TipoMaterialEducativo;
  estado?: EstadoMaterial;
  autor_id?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  busqueda?: string;
  skip?: number;
  limit?: number;
}