// ====================================
// ENUMS
// ====================================

export enum EstadoTarea {
  ASIGNADA = 'asignada',
  EN_PROGRESO = 'en_progreso',
  ENTREGADA = 'entregada',
  CALIFICADA = 'calificada',
  VENCIDA = 'vencida',
  CERRADA = 'cerrada',
}

export enum TipoTarea {
  ENSAYO = 'ensayo',
  PROYECTO = 'proyecto',
  EJERCICIOS = 'ejercicios',
  INVESTIGACION = 'investigacion',
  PRESENTACION = 'presentacion',
  LABORATORIO = 'laboratorio',
  LECTURA = 'lectura',
  EXAMEN = 'examen',
  QUIZ = 'quiz',
  OTRO = 'otro',
}

export enum PrioridadTarea {
  BAJA = 'baja',
  MEDIA = 'media',
  ALTA = 'alta',
}

export enum EstadoEntrega {
  BORRADOR = 'borrador',
  ENTREGADA = 'entregada',
  EN_REVISION = 'en_revision',
  CALIFICADA = 'calificada',
  DEVUELTA = 'devuelta',
}

// Enum para el estado visual calculado (enriquecido)
export enum EstadoVisualizacion {
  PENDIENTE = 'pendiente',
  PROXIMA_A_VENCER = 'proxima_a_vencer',
  VENCIDA = 'vencida',
  ENTREGADA = 'entregada',
  CALIFICADA = 'calificada',
  CERRADA = 'cerrada',
}

// ====================================
// INTERFACES PRINCIPALES
// ====================================

/**
 * Interfaz completa de Tarea basada en el modelo del backend
 * Incluye TODOS los campos de la base de datos
 */
export interface Tarea {
  // === IDENTIFICACIÓN ===
  tarea_id?: string;
  grupo_id: string;
  docente_id: string;
  clase_id?: string;
  
  // === INFORMACIÓN BÁSICA ===
  titulo: string;
  descripcion?: string;
  instrucciones?: string;
  objetivos?: string;
  archivo_adjunto?: string;
  
  // === CLASIFICACIÓN ===
  tipo: TipoTarea;
  prioridad: PrioridadTarea;
  categoria?: string;
  tags?: string[];
  
  // === FECHAS Y TIEMPO ===
  fecha_asignacion: string; // ISO string
  fecha_limite: string; // ISO string
  fecha_inicio_disponible?: string;
  tiempo_estimado?: number; // minutos
  
  // === CONFIGURACIÓN DE ENTREGA ===
  permite_entrega_tardia: boolean;
  permite_entregas_tardias?: boolean; // campo duplicado en BD
  penalizacion_tardia: number; // porcentaje
  intentos_maximos: number;
  formato_entrega?: string;
  tamano_maximo_mb: number;
  restricciones_archivo?: Record<string, unknown>;
  
  // === EVALUACIÓN Y CALIFICACIÓN ===
  puntuacion_maxima: number;
  peso_evaluacion: number;
  peso_calificacion?: number;
  rubrica_id?: string;
  rubrica?: Record<string, unknown>; // JSONB
  criterios_evaluacion?: string;
  
  // === GAMIFICACIÓN ===
  puntos_base?: number;
  puntos_bonificacion?: number;
  
  // === IA Y RETROALIMENTACIÓN ===
  habilitar_retroalimentacion_ia: boolean;
  prompt_ia_personalizado?: string;
  
  // === ESTADO Y VISIBILIDAD ===
  estado: EstadoTarea;
  visible_estudiantes: boolean;
  requiere_confirmacion_lectura: boolean;
  
  // === AUDITORÍA ===
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
  
  // === RELACIONES (opcional, pueden venir del backend) ===
  entregas?: EntregaTarea[];
  
  // === CAMPOS CALCULADOS (del backend enriquecido) ===
  total_entregas?: number;
  entregas_pendientes?: number;
  entregas_calificadas?: number;
  promedio_calificaciones?: number;
  esta_vencida?: boolean;
}

/**
 * Tarea con detalles extendidos para visualización completa
 */
export interface TareaDetallada extends Tarea {
  docente_nombre?: string;
  docente_apellido?: string;
  grupo_nombre?: string;
  rubrica_nombre?: string;
  estudiantes_asignados?: number;
  porcentaje_completitud?: number;
  
  // Información del grupo/clase
  clase_nombre?: string;
  curso_nombre?: string;
}

/**
 * DTO para crear una nueva tarea
 */
export interface TareaCreate {
  titulo: string;
  descripcion?: string;
  fecha_limite: string;
  puntos_max?: number;
  tipo?: TipoTarea;
  prioridad?: PrioridadTarea;
  instrucciones?: string;
  permite_entrega_tardia?: boolean;
  habilitar_retroalimentacion_ia?: boolean;
}

// ====================================
// ENTREGAS DE TAREAS
// ====================================

/**
 * Interfaz completa de EntregaTarea basada en el modelo del backend
 */
export interface EntregaTarea {
  // === IDENTIFICACIÓN ===
  entrega_id: string;
  tarea_id: string;
  estudiante_id: string;
  
  // === INFORMACIÓN DE LA ENTREGA ===
  titulo_entrega?: string;
  descripcion_entrega?: string;
  comentarios_estudiante?: string;
  
  // === ARCHIVOS Y CONTENIDO ===
  archivo_url?: string;
  archivo_metadata?: Record<string, unknown>; // JSONB
  archivos_adicionales?: string; // JSON array de archivos
  contenido_texto?: string;
  enlaces_externos?: string; // JSON array
  
  // === FECHAS Y CONTROL ===
  fecha_entrega?: string;
  fecha_limite_original?: string;
  numero_intento: number;
  intentos?: number;
  es_entrega_tardia: boolean;
  es_tardia?: boolean; // campo duplicado en BD
  
  // === CALIFICACIÓN MANUAL ===
  calificacion?: number;
  calificacion_letras?: string;
  comentarios_docente?: string;
  retroalimentacion_docente?: string;
  rubrica_calificacion?: Record<string, unknown>; // JSON
  comentarios_privados?: string;
  
  // === CALIFICACIÓN IA ===
  calificacion_preliminar_ia?: number;
  retroalimentacion_ia?: Record<string, unknown>; // JSONB con análisis detallado
  
  // === GAMIFICACIÓN ===
  puntos_otorgados?: number;
  
  // === ESTADO ===
  estado: EstadoEntrega;
  es_final: boolean;
  requiere_revision: boolean;
  
  // === METADATA Y FEEDBACK ===
  tiempo_empleado?: number; // minutos
  dificultad_percibida?: number; // 1-5
  satisfaccion_estudiante?: number; // 1-5
  
  // === AUDITORÍA ===
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  calificado_por?: string;
  fecha_calificacion?: string;
  
  // === RELACIONES (opcional) ===
  estudiante_nombre?: string;
  estudiante_apellido?: string;
  
  // === CAMPOS CALCULADOS ===
  dias_desde_entrega?: number;
  porcentaje_calificacion?: number;
}

export interface EntregaTareaDetallada extends EntregaTarea {
  estudiante_email?: string;
  tarea_titulo?: string;
  tarea_puntuacion_maxima?: number;
  calificador_nombre?: string;
  calificador_apellido?: string;
  tarea?: Tarea; // Relación completa con la tarea
}

export interface EntregaTareaCreate {
  tarea_id: string;
  contenido: string;
  archivos?: string; // JSON string de archivos
}

// ====================================
// TAREAS ENRIQUECIDAS (Sistema avanzado con cálculos)
// ====================================

/**
 * Tiempo restante calculado
 */
export interface TiempoRestante {
  dias: number;
  horas: number;
  minutos: number;
  total_horas: number;
  es_urgente: boolean; // < 48 horas
  es_muy_urgente: boolean; // < 24 horas
  mensaje_tiempo: string; // "2d 5h" o "12h 30m"
}

/**
 * Información visual del estado (para UI)
 */
export interface InfoEstadoVisual {
  estado: EstadoVisualizacion;
  color: string; // ej: "yellow-500", "red-600", "green-500"
  icono: string; // ej: "⏰", "✅", "❌"
  texto: string; // ej: "Próxima a vencer"
  descripcion: string; // Descripción larga
}

/**
 * Métricas de progreso de la tarea
 */
export interface MetricasProgreso {
  total_estudiantes: number;
  entregas_realizadas: number;
  entregas_calificadas: number;
  entregas_pendientes: number;
  entregas_tardias: number;
  porcentaje_completitud: number;
  porcentaje_calificadas: number;
  tasa_puntualidad: number;
}

/**
 * Estadísticas de calificaciones
 */
export interface EstadisticasCalificacion {
  promedio_calificacion: number;
  calificacion_maxima: number;
  calificacion_minima: number;
  desviacion_estandar: number;
  mediana: number;
  rango_calificacion: number;
}

/**
 * Tarea Enriquecida con datos calculados y métricas
 * Esta es la interfaz principal para la UI
 */
export interface TareaEnriquecida extends Tarea {
  tiempo_restante?: TiempoRestante;
  estado_visual: EstadoVisualizacion;
  info_estado: InfoEstadoVisual;
  metricas: MetricasProgreso;
  estadisticas_calificacion?: EstadisticasCalificacion;
}

// ====================================
// RESPUESTA DE CALIFICACIÓN CON GAMIFICACIÓN
// ====================================

/**
 * Desglose de puntos al calificar (gamificación)
 */
export interface DesglosePuntos {
  puntos_base: number;
  bono_calidad: number;
  bono_rapidez: number;
  penalizacion_tardia: number;
  penalizacion_intentos: number;
  total: number;
}

/**
 * Actualización de racha del estudiante
 */
export interface RachaActualizada {
  dias_actuales: number;
  puntos_racha: number;
  siguiente_ciclo?: number;
}

/**
 * Respuesta completa al calificar una entrega (con gamificación)
 */
export interface CalificacionResponse {
  success: boolean;
  entrega: EntregaTarea;
  puntos_otorgados: number;
  desglose_puntos: DesglosePuntos;
  racha_actualizada?: RachaActualizada;
  milestones_alcanzados?: string[];
}

// Interfaces para Rúbricas
export interface Rubrica {
  rubrica_id: string;
  nombre: string;
  descripcion?: string;
  criterios: Record<string, unknown>;
  puntuacion_total: number;
  es_publica: boolean;
  es_plantilla: boolean;
  creado_por: string;
  activa: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface RubricaDetallada extends Rubrica {
  creador_nombre?: string;
  creador_apellido?: string;
  veces_utilizada?: number;
  tareas_asociadas?: number;
}

export interface RubricaCreate {
  nombre: string;
  descripcion?: string;
  criterios: Record<string, unknown>;
  puntuacion_total: number;
  es_publica: boolean;
  es_plantilla: boolean;
  creado_por: string;
}

// Interfaces auxiliares
export interface ArchivoAdicional {
  nombre: string;
  url: string;
  tamaño: number;
  tipo: string;
}

export interface EnlaceExterno {
  titulo: string;
  url: string;
  descripcion?: string;
}

// ====================================
// RESPUESTA PAGINADA
// ====================================

/**
 * Respuesta paginada genérica
 */
export interface RespuestaPaginada<T> {
  items: T[];
  total: number;
  pagina: number;
  limite: number;
  paginas_totales: number;
}

// Interfaces para filtros
export interface FiltrosTarea {
  grupo_id?: string;
  curso_id?: string;
  docente_id?: string;
  tipo?: TipoTarea; // Usa 'tipo' en lugar de 'tipo_tarea' para coincidir con backend
  estado?: EstadoTarea;
  estado_visual?: EstadoVisualizacion;
  prioridad?: PrioridadTarea;
  solo_activas?: boolean;
  solo_urgentes?: boolean;
  solo_vencidas?: boolean;
  fecha_desde?: string;
  fecha_hasta?: string;
  busqueda?: string;
  ordenar_por?: string;
  orden_desc?: boolean;
  pagina?: number;
  tamaño_pagina?: number;
}

export interface FiltrosEntrega {
  tarea_id?: string;
  estudiante_id?: string;
  estado?: EstadoEntrega;
  solo_calificadas?: boolean;
  solo_pendientes?: boolean;
  solo_tardias?: boolean;
  fecha_desde?: string;
  fecha_hasta?: string;
  ordenar_por?: string;
  orden_desc?: boolean;
  pagina?: number;
  tamaño_pagina?: number;
}

// Interfaces para estadísticas
export interface EstadisticasTarea {
  total_tareas: number;
  tareas_activas: number;
  tareas_vencidas: number;
  tareas_completadas: number;
  promedio_entregas_por_tarea: number;
  promedio_calificaciones: number;
  tiempo_promedio_calificacion?: number;
}

export interface EstadisticasEntrega {
  total_entregas: number;
  entregas_calificadas: number;
  entregas_pendientes: number;
  entregas_tardias: number;
  promedio_calificacion: number;
  tiempo_promedio_entrega?: number;
}