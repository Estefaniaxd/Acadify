import { 
  Examen, 
  PreguntaExamen, 
  BancoPregunta, 
  IntentoExamen, 
  RespuestaEstudiante,
  EstadisticaExamen,
  ConfiguracionEvaluacion,
  FormularioExamen,
  FormularioPregunta,
  FiltrosBancoPreguntas,
  DashboardEstadisticas
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class EvaluacionesService {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}/api/v1${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      (config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // ================================
  // CONFIGURACIÓN DE EVALUACIONES
  // ================================
  
  async obtenerConfiguracion(): Promise<ConfiguracionEvaluacion> {
    return this.request<ConfiguracionEvaluacion>('/evaluaciones/configuracion');
  }

  async actualizarConfiguracion(config: Partial<ConfiguracionEvaluacion>): Promise<ConfiguracionEvaluacion> {
    return this.request<ConfiguracionEvaluacion>('/evaluaciones/configuracion', {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  // ================================
  // GESTIÓN DE EXÁMENES
  // ================================
  
  async obtenerExamenes(filtros?: {
    estado?: string;
    tipo?: string;
    creado_por?: string;
    fecha_desde?: string;
    fecha_hasta?: string;
  }): Promise<Examen[]> {
    const params = new URLSearchParams();
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    
    const query = params.toString();
    return this.request<Examen[]>(`/evaluaciones/examenes${query ? `?${query}` : ''}`);
  }

  async obtenerExamen(examenId: string): Promise<Examen> {
    return this.request<Examen>(`/evaluaciones/examenes/${examenId}`);
  }

  async crearExamen(examen: FormularioExamen): Promise<Examen> {
    return this.request<Examen>('/evaluaciones/examenes', {
      method: 'POST',
      body: JSON.stringify(examen),
    });
  }

  async actualizarExamen(examenId: string, examen: Partial<FormularioExamen>): Promise<Examen> {
    return this.request<Examen>(`/evaluaciones/examenes/${examenId}`, {
      method: 'PUT',
      body: JSON.stringify(examen),
    });
  }

  async eliminarExamen(examenId: string): Promise<void> {
    return this.request<void>(`/evaluaciones/examenes/${examenId}`, {
      method: 'DELETE',
    });
  }

  async cambiarEstadoExamen(examenId: string, estado: string): Promise<Examen> {
    return this.request<Examen>(`/evaluaciones/examenes/${examenId}/estado`, {
      method: 'PATCH',
      body: JSON.stringify({ estado }),
    });
  }

  async clonarExamen(examenId: string, nuevoTitulo: string): Promise<Examen> {
    return this.request<Examen>(`/evaluaciones/examenes/${examenId}/clonar`, {
      method: 'POST',
      body: JSON.stringify({ titulo: nuevoTitulo }),
    });
  }

  // ================================
  // GESTIÓN DE PREGUNTAS DE EXAMEN
  // ================================
  
  async obtenerPreguntasExamen(examenId: string): Promise<PreguntaExamen[]> {
    return this.request<PreguntaExamen[]>(`/evaluaciones/examenes/${examenId}/preguntas`);
  }

  async agregarPreguntaExamen(examenId: string, pregunta: FormularioPregunta): Promise<PreguntaExamen> {
    return this.request<PreguntaExamen>(`/evaluaciones/examenes/${examenId}/preguntas`, {
      method: 'POST',
      body: JSON.stringify(pregunta),
    });
  }

  async actualizarPreguntaExamen(
    examenId: string, 
    preguntaId: string, 
    pregunta: Partial<FormularioPregunta>
  ): Promise<PreguntaExamen> {
    return this.request<PreguntaExamen>(`/evaluaciones/examenes/${examenId}/preguntas/${preguntaId}`, {
      method: 'PUT',
      body: JSON.stringify(pregunta),
    });
  }

  async eliminarPreguntaExamen(examenId: string, preguntaId: string): Promise<void> {
    return this.request<void>(`/evaluaciones/examenes/${examenId}/preguntas/${preguntaId}`, {
      method: 'DELETE',
    });
  }

  async reordenarPreguntasExamen(examenId: string, ordenPreguntas: { pregunta_id: string; orden: number }[]): Promise<void> {
    return this.request<void>(`/evaluaciones/examenes/${examenId}/preguntas/reordenar`, {
      method: 'PUT',
      body: JSON.stringify({ orden_preguntas: ordenPreguntas }),
    });
  }

  async importarPreguntasDeBanco(
    examenId: string, 
    preguntasIds: string[],
    configuracion?: { puntuacion?: number; randomizar?: boolean }
  ): Promise<PreguntaExamen[]> {
    return this.request<PreguntaExamen[]>(`/evaluaciones/examenes/${examenId}/preguntas/importar`, {
      method: 'POST',
      body: JSON.stringify({ 
        preguntas_ids: preguntasIds,
        ...configuracion 
      }),
    });
  }

  // ================================
  // BANCO DE PREGUNTAS
  // ================================
  
  async obtenerBancoPreguntas(filtros?: FiltrosBancoPreguntas): Promise<BancoPregunta[]> {
    const params = new URLSearchParams();
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, String(value));
          }
        }
      });
    }
    
    const query = params.toString();
    return this.request<BancoPregunta[]>(`/evaluaciones/banco-preguntas${query ? `?${query}` : ''}`);
  }

  async obtenerPreguntaBanco(preguntaId: string): Promise<BancoPregunta> {
    return this.request<BancoPregunta>(`/evaluaciones/banco-preguntas/${preguntaId}`);
  }

  async crearPreguntaBanco(pregunta: Omit<FormularioPregunta, 'puntuacion'> & {
    materia: string;
    tema: string;
    categoria: string;
    nivel_educativo: string;
    es_publica: boolean;
  }): Promise<BancoPregunta> {
    return this.request<BancoPregunta>('/evaluaciones/banco-preguntas', {
      method: 'POST',
      body: JSON.stringify(pregunta),
    });
  }

  async actualizarPreguntaBanco(
    preguntaId: string, 
    pregunta: Partial<BancoPregunta>
  ): Promise<BancoPregunta> {
    return this.request<BancoPregunta>(`/evaluaciones/banco-preguntas/${preguntaId}`, {
      method: 'PUT',
      body: JSON.stringify(pregunta),
    });
  }

  async eliminarPreguntaBanco(preguntaId: string): Promise<void> {
    return this.request<void>(`/evaluaciones/banco-preguntas/${preguntaId}`, {
      method: 'DELETE',
    });
  }

  async buscarPreguntasBanco(
    query: string, 
    filtros?: Omit<FiltrosBancoPreguntas, 'busqueda'>
  ): Promise<BancoPregunta[]> {
    return this.request<BancoPregunta[]>('/evaluaciones/banco-preguntas/buscar', {
      method: 'POST',
      body: JSON.stringify({ query, ...filtros }),
    });
  }

  async obtenerMaterias(): Promise<string[]> {
    return this.request<string[]>('/evaluaciones/banco-preguntas/materias');
  }

  async obtenerTemasPorMateria(materia: string): Promise<string[]> {
    return this.request<string[]>(`/evaluaciones/banco-preguntas/materias/${materia}/temas`);
  }

  // ================================
  // GESTIÓN DE INTENTOS DE EXAMEN
  // ================================
  
  async iniciarIntento(examenId: string, contraseña?: string): Promise<IntentoExamen> {
    return this.request<IntentoExamen>(`/evaluaciones/examenes/${examenId}/iniciar-intento`, {
      method: 'POST',
      body: JSON.stringify({ contraseña }),
    });
  }

  async obtenerIntentoActivo(examenId: string): Promise<IntentoExamen | null> {
    return this.request<IntentoExamen | null>(`/evaluaciones/examenes/${examenId}/intento-activo`);
  }

  async obtenerIntento(intentoId: string): Promise<IntentoExamen> {
    return this.request<IntentoExamen>(`/evaluaciones/intentos/${intentoId}`);
  }

  async finalizarIntento(intentoId: string, forzar: boolean = false): Promise<IntentoExamen> {
    return this.request<IntentoExamen>(`/evaluaciones/intentos/${intentoId}/finalizar`, {
      method: 'POST',
      body: JSON.stringify({ forzar }),
    });
  }

  async abandonarIntento(intentoId: string): Promise<IntentoExamen> {
    return this.request<IntentoExamen>(`/evaluaciones/intentos/${intentoId}/abandonar`, {
      method: 'POST',
    });
  }

  async guardarProgreso(intentoId: string): Promise<void> {
    return this.request<void>(`/evaluaciones/intentos/${intentoId}/guardar-progreso`, {
      method: 'POST',
    });
  }

  // ================================
  // GESTIÓN DE RESPUESTAS
  // ================================
  
  async obtenerRespuestasIntento(intentoId: string): Promise<RespuestaEstudiante[]> {
    return this.request<RespuestaEstudiante[]>(`/evaluaciones/intentos/${intentoId}/respuestas`);
  }

  async enviarRespuesta(
    intentoId: string, 
    preguntaId: string, 
    respuesta: Record<string, any> | string
  ): Promise<RespuestaEstudiante> {
    return this.request<RespuestaEstudiante>(`/evaluaciones/intentos/${intentoId}/respuestas`, {
      method: 'POST',
      body: JSON.stringify({
        pregunta_id: preguntaId,
        respuesta: typeof respuesta === 'string' ? { texto: respuesta } : respuesta,
      }),
    });
  }

  async actualizarRespuesta(
    respuestaId: string, 
    respuesta: Record<string, any> | string
  ): Promise<RespuestaEstudiante> {
    return this.request<RespuestaEstudiante>(`/evaluaciones/respuestas/${respuestaId}`, {
      method: 'PUT',
      body: JSON.stringify({
        respuesta: typeof respuesta === 'string' ? { texto: respuesta } : respuesta,
      }),
    });
  }

  // ================================
  // ESTADÍSTICAS Y REPORTES
  // ================================
  
  async obtenerEstadisticasExamen(examenId: string): Promise<EstadisticaExamen> {
    return this.request<EstadisticaExamen>(`/evaluaciones/examenes/${examenId}/estadisticas`);
  }

  async obtenerDashboardEstadisticas(): Promise<DashboardEstadisticas> {
    return this.request<DashboardEstadisticas>('/evaluaciones/dashboard/estadisticas');
  }

  async obtenerReporteExamen(examenId: string, formato: 'pdf' | 'excel' = 'pdf'): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/v1/evaluaciones/examenes/${examenId}/reporte?formato=${formato}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Error al generar reporte');
    }

    return response.blob();
  }

  async obtenerIntentosExamen(
    examenId: string, 
    filtros?: {
      estado?: string;
      estudiante_id?: string;
      fecha_desde?: string;
      fecha_hasta?: string;
    }
  ): Promise<IntentoExamen[]> {
    const params = new URLSearchParams();
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    
    const query = params.toString();
    return this.request<IntentoExamen[]>(
      `/evaluaciones/examenes/${examenId}/intentos${query ? `?${query}` : ''}`
    );
  }

  // ================================
  // SISTEMA ANTI-TRAMPA
  // ================================
  
  async reportarEventoSospechoso(
    intentoId: string,
    tipoEvento: string,
    descripcion: string,
    datosAdicionales?: Record<string, any>
  ): Promise<void> {
    return this.request<void>(`/evaluaciones/intentos/${intentoId}/evento-sospechoso`, {
      method: 'POST',
      body: JSON.stringify({
        tipo_evento: tipoEvento,
        descripcion,
        datos_adicionales: datosAdicionales,
      }),
    });
  }

  async verificarIntegridad(intentoId: string): Promise<{
    es_valido: boolean;
    nivel_confianza: number;
    alertas: string[];
  }> {
    return this.request(`/evaluaciones/intentos/${intentoId}/verificar-integridad`);
  }

  // ================================
  // UTILIDADES
  // ================================
  
  async validarExamen(examen: FormularioExamen): Promise<{
    es_valido: boolean;
    errores: string[];
    advertencias: string[];
  }> {
    return this.request('/evaluaciones/utilidades/validar-examen', {
      method: 'POST',
      body: JSON.stringify(examen),
    });
  }

  async previsualizarExamen(examenId: string): Promise<{
    examen: Examen;
    preguntas: PreguntaExamen[];
    tiempo_estimado: number;
  }> {
    return this.request(`/evaluaciones/examenes/${examenId}/preview`);
  }
}

// Singleton instance
export const evaluacionesService = new EvaluacionesService();
export default evaluacionesService;