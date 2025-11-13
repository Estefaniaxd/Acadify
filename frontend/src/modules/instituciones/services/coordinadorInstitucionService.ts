/**
 * Servicio API para Coordinadores - Gestión de Sus Instituciones
 * 
 * Endpoints base: /api/instituciones
 * Autenticación: Requiere token JWT con rol COORDINADOR
 */

import axios, { AxiosInstance } from 'axios';
import { toSnakeCase, toCamelCase } from '../../../utils/transformers';
import type {
  Institucion,
  ActualizarInstitucionDTO,
  PersonalizacionInstitucion,
  EstadisticasDetalladas,
  OnboardingStatus,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BASE_PATH = '/api/instituciones';

/**
 * Cliente axios configurado para endpoints de coordinador
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores
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
 * Servicio para operaciones de coordinador sobre sus instituciones
 */
export class CoordinadorInstitucionService {
  /**
   * Obtener lista de instituciones del coordinador actual
   * GET /api/instituciones/mis-instituciones/list
   */
  async misInstituciones(incluirEstadisticas = false): Promise<{
    success: boolean;
    data: Institucion[];
    total: number;
  }> {
    const params = { incluir_estadisticas: incluirEstadisticas };
    const response = await apiClient.get<any>(`${BASE_PATH}/mis-instituciones/list`, { params });
    
    // Transformar respuesta
    return {
      success: response.data.success,
      data: toCamelCase<Institucion[]>(response.data.data),
      total: response.data.total,
    };
  }

  /**
   * Obtener una institución específica (solo si el coordinador tiene acceso)
   * GET /api/instituciones/{id}
   */
  async obtenerPorId(institucionId: string): Promise<Institucion> {
    const response = await apiClient.get<any>(`${BASE_PATH}/${institucionId}`);
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Actualizar información de la institución
   * PUT /api/instituciones/{id}
   */
  async actualizar(institucionId: string, data: ActualizarInstitucionDTO): Promise<Institucion> {
    const dataSnakeCase = toSnakeCase(data);
    const response = await apiClient.put<any>(`${BASE_PATH}/${institucionId}`, dataSnakeCase);
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Actualizar branding (logo y colores)
   * PUT /api/instituciones/{id}/branding
   */
  async actualizarBranding(
    institucionId: string,
    branding: PersonalizacionInstitucion
  ): Promise<Institucion> {
    const dataSnakeCase = toSnakeCase(branding);
    const response = await apiClient.put<any>(
      `${BASE_PATH}/${institucionId}/branding`,
      dataSnakeCase
    );
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Actualizar información de contacto
   * PUT /api/instituciones/{id}/contacto
   */
  async actualizarContacto(
    institucionId: string,
    contacto: {
      correoInstitucional?: string;
      telefono?: string;
      direccion?: string;
      ciudad?: string;
    }
  ): Promise<Institucion> {
    const dataSnakeCase = toSnakeCase(contacto);
    const response = await apiClient.put<any>(
      `${BASE_PATH}/${institucionId}/contacto`,
      dataSnakeCase
    );
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Actualizar redes sociales
   * PUT /api/instituciones/{id}/redes-sociales
   */
  async actualizarRedesSociales(
    institucionId: string,
    redesSociales: Record<string, string>
  ): Promise<Institucion> {
    const dataSnakeCase = toSnakeCase({ redes_sociales: redesSociales });
    const response = await apiClient.put<any>(
      `${BASE_PATH}/${institucionId}/redes-sociales`,
      dataSnakeCase
    );
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Agregar un dominio adicional
   * POST /api/instituciones/{id}/dominios
   */
  async agregarDominio(institucionId: string, dominio: string): Promise<Institucion> {
    const response = await apiClient.post<any>(`${BASE_PATH}/${institucionId}/dominios`, {
      dominio,
    });
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Eliminar un dominio adicional
   * DELETE /api/instituciones/{id}/dominios/{dominio}
   */
  async eliminarDominio(institucionId: string, dominio: string): Promise<Institucion> {
    const response = await apiClient.delete<any>(
      `${BASE_PATH}/${institucionId}/dominios/${encodeURIComponent(dominio)}`
    );
    return toCamelCase<Institucion>(response.data);
  }

  /**
   * Obtener estadísticas detalladas de la institución
   * GET /api/instituciones/{id}/estadisticas
   */
  async obtenerEstadisticas(institucionId: string): Promise<EstadisticasDetalladas> {
    const response = await apiClient.get<any>(`${BASE_PATH}/${institucionId}/estadisticas`);
    return toCamelCase<EstadisticasDetalladas>(response.data);
  }

  /**
   * Obtener estado del onboarding
   * GET /api/instituciones/{id}/onboarding-status
   */
  async obtenerEstadoOnboarding(institucionId: string): Promise<OnboardingStatus> {
    const response = await apiClient.get<any>(`${BASE_PATH}/${institucionId}/onboarding-status`);
    return toCamelCase<OnboardingStatus>(response.data);
  }

  /**
   * Marcar paso de onboarding como completado
   * POST /api/instituciones/{id}/onboarding/completar-paso
   */
  async completarPasoOnboarding(institucionId: string, paso: string): Promise<OnboardingStatus> {
    const response = await apiClient.post<any>(
      `${BASE_PATH}/${institucionId}/onboarding/completar-paso`,
      { paso }
    );
    return toCamelCase<OnboardingStatus>(response.data);
  }

  /**
   * Subir logo de la institución
   * POST /api/instituciones/{id}/logo
   */
  async subirLogo(institucionId: string, file: File): Promise<{ logo_url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<any>(`${BASE_PATH}/${institucionId}/logo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  /**
   * Verificar si un dominio está disponible
   * GET /api/instituciones/verificar-dominio/{dominio}
   */
  async verificarDominio(dominio: string): Promise<{ disponible: boolean; mensaje: string }> {
    const response = await apiClient.get<any>(
      `${BASE_PATH}/verificar-dominio/${encodeURIComponent(dominio)}`
    );
    return response.data;
  }
}

// Exportar instancia única del servicio
export const coordinadorInstitucionService = new CoordinadorInstitucionService();

// Export por defecto
export default coordinadorInstitucionService;
