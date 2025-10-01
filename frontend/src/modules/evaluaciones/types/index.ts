export type TipoExamen = 'QUIZ' | 'EVALUACION' | 'PARCIAL' | 'FINAL' | 'PRACTICA';
export type EstadoExamen = 'BORRADOR' | 'ACTIVO' | 'PAUSADO' | 'FINALIZADO' | 'ARCHIVADO';
export type TipoPregunta = 'OPCION_MULTIPLE' | 'VERDADERO_FALSO' | 'ENSAYO' | 'COMPLETAR' | 'ORDENAR';
export type DificultadPregunta = 'FACIL' | 'MEDIO' | 'DIFICIL';
export type EstadoIntento = 'EN_PROGRESO' | 'FINALIZADO' | 'ABANDONADO' | 'EXPIRADO';

export interface ConfiguracionEvaluacion {
  config_id: string;
  tiempo_gracia_segundos: number;
  maximo_intentos_globales: number;
  tiempo_minimo_entre_intentos: number;
  max_cambios_pestana_permitidos: number;
  tiempo_max_inactividad_global: number;
  habilitar_deteccion_copia_texto: boolean;
  habilitar_deteccion_pantalla_completa: boolean;
  algoritmo_calificacion_ensayos: string;
  umbral_similitud_plagio: number;
  habilitar_feedback_automatico: boolean;
  notificar_intento_finalizado: boolean;
  notificar_resultado_disponible: boolean;
  notificar_tiempo_restante: boolean;
  tiempo_notificacion_previa_minutos: number;
  guardar_progreso_cada_segundos: number;
  habilitar_recuperacion_sesion: boolean;
  tiempo_expiracion_backup_horas: number;
  institucion_id?: string;
  aplicar_globalmente: boolean;
  creado_por: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface Examen {
  examen_id: string;
  titulo: string;
  descripcion: string;
  tipo_examen: TipoExamen;
  estado_examen: EstadoExamen;
  tiempo_limite: number;
  fecha_inicio: string;
  fecha_limite: string;
  intentos_permitidos: number;
  requiere_contraseña: boolean;
  contraseña_acceso?: string;
  randomizar_preguntas: boolean;
  mostrar_resultados_inmediatos: boolean;
  permitir_revision: boolean;
  mostrar_respuestas_correctas: boolean;
  modo_pantalla_completa: boolean;
  bloquear_navegacion: boolean;
  detectar_cambio_pestana: boolean;
  tiempo_maximo_inactividad: number;
  puntuacion_total: number;
  puntuacion_minima_aprobacion: number;
  calificacion_automatica: boolean;
  curso_id?: string;
  grupo_id?: string;
  creado_por: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  configuracion_avanzada?: Record<string, any>;
  instrucciones?: string;
  total_preguntas: number;
  total_intentos: number;
  promedio_calificacion?: number;
}

export interface OpcionRespuesta {
  id: string;
  texto: string;
  es_correcta?: boolean;
  explicacion?: string;
}

export interface PreguntaExamen {
  pregunta_id: string;
  examen_id: string;
  titulo: string;
  descripcion?: string;
  tipo_pregunta: TipoPregunta;
  orden: number;
  puntuacion: number;
  es_obligatoria: boolean;
  tiempo_limite_segundos?: number;
  opciones_respuesta: OpcionRespuesta[];
  respuesta_correcta: Record<string, any>;
  explicacion?: string;
  puntos_respuesta_parcial: boolean;
  dificultad: DificultadPregunta;
  imagen_url?: string;
  audio_url?: string;
  video_url?: string;
  banco_pregunta_id?: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  veces_utilizada: number;
  promedio_aciertos?: number;
  tiempo_promedio_respuesta?: number;
}

export interface BancoPregunta {
  pregunta_id: string;
  titulo: string;
  descripcion?: string;
  tipo_pregunta: TipoPregunta;
  dificultad: DificultadPregunta;
  materia: string;
  tema: string;
  subtema?: string;
  opciones_respuesta?: OpcionRespuesta[];
  respuesta_correcta: Record<string, any>;
  explicacion?: string;
  imagen_url?: string;
  audio_url?: string;
  video_url?: string;
  creado_por: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
  institucion_id?: string;
  es_publica: boolean;
  categoria: string;
  nivel_educativo: string;
  puntuacion_sugerida: number;
  tiempo_estimado_segundos?: number;
  veces_utilizada: number;
  promedio_aciertos?: number;
  calificacion_dificultad?: number;
  ultima_vez_utilizada?: string;
  tags?: string[];
  revisado_por?: string;
  fecha_revision?: string;
  estado_revision: string;
  comentarios_revision?: string;
}

export interface IntentoExamen {
  intento_id: string;
  examen_id: string;
  estudiante_id: string;
  numero_intento: number;
  estado_intento: EstadoIntento;
  fecha_inicio: string;
  fecha_fin?: string;
  tiempo_total_segundos?: number;
  tiempo_limite_vencido: boolean;
  puntuacion_obtenida: number;
  puntuacion_maxima: number;
  porcentaje?: number;
  aprobado?: boolean;
  preguntas_respondidas: number;
  total_preguntas: number;
  pregunta_actual: number;
  cambios_pestana_detectados: number;
  tiempo_inactividad_total: number;
  ip_address: string;
  user_agent: string;
  eventos_sospechosos?: Record<string, any>[];
  orden_preguntas: string[];
  configuracion_intento?: Record<string, any>;
  finalizado_por: string;
  comentarios_finalizacion?: string;
  fecha_revision?: string;
  revisado_por?: string;
  comentarios_profesor?: string;
}

export interface RespuestaEstudiante {
  respuesta_id: string;
  intento_id: string;
  pregunta_id: string;
  respuesta_estudiante?: Record<string, any>;
  texto_respuesta?: string;
  puntuacion_obtenida: number;
  puntuacion_maxima: number;
  es_correcta: boolean;
  calificada_automaticamente: boolean;
  tiempo_empleado_segundos: number;
  fecha_respuesta: string;
  fecha_ultima_modificacion?: string;
  numero_modificaciones: number;
  feedback_automatico?: string;
  feedback_profesor?: string;
  mostrar_respuesta_correcta: boolean;
  palabras_clave_encontradas?: string[];
  similitud_respuesta_correcta?: number;
  version_pregunta?: number;
}

export interface EstadisticaExamen {
  estadistica_id: string;
  examen_id: string;
  total_estudiantes_asignados: number;
  total_intentos_realizados: number;
  total_intentos_finalizados: number;
  total_aprobados: number;
  total_reprobados: number;
  puntuacion_promedio: number;
  puntuacion_mediana: number;
  puntuacion_maxima_obtenida: number;
  puntuacion_minima_obtenida: number;
  desviacion_estandar: number;
  tiempo_promedio_minutos: number;
  tiempo_maximo_empleado: number;
  tiempo_minimo_empleado: number;
  estadisticas_preguntas: Record<string, any>;
  preguntas_mas_dificiles: string[];
  preguntas_mas_faciles: string[];
  fecha_calculo: string;
  fecha_ultima_actualizacion?: string;
  incluir_intentos_incompletos: boolean;
  periodo_calculo: string;
}

// Interfaces para formularios y UI
export interface FormularioExamen {
  titulo: string;
  descripcion: string;
  tipo_examen: TipoExamen;
  tiempo_limite: number;
  fecha_inicio: string;
  fecha_limite: string;
  intentos_permitidos: number;
  puntuacion_minima_aprobacion: number;
  randomizar_preguntas: boolean;
  mostrar_resultados_inmediatos: boolean;
  permitir_revision: boolean;
  modo_pantalla_completa: boolean;
  detectar_cambio_pestana: boolean;
  instrucciones?: string;
  requiere_contraseña: boolean;
  contraseña_acceso?: string;
}

export interface FormularioPregunta {
  titulo: string;
  descripcion?: string;
  tipo_pregunta: TipoPregunta;
  puntuacion: number;
  dificultad: DificultadPregunta;
  opciones_respuesta: OpcionRespuesta[];
  respuesta_correcta: Record<string, any>;
  explicacion?: string;
  tiempo_limite_segundos?: number;
  imagen_url?: string;
  es_obligatoria: boolean;
}

export interface FiltrosBancoPreguntas {
  materia?: string;
  tema?: string;
  tipo_pregunta?: TipoPregunta;
  dificultad?: DificultadPregunta;
  categoria?: string;
  nivel_educativo?: string;
  es_publica?: boolean;
  creado_por?: string;
  tags?: string[];
  busqueda?: string;
}

export interface ConfiguracionAntiTrampa {
  habilitar_deteccion_copia_texto: boolean;
  habilitar_deteccion_pantalla_completa: boolean;
  max_cambios_pestana_permitidos: number;
  tiempo_max_inactividad_global: number;
  habilitar_captura_pantalla: boolean;
  habilitar_deteccion_dispositivos: boolean;
  bloquear_click_derecho: boolean;
  bloquear_atajos_teclado: boolean;
}

export interface EventoAntiTrampa {
  tipo_evento: string;
  descripcion: string;
  timestamp: string;
  datos_adicionales?: Record<string, any>;
  nivel_sospecha: 'BAJO' | 'MEDIO' | 'ALTO';
}

export interface DashboardEstadisticas {
  examenes_activos: number;
  examenes_finalizados: number;
  total_intentos_hoy: number;
  promedio_calificaciones: number;
  examenes_recientes: Examen[];
  estadisticas_generales: EstadisticaExamen[];
  alertas_integridad: EventoAntiTrampa[];
}