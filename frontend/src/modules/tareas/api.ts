import axios, { AxiosResponse } from 'axios';
import {
  Tarea,
  TareaDetallada,
  TareaCreate,
  EntregaTarea,
  EntregaTareaDetallada,
  EntregaTareaCreate,
  CalificarEntrega,
  CalificacionResponse,
  Rubrica,
  RubricaCreate,
  FiltrosTarea,
  FiltrosEntrega,
  EstadoTarea,
  EstadoEntrega,
} from './types';

// Configuración base del cliente API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClientTareas {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = `${baseURL}/api/cursos/tareas`;
    
    // Interceptor para agregar token de autenticación
    axios.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para manejar errores de respuesta
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('Error en API Tareas:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
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
    const response = await axios.get(
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
      descripcion: string;
      fecha_limite: string;
      puntos_max?: number;
    }
  ): Promise<Tarea> {
    const response = await axios.post(
      `${this.baseURL}/${cursoId}/tareas`,
      tareaData
    );
    return response.data;
  }

  // === MÉTODOS PARA ENTREGAS ===

  /**
   * Entregar una tarea
   * POST /api/cursos/tareas/tareas/{tarea_id}/entregar
   */
  async entregarTarea(
    tareaId: string,
    entregaData: {
      contenido: string;
      archivos?: string;
    }
  ): Promise<EntregaTarea> {
    const response = await axios.post(
      `${this.baseURL}/tareas/${tareaId}/entregar`,
      entregaData
    );
    return response.data;
  }

  /**
   * Calificar una entrega con gamificación completa
   * POST /api/cursos/tareas/entregas/{entrega_id}/calificar
   */
  async calificarEntrega(
    entregaId: string,
    calificacionData: {
      calificacion: number;
      comentarios?: string;
    }
  ): Promise<CalificacionResponse> {
    const response = await axios.post(
      `${this.baseURL}/entregas/${entregaId}/calificar`,
      calificacionData
    );
    return response.data;
  }

  // === MÉTODOS LEGACY (MANTENER COMPATIBILIDAD) ===

  async obtenerTareasGrupo(
    grupoId: string, 
    filtros?: Partial<FiltrosTarea>
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

    const response: AxiosResponse<Tarea[]> = await axios.get(
      `${this.baseURL}/grupo/${grupoId}?${params.toString()}`
    );
    return response.data;
  }

  async obtenerTareasDocente(
    docenteId: string, 
    soloActivas: boolean = true
  ): Promise<Tarea[]> {
    const response: AxiosResponse<Tarea[]> = await axios.get(
      `${this.baseURL}/docente/${docenteId}?solo_activas=${soloActivas}`
    );
    return response.data;
  }

  async obtenerTarea(tareaId: string): Promise<TareaDetallada> {
    const response: AxiosResponse<TareaDetallada> = await axios.get(
      `${this.baseURL}/${tareaId}`
    );
    return response.data;
  }

  async actualizarTarea(
    tareaId: string, 
    tareaData: Partial<TareaCreate>
  ): Promise<Tarea> {
    const response: AxiosResponse<Tarea> = await axios.put(
      `${this.baseURL}/${tareaId}`,
      tareaData
    );
    return response.data;
  }

  async cambiarEstadoTarea(
    tareaId: string, 
    nuevoEstado: EstadoTarea
  ): Promise<Tarea> {
    const response: AxiosResponse<Tarea> = await axios.patch(
      `${this.baseURL}/${tareaId}/estado`,
      { nuevo_estado: nuevoEstado }
    );
    return response.data;
  }

  async obtenerEstadisticasTarea(tareaId: string): Promise<Record<string, unknown>> {
    const response: AxiosResponse<Record<string, unknown>> = await axios.get(
      `${this.baseURL}/${tareaId}/estadisticas`
    );
    return response.data;
  }

  async eliminarTarea(tareaId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/${tareaId}`);
  }
}

// Instancia singleton del cliente API
export const apiClientTareas = new ApiClientTareas();

// Exportar también la clase para casos específicos
export default ApiClientTareas;