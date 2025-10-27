import { 
  TipoExamen, 
  EstadoExamen, 
  TipoPregunta, 
  DificultadPregunta,
  Examen,
  PreguntaExamen,
  IntentoExamen,
  RespuestaEstudiante
} from '../types';

// ================================
// FORMATEO DE TIEMPO
// ================================

/**
 * Convierte segundos a formato legible (ej: "1h 30m 45s")
 */
export function formatearTiempo(segundos: number): string {
  if (segundos < 0) return '0s';
  
  const horas = Math.floor(segundos / 3600);
  const minutos = Math.floor((segundos % 3600) / 60);
  const segs = segundos % 60;
  
  const partes: string[] = [];
  
  if (horas > 0) partes.push(`${horas}h`);
  if (minutos > 0) partes.push(`${minutos}m`);
  if (segs > 0 || partes.length === 0) partes.push(`${segs}s`);
  
  return partes.join(' ');
}

/**
 * Convierte minutos a formato de tiempo legible
 */
export function formatearTiempoMinutos(minutos: number): string {
  if (minutos < 1) return 'Menos de 1 minuto';
  if (minutos < 60) return `${Math.round(minutos)} minutos`;
  
  const horas = Math.floor(minutos / 60);
  const mins = Math.round(minutos % 60);
  
  if (mins === 0) return `${horas}h`;
  return `${horas}h ${mins}m`;
}

/**
 * Obtiene el tiempo restante formateado para un intento
 */
export function obtenerTiempoRestante(intento: IntentoExamen, tiempoLimiteMinutos: number): string {
  const inicio = new Date(intento.fecha_inicio).getTime();
  const limite = inicio + (tiempoLimiteMinutos * 60 * 1000);
  const ahora = Date.now();
  const restante = Math.max(0, limite - ahora);
  
  return formatearTiempo(Math.floor(restante / 1000));
}

// ================================
// FORMATEO DE FECHAS
// ================================

/**
 * Formatea una fecha para mostrar de manera legible
 */
export function formatearFecha(fecha: string): string {
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(fecha));
}

/**
 * Formatea una fecha relativa (ej: "hace 2 días")
 */
export function formatearFechaRelativa(fecha: string): string {
  const ahora = new Date();
  const fechaObj = new Date(fecha);
  const diferencia = ahora.getTime() - fechaObj.getTime();
  
  const minutos = Math.floor(diferencia / (1000 * 60));
  const horas = Math.floor(diferencia / (1000 * 60 * 60));
  const dias = Math.floor(diferencia / (1000 * 60 * 60 * 24));
  
  if (minutos < 60) return `hace ${minutos} minutos`;
  if (horas < 24) return `hace ${horas} horas`;
  if (dias < 7) return `hace ${dias} días`;
  
  return formatearFecha(fecha);
}

// ================================
// FORMATEO DE PUNTUACIONES
// ================================

/**
 * Formatea una puntuación con decimales apropiados
 */
export function formatearPuntuacion(puntuacion: number, decimales: number = 1): string {
  return puntuacion.toFixed(decimales);
}

/**
 * Formatea un porcentaje con color basado en el valor
 */
export function formatearPorcentaje(porcentaje: number): string {
  return `${Math.round(porcentaje)}%`;
}

/**
 * Obtiene el color de una puntuación basado en umbrales
 */
export function obtenerColorPuntuacion(porcentaje: number): string {
  if (porcentaje >= 90) return 'text-green-600 dark:text-green-400';
  if (porcentaje >= 70) return 'text-blue-600 dark:text-blue-400';
  if (porcentaje >= 60) return 'text-yellow-600 dark:text-yellow-400';
  return 'text-red-600 dark:text-red-400';
}

// ================================
// MAPEO DE ENUMS A TEXTOS LEGIBLES
// ================================

export const TIPO_EXAMEN_LABELS: Record<TipoExamen, string> = {
  QUIZ: 'Quiz',
  EVALUACION: 'Evaluación',
  PARCIAL: 'Examen Parcial',
  FINAL: 'Examen Final',
  PRACTICA: 'Práctica'
};

export const ESTADO_EXAMEN_LABELS: Record<EstadoExamen, string> = {
  BORRADOR: 'Borrador',
  ACTIVO: 'Activo',
  PAUSADO: 'Pausado',
  FINALIZADO: 'Finalizado',
  ARCHIVADO: 'Archivado'
};

export const TIPO_PREGUNTA_LABELS: Record<TipoPregunta, string> = {
  OPCION_MULTIPLE: 'Opción Múltiple',
  VERDADERO_FALSO: 'Verdadero/Falso',
  ENSAYO: 'Ensayo',
  COMPLETAR: 'Completar',
  ORDENAR: 'Ordenar'
};

export const DIFICULTAD_LABELS: Record<DificultadPregunta, string> = {
  FACIL: 'Fácil',
  MEDIO: 'Medio',
  DIFICIL: 'Difícil'
};

// ================================
// COLORES PARA ESTADOS Y TIPOS
// ================================

export function obtenerColorEstado(estado: EstadoExamen): string {
  const colores = {
    BORRADOR: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
    ACTIVO: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-300',
    PAUSADO: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-300',
    FINALIZADO: 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-300',
    ARCHIVADO: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-300'
  };
  return colores[estado];
}

export function obtenerColorTipo(tipo: TipoExamen): string {
  const colores = {
    QUIZ: 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-300',
    EVALUACION: 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-300',
    PARCIAL: 'bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-300',
    FINAL: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-300',
    PRACTICA: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-300'
  };
  return colores[tipo];
}

export function obtenerColorDificultad(dificultad: DificultadPregunta): string {
  const colores = {
    FACIL: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-300',
    MEDIO: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-300',
    DIFICIL: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-300'
  };
  return colores[dificultad];
}

// ================================
// VALIDACIONES
// ================================

/**
 * Valida si un examen está completo y listo para ser publicado
 */
export function validarExamen(examen: Examen, preguntas: PreguntaExamen[]): {
  esValido: boolean;
  errores: string[];
  advertencias: string[];
} {
  const errores: string[] = [];
  const advertencias: string[] = [];

  // Validaciones obligatorias
  if (!examen.titulo?.trim()) {
    errores.push('El título del examen es obligatorio');
  }
  
  if (preguntas.length === 0) {
    errores.push('El examen debe tener al menos una pregunta');
  }
  
  if (examen.tiempo_limite <= 0) {
    errores.push('El tiempo límite debe ser mayor a 0');
  }
  
  if (examen.puntuacion_minima_aprobacion < 0 || examen.puntuacion_minima_aprobacion > examen.puntuacion_total) {
    errores.push('La puntuación mínima de aprobación debe estar entre 0 y la puntuación total');
  }
  
  if (new Date(examen.fecha_inicio) >= new Date(examen.fecha_limite)) {
    errores.push('La fecha de inicio debe ser anterior a la fecha límite');
  }

  // Validar preguntas
  const preguntasSinRespuesta = preguntas.filter(p => 
    !p.respuesta_correcta || 
    (Array.isArray(p.respuesta_correcta) && p.respuesta_correcta.length === 0)
  );
  
  if (preguntasSinRespuesta.length > 0) {
    errores.push(`${preguntasSinRespuesta.length} preguntas no tienen respuesta correcta definida`);
  }

  // Advertencias
  if (examen.tiempo_limite < preguntas.length * 2) {
    advertencias.push('El tiempo límite podría ser insuficiente (menos de 2 minutos por pregunta)');
  }
  
  if (preguntas.length < 5) {
    advertencias.push('Se recomienda tener al menos 5 preguntas para una evaluación completa');
  }
  
  const puntuacionTotal = preguntas.reduce((sum, p) => sum + p.puntuacion, 0);
  if (Math.abs(puntuacionTotal - examen.puntuacion_total) > 0.1) {
    advertencias.push('La suma de puntuaciones de las preguntas no coincide con la puntuación total del examen');
  }

  return {
    esValido: errores.length === 0,
    errores,
    advertencias
  };
}

/**
 * Valida una respuesta de estudiante
 */
export function validarRespuesta(
  pregunta: PreguntaExamen, 
  respuesta: any
): { esValida: boolean; mensaje?: string } {
  if (!respuesta && pregunta.es_obligatoria) {
    return { esValida: false, mensaje: 'Esta pregunta es obligatoria' };
  }

  switch (pregunta.tipo_pregunta) {
    case 'OPCION_MULTIPLE':
      if (!respuesta?.seleccion) {
        return { esValida: false, mensaje: 'Debe seleccionar una opción' };
      }
      break;
      
    case 'VERDADERO_FALSO':
      if (respuesta?.seleccion === undefined) {
        return { esValida: false, mensaje: 'Debe seleccionar verdadero o falso' };
      }
      break;
      
    case 'ENSAYO':
      if (!respuesta?.texto?.trim()) {
        return { esValida: false, mensaje: 'Debe escribir una respuesta' };
      }
      if (respuesta.texto.length < 10) {
        return { esValida: false, mensaje: 'La respuesta debe tener al menos 10 caracteres' };
      }
      break;
  }

  return { esValida: true };
}

// ================================
// CÁLCULOS DE ESTADÍSTICAS
// ================================

/**
 * Calcula el progreso de un intento
 */
export function calcularProgreso(intento: IntentoExamen): {
  porcentaje: number;
  respondidas: number;
  total: number;
} {
  const total = intento.total_preguntas;
  const respondidas = intento.preguntas_respondidas;
  const porcentaje = total > 0 ? Math.round((respondidas / total) * 100) : 0;
  
  return { porcentaje, respondidas, total };
}

/**
 * Calcula estadísticas de tiempo para un examen
 */
export function calcularEstadisticasTiempo(intentos: IntentoExamen[]): {
  promedio: number;
  maximo: number;
  minimo: number;
  mediana: number;
} {
  const tiempos = intentos
    .filter(i => i.tiempo_total_segundos && i.tiempo_total_segundos > 0)
    .map(i => i.tiempo_total_segundos!)
    .sort((a, b) => a - b);

  if (tiempos.length === 0) {
    return { promedio: 0, maximo: 0, minimo: 0, mediana: 0 };
  }

  const promedio = tiempos.reduce((sum, t) => sum + t, 0) / tiempos.length;
  const maximo = tiempos[tiempos.length - 1];
  const minimo = tiempos[0];
  const mediana = tiempos[Math.floor(tiempos.length / 2)];

  return { promedio, maximo, minimo, mediana };
}

// ================================
// UTILIDADES DE NAVEGACIÓN
// ================================

/**
 * Genera la URL para una página del módulo de evaluaciones
 */
export function generarUrlEvaluacion(seccion: string, id?: string): string {
  const base = '/evaluaciones';
  if (!id) return `${base}/${seccion}`;
  return `${base}/${seccion}/${id}`;
}

// ================================
// UTILIDADES DE ALMACENAMIENTO LOCAL
// ================================

/**
 * Guarda el progreso de un intento en localStorage
 */
export function guardarProgresoLocal(intentoId: string, respuestas: Map<string, any>): void {
  try {
    const datos = {
      timestamp: Date.now(),
      respuestas: Array.from(respuestas.entries())
    };
    localStorage.setItem(`intento_${intentoId}`, JSON.stringify(datos));
  } catch (error) {
    console.warn('No se pudo guardar el progreso local:', error);
  }
}

/**
 * Recupera el progreso de un intento del localStorage
 */
export function recuperarProgresoLocal(intentoId: string): Map<string, any> | null {
  try {
    const datos = localStorage.getItem(`intento_${intentoId}`);
    if (!datos) return null;
    
    const parsed = JSON.parse(datos);
    return new Map(parsed.respuestas);
  } catch (error) {
    console.warn('No se pudo recuperar el progreso local:', error);
    return null;
  }
}

/**
 * Limpia el progreso local de un intento
 */
export function limpiarProgresoLocal(intentoId: string): void {
  try {
    localStorage.removeItem(`intento_${intentoId}`);
  } catch (error) {
    console.warn('No se pudo limpiar el progreso local:', error);
  }
}

// ================================
// UTILIDADES DE EXPORTACIÓN
// ================================

/**
 * Convierte datos a CSV
 */
export function convertirACSV(datos: any[], encabezados: string[]): string {
  const filas = datos.map(fila => 
    encabezados.map(header => {
      const valor = fila[header];
      if (valor === null || valor === undefined) return '';
      if (typeof valor === 'string' && valor.includes(',')) {
        return `"${valor.replace(/"/g, '""')}"`;
      }
      return valor.toString();
    }).join(',')
  );
  
  return [encabezados.join(','), ...filas].join('\n');
}

/**
 * Descarga un archivo
 */
export function descargarArchivo(contenido: string | Blob, nombreArchivo: string, tipo: string = 'text/plain'): void {
  const blob = contenido instanceof Blob ? contenido : new Blob([contenido], { type: tipo });
  const url = URL.createObjectURL(blob);
  
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombreArchivo;
  enlace.style.display = 'none';
  
  document.body.appendChild(enlace);
  enlace.click();
  document.body.removeChild(enlace);
  
  URL.revokeObjectURL(url);
}

// ================================
// UTILIDADES DE ACCESIBILIDAD
// ================================

/**
 * Anuncia un mensaje a lectores de pantalla
 */
export function anunciarALectorPantalla(mensaje: string): void {
  const elemento = document.createElement('div');
  elemento.setAttribute('aria-live', 'polite');
  elemento.setAttribute('aria-atomic', 'true');
  elemento.style.position = 'absolute';
  elemento.style.left = '-10000px';
  elemento.style.width = '1px';
  elemento.style.height = '1px';
  elemento.style.overflow = 'hidden';
  
  document.body.appendChild(elemento);
  elemento.textContent = mensaje;
  
  setTimeout(() => {
    if (elemento.parentNode) {
      elemento.parentNode.removeChild(elemento);
    }
  }, 1000);
}

// ================================
// UTILIDADES DE DEBOUNCE Y THROTTLE
// ================================

/**
 * Función debounce para optimizar renders
 */
export function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Función throttle para limitar frecuencia de llamadas
 */
export function throttle<T extends (...args: any[]) => void>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}