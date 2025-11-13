/**
 * Servicio de administración
 * Gestiona estadísticas, usuarios pendientes y reportes
 */

import { api } from "../utils/api";

export interface AdminStats {
  totalUsers: number;
  totalInstitutions: number;
  activeCoordinators: number;
  totalCourses: number;
  activeStudents: number;
  systemUptime: string;
  pendingApprovals: number;
}

export interface SystemAlert {
  id: string;
  type: "warning" | "error" | "info" | "success";
  message: string;
  timestamp: string;
  details?: string;
}

export interface UsuarioPendiente {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono?: string;
  rol_solicitado: string;
  institucion_id?: string;
  institucion_nombre?: string;
  fecha_registro: string;
  documento?: string;
  mensaje?: string;
}

export interface AprobarUsuarioRequest {
  usuario_id: string;
  comentario?: string;
}

export interface RechazarUsuarioRequest {
  usuario_id: string;
  motivo: string;
}

const adminService = {
  /**
   * Obtener estadísticas generales del sistema
   */
  async getStats(): Promise<AdminStats> {
    try {
      const response = await api.get("/admin/stats", { timeout: 2000 }); // Timeout reducido a 2s
      return response.data;
    } catch (error) {
      // Silenciar error 405 (endpoint no implementado)
      if (error && typeof error === "object" && "response" in error) {
        const axiosError = error as { response?: { status?: number } };
        if (axiosError.response?.status !== 405) {
          console.error("Error al obtener estadísticas:", error);
        }
      }
      // Retornar datos por defecto en caso de error
      return {
        totalUsers: 0,
        totalInstitutions: 0,
        activeCoordinators: 0,
        totalCourses: 0,
        activeStudents: 0,
        systemUptime: "0%",
        pendingApprovals: 0,
      };
    }
  },

  /**
   * Obtener alertas del sistema
   */
  async getAlerts(): Promise<SystemAlert[]> {
    try {
      const response = await api.get("/admin/alerts", { timeout: 2000 }); // Timeout reducido a 2s
      return response.data;
    } catch (error) {
      // Silenciar error 405 (endpoint no implementado)
      if (error && typeof error === "object" && "response" in error) {
        const axiosError = error as { response?: { status?: number } };
        if (axiosError.response?.status !== 405) {
          console.error("Error al obtener alertas:", error);
        }
      }
      return [];
    }
  },

  /**
   * Obtener usuarios pendientes de aprobación
   */
  async getUsuariosPendientes(): Promise<UsuarioPendiente[]> {
    try {
      const response = await api.get("/admin/usuarios-pendientes");
      return response.data;
    } catch (error) {
      console.error("Error al obtener usuarios pendientes:", error);
      return [];
    }
  },

  /**
   * Aprobar un usuario pendiente
   */
  async aprobarUsuario(
    data: AprobarUsuarioRequest
  ): Promise<{ success: boolean; message: string }> {
    try {
      const response = await api.post(`/admin/usuarios/${data.usuario_id}/aprobar`, {
        comentario: data.comentario,
      });
      return { success: true, message: response.data.message || "Usuario aprobado exitosamente" };
    } catch (error: any) {
      console.error("Error al aprobar usuario:", error);
      throw new Error(error.response?.data?.detail || "Error al aprobar usuario");
    }
  },

  /**
   * Rechazar un usuario pendiente
   */
  async rechazarUsuario(
    data: RechazarUsuarioRequest
  ): Promise<{ success: boolean; message: string }> {
    try {
      const response = await api.post(`/admin/usuarios/${data.usuario_id}/rechazar`, {
        motivo: data.motivo,
      });
      return { success: true, message: response.data.message || "Usuario rechazado" };
    } catch (error: any) {
      console.error("Error al rechazar usuario:", error);
      throw new Error(error.response?.data?.detail || "Error al rechazar usuario");
    }
  },

  /**
   * Obtener reportes generales
   */
  async getReportes(): Promise<any> {
    try {
      const response = await api.get("/admin/reportes");
      return response.data;
    } catch (error) {
      console.error("Error al obtener reportes:", error);
      return {
        usuariosActivos: 0,
        cursosActivos: 0,
        sesionesHoy: 0,
        tasaFinalizacion: 0,
        crecimientoMensual: 0,
        satisfaccionPromedio: 0,
      };
    }
  },

  /**
   * Obtener métricas del sistema
   */
  async getSystemMetrics(): Promise<{
    cpu: number;
    memory: number;
    disk: number;
    services: Array<{ name: string; status: "online" | "offline" }>;
  }> {
    try {
      const response = await api.get("/admin/system/metrics");
      return response.data;
    } catch (error) {
      console.error("Error al obtener métricas del sistema:", error);
      return {
        cpu: 0,
        memory: 0,
        disk: 0,
        services: [
          { name: "Servidor Web", status: "online" },
          { name: "Base de Datos", status: "online" },
          { name: "Sistema de Archivos", status: "online" },
          { name: "WebSockets", status: "online" },
        ],
      };
    }
  },
};

export default adminService;
