/**
 * Servicio API para Invitaciones - Endpoints Públicos y Admin
 *
 * Endpoints públicos: /invitaciones (NO requieren autenticación)
 * Endpoints admin: /admin/instituciones/{id}/invitar-coordinador (requieren token)
 *
 * ACTUALIZADO para coincidir con backend real
 */

import axios, { AxiosError, AxiosInstance } from "axios";
import { toCamelCase, toSnakeCase } from "../../../utils/transformers";
import { API_BASE_URL } from "../../../config/api.config";
import type {
  AceptarInvitacionDTO,
  CrearInvitacionDTO,
  EstadisticasInvitaciones,
  FiltrosInvitaciones,
  HistorialInvitacion,
  Invitacion,
  NotificacionInvitacion,
  RechazarInvitacionDTO,
  RespuestaEnvioInvitacion,
  RespuestaPaginada,
  ValidacionInvitacion,
} from "../types";

// ============================================
// TIPOS (actualizados para backend real)
// ============================================

export interface InvitacionInfo {
  valido: boolean;
  invitacion: {
    invitacion_id: string;
    codigo: string;
    email_destino: string;
    fecha_creacion: string;
    fecha_expiracion: string;
  };
  institucion: {
    institucion_id: string;
    nombre: string;
    sigla?: string;
    logo_url: string;
    tipo_institucion: string;
    nivel_educativo: string;
    ciudad?: string;
    pais: string;
  };
}

export interface AceptarInvitacionRequest {
  codigo: string;
  nombre: string;
  apellido: string;
  password: string;
}

export interface AceptarInvitacionResponse {
  success: boolean;
  message: string;
  usuario: {
    usuario_id: string;
    email: string;
    username: string;
    nombre: string;
    apellido: string;
    rol: string;
  };
  institucion: {
    institucion_id: string;
    nombre: string;
    sigla?: string;
    estado: string;
    fecha_activacion?: string;
  };
}

// ============================================
// CONFIGURACIÓN DE AXIOS
// ============================================

const BASE_PATH = "/invitaciones";

/**
 * Cliente axios para endpoints PÚBLICOS de invitaciones
 * NO incluye token de autenticación automáticamente
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para manejo de errores (sin redirección a login - son públicos)
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Solo mostrar errores que no sean 401 (no autenticado es esperado)
    if (error.response?.status !== 401) {
      console.error("Error en invitación:", error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================
// SERVICIO DE INVITACIONES
// ============================================

/**
 * Servicio para operaciones públicas de invitaciones
 */
export const invitacionService = {
  /**
   * Validar un código de invitación
   * GET /invitaciones/validar/{codigo}
   *
   * Verifica si el código es válido y no ha expirado.
   * Retorna información de la invitación y la institución.
   */
  async validarCodigo(codigo: string): Promise<InvitacionInfo> {
    try {
      const response = await apiClient.get<InvitacionInfo>(`${BASE_PATH}/validar/${codigo}`);
      return toCamelCase<InvitacionInfo>(response.data);
    } catch (error: unknown) {
      console.error("Error al validar código:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Aceptar una invitación y registrar coordinador
   * POST /invitaciones/aceptar
   *
   * Crea el usuario coordinador y lo asigna a la institución.
   * Activa la institución si estaba pendiente.
   */
  async aceptar(data: AceptarInvitacionRequest): Promise<AceptarInvitacionResponse> {
    try {
      const dataSnakeCase = toSnakeCase(data);
      const response = await apiClient.post<AceptarInvitacionResponse>(`${BASE_PATH}/aceptar`, dataSnakeCase);
      return toCamelCase<AceptarInvitacionResponse>(response.data);
    } catch (error: unknown) {
      console.error("Error al aceptar invitación:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Verificar si un email ya tiene una invitación pendiente
   * GET /invitaciones/verificar-email/{email}
   */
  async verificarEmail(email: string): Promise<{
    tieneInvitacion: boolean;
    institucion?: string;
    fechaExpiracion?: string;
  }> {
    try {
      const response = await apiClient.get<any>(
        `${BASE_PATH}/verificar-email/${encodeURIComponent(email)}`
      );
      return toCamelCase(response.data);
    } catch (error: any) {
      console.error("Error al verificar email:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Solicitar reenvío de código de invitación
   * POST /invitaciones/reenviar
   *
   * Genera un nuevo código y lo envía por email
   */
  async reenviarCodigo(email: string): Promise<{
    success: boolean;
    message: string;
    codigo?: string;
  }> {
    try {
      const response = await apiClient.post<any>(`${BASE_PATH}/reenviar`, {
        email_destino: email,
      });
      return response.data;
    } catch (error: any) {
      console.error("Error al reenviar código:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Obtener información básica de una invitación sin validar
   * GET /invitaciones/info/{codigo}
   *
   * Similar a validar pero no verifica expiración
   */
  async obtenerInfo(codigo: string): Promise<InvitacionInfo> {
    try {
      const response = await apiClient.get<any>(`${BASE_PATH}/info/${codigo}`);
      return toCamelCase<InvitacionInfo>(response.data);
    } catch (error: any) {
      console.error("Error al obtener info:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Manejo de errores
   */
  handleError(error: any): Error {
    if (error.response) {
      // El servidor respondió con un código de error
      const mensaje =
        error.response.data?.detail || error.response.data?.message || "Error del servidor";
      return new Error(mensaje);
    } else if (error.request) {
      // La solicitud se hizo pero no se recibió respuesta
      return new Error("No se recibió respuesta del servidor. Verifica tu conexión.");
    } else {
      // Algo más salió mal
      return new Error(error.message || "Error desconocido");
    }
  },

  // ============================================
  // MÉTODOS LEGACY (para compatibilidad con código existente)
  // Estos métodos se mantienen pero ahora usan las rutas correctas
  // ============================================
  async crear(dto: CrearInvitacionDTO): Promise<RespuestaEnvioInvitacion> {
    try {
      const { data } = await apiClient.post<RespuestaEnvioInvitacion>("/", dto);
      return data;
    } catch (error: any) {
      console.error("Error al crear invitación:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Enviar invitación por email
   * Genera nuevo código si es reenvío
   */
  async enviar(id: number): Promise<RespuestaEnvioInvitacion> {
    try {
      const { data } = await apiClient.post<RespuestaEnvioInvitacion>(`/${id}/enviar`);
      return data;
    } catch (error: any) {
      console.error(`Error al enviar invitación ${id}:`, error);
      throw this.handleError(error);
    }
  },

  /**
   * Reenviar invitación (genera nuevo código)
   */
  async reenviar(id: number): Promise<RespuestaEnvioInvitacion> {
    try {
      const { data } = await apiClient.post<RespuestaEnvioInvitacion>(`/${id}/reenviar`);
      return data;
    } catch (error: any) {
      console.error(`Error al reenviar invitación ${id}:`, error);
      throw this.handleError(error);
    }
  },

  /**
   * Cancelar invitación pendiente
   */
  async cancelar(id: number): Promise<Invitacion> {
    try {
      const { data } = await apiClient.patch<Invitacion>(`/${id}/cancelar`);
      return data;
    } catch (error: any) {
      console.error(`Error al cancelar invitación ${id}:`, error);
      throw this.handleError(error);
    }
  },

  /**
   * Validar token de invitación (sin autenticación)
   * Usa endpoint público
   */
  async validarToken(token: string): Promise<ValidacionInvitacion> {
    try {
      const { data } = await axios.get<ValidacionInvitacion>(
        `/api/v1/invitaciones/validar/${token}`
      );
      return data;
    } catch (error: any) {
      console.error("Error al validar token:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Aceptar invitación con código (LEGACY - usar el método principal aceptar)
   * Crea usuario y lo asocia a la institución
   */
  async aceptarLegacy(dto: AceptarInvitacionDTO): Promise<{
    usuario: any;
    token: string;
    invitacion: Invitacion;
  }> {
    try {
      const { data } = await axios.post("/api/v1/invitaciones/aceptar", dto);

      // Guardar token de autenticación del nuevo usuario
      if (data.token) {
        localStorage.setItem("authToken", data.token);
      }

      return data;
    } catch (error: any) {
      console.error("Error al aceptar invitación:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Rechazar invitación (sin autenticación)
   */
  async rechazar(dto: RechazarInvitacionDTO): Promise<Invitacion> {
    try {
      const { data } = await axios.post<Invitacion>("/api/v1/invitaciones/rechazar", dto);
      return data;
    } catch (error: any) {
      console.error("Error al rechazar invitación:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Obtener estadísticas de invitaciones
   */
  async getEstadisticas(institucionId?: number): Promise<EstadisticasInvitaciones> {
    try {
      const params = institucionId ? { institucionId } : {};
      const { data } = await apiClient.get<EstadisticasInvitaciones>("/estadisticas", { params });
      return data;
    } catch (error: any) {
      console.error("Error al obtener estadísticas:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Obtener historial de una invitación
   */
  async getHistorial(id: number): Promise<HistorialInvitacion[]> {
    try {
      const { data } = await apiClient.get<HistorialInvitacion[]>(`/${id}/historial`);
      return data;
    } catch (error: any) {
      console.error(`Error al obtener historial de invitación ${id}:`, error);
      throw this.handleError(error);
    }
  },

  /**
   * Obtener invitaciones pendientes del usuario actual (notificaciones)
   */
  async getMisInvitaciones(): Promise<NotificacionInvitacion[]> {
    try {
      const token = localStorage.getItem('access_token');
      const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

      const { data } = await apiClient.get<NotificacionInvitacion[]>(
        `${BASE_PATH}/mis-invitaciones`,
        config
      );
      return data;
    } catch (error: any) {
      // Si es 401, el usuario no está autenticado - retornar array vacío sin error
      if (error.response?.status === 401) {
        return [];
      }
      console.error("Error al obtener mis invitaciones:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Marcar notificación de invitación como leída
   */
  async marcarLeida(notificacionId: number): Promise<void> {
    try {
      await apiClient.patch(`/notificaciones/${notificacionId}/leer`);
    } catch (error: any) {
      console.error(`Error al marcar notificación ${notificacionId} como leída:`, error);
      throw this.handleError(error);
    }
  },

  /**
   * Obtener invitaciones por institución
   */
  async getPorInstitucion(
    institucionId: number,
    filtros?: Omit<FiltrosInvitaciones, "institucionId">
  ): Promise<RespuestaPaginada<Invitacion>> {
    try {
      const { data } = await apiClient.get("/", {
        params: { ...filtros, institucionId },
      });
      return data;
    } catch (error: any) {
      console.error("Error al obtener invitaciones por institución:", error);
      throw this.handleError(error);
    }
  },

  /**
   * Verificar si un email ya tiene invitación pendiente
   */
  async verificarEmailDisponible(
    email: string,
    institucionId: number
  ): Promise<{
    disponible: boolean;
    invitacionExistente?: Invitacion;
  }> {
    try {
      const { data } = await apiClient.get("/verificar-email", {
        params: { email, institucionId },
      });
      return data;
    } catch (error: any) {
      console.error("Error al verificar email:", error);
      throw this.handleError(error);
    }
  },
};

export default invitacionService;
