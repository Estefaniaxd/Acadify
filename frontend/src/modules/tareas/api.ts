import axios, { AxiosResponse } from 'axios';
import { API_BASE_URL } from '../../config/api.config';
import {
  Tarea,
  TareaDetallada,
  TareaCreate,
  EntregaTarea,
  EntregaTareaDetallada,
  EntregaTareaCreate,
  CalificacionResponse,
  Rubrica,
  RubricaCreate,
  FiltrosTarea,
  FiltrosEntrega,
  EstadoTarea,
  EstadoEntrega,
} from './types';

// Crear instancia PRIVADA de axios para este módulo (no global)
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

// Interceptor para agregar token de autenticación (solo para esta instancia)
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de respuesta (solo para esta instancia)
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorData = error.response?.data;
    console.error('❌ Error en API Tareas:', {
      status: error.response?.status,
      data: errorData,
      message: error.message,
      config: {
        method: error.config?.method,
        url: error.config?.url,
        headers: error.config?.headers,
      },
    });
    return Promise.reject(error);
  }
);

class ApiClientTareas {
  private baseURL: string;
  private tareasBaseURL: string;
  private axiosClient: typeof axiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = `${baseURL}/api/cursos/tareas`;
    this.tareasBaseURL = `${baseURL}/api/tareas`;
    this.axiosClient = axiosInstance;
  }

  // === MÉTODOS PARA TAREAS ===

  /**
   * Obtener todas las tareas de un curso
   * GET /api/cursos/tareas/{curso_id}/tareas
   */
  async obtenerTareasCurso(
    cursoId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<{ tareas: Tarea[]; total: number }> {
    const response = await this.axiosClient.get(
      `${this.baseURL}/${cursoId}/tareas`,
      { params: { limit, offset } }
    );
    return response.data;
  }

  /**
   * Crear una nueva tarea en un curso
   * POST /api/cursos/tareas/{curso_id}/tareas
   */
  async crearTarea(
    cursoId: string,
    tareaData: {
      titulo: string;
      descripcion?: string;
      fecha_limite: string;
      puntos_max?: number;
      tipo?: string;
      prioridad?: string;
    }
  ): Promise<Tarea> {
    const response = await this.axiosClient.post(
      `${this.baseURL}/${cursoId}/tareas`,
      tareaData
    );
    return response.data;
  }

  // === MÉTODOS PARA ENTREGAS ===

  async entregarTarea(
    tareaId: string,
    formData: FormData
  ): Promise<EntregaTarea> {
    const token = localStorage.getItem('access_token');

    console.log('🔍🔍🔍 ENTREGAR TAREA - RECIBIDO EN API CLIENT:');
    console.log(`  - Parámetro formData type: ${typeof formData}`);
    console.log(`  - constructor.name: ${formData?.constructor?.name}`);
    console.log(`  - instanceof FormData ANTES: ${formData instanceof FormData}`);

    // **NUEVA ESTRATEGIA**: Forzar que sea FormData
    // Si no es FormData, reconstruir
    let realFormData: FormData;

    if (formData instanceof FormData) {
      console.log('✅ Ya es FormData, usar directamente');
      realFormData = formData;
    } else {
      console.error('🚨 NO es FormData, reconstruyendo...');
      console.log('  - Contenido recibido:', formData);

      // Reconstruir FormData desde Object
      realFormData = new FormData();

      if (typeof formData === 'object' && formData !== null) {
        for (const [key, value] of Object.entries(formData)) {
          console.log(`    - Key: ${key}, Value type: ${typeof value}, instanceof File: ${value instanceof File}`);

          if (value instanceof File) {
            console.log(`      ✅ Agregando File: ${(value as File).name}`);
            realFormData.append(key, value);
          } else if (value instanceof Blob) {
            console.log(`      ✅ Agregando Blob`);
            realFormData.append(key, value);
          } else if (Array.isArray(value)) {
            console.log(`      ⚠️  Es Array, intentando extraer Files...`);
            // Si es array de Files, agregar cada uno
            for (const item of value) {
              if (item instanceof File) {
                realFormData.append(key, item);
              } else if (typeof item === 'object' && item.nombre) {
                // Es JSON metadata de un File, probablemente serializado
                console.log(`      ❌ Es JSON metadata, no es un File real:`, item);
              }
            }
          } else if (value !== null && value !== undefined) {
            console.log(`      ✅ Agregando string/primitivo: "${value}"`);
            realFormData.append(key, String(value));
          }
        }
      }
    }

    console.log('🔍 VERIFICAR FormData FINAL:');
    console.log(`  - instanceof FormData: ${realFormData instanceof FormData}`);

    // Debug: intentar iterar FormData
    try {
      let count = 0;
      for (const [key, value] of (realFormData as any).entries()) {
        console.log(`    - Entry ${count}: ${key} = ${value instanceof File ? `File(${(value as File).name})` : value}`);
        count++;
      }
      console.log(`  - Total entries: ${count}`);
    } catch (e) {
      console.log(`  - Error iterando: ${e}`);
    }

    return this._doFetch(tareaId, realFormData, token);
  }

  private async _doFetch(tareaId: string, formData: FormData, token: string | null): Promise<EntregaTarea> {
    const headers: Record<string, string> = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    console.log('🔍 FETCH CONFIG:');
    console.log(`  - URL: ${this.baseURL}/${tareaId}/entregar`);
    console.log(`  - Method: POST`);
    console.log(`  - Headers (pre-fetch):`, JSON.stringify(headers));
    console.log(`  - Body: FormData (${formData instanceof FormData ? 'YES' : 'NO'})`);

    const response = await fetch(
      `${this.baseURL}/${tareaId}/entregar`,
      {
        method: 'POST',
        headers,
        body: formData,
      }
    );

    console.log(`🔍 RESPONSE STATUS: ${response.status}`);
    const responseText = await response.text();
    console.log(`🔍 RESPONSE BODY (primeros 500 chars): ${responseText.substring(0, 500)}`);

    if (!response.ok) {
      let errorData = {};
      try {
        errorData = JSON.parse(responseText);
      } catch (e) {
        errorData = { raw: responseText };
      }
      console.error('❌ Error en entregarTarea:', { status: response.status, data: errorData });
      throw new Error(`HTTP ${response.status}: ${(errorData as any)?.detail || 'Error'}`);
    }

    return JSON.parse(responseText);
  }

  /**
   * Calificar una entrega con gamificación completa
   * PATCH /api/tareas/entregas/{entrega_id}/calificar
   */
  async calificarEntrega(
    entregaId: string,
    calificacionData: {
      calificacion: number;
      comentarios?: string;
    }
  ): Promise<CalificacionResponse> {
    const response = await this.axiosClient.patch(
      `${this.tareasBaseURL}/entregas/${entregaId}/calificar`,
      calificacionData
    );
    return response.data;
  }

  // === MÉTODOS LEGACY (MANTENER COMPATIBILIDAD) ===

  async obtenerTareasPorGrupo(
    grupoId: string,
    filtros?: Partial<FiltrosTarea> & { incluir_vencidas?: boolean }
  ): Promise<Tarea[]> {
    // Por ahora redirigir a obtenerTareasCurso
    // TODO: Implementar endpoint específico para grupos
    const params = new URLSearchParams();

    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response: AxiosResponse<Tarea[]> = await this.axiosClient.get(
      `${this.baseURL}/grupo/${grupoId}?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Subir un archivo para una entrega existente
   * POST /api/cursos/tareas/entregas/{entrega_id}/subir-archivo
   */
  async subirArchivoEntrega(
    entregaId: string,
    archivo: File
  ): Promise<{ archivo_url: string; metadata: any }> {
    const formData = new FormData();
    formData.append('archivo', archivo);

    const response = await this.axiosClient.post(
      `${this.tareasBaseURL}/entregas/${entregaId}/subir-archivo`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async obtenerTareasDocente(
    docenteId: string,
    soloActivas: boolean = true
  ): Promise<Tarea[]> {
    const response: AxiosResponse<Tarea[]> = await this.axiosClient.get(
      `${this.baseURL}/docente/${docenteId}?solo_activas=${soloActivas}`
    );
    return response.data;
  }

  async obtenerTarea(tareaId: string): Promise<TareaDetallada> {
    const response: AxiosResponse<TareaDetallada> = await this.axiosClient.get(
      `${this.baseURL}/${tareaId}`
    );
    return response.data;
  }

  async obtenerEntrega(entregaId: string): Promise<EntregaTareaDetallada> {
    const response: AxiosResponse<EntregaTareaDetallada> = await this.axiosClient.get(
      `${this.baseURL}/entregas/${entregaId}`
    );
    return response.data;
  }

  async cancelarEntrega(entregaId: string): Promise<{ success: boolean, message: string }> {
    const response: AxiosResponse<{ success: boolean, message: string }> = await this.axiosClient.delete(
      `${this.baseURL}/entregas/${entregaId}`
    );
    return response.data;
  }

  async actualizarTarea(
    tareaId: string,
    tareaData: Partial<TareaCreate>
  ): Promise<Tarea> {
    const response: AxiosResponse<Tarea> = await this.axiosClient.put(
      `${this.baseURL}/${tareaId}`,
      tareaData
    );
    return response.data;
  }

  async cambiarEstadoTarea(
    tareaId: string,
    nuevoEstado: EstadoTarea
  ): Promise<Tarea> {
    const response: AxiosResponse<Tarea> = await this.axiosClient.patch(
      `${this.baseURL}/${tareaId}/estado`,
      { nuevo_estado: nuevoEstado }
    );
    return response.data;
  }

  async obtenerEstadisticasTarea(tareaId: string): Promise<Record<string, unknown>> {
    const response: AxiosResponse<Record<string, unknown>> = await this.axiosClient.get(
      `${this.baseURL}/${tareaId}/estadisticas`
    );
    return response.data;
  }

  async eliminarTarea(tareaId: string): Promise<void> {
    await this.axiosClient.delete(`${this.baseURL}/${tareaId}`);
  }

  /**
   * Obtener todas las entregas de una tarea (para docentes)
   * GET /api/cursos/tareas/{tarea_id}/entregas
   */
  async obtenerEntregasTarea(
    tareaId: string,
    filtros?: {
      estado?: EstadoEntrega;
      solo_calificadas?: boolean;
      solo_pendientes?: boolean;
      pagina?: number;
      tamano_pagina?: number;
    }
  ): Promise<EntregaTarea[]> {
    const params = new URLSearchParams();
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response = await this.axiosClient.get(
      `${this.tareasBaseURL}/${tareaId}/entregas?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Generar retroalimentación individual con IA
   * POST /api/tareas/retroalimentacion-individual
   */
  async generarRetroalimentacionIndividual(
    entregaId: string,
    opciones?: {
      modelo?: string;
      nivel_detalle?: string;
      incluir_calificacion?: boolean;
    }
  ): Promise<{
    success: boolean;
    retroalimentacion: any;
    fecha_generacion: string;
  }> {
    const params = new URLSearchParams();
    params.append('entrega_id', entregaId);

    if (opciones?.modelo) {
      params.append('modelo', opciones.modelo);
    }
    if (opciones?.nivel_detalle) {
      params.append('nivel_detalle', opciones.nivel_detalle);
    }
    if (opciones?.incluir_calificacion !== undefined) {
      params.append('incluir_calificacion', String(opciones.incluir_calificacion));
    }

    const response = await this.axiosClient.post(
      `/api/retroalimentacion-individual?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Exportar reporte completo del curso en CSV
   * GET /api/cursos/tareas/{curso_id}/reporte/export
   */
  async exportarReporteCurso(cursoId: string): Promise<Blob> {
    const response = await this.axiosClient.get(
      `${this.baseURL}/${cursoId}/reporte/export`,
      {
        responseType: 'blob', // Importante para archivos
      }
    );
    return response.data;
  }
}

// Instancia singleton del cliente API
export const apiClientTareas = new ApiClientTareas();

// Exportar también la clase para casos específicos
export default ApiClientTareas;