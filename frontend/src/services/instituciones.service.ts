/**
 * Servicio de gestión de instituciones
 * CRUD completo para instituciones educativas
 */

import { api } from '../utils/api';

export interface Institucion {
  institucion_id: string;
  nombre: string;
  sigla?: string;
  codigo?: string;
  lema?: string;
  tipo_institucion: 'escuela' | 'colegio' | 'instituto' | 'universidad' | 'politecnico' | 'centro_de_formacion' | 'corporacion' | 'fundacion' | 'academia' | 'centro_idiomas' | 'centro_deportivo' | 'seminario' | 'conservatorio' | 'escuela_militar' | 'otro';
  usa_programas: boolean;
  nivel_educativo: 'basica' | 'media' | 'tecnica' | 'tecnologica' | 'superior';
  sector: 'publico' | 'privado';
  estado: 'activa' | 'inactiva' | 'pendiente' | 'suspendida';
  
  // Información de contacto
  correo_institucional: string;
  telefono: string;
  
  // Ubicación
  pais: string;
  ciudad?: string;
  direccion?: string;
  
  // Configuración
  nit?: string;
  logo_url?: string;
  
  // Estadísticas (agregadas por el backend)
  total_usuarios?: number;
  total_cursos?: number;
  total_estudiantes?: number;
  total_profesores?: number;
  
  // Fechas
  fecha_creacion?: string;
  fecha_activacion?: string;
}

export interface InstitucionCreate {
  nombre: string;
  sigla?: string;
  lema?: string;
  tipo_institucion: 'escuela' | 'colegio' | 'instituto' | 'universidad' | 'politecnico' | 'centro_de_formacion' | 'corporacion' | 'fundacion' | 'academia' | 'centro_idiomas' | 'centro_deportivo' | 'seminario' | 'conservatorio' | 'escuela_militar' | 'otro';
  usa_programas: boolean;
  nivel_educativo: 'basica' | 'media' | 'tecnica' | 'tecnologica' | 'superior';
  sector: 'publico' | 'privado';
  direccion?: string;
  ciudad?: string;
  pais: string;
  correo_institucional: string;
  telefono: string;
  nit?: string;
}

export interface InstitucionUpdate {
  nombre?: string;
  sigla?: string;
  lema?: string;
  tipo_institucion?: 'escuela' | 'colegio' | 'instituto' | 'universidad' | 'politecnico' | 'centro_de_formacion' | 'corporacion' | 'fundacion' | 'academia' | 'centro_idiomas' | 'centro_deportivo' | 'seminario' | 'conservatorio' | 'escuela_militar' | 'otro';
  usa_programas?: boolean;
  nivel_educativo?: 'basica' | 'media' | 'tecnica' | 'tecnologica' | 'superior';
  sector?: 'publico' | 'privado';
  direccion?: string;
  ciudad?: string;
  pais?: string;
  correo_institucional?: string;
  telefono?: string;
  nit?: string;
  estado?: 'activa' | 'inactiva' | 'pendiente' | 'suspendida';
}

export interface InvitacionCoordinador {
  email_destino: string;
}

const institucionesService = {
  /**
   * Obtener todas las instituciones (endpoint público)
   */
  async getAll(): Promise<Institucion[]> {
    try {
      // IMPORTANTE: FastAPI requiere barra final en /api/instituciones/
      const response = await api.get('/api/instituciones/', {
        params: {
          skip: 0,
          limit: 1000, // Obtener todas las instituciones
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error al obtener instituciones:', error);
      console.error('Response:', error.response?.data);
      console.error('Status:', error.response?.status);
      // Si falla, retornar array vacío en lugar de lanzar error
      return [];
    }
  },

  /**
   * Obtener una institución por ID
   */
  async getById(id: string): Promise<Institucion | null> {
    try {
      const response = await api.get(`/api/instituciones/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener institución ${id}:`, error);
      return null;
    }
  },

  /**
   * Crear nueva institución
   */
  async create(data: InstitucionCreate): Promise<Institucion> {
    try {
      const response = await api.post('/admin/instituciones', data);
      return response.data;
    } catch (error: any) {
      console.error('Error al crear institución:', error);
      throw new Error(error.response?.data?.detail || 'Error al crear institución');
    }
  },

  /**
   * Actualizar institución existente
   */
  async update(id: string, data: InstitucionUpdate): Promise<Institucion> {
    try {
      const response = await api.put(`/api/instituciones/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Error al actualizar institución:', error);
      throw new Error(error.response?.data?.detail || 'Error al actualizar institución');
    }
  },

  /**
   * Eliminar institución
   */
  async delete(id: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await api.delete(`/api/instituciones/${id}`);
      return { success: true, message: response.data.message || 'Institución eliminada' };
    } catch (error) {
      console.error('Error al eliminar institución:', error);
      throw new Error(error.response?.data?.detail || 'Error al eliminar institución');
    }
  },

  /**
   * Invitar coordinador a una institución
   */
  async invitarCoordinador(
    institucionId: string,
    data: InvitacionCoordinador
  ): Promise<{ success: boolean; codigo: string; message: string }> {
    try {
      const response = await api.post(`/admin/instituciones/${institucionId}/invitar-coordinador`, data);
      return {
        success: true,
        codigo: response.data.codigo,
        message: 'Invitación enviada exitosamente',
      };
    } catch (error: any) {
      console.error('Error al enviar invitación:', error);
      throw new Error(error.response?.data?.detail || 'Error al enviar invitación');
    }
  },

  /**
   * Obtener estadísticas de una institución
   */
  async getStats(id: string): Promise<{
    total_usuarios: number;
    total_cursos: number;
    total_estudiantes: number;
    total_profesores: number;
  }> {
    try {
      const response = await api.get(`/api/instituciones/${id}/estadisticas`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener estadísticas de institución ${id}:`, error);
      return {
        total_usuarios: 0,
        total_cursos: 0,
        total_estudiantes: 0,
        total_profesores: 0,
      };
    }
  },
};

export default institucionesService;
