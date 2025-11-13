/**
 * Servicio API para Administradores - Gestión de Instituciones
 * 
 * Endpoints base: /admin/instituciones
 * Autenticación: Requiere token JWT con rol ADMIN
 */

import axios, { AxiosInstance } from 'axios';
import { toSnakeCase, toCamelCase, toSnakeCaseParams } from '../../../utils/transformers';
import type {
  Institucion,
  CrearInstitucionDTO,
  ActualizarInstitucionDTO,
  FiltrosInstitucion,
  RespuestaPaginada,
  InvitarCoordinadorRequest,
  InvitarCoordinadorResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BASE_PATH = '/admin/instituciones';

/**
 * Cliente axios configurado para endpoints de admin
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Servicio para operaciones de admin sobre instituciones
 */
export class AdminInstitucionService {
  /**
   * Crear una nueva institución
   * POST /admin/instituciones
   */
  async crear(data: CrearInstitucionDTO): Promise<Institucion> {
    // Transformar a snake_case antes de enviar
    const dataSnakeCase = toSnakeCase(data);
    
    const response = await apiClient.post<any>(BASE_PATH, dataSnakeCase);
    
    // Transformar respuesta a camelCase
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Listar todas las instituciones (admin ve todas)
   * GET /admin/instituciones
   */
  async listar(filtros: FiltrosInstitucion = {}): Promise<RespuestaPaginada<Institucion>> {
    // Construir query params en snake_case
    const params = toSnakeCaseParams(filtros);
    
    const response = await apiClient.get<any>(BASE_PATH, { params });
    
    // Transformar respuesta a camelCase
    return toCamelCase<RespuestaPaginada<Institucion>>(response.data);
  }

  /**
   * Obtener una institución por ID
   * GET /admin/instituciones/{id}
   */
  async obtenerPorId(institucionId: string): Promise<Institucion> {
    const response = await apiClient.get<any>(`${BASE_PATH}/${institucionId}`);
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Actualizar una institución
   * PUT /admin/instituciones/{id}
   */
  async actualizar(institucionId: string, data: ActualizarInstitucionDTO): Promise<Institucion> {
    const dataSnakeCase = toSnakeCase(data);
    const response = await apiClient.put<any>(`${BASE_PATH}/${institucionId}`, dataSnakeCase);
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Eliminar una institución
   * DELETE /admin/instituciones/{id}
   */
  async eliminar(institucionId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete<any>(`${BASE_PATH}/${institucionId}`);
    return response.data;
  }

  /**
   * Invitar coordinador a una institución
   * POST /admin/instituciones/{id}/invitar-coordinador
   * 
   * Genera un código de 6 dígitos y envía email al coordinador
   */
  async invitarCoordinador(
    institucionId: string,
    request: InvitarCoordinadorRequest
  ): Promise<InvitarCoordinadorResponse> {
    const dataSnakeCase = toSnakeCase(request);
    
    const response = await apiClient.post<any>(
      `${BASE_PATH}/${institucionId}/invitar-coordinador`,
      dataSnakeCase
    );
    
    return toCamelCase<InvitarCoordinadorResponse>(response.data);
  }

  /**
   * Activar una institución (cambiar estado a ACTIVA)
   * POST /admin/instituciones/{id}/activar
   */
  async activar(institucionId: string): Promise<Institucion> {
    const response = await apiClient.post<any>(`${BASE_PATH}/${institucionId}/activar`);
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Suspender una institución (cambiar estado a SUSPENDIDA)
   * POST /admin/instituciones/{id}/suspender
   */
  async suspender(institucionId: string, motivo?: string): Promise<Institucion> {
    const data = motivo ? { motivo } : {};
    const response = await apiClient.post<any>(`${BASE_PATH}/${institucionId}/suspender`, data);
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Desactivar una institución (cambiar estado a INACTIVA)
   * POST /admin/instituciones/{id}/desactivar
   */
  async desactivar(institucionId: string): Promise<Institucion> {
    const response = await apiClient.post<any>(`${BASE_PATH}/${institucionId}/desactivar`);
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Obtener estadísticas detalladas de una institución
   * GET /admin/instituciones/{id}/estadisticas
   */
  async obtenerEstadisticas(institucionId: string): Promise<any> {
    const response = await apiClient.get<any>(`${BASE_PATH}/${institucionId}/estadisticas`);
    return toCamelCase(response.data);
  }

  /**
   * Listar coordinadores de una institución
   * GET /admin/instituciones/{id}/coordinadores
   */
  async listarCoordinadores(institucionId: string): Promise<any[]> {
    const response = await apiClient.get<any>(`${BASE_PATH}/${institucionId}/coordinadores`);
    return toCamelCase(response.data);
  }
}

// Exportar instancia única del servicio
export const adminInstitucionService = new AdminInstitucionService();

// Export por defecto
export default adminInstitucionService;
