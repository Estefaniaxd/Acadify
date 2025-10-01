import axios, { AxiosResponse } from 'axios';
import {
  Tarea,
  TareaDetallada,
  TareaCreate,
  EntregaTarea,
  EntregaTareaDetallada,
  EntregaTareaCreate,
  CalificarEntrega,
  Rubrica,
  RubricaCreate,
  FiltrosTarea,
  FiltrosEntrega,
  EstadoTarea,
  EstadoEntrega,
} from './types';

// Configuración base del cliente API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiClientTareas {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = `${baseURL}/tareas`;
    
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

  async crearTarea(tareaData: TareaCreate): Promise<Tarea> {
    const response: AxiosResponse<Tarea> = await axios.post(
      `${this.baseURL}/`,
      tareaData
    );
    return response.data;
  }

  async obtenerTareasGrupo(
    grupoId: string, 
    filtros?: Partial<FiltrosTarea>
  ): Promise<Tarea[]> {
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

  async obtenerEstadisticasTarea(tareaId: string): Promise<any> {
    const response: AxiosResponse<any> = await axios.get(
      `${this.baseURL}/${tareaId}/estadisticas`
    );
    return response.data;
  }

  async eliminarTarea(tareaId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/${tareaId}`);
  }

  // === MÉTODOS PARA ENTREGAS ===

  async crearEntrega(
    tareaId: string, 
    entregaData: EntregaTareaCreate
  ): Promise<EntregaTarea> {
    const response: AxiosResponse<EntregaTarea> = await axios.post(
      `${this.baseURL}/${tareaId}/entregas`,
      entregaData
    );
    return response.data;
  }

  async subirArchivoEntrega(
    entregaId: string, 
    archivo: File
  ): Promise<{ mensaje: string; archivo_url: string }> {
    const formData = new FormData();
    formData.append('archivo', archivo);

    const response: AxiosResponse<{ mensaje: string; archivo_url: string }> = 
      await axios.post(
        `${this.baseURL}/entregas/${entregaId}/subir-archivo`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
    return response.data;
  }

  async entregarTarea(entregaId: string): Promise<EntregaTarea> {
    const response: AxiosResponse<EntregaTarea> = await axios.patch(
      `${this.baseURL}/entregas/${entregaId}/entregar`
    );
    return response.data;
  }

  async calificarEntrega(
    entregaId: string, 
    calificacionData: CalificarEntrega
  ): Promise<EntregaTarea> {
    const response: AxiosResponse<EntregaTarea> = await axios.patch(
      `${this.baseURL}/entregas/${entregaId}/calificar`,
      calificacionData
    );
    return response.data;
  }

  async obtenerEntregasTarea(
    tareaId: string, 
    filtros?: Partial<FiltrosEntrega>
  ): Promise<EntregaTarea[]> {
    const params = new URLSearchParams();
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response: AxiosResponse<EntregaTarea[]> = await axios.get(
      `${this.baseURL}/${tareaId}/entregas?${params.toString()}`
    );
    return response.data;
  }

  async obtenerEntrega(entregaId: string): Promise<EntregaTareaDetallada> {
    const response: AxiosResponse<EntregaTareaDetallada> = await axios.get(
      `${this.baseURL}/entregas/${entregaId}`
    );
    return response.data;
  }

  // === MÉTODOS PARA RÚBRICAS ===

  async crearRubrica(rubricaData: RubricaCreate): Promise<Rubrica> {
    const response: AxiosResponse<Rubrica> = await axios.post(
      `${this.baseURL}/rubricas`,
      rubricaData
    );
    return response.data;
  }

  async obtenerRubricas(incluirPublicas: boolean = true): Promise<Rubrica[]> {
    const response: AxiosResponse<Rubrica[]> = await axios.get(
      `${this.baseURL}/rubricas?incluir_publicas=${incluirPublicas}`
    );
    return response.data;
  }

  async obtenerRubricasPublicas(): Promise<Rubrica[]> {
    const response: AxiosResponse<Rubrica[]> = await axios.get(
      `${this.baseURL}/rubricas/publicas`
    );
    return response.data;
  }

  async duplicarRubrica(
    rubricaId: string, 
    nuevoNombre: string
  ): Promise<Rubrica> {
    const response: AxiosResponse<Rubrica> = await axios.post(
      `${this.baseURL}/rubricas/${rubricaId}/duplicar`,
      { nuevo_nombre: nuevoNombre }
    );
    return response.data;
  }

  // === MÉTODOS DE UTILIDAD ===

  async buscarTareas(
    busqueda: string, 
    grupoId?: string
  ): Promise<Tarea[]> {
    const filtros: Partial<FiltrosTarea> = {
      busqueda,
      grupo_id: grupoId,
      solo_activas: true,
    };

    if (grupoId) {
      return this.obtenerTareasGrupo(grupoId, filtros);
    } else {
      // Si no hay grupo específico, buscar en todas las tareas del docente actual
      // Esto requeriría obtener el ID del docente desde el contexto de autenticación
      throw new Error('Búsqueda global no implementada aún');
    }
  }

  async obtenerTareasPorEstado(
    estado: EstadoTarea, 
    grupoId?: string
  ): Promise<Tarea[]> {
    const filtros: Partial<FiltrosTarea> = {
      estado,
      grupo_id: grupoId,
      solo_activas: true,
    };

    if (grupoId) {
      return this.obtenerTareasGrupo(grupoId, filtros);
    } else {
      throw new Error('Filtrado por estado global no implementado aún');
    }
  }

  async obtenerEntregasPendientes(tareaId?: string): Promise<EntregaTarea[]> {
    const filtros: Partial<FiltrosEntrega> = {
      solo_pendientes: true,
      tarea_id: tareaId,
    };

    if (tareaId) {
      return this.obtenerEntregasTarea(tareaId, filtros);
    } else {
      throw new Error('Obtener entregas pendientes globales no implementado aún');
    }
  }

  // === MÉTODOS PARA ESTADÍSTICAS ===

  async obtenerResumenTareas(grupoId: string): Promise<{
    total: number;
    activas: number;
    vencidas: number;
    completadas: number;
  }> {
    try {
      const tareas = await this.obtenerTareasGrupo(grupoId);
      
      const total = tareas.length;
      const activas = tareas.filter(t => t.estado === EstadoTarea.PUBLICADA || t.estado === EstadoTarea.EN_PROGRESO).length;
      const vencidas = tareas.filter(t => t.esta_vencida).length;
      const completadas = tareas.filter(t => t.estado === EstadoTarea.CERRADA).length;

      return { total, activas, vencidas, completadas };
    } catch (error) {
      console.error('Error obteniendo resumen de tareas:', error);
      return { total: 0, activas: 0, vencidas: 0, completadas: 0 };
    }
  }

  async obtenerResumenEntregas(tareaId: string): Promise<{
    total: number;
    calificadas: number;
    pendientes: number;
    tardias: number;
  }> {
    try {
      const entregas = await this.obtenerEntregasTarea(tareaId);
      
      const total = entregas.filter(e => e.estado !== EstadoEntrega.BORRADOR).length;
      const calificadas = entregas.filter(e => e.calificacion !== null && e.calificacion !== undefined).length;
      const pendientes = entregas.filter(e => e.estado === EstadoEntrega.ENVIADA && !e.calificacion).length;
      const tardias = entregas.filter(e => e.es_entrega_tardia).length;

      return { total, calificadas, pendientes, tardias };
    } catch (error) {
      console.error('Error obteniendo resumen de entregas:', error);
      return { total: 0, calificadas: 0, pendientes: 0, tardias: 0 };
    }
  }
}

// Instancia singleton del cliente API
export const apiClientTareas = new ApiClientTareas();

// Exportar también la clase para casos específicos
export default ApiClientTareas;