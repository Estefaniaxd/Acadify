/**
 * Tipos y DTOs para el módulo de Programas Académicos
 * 
 * Define las estructuras de datos utilizadas en:
 * - Comunicación con el backend (API REST)
 * - Estado de la aplicación (React Query)
 * - Props de componentes
 */

/**
 * Información básica de una institución
 * Usado en selects y referencias
 */
export interface InstitucionBasica {
  id: number;
  nombre: string;
  logo?: string;
}

/**
 * Información básica de un coordinador
 */
export interface CoordinadorBasico {
  id: number;
  nombre: string;
  email: string;
  avatar?: string;
}

/**
 * Información básica de un curso
 */
export interface CursoBasico {
  id: number;
  nombre: string;
  codigo: string;
  creditos: number;
  nivel?: number;
}

/**
 * Niveles académicos disponibles
 */
export enum NivelAcademico {
  TECNICO = 'TECNICO',
  TECNOLOGO = 'TECNOLOGO',
  PROFESIONAL = 'PROFESIONAL',
  ESPECIALIZACION = 'ESPECIALIZACION',
  MAESTRIA = 'MAESTRIA',
  DOCTORADO = 'DOCTORADO'
}

/**
 * Modalidades de estudio
 */
export enum ModalidadEstudio {
  PRESENCIAL = 'PRESENCIAL',
  VIRTUAL = 'VIRTUAL',
  HIBRIDO = 'HIBRIDO'
}

/**
 * Estados de un programa académico
 */
export enum EstadoPrograma {
  ACTIVO = 'ACTIVO',
  INACTIVO = 'INACTIVO',
  EN_REVISION = 'EN_REVISION',
  ARCHIVADO = 'ARCHIVADO'
}

/**
 * Modelo principal de Programa Académico
 * Representa un programa completo con todas sus relaciones
 */
export interface Programa {
  id: number;
  codigo: string; // Código único del programa (ej: "ING-001")
  nombre: string;
  descripcion?: string;
  nivel: NivelAcademico;
  modalidad: ModalidadEstudio;
  duracionSemestres: number;
  creditosRequeridos: number;
  estado: EstadoPrograma;
  
  // Relaciones
  institucionId: number;
  institucion?: InstitucionBasica;
  coordinadorId?: number;
  coordinador?: CoordinadorBasico;
  cursos?: CursoBasico[];
  
  // Estadísticas
  totalCursos: number;
  totalEstudiantes: number;
  tasaGraduacion?: number; // Porcentaje (0-100)
  
  // Configuración
  requiereProyectoGrado: boolean;
  requierePracticas: boolean;
  horasPracticas?: number;
  
  // Metadata
  fechaCreacion: string;
  fechaActualizacion: string;
  creadoPor?: string;
  actualizadoPor?: string;
}

/**
 * DTO para crear un nuevo programa
 * Campos mínimos requeridos
 */
export interface CrearProgramaDTO {
  codigo: string;
  nombre: string;
  descripcion?: string;
  nivel: NivelAcademico;
  modalidad: ModalidadEstudio;
  duracionSemestres: number;
  creditosRequeridos: number;
  institucionId: number;
  coordinadorId?: number;
  requiereProyectoGrado: boolean;
  requierePracticas: boolean;
  horasPracticas?: number;
}

/**
 * DTO para actualizar un programa existente
 * Todos los campos opcionales excepto lo que se quiera cambiar
 */
export interface ActualizarProgramaDTO {
  codigo?: string;
  nombre?: string;
  descripcion?: string;
  nivel?: NivelAcademico;
  modalidad?: ModalidadEstudio;
  duracionSemestres?: number;
  creditosRequeridos?: number;
  estado?: EstadoPrograma;
  coordinadorId?: number;
  requiereProyectoGrado?: boolean;
  requierePracticas?: boolean;
  horasPracticas?: number;
}

/**
 * Estadísticas detalladas de un programa
 */
export interface EstadisticasPrograma {
  programaId: number;
  totalCursos: number;
  totalEstudiantes: number;
  estudiantesActivos: number;
  estudiantesGraduados: number;
  estudiantesDesercion: number;
  tasaGraduacion: number;
  tasaDesercion: number;
  promedioSemestres: number;
  cursosObligatorios: number;
  cursosElectivos: number;
  creditosPromedio: number;
}

/**
 * Filtros para buscar programas
 */
export interface FiltrosProgramas {
  busqueda?: string; // Búsqueda en nombre, código, descripción
  institucionId?: number;
  nivel?: NivelAcademico;
  modalidad?: ModalidadEstudio;
  estado?: EstadoPrograma;
  coordinadorId?: number;
  ordenarPor?: 'nombre' | 'codigo' | 'fecha' | 'estudiantes' | 'cursos';
  orden?: 'asc' | 'desc';
  pagina?: number;
  limite?: number;
}

/**
 * Respuesta paginada genérica
 */
export interface RespuestaPaginada<T> {
  items: T[];
  total: number;
  pagina: number;
  limite: number;
  totalPaginas: number;
}

/**
 * DTO para asignar cursos a un programa
 */
export interface AsignarCursosDTO {
  programaId: number;
  cursoIds: number[];
  nivel?: number; // Nivel/semestre en el que se dicta
  esObligatorio?: boolean;
}

/**
 * Respuesta de API estándar
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/**
 * Configuración de malla curricular
 */
export interface MallaCurricular {
  programaId: number;
  semestres: SemestreMalla[];
  creditosTotales: number;
  horasTotales: number;
}

export interface SemestreMalla {
  numero: number;
  cursos: CursoMalla[];
  creditos: number;
}

export interface CursoMalla {
  cursoId: number;
  curso: CursoBasico;
  esObligatorio: boolean;
  prerrequisitos?: number[];
}
