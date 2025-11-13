/**
 * Service para gestión de Instituciones
 * Implementa CRUD completo y operaciones adicionales
 * Principio: Single Responsibility - Solo maneja la comunicación con la API de instituciones
 */

import axios from 'axios';
import type {
  Institucion,
  CrearInstitucionDTO,
  ActualizarInstitucionDTO,
  FiltrosInstitucion,
  RespuestaPaginada,
  EstadisticasInstitucion,
  PersonalizacionInstitucion,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BASE_URL = '/api/v1/academic/instituciones';

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

// Interceptor para manejar errores de respuesta
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.dispatchEvent(new CustomEvent('auth-token-expired'));
      setTimeout(() => {
        window.location.href = '/login';
      }, 1000);
    }
    return Promise.reject(error);
  }
);

/**
 * Servicio genérico para operaciones CRUD
 * Aplica DIP: Componentes dependen de esta abstracción, no de fetch directo
 */
class InstitucionService {
  /**
   * Obtener todas las instituciones con filtros opcionales
   */
  async getAll(filtros?: FiltrosInstitucion): Promise<RespuestaPaginada<Institucion>> {
    try {
      const params = new URLSearchParams();
      
      if (filtros?.busqueda) params.append('busqueda', filtros.busqueda);
      if (filtros?.activo !== undefined) params.append('activo', String(filtros.activo));
      if (filtros?.ordenarPor) params.append('ordenar_por', filtros.ordenarPor);
      if (filtros?.orden) params.append('orden', filtros.orden);
      if (filtros?.pagina) params.append('pagina', String(filtros.pagina));
      if (filtros?.limite) params.append('limite', String(filtros.limite));

      const { data } = await apiClient.get<RespuestaPaginada<Institucion>>(
        `${BASE_URL}?${params.toString()}`
      );
      
      return data;
    } catch (error) {
      console.error('Error al obtener instituciones:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Obtener una institución por ID
   */
  async getById(id: string): Promise<Institucion> {
    try {
      const { data } = await apiClient.get<Institucion>(`${BASE_URL}/${id}`);
      return data;
    } catch (error) {
      console.error(`Error al obtener institución ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Crear una nueva institución
   */
  async create(institucion: CrearInstitucionDTO): Promise<Institucion> {
    try {
      const { data } = await apiClient.post<Institucion>(BASE_URL, institucion);
      return data;
    } catch (error) {
      console.error('Error al crear institución:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Actualizar una institución existente
   */
  async update(id: string, institucion: ActualizarInstitucionDTO): Promise<Institucion> {
    try {
      const { data } = await apiClient.put<Institucion>(`${BASE_URL}/${id}`, institucion);
      return data;
    } catch (error) {
      console.error(`Error al actualizar institución ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Eliminar una institución
   */
  async delete(id: string): Promise<void> {
    try {
      await apiClient.delete(`${BASE_URL}/${id}`);
    } catch (error) {
      console.error(`Error al eliminar institución ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Activar/Desactivar una institución
   */
  async toggleActivo(id: string, activo: boolean): Promise<Institucion> {
    try {
      return await this.update(id, { activo });
    } catch (error) {
      console.error(`Error al cambiar estado de institución ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Obtener estadísticas de una institución
   */
  async getEstadisticas(id: string): Promise<EstadisticasInstitucion> {
    try {
      const { data } = await apiClient.get<EstadisticasInstitucion>(
        `${BASE_URL}/${id}/estadisticas`
      );
      return data;
    } catch (error) {
      console.error(`Error al obtener estadísticas de institución ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Actualizar personalización visual de la institución
   */
  async updatePersonalizacion(
    id: string,
    personalizacion: PersonalizacionInstitucion
  ): Promise<Institucion> {
    try {
      const formData = new FormData();
      
      if (personalizacion.logo instanceof File) {
        formData.append('logo', personalizacion.logo);
      }
      if (personalizacion.favicon instanceof File) {
        formData.append('favicon', personalizacion.favicon);
      }
      
      formData.append('colorPrimario', personalizacion.colorPrimario);
      formData.append('colorSecundario', personalizacion.colorSecundario);

      const { data } = await apiClient.post<Institucion>(
        `${BASE_URL}/${id}/personalizacion`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      return data;
    } catch (error) {
      console.error(`Error al actualizar personalización de institución ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Subir logo de la institución
   */
  async uploadLogo(id: string, file: File): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('logo', file);

      const { data } = await apiClient.post<{ url: string }>(
        `${BASE_URL}/${id}/logo`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      return data.url;
    } catch (error) {
      console.error(`Error al subir logo de institución ${id}:`, error);
      throw this.handleError(error);
    }
  }

  /**
   * Buscar instituciones por término
   */
  async search(termino: string): Promise<Institucion[]> {
    try {
      const { data } = await apiClient.get<Institucion[]>(
        `${BASE_URL}/buscar?q=${encodeURIComponent(termino)}`
      );
      return data;
    } catch (error) {
      console.error('Error al buscar instituciones:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Manejador centralizado de errores
   * Principio: DRY - Don't Repeat Yourself
   */
  private handleError(error: any): Error {
    if (error.response) {
      // Error del servidor con respuesta
      const status = error.response.status;
      const message = error.response.data?.message || error.response.data?.detail;

      switch (status) {
        case 400:
          return new Error(message || 'Datos inválidos');
        case 401:
          return new Error('No autorizado. Por favor inicia sesión.');
        case 403:
          return new Error('No tienes permisos para realizar esta acción');
        case 404:
          return new Error('Institución no encontrada');
        case 409:
          return new Error(message || 'La institución ya existe');
        case 500:
          return new Error('Error interno del servidor');
        default:
          return new Error(message || 'Error al procesar la solicitud');
      }
    } else if (error.request) {
      // Error de red
      return new Error('No se pudo conectar con el servidor. Verifica tu conexión.');
    } else {
      // Error desconocido
      return new Error(error.message || 'Error desconocido');
    }
  }
}

// Exportar instancia única (Singleton)
export const institucionService = new InstitucionService();
