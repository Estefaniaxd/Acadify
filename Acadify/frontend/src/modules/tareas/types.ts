// Enums para Tareas
export enum EstadoTarea {
  BORRADOR = 'borrador',
  PUBLICADA = 'publicada',
  EN_PROGRESO = 'en_progreso',
  VENCIDA = 'vencida',
  CERRADA = 'cerrada',
  ARCHIVADA = 'archivada',
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
  OTRO = 'otro',
}

export enum PrioridadTarea {
  BAJA = 'baja',
  MEDIA = 'media',
  ALTA = 'alta',
  URGENTE = 'urgente',
}

export enum EstadoEntrega {
  BORRADOR = 'borrador',
  ENVIADA = 'enviada',
  EN_REVISION = 'en_revision',
  CALIFICADA = 'calificada',
  DEVUELTA = 'devuelta',
  RECHAZADA = 'rechazada',
}

// Interfaces para Tareas
export interface Tarea {
  id?: string;
  grupo_id: string;
  docente_id: string;
  titulo: string;
  descripcion?: string;
  instrucciones?: string;
  objetivos?: string;
  tipo_tarea: TipoTarea;
  prioridad: PrioridadTarea;
  categoria?: string;
  tags?: string;
  fecha_asignacion: string;
  fecha_limite: string;
  fecha_inicio_disponible?: string;
  tiempo_estimado?: number;
  permite_entrega_tardia: boolean;
  penalizacion_tardia: number;
  intentos_maximos: number;
  formato_entrega?: string;
  tamano_maximo_mb: number;
  puntuacion_maxima: number;
  peso_evaluacion: number;
  estado: EstadoTarea;
  es_grupal: boolean;
  es_publica: boolean;
  requiere_aprobacion: boolean;
  recursos_necesarios?: string;
  criterios_evaluacion?: string;
  rubrica_id?: string;
  configuracion_json?: Record<string, any>;
  activa: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  creado_por?: string;
  actualizado_por?: string;
  
  // Propiedades calculadas
  total_entregas?: number;
  entregas_pendientes?: number;
  promedio_calificaciones?: number;
  esta_vencida?: boolean;
}

export interface TareaDetallada extends Tarea {
  docente_nombre?: string;
  docente_apellido?: string;
  grupo_nombre?: string;
  rubrica_nombre?: string;
  estudiantes_asignados?: number;
  entregas_calificadas?: number;
  porcentaje_completitud?: number;
}

export interface TareaCreate {
  grupo_id: string;
  docente_id: string;
  titulo: string;
  descripcion?: string;
  instrucciones?: string;
  objetivos?: string;
  tipo_tarea: TipoTarea;
  prioridad: PrioridadTarea;
  categoria?: string;
  tags?: string;
  fecha_limite: string;
  fecha_inicio_disponible?: string;
  tiempo_estimado?: number;
  permite_entrega_tardia: boolean;
  penalizacion_tardia: number;
  intentos_maximos: number;
  formato_entrega?: string;
  tamano_maximo_mb: number;
  puntuacion_maxima: number;
  peso_evaluacion: number;
  es_grupal: boolean;
  es_publica: boolean;
  requiere_aprobacion: boolean;
  recursos_necesarios?: string;
  criterios_evaluacion?: string;
  rubrica_id?: string;
  configuracion_json?: Record<string, any>;
}

// Interfaces para Entregas
export interface EntregaTarea {
  id?: string;
  entrega_id?: string;
  tarea_id: string;
  estudiante_id: string;
  estudiante_nombre?: string;
  titulo_entrega?: string;
  descripcion_entrega?: string;
  comentarios_estudiante?: string;
  archivo_url?: string;
  archivos_adicionales?: ArchivoAdicional[];
  contenido_texto?: string;
  enlaces_externos?: EnlaceExterno[];
  fecha_entrega?: string;
  fecha_limite_original?: string;
  numero_intento: number;
  es_entrega_tardia: boolean;
  calificacion?: number;
  calificacion_letras?: string;
  comentarios_docente?: string;
  rubrica_calificacion?: Record<string, any>;
  estado: EstadoEntrega;
  es_final: boolean;
  requiere_revision: boolean;
  tiempo_empleado?: number;
  dificultad_percibida?: number;
  satisfaccion_estudiante?: number;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  calificado_por?: string;
  fecha_calificacion?: string;
  
  // Propiedades calculadas
  dias_desde_entrega?: number;
  porcentaje_calificacion?: number;
}

export interface EntregaTareaDetallada extends EntregaTarea {
  estudiante_nombre?: string;
  estudiante_apellido?: string;
  estudiante_email?: string;
  tarea_titulo?: string;
  tarea_puntuacion_maxima?: number;
  calificador_nombre?: string;
  calificador_apellido?: string;
}

export interface EntregaTareaCreate {
  tarea_id: string;
  estudiante_id: string;
  titulo_entrega?: string;
  descripcion_entrega?: string;
  comentarios_estudiante?: string;
  archivo_url?: string;
  archivos_adicionales?: ArchivoAdicional[];
  contenido_texto?: string;
  enlaces_externos?: EnlaceExterno[];
  tiempo_empleado?: number;
  dificultad_percibida?: number;
  satisfaccion_estudiante?: number;
}

export interface CalificarEntrega {
  calificacion: number;
  calificacion_letras?: string;
  comentarios_docente?: string;
  rubrica_calificacion?: Record<string, any>;
  requiere_revision: boolean;
}

// Interfaces para Rúbricas
export interface Rubrica {
  rubrica_id: string;
  nombre: string;
  descripcion?: string;
  criterios: Record<string, any>;
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
  criterios: Record<string, any>;
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

// Interfaces para filtros
export interface FiltrosTarea {
  grupo_id?: string;
  docente_id?: string;
  tipo_tarea?: TipoTarea;
  estado?: EstadoTarea;
  prioridad?: PrioridadTarea;
  es_grupal?: boolean;
  solo_activas?: boolean;
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