import { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Examen, 
  PreguntaExamen, 
  BancoPregunta, 
  IntentoExamen,
  RespuestaEstudiante,
  EstadisticaExamen,
  FiltrosBancoPreguntas,
  FormularioExamen,
  FormularioPregunta
} from '../types';
import { evaluacionesService } from '../services/evaluacionesService';

// ================================
// HOOK PARA GESTIÓN DE EXÁMENES
// ================================

export interface UseExamenesOptions {
  filtros?: {
    estado?: string;
    tipo?: string;
    creado_por?: string;
    fecha_desde?: string;
    fecha_hasta?: string;
  };
  autoFetch?: boolean;
}

export function useExamenes(options: UseExamenesOptions = {}) {
  const { filtros, autoFetch = true } = options;
  const [examenes, setExamenes] = useState<Examen[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cargarExamenes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await evaluacionesService.obtenerExamenes(filtros);
      setExamenes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar exámenes');
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  const crearExamen = useCallback(async (examen: FormularioExamen): Promise<Examen> => {
    try {
      setError(null);
      const nuevoExamen = await evaluacionesService.crearExamen(examen);
      setExamenes(prev => [nuevoExamen, ...prev]);
      return nuevoExamen;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al crear examen';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const actualizarExamen = useCallback(async (
    examenId: string, 
    actualizacion: Partial<FormularioExamen>
  ): Promise<Examen> => {
    try {
      setError(null);
      const examenActualizado = await evaluacionesService.actualizarExamen(examenId, actualizacion);
      setExamenes(prev => prev.map(e => e.examen_id === examenId ? examenActualizado : e));
      return examenActualizado;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al actualizar examen';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const eliminarExamen = useCallback(async (examenId: string): Promise<void> => {
    try {
      setError(null);
      await evaluacionesService.eliminarExamen(examenId);
      setExamenes(prev => prev.filter(e => e.examen_id !== examenId));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al eliminar examen';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const cambiarEstado = useCallback(async (examenId: string, estado: string): Promise<void> => {
    try {
      setError(null);
      const examenActualizado = await evaluacionesService.cambiarEstadoExamen(examenId, estado);
      setExamenes(prev => prev.map(e => e.examen_id === examenId ? examenActualizado : e));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al cambiar estado';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const clonarExamen = useCallback(async (examenId: string, nuevoTitulo: string): Promise<Examen> => {
    try {
      setError(null);
      const examenClonado = await evaluacionesService.clonarExamen(examenId, nuevoTitulo);
      setExamenes(prev => [examenClonado, ...prev]);
      return examenClonado;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al clonar examen';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  useEffect(() => {
    if (autoFetch) {
      cargarExamenes();
    }
  }, [autoFetch, cargarExamenes]);

  const examenesFiltrados = useMemo(() => {
    if (!filtros) return examenes;
    
    return examenes.filter(examen => {
      if (filtros.estado && examen.estado_examen !== filtros.estado) return false;
      if (filtros.tipo && examen.tipo_examen !== filtros.tipo) return false;
      if (filtros.creado_por && examen.creado_por !== filtros.creado_por) return false;
      return true;
    });
  }, [examenes, filtros]);

  return {
    examenes: examenesFiltrados,
    loading,
    error,
    cargarExamenes,
    crearExamen,
    actualizarExamen,
    eliminarExamen,
    cambiarEstado,
    clonarExamen,
  };
}

// ================================
// HOOK PARA GESTIÓN DE UN EXAMEN ESPECÍFICO
// ================================

export function useExamen(examenId: string | null) {
  const [examen, setExamen] = useState<Examen | null>(null);
  const [preguntas, setPreguntas] = useState<PreguntaExamen[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cargarExamen = useCallback(async () => {
    if (!examenId) return;
    
    try {
      setLoading(true);
      setError(null);
      const [examenData, preguntasData] = await Promise.all([
        evaluacionesService.obtenerExamen(examenId),
        evaluacionesService.obtenerPreguntasExamen(examenId),
      ]);
      setExamen(examenData);
      setPreguntas(preguntasData.sort((a, b) => a.orden - b.orden));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar examen');
    } finally {
      setLoading(false);
    }
  }, [examenId]);

  const agregarPregunta = useCallback(async (pregunta: FormularioPregunta): Promise<PreguntaExamen> => {
    if (!examenId) throw new Error('No hay examen seleccionado');
    
    try {
      setError(null);
      const nuevaPregunta = await evaluacionesService.agregarPreguntaExamen(examenId, pregunta);
      setPreguntas(prev => [...prev, nuevaPregunta].sort((a, b) => a.orden - b.orden));
      return nuevaPregunta;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al agregar pregunta';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [examenId]);

  const actualizarPregunta = useCallback(async (
    preguntaId: string, 
    actualizacion: Partial<FormularioPregunta>
  ): Promise<PreguntaExamen> => {
    if (!examenId) throw new Error('No hay examen seleccionado');
    
    try {
      setError(null);
      const preguntaActualizada = await evaluacionesService.actualizarPreguntaExamen(
        examenId, 
        preguntaId, 
        actualizacion
      );
      setPreguntas(prev => prev.map(p => 
        p.pregunta_id === preguntaId ? preguntaActualizada : p
      ));
      return preguntaActualizada;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al actualizar pregunta';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [examenId]);

  const eliminarPregunta = useCallback(async (preguntaId: string): Promise<void> => {
    if (!examenId) throw new Error('No hay examen seleccionado');
    
    try {
      setError(null);
      await evaluacionesService.eliminarPreguntaExamen(examenId, preguntaId);
      setPreguntas(prev => prev.filter(p => p.pregunta_id !== preguntaId));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al eliminar pregunta';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [examenId]);

  const reordenarPreguntas = useCallback(async (nuevoOrden: { pregunta_id: string; orden: number }[]): Promise<void> => {
    if (!examenId) throw new Error('No hay examen seleccionado');
    
    try {
      setError(null);
      await evaluacionesService.reordenarPreguntasExamen(examenId, nuevoOrden);
      setPreguntas(prev => {
        const preguntasActualizadas = [...prev];
        nuevoOrden.forEach(({ pregunta_id, orden }) => {
          const pregunta = preguntasActualizadas.find(p => p.pregunta_id === pregunta_id);
          if (pregunta) {
            pregunta.orden = orden;
          }
        });
        return preguntasActualizadas.sort((a, b) => a.orden - b.orden);
      });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al reordenar preguntas';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [examenId]);

  const importarPreguntasDeBanco = useCallback(async (
    preguntasIds: string[],
    configuracion?: { puntuacion?: number; randomizar?: boolean }
  ): Promise<PreguntaExamen[]> => {
    if (!examenId) throw new Error('No hay examen seleccionado');
    
    try {
      setError(null);
      const preguntasImportadas = await evaluacionesService.importarPreguntasDeBanco(
        examenId, 
        preguntasIds, 
        configuracion
      );
      setPreguntas(prev => [...prev, ...preguntasImportadas].sort((a, b) => a.orden - b.orden));
      return preguntasImportadas;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al importar preguntas';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [examenId]);

  useEffect(() => {
    cargarExamen();
  }, [cargarExamen]);

  return {
    examen,
    preguntas,
    loading,
    error,
    cargarExamen,
    agregarPregunta,
    actualizarPregunta,
    eliminarPregunta,
    reordenarPreguntas,
    importarPreguntasDeBanco,
  };
}

// ================================
// HOOK PARA BANCO DE PREGUNTAS
// ================================

// Datos mock como fallback
const preguntasMock: BancoPregunta[] = [
  {
    pregunta_id: '1',
    titulo: 'Pregunta de Matemáticas',
    descripcion: 'Resuelve la siguiente ecuación: 2x + 4 = 8',
    tipo_pregunta: 'OPCION_MULTIPLE',
    dificultad: 'MEDIO',
    materia: 'Matemáticas',
    tema: 'Álgebra',
    categoria: 'Ecuaciones',
    nivel_educativo: 'Secundaria',
    opciones_respuesta: [
      { id: 'opt1_1', texto: 'x = 2', es_correcta: true },
      { id: 'opt1_2', texto: 'x = 3', es_correcta: false },
      { id: 'opt1_3', texto: 'x = 4', es_correcta: false }
    ],
    respuesta_correcta: { opcion: 0 },
    creado_por: 'profesor1',
    fecha_creacion: new Date().toISOString(),
    fecha_actualizacion: new Date().toISOString(),
    es_publica: true,
    puntuacion_sugerida: 10,
    veces_utilizada: 5,
    estado_revision: 'aprobada',
    tags: ['álgebra', 'ecuaciones']
  },
  {
    pregunta_id: '2',
    titulo: 'Pregunta de Historia',
    descripcion: '¿En qué año comenzó la Primera Guerra Mundial?',
    tipo_pregunta: 'OPCION_MULTIPLE',
    dificultad: 'FACIL',
    materia: 'Historia',
    tema: 'Siglo XX',
    categoria: 'Guerras Mundiales',
    nivel_educativo: 'Secundaria',
    opciones_respuesta: [
      { id: 'opt2_1', texto: '1914', es_correcta: true },
      { id: 'opt2_2', texto: '1916', es_correcta: false },
      { id: 'opt2_3', texto: '1912', es_correcta: false }
    ],
    respuesta_correcta: { opcion: 0 },
    creado_por: 'profesor2',
    fecha_creacion: new Date().toISOString(),
    fecha_actualizacion: new Date().toISOString(),
    es_publica: true,
    puntuacion_sugerida: 5,
    veces_utilizada: 12,
    estado_revision: 'aprobada',
    tags: ['guerra', 'historia mundial']
  }
];

export function useBancoPreguntas(filtros: FiltrosBancoPreguntas = {}) {
  const [preguntas, setPreguntas] = useState<BancoPregunta[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cargarPreguntas = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await evaluacionesService.obtenerBancoPreguntas(filtros);
      setPreguntas(data);
    } catch (err) {
      console.warn('Backend no disponible, usando datos mock:', err);
      setError('Modo offline - usando datos de ejemplo');
      setPreguntas(preguntasMock);
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  const buscarPreguntas = useCallback(async (
    query: string, 
    filtrosBusqueda?: Omit<FiltrosBancoPreguntas, 'busqueda'>
  ): Promise<BancoPregunta[]> => {
    try {
      setError(null);
      const resultados = await evaluacionesService.buscarPreguntasBanco(query, filtrosBusqueda);
      setPreguntas(resultados);
      return resultados;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error en la búsqueda';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const crearPregunta = useCallback(async (pregunta: Omit<FormularioPregunta, 'puntuacion'> & {
    materia: string;
    tema: string;
    categoria: string;
    nivel_educativo: string;
    es_publica: boolean;
  }): Promise<BancoPregunta> => {
    try {
      setError(null);
      const nuevaPregunta = await evaluacionesService.crearPreguntaBanco(pregunta);
      setPreguntas(prev => [nuevaPregunta, ...prev]);
      return nuevaPregunta;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al crear pregunta';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const actualizarPregunta = useCallback(async (
    preguntaId: string, 
    actualizacion: Partial<BancoPregunta>
  ): Promise<BancoPregunta> => {
    try {
      setError(null);
      const preguntaActualizada = await evaluacionesService.actualizarPreguntaBanco(preguntaId, actualizacion);
      setPreguntas(prev => prev.map(p => p.pregunta_id === preguntaId ? preguntaActualizada : p));
      return preguntaActualizada;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al actualizar pregunta';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const eliminarPregunta = useCallback(async (preguntaId: string): Promise<void> => {
    try {
      setError(null);
      await evaluacionesService.eliminarPreguntaBanco(preguntaId);
      setPreguntas(prev => prev.filter(p => p.pregunta_id !== preguntaId));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al eliminar pregunta';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  useEffect(() => {
    cargarPreguntas();
  }, [cargarPreguntas]);

  return {
    preguntas,
    loading,
    error,
    cargarPreguntas,
    buscarPreguntas,
    crearPregunta,
    actualizarPregunta,
    eliminarPregunta,
  };
}

// ================================
// HOOK PARA TOMAR UN EXAMEN
// ================================

export function useTomarExamen(examenId: string) {
  const [intento, setIntento] = useState<IntentoExamen | null>(null);
  const [preguntasExamen, setPreguntasExamen] = useState<PreguntaExamen[]>([]);
  const [respuestas, setRespuestas] = useState<Map<string, RespuestaEstudiante>>(new Map());
  const [preguntaActual, setPreguntaActual] = useState(0);
  const [tiempoRestante, setTiempoRestante] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const iniciarIntento = useCallback(async (contraseña?: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      const [intentoData, preguntasData] = await Promise.all([
        evaluacionesService.iniciarIntento(examenId, contraseña),
        evaluacionesService.obtenerPreguntasExamen(examenId),
      ]);
      setIntento(intentoData);
      setPreguntasExamen(preguntasData.sort((a, b) => a.orden - b.orden));
      
      // Cargar respuestas existentes si es un intento continuado
      if (intentoData.estado_intento === 'EN_PROGRESO') {
        const respuestasData = await evaluacionesService.obtenerRespuestasIntento(intentoData.intento_id);
        const respuestasMap = new Map();
        respuestasData.forEach(resp => {
          respuestasMap.set(resp.pregunta_id, resp);
        });
        setRespuestas(respuestasMap);
        setPreguntaActual(intentoData.pregunta_actual - 1);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar intento');
    } finally {
      setLoading(false);
    }
  }, [examenId]);

  const enviarRespuesta = useCallback(async (
    preguntaId: string, 
    respuesta: Record<string, any> | string
  ): Promise<void> => {
    if (!intento) throw new Error('No hay intento activo');
    
    try {
      setError(null);
      const respuestaGuardada = await evaluacionesService.enviarRespuesta(
        intento.intento_id, 
        preguntaId, 
        respuesta
      );
      setRespuestas(prev => new Map(prev.set(preguntaId, respuestaGuardada)));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al enviar respuesta';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [intento]);

  const finalizarIntento = useCallback(async (forzar: boolean = false): Promise<IntentoExamen> => {
    if (!intento) throw new Error('No hay intento activo');
    
    try {
      setError(null);
      const intentoFinalizado = await evaluacionesService.finalizarIntento(intento.intento_id, forzar);
      setIntento(intentoFinalizado);
      return intentoFinalizado;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al finalizar intento';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [intento]);

  const navegarPregunta = useCallback((indice: number) => {
    if (indice >= 0 && indice < preguntasExamen.length) {
      setPreguntaActual(indice);
    }
  }, [preguntasExamen.length]);

  const siguientePregunta = useCallback(() => {
    navegarPregunta(preguntaActual + 1);
  }, [preguntaActual, navegarPregunta]);

  const preguntaAnterior = useCallback(() => {
    navegarPregunta(preguntaActual - 1);
  }, [preguntaActual, navegarPregunta]);

  // Timer para tiempo restante
  useEffect(() => {
    if (!intento || intento.estado_intento !== 'EN_PROGRESO') {
      setTiempoRestante(null);
      return;
    }

    const calcularTiempoRestante = () => {
      const inicioTime = new Date(intento.fecha_inicio).getTime();
      const tiempoLimiteMs = intento.tiempo_total_segundos ? 
        intento.tiempo_total_segundos * 1000 : 
        preguntasExamen.length * 30 * 60 * 1000; // 30 min por pregunta por defecto
      
      const tiempoTranscurrido = Date.now() - inicioTime;
      const restante = Math.max(0, tiempoLimiteMs - tiempoTranscurrido);
      
      if (restante === 0) {
        finalizarIntento(true); // Forzar finalización por tiempo
      }
      
      return Math.floor(restante / 1000);
    };

    const interval = setInterval(() => {
      setTiempoRestante(calcularTiempoRestante());
    }, 1000);

    // Calcular tiempo inicial
    setTiempoRestante(calcularTiempoRestante());

    return () => clearInterval(interval);
  }, [intento, preguntasExamen.length, finalizarIntento]);

  const preguntaActualData = useMemo(() => {
    return preguntasExamen[preguntaActual] || null;
  }, [preguntasExamen, preguntaActual]);

  const respuestaActual = useMemo(() => {
    if (!preguntaActualData) return null;
    return respuestas.get(preguntaActualData.pregunta_id) || null;
  }, [preguntaActualData, respuestas]);

  const progreso = useMemo(() => {
    const respondidas = Array.from(respuestas.keys()).length;
    const total = preguntasExamen.length;
    return {
      respondidas,
      total,
      porcentaje: total > 0 ? Math.round((respondidas / total) * 100) : 0,
    };
  }, [respuestas, preguntasExamen.length]);

  return {
    intento,
    preguntasExamen,
    preguntaActual: preguntaActualData,
    respuestaActual,
    respuestas,
    indicePreguntaActual: preguntaActual,
    tiempoRestante,
    progreso,
    loading,
    error,
    iniciarIntento,
    enviarRespuesta,
    finalizarIntento,
    navegarPregunta,
    siguientePregunta,
    preguntaAnterior,
  };
}

// ================================
// HOOK PARA ESTADÍSTICAS
// ================================

export function useEstadisticas(examenId: string | null) {
  const [estadisticas, setEstadisticas] = useState<EstadisticaExamen | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cargarEstadisticas = useCallback(async () => {
    if (!examenId) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await evaluacionesService.obtenerEstadisticasExamen(examenId);
      setEstadisticas(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  }, [examenId]);

  useEffect(() => {
    cargarEstadisticas();
  }, [cargarEstadisticas]);

  return {
    estadisticas,
    loading,
    error,
    cargarEstadisticas,
  };
}