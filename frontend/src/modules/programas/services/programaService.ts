/**
 * Servicio de API para Programas Académicos
 * 
 * Maneja toda la comunicación con el backend para operaciones CRUD
 * de programas académicos.
 * 
 * @module programaService
 */

import axios from 'axios';
import type {
  Programa,
  CrearProgramaDTO,
  ActualizarProgramaDTO,
  FiltrosProgramas,
  RespuestaPaginada,
  EstadisticasPrograma,
  AsignarCursosDTO,
  MallaCurricular,
  EstadoPrograma
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BASE_URL = '/api/v1/academic/programas';

// Configuración de axios con interceptores
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Interceptor para agregar token de autorización
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejo global de errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Servicio centralizado para operaciones de programas
 * Implementa el patrón Service Layer
 */
export const programaService = {
  /**
   * Obtiene lista paginada de programas con filtros opcionales
   * 
   * @param filtros - Parámetros de búsqueda y filtrado
   * @returns Promesa con respuesta paginada de programas
   * 
   * @example
   * ```typescript
   * const programas = await programaService.getAll({
   *   institucionId: 1,
   *   nivel: 'PROFESIONAL',
   *   pagina: 1,
   *   limite: 10
   * });
   * ```
   */
  async getAll(filtros?: FiltrosProgramas): Promise<RespuestaPaginada<Programa>> {
    try {
      const params = new URLSearchParams();
      
      if (filtros?.busqueda) params.append('busqueda', filtros.busqueda);
      if (filtros?.institucionId) params.append('institucionId', filtros.institucionId.toString());
      if (filtros?.nivel) params.append('nivel', filtros.nivel);
      if (filtros?.modalidad) params.append('modalidad', filtros.modalidad);
      if (filtros?.estado) params.append('estado', filtros.estado);
      if (filtros?.coordinadorId) params.append('coordinadorId', filtros.coordinadorId.toString());
      if (filtros?.ordenarPor) params.append('ordenarPor', filtros.ordenarPor);
      if (filtros?.orden) params.append('orden', filtros.orden);
      if (filtros?.pagina) params.append('pagina', filtros.pagina.toString());
      if (filtros?.limite) params.append('limite', filtros.limite.toString());

      const { data } = await apiClient.get<RespuestaPaginada<Programa>>(
        `${BASE_URL}?${params.toString()}`
      );
      
      return data;
    } catch (error: any) {
      console.error('Error al obtener programas:', error);
      
      if (error.response?.status === 401) {
        throw new Error('No estás autorizado. Por favor inicia sesión nuevamente.');
      }
      if (error.response?.status === 403) {
        throw new Error('No tienes permisos para ver los programas.');
      }
      if (error.response?.status === 500) {
        throw new Error('Error en el servidor. Por favor intenta más tarde.');
      }
      
      throw new Error(error.response?.data?.message || 'Error al obtener programas');
    }
  },

  /**
   * Obtiene un programa por su ID
   * 
   * @param id - ID del programa
   * @returns Promesa con el programa encontrado
   * 
   * @throws Error si el programa no existe (404)
   * 
   * @example
   * ```typescript
   * const programa = await programaService.getById(5);
   * console.log(programa.nombre); // "Ingeniería de Software"
   * ```
   */
  async getById(id: number): Promise<Programa> {
    try {
      const { data } = await apiClient.get<Programa>(`${BASE_URL}/${id}`);
      return data;
    } catch (error: any) {
      console.error(`Error al obtener programa ${id}:`, error);
      
      if (error.response?.status === 404) {
        throw new Error('Programa no encontrado');
      }
      if (error.response?.status === 401) {
        throw new Error('No estás autorizado. Por favor inicia sesión nuevamente.');
      }
      
      throw new Error(error.response?.data?.message || 'Error al obtener programa');
    }
  },

  /**
   * Obtiene programas de una institución específica
   * 
   * @param institucionId - ID de la institución
   * @param filtros - Filtros adicionales opcionales
   * @returns Promesa con respuesta paginada de programas
   * 
   * @example
   * ```typescript
   * const programas = await programaService.getPorInstitucion(1, {
   *   estado: 'ACTIVO'
   * });
   * ```
   */
  async getPorInstitucion(
    institucionId: number,
    filtros?: Omit<FiltrosProgramas, 'institucionId'>
  ): Promise<RespuestaPaginada<Programa>> {
    return this.getAll({ ...filtros, institucionId });
  },

  /**
   * Crea un nuevo programa académico
   * 
   * @param data - Datos del programa a crear
   * @returns Promesa con el programa creado
   * 
   * @throws Error si hay validaciones fallidas (400)
   * @throws Error si el código ya existe (409)
   * 
   * @example
   * ```typescript
   * const nuevoPrograma = await programaService.create({
   *   codigo: 'ING-SW-001',
   *   nombre: 'Ingeniería de Software',
   *   nivel: 'PROFESIONAL',
   *   modalidad: 'PRESENCIAL',
   *   duracionSemestres: 10,
   *   creditosRequeridos: 160,
   *   institucionId: 1,
   *   requiereProyectoGrado: true,
   *   requierePracticas: true,
   *   horasPracticas: 480
   * });
   * ```
   */
  async create(data: CrearProgramaDTO): Promise<Programa> {
    try {
      const { data: programa } = await apiClient.post<Programa>(BASE_URL, data);
      return programa;
    } catch (error: any) {
      console.error('Error al crear programa:', error);
      
      if (error.response?.status === 400) {
        const message = error.response.data?.message || 'Datos inválidos';
        throw new Error(message);
      }
      if (error.response?.status === 409) {
        throw new Error('Ya existe un programa con ese código');
      }
      if (error.response?.status === 401) {
        throw new Error('No estás autorizado. Por favor inicia sesión nuevamente.');
      }
      if (error.response?.status === 403) {
        throw new Error('No tienes permisos para crear programas.');
      }
      
      throw new Error(error.response?.data?.message || 'Error al crear programa');
    }
  },

  /**
   * Actualiza un programa existente
   * 
   * @param id - ID del programa a actualizar
   * @param data - Datos a actualizar (parciales)
   * @returns Promesa con el programa actualizado
   * 
   * @throws Error si el programa no existe (404)
   * 
   * @example
   * ```typescript
   * const actualizado = await programaService.update(5, {
   *   nombre: 'Ingeniería de Software Actualizado',
   *   duracionSemestres: 9
   * });
   * ```
   */
  async update(id: number, data: ActualizarProgramaDTO): Promise<Programa> {
    try {
      const { data: programa } = await apiClient.put<Programa>(`${BASE_URL}/${id}`, data);
      return programa;
    } catch (error: any) {
      console.error(`Error al actualizar programa ${id}:`, error);
      
      if (error.response?.status === 404) {
        throw new Error('Programa no encontrado');
      }
      if (error.response?.status === 400) {
        const message = error.response.data?.message || 'Datos inválidos';
        throw new Error(message);
      }
      if (error.response?.status === 401) {
        throw new Error('No estás autorizado. Por favor inicia sesión nuevamente.');
      }
      if (error.response?.status === 403) {
        throw new Error('No tienes permisos para actualizar este programa.');
      }
      
      throw new Error(error.response?.data?.message || 'Error al actualizar programa');
    }
  },

  /**
   * Elimina un programa
   * 
   * @param id - ID del programa a eliminar
   * @returns Promesa que se resuelve al eliminar
   * 
   * @throws Error si el programa tiene estudiantes activos (409)
   * 
   * @example
   * ```typescript
   * await programaService.delete(5);
   * console.log('Programa eliminado exitosamente');
   * ```
   */
  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`${BASE_URL}/${id}`);
    } catch (error: any) {
      console.error(`Error al eliminar programa ${id}:`, error);
      
      if (error.response?.status === 404) {
        throw new Error('Programa no encontrado');
      }
      if (error.response?.status === 409) {
        throw new Error('No se puede eliminar un programa con estudiantes activos');
      }
      if (error.response?.status === 401) {
        throw new Error('No estás autorizado. Por favor inicia sesión nuevamente.');
      }
      if (error.response?.status === 403) {
        throw new Error('No tienes permisos para eliminar este programa.');
      }
      
      throw new Error(error.response?.data?.message || 'Error al eliminar programa');
    }
  },

  /**
   * Cambia el estado de un programa
   * 
   * @param id - ID del programa
   * @param estado - Nuevo estado
   * @returns Promesa con el programa actualizado
   * 
   * @example
   * ```typescript
   * await programaService.cambiarEstado(5, 'INACTIVO');
   * ```
   */
  async cambiarEstado(id: number, estado: EstadoPrograma): Promise<Programa> {
    try {
      const { data } = await apiClient.patch<Programa>(`${BASE_URL}/${id}/estado`, { estado });
      return data;
    } catch (error: any) {
      console.error(`Error al cambiar estado del programa ${id}:`, error);
      
      if (error.response?.status === 404) {
        throw new Error('Programa no encontrado');
      }
      if (error.response?.status === 401) {
        throw new Error('No estás autorizado. Por favor inicia sesión nuevamente.');
      }
      
      throw new Error(error.response?.data?.message || 'Error al cambiar estado');
    }
  },

  /**
   * Obtiene estadísticas detalladas de un programa
   * 
   * @param id - ID del programa
   * @returns Promesa con las estadísticas
   * 
   * @example
   * ```typescript
   * const stats = await programaService.getEstadisticas(5);
   * console.log(`Tasa de graduación: ${stats.tasaGraduacion}%`);
   * ```
   */
  async getEstadisticas(id: number): Promise<EstadisticasPrograma> {
    try {
      const { data } = await apiClient.get<EstadisticasPrograma>(`${BASE_URL}/${id}/estadisticas`);
      return data;
    } catch (error: any) {
      console.error(`Error al obtener estadísticas del programa ${id}:`, error);
      
      if (error.response?.status === 404) {
        throw new Error('Programa no encontrado');
      }
      
      throw new Error(error.response?.data?.message || 'Error al obtener estadísticas');
    }
  },

  /**
   * Asigna cursos a un programa
   * 
   * @param data - Datos de asignación
   * @returns Promesa con el programa actualizado
   * 
   * @example
   * ```typescript
   * await programaService.asignarCursos({
   *   programaId: 5,
   *   cursoIds: [1, 2, 3],
   *   nivel: 1,
   *   esObligatorio: true
   * });
   * ```
   */
  async asignarCursos(data: AsignarCursosDTO): Promise<Programa> {
    try {
      const { data: programa } = await apiClient.post<Programa>(
        `${BASE_URL}/${data.programaId}/cursos`,
        data
      );
      return programa;
    } catch (error: any) {
      console.error('Error al asignar cursos:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Programa no encontrado');
      }
      if (error.response?.status === 400) {
        throw new Error(error.response.data?.message || 'Datos inválidos');
      }
      
      throw new Error(error.response?.data?.message || 'Error al asignar cursos');
    }
  },

  /**
   * Obtiene la malla curricular de un programa
   * 
   * @param id - ID del programa
   * @returns Promesa con la malla curricular
   * 
   * @example
   * ```typescript
   * const malla = await programaService.getMallaCurricular(5);
   * console.log(`Total créditos: ${malla.creditosTotales}`);
   * ```
   */
  async getMallaCurricular(id: number): Promise<MallaCurricular> {
    try {
      const { data } = await apiClient.get<MallaCurricular>(`${BASE_URL}/${id}/malla-curricular`);
      return data;
    } catch (error: any) {
      console.error(`Error al obtener malla curricular del programa ${id}:`, error);
      
      if (error.response?.status === 404) {
        throw new Error('Programa no encontrado');
      }
      
      throw new Error(error.response?.data?.message || 'Error al obtener malla curricular');
    }
  },

  /**
   * Busca programas por término
   * 
   * @param termino - Término de búsqueda (nombre, código, descripción)
   * @returns Promesa con lista de programas encontrados
   * 
   * @example
   * ```typescript
   * const resultados = await programaService.search('ingeniería');
   * ```
   */
  async search(termino: string): Promise<Programa[]> {
    try {
      const { data } = await apiClient.get<RespuestaPaginada<Programa>>(
        `${BASE_URL}/search?q=${encodeURIComponent(termino)}`
      );
      return data.items;
    } catch (error: any) {
      console.error('Error al buscar programas:', error);
      throw new Error(error.response?.data?.message || 'Error al buscar programas');
    }
  }
};

export default programaService;
