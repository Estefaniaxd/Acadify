import axios, { AxiosInstance } from 'axios';

/**
 * 🚀 Servicio IA - Integración con Google Gemini
 * 
 * Proporciona acceso a los endpoints reales de retroalimentación:
 * - POST /ia/retroalimentacion-tareas - Retroalimentación individual
 * - POST /ia/retroalimentacion-masiva - Retroalimentación bulk
 * - GET /ia/retroalimentacion/{entrega_id} - Obtener existente
 * - GET /ia/modelos - Listar modelos disponibles
 */

// ============================================================================
// TIPOS
// ============================================================================

export interface RetroalimentacionIAData {
  retroalimentacion_texto: string;
  fortalezas: string[];
  areas_mejora: string[];
  recursos_recomendados: string[];
  calificacion_sugerida?: number;
  razonamiento_calificacion?: string;
  modelo_usado: string;
  nivel_profundidad: string;
  tokens_usados: number;
  confianza: number;
  metadata?: Record<string, any>;
}

export interface RetroalimentacionResponse {
  entrega_id: string;
  tarea_id: string;
  retroalimentacion?: RetroalimentacionIAData;
  fecha_generacion?: string;
}

export interface RetroalimentacionRequest {
  entrega_id: string;
  modelo?: string;
  nivel_detalle?: 'basico' | 'medio' | 'completo';
  incluir_calificacion?: boolean;
}

export interface BulkRetroalimentacionRequest {
  entrega_ids: string[];
  modelo?: string;
  nivel_detalle?: 'basico' | 'medio' | 'completo';
  incluir_calificacion?: boolean;
  notificar_estudiantes?: boolean;
}

export interface BulkRetroalimentacionResponse {
  job_id: string;
  total_entregas: number;
  estado: 'procesando' | 'completado' | 'error';
  progreso?: number;
}

export interface ModeloIAInfo {
  nombre: string;
  descripcion: string;
  costo_entrada: number;
  costo_salida: number;
  velocidad: 'rapido' | 'normal' | 'lento';
  capaz_multimedia: boolean;
}

// ============================================================================
// SERVICIO
// ============================================================================

class IAService {
  private apiClient: AxiosInstance;

  constructor() {
    this.apiClient = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - Agregar token JWT
    this.apiClient.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor - Manejo de errores
    this.apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('❌ IA API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  /**
   * 🚀 Generar retroalimentación INDIVIDUAL para una entrega
   * 
   * POST /ia/retroalimentacion-tareas
   * 
   * Flujo:
   * 1. Backend obtiene entrega y archivos
   * 2. Envía a Google Gemini
   * 3. Almacena resultado en BD
   * 4. Retorna retroalimentación al profesor
   * 
   * @param entregaId ID de la entrega del estudiante
   * @param modelo Modelo IA (gemini-2.5-flash por defecto)
   * @param nivelDetalle Nivel: 'basico', 'medio' o 'completo'
   * @param incluirCalificacion Si incluir calificación sugerida
   * @returns Retroalimentación generada
   */
  async generarRetroalimentacionIndividual(
    entregaId: string,
    modelo: string = 'gemini-2.5-flash',
    nivelDetalle: 'basico' | 'medio' | 'completo' = 'completo',
    incluirCalificacion: boolean = true
  ): Promise<RetroalimentacionResponse> {
    try {
      console.log(`🚀 Generando retroalimentación para entrega: ${entregaId}`);

      const request: RetroalimentacionRequest = {
        entrega_id: entregaId,
        modelo,
        nivel_detalle: nivelDetalle,
        incluir_calificacion: incluirCalificacion,
      };

      const response = await this.apiClient.post<RetroalimentacionResponse>(
        '/ia/retroalimentacion-tareas',
        request
      );

      console.log(`✅ Retroalimentación generada exitosamente`, response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error generando retroalimentación:', error);
      throw error;
    }
  }

  /**
   * 🚀 Generar retroalimentación MASIVA para múltiples entregas
   * 
   * POST /ia/retroalimentacion-masiva
   * 
   * Retorna inmediatamente con job_id y procesa en background
   * 
   * @param entregaIds IDs de entregas a procesar
   * @param modelo Modelo IA
   * @param nivelDetalle Nivel de análisis
   * @param incluirCalificacion Si incluir calificación sugerida
   * @param notificarEstudiantes Enviar notificación al completar
   * @returns job_id para tracking del progreso
   */
  async generarRetroalimentacionMasiva(
    entregaIds: string[],
    modelo: string = 'gemini-2.5-flash',
    nivelDetalle: 'basico' | 'medio' | 'completo' = 'completo',
    incluirCalificacion: boolean = true,
    notificarEstudiantes: boolean = true
  ): Promise<BulkRetroalimentacionResponse> {
    try {
      console.log(`🚀 Iniciando retroalimentación MASIVA para ${entregaIds.length} entregas`);

      const request: BulkRetroalimentacionRequest = {
        entrega_ids: entregaIds,
        modelo,
        nivel_detalle: nivelDetalle,
        incluir_calificacion: incluirCalificacion,
        notificar_estudiantes: notificarEstudiantes,
      };

      const response = await this.apiClient.post<BulkRetroalimentacionResponse>(
        '/ia/retroalimentacion-masiva',
        request
      );

      console.log(`✅ Proceso masivo iniciado. Job ID: ${response.data.job_id}`);
      return response.data;
    } catch (error) {
      console.error('❌ Error iniciando retroalimentación masiva:', error);
      throw error;
    }
  }

  /**
   * � Obtener estado de un job masivo
   *
   * GET /ia/retroalimentacion-masiva/{job_id}
   */
  async obtenerEstadoJobMasivo(jobId: string): Promise<any> {
    try {
      console.log(`📡 Consultando estado del job: ${jobId}`);
      const response = await this.apiClient.get(`/ia/retroalimentacion-masiva/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('❌ Error consultando estado de job:', error);
      throw error;
    }
  }

  /**
   * �📥 Obtener retroalimentación existente de una entrega
   * 
   * GET /ia/retroalimentacion/{entrega_id}
   * 
   * @param entregaId ID de la entrega
   * @returns Retroalimentación guardada o null si no existe
   */
  async obtenerRetroalimentacion(entregaId: string): Promise<RetroalimentacionResponse | null> {
    try {
      console.log(`📥 Obteniendo retroalimentación de entrega: ${entregaId}`);

      const response = await this.apiClient.get<RetroalimentacionResponse>(
        `/ia/retroalimentacion/${entregaId}`
      );

      console.log(`✅ Retroalimentación obtenida`, response.data);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        console.log('📭 No hay retroalimentación para esta entrega');
        return null;
      }
      console.error('❌ Error obteniendo retroalimentación:', error);
      throw error;
    }
  }

  /**
   * 📋 Listar modelos IA disponibles
   * 
   * GET /ia/modelos
   * 
   * @returns Lista de modelos con información de costo y velocidad
   */
  async listarModelos(): Promise<ModeloIAInfo[]> {
    try {
      console.log('📋 Obteniendo modelos IA disponibles...');

      const response = await this.apiClient.get<ModeloIAInfo[]>('/ia/modelos');

      console.log(`✅ ${response.data.length} modelos disponibles:`, response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error obteniendo modelos:', error);
      throw error;
    }
  }

  /**
   * ✅ Verificar si una entrega tiene retroalimentación
   * 
   * @param entregaId ID de la entrega
   * @returns true si tiene retroalimentación, false si no
   */
  async tieneRetroalimentacion(entregaId: string): Promise<boolean> {
    try {
      const resultado = await this.obtenerRetroalimentacion(entregaId);
      return resultado !== null && resultado.retroalimentacion !== undefined;
    } catch (error) {
      return false;
    }
  }
}

// ============================================================================
// INSTANCIA GLOBAL
// ============================================================================

export const iaService = new IAService();
