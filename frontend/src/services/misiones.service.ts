/**
 * Servicio de Misiones - Sistema de gamificación
 * Gestiona misiones diarias, semanales, mensuales y únicas
 */

import axios, { AxiosInstance } from 'axios';

// ==================== Tipos y Enumeraciones ====================
export type TipoMision = 
  | 'participacion' 
  | 'entrega' 
  | 'evaluacion' 
  | 'racha' 
  | 'social' 
  | 'logro' 
  | 'puntos';

export type EstadoMision = 
  | 'disponible' 
  | 'en_progreso' 
  | 'completada' 
  | 'reclamada' 
  | 'expirada' 
  | 'bloqueada';

export type FrecuenciaMision = 'diaria' | 'semanal' | 'mensual' | 'unica';

export type DificultadMision = 'facil' | 'normal' | 'dificil' | 'epica';

// ==================== Interfaces ====================
export interface Mision {
  mision_id: string;
  nombre: string;
  descripcion: string;
  icono?: string;
  tipo: TipoMision;
  frecuencia: FrecuenciaMision;
  dificultad: DificultadMision;
  objetivo: number;
  unidad?: string;
  puntos_recompensa: number;
  experiencia_recompensa: number;
  recompensas_extra?: Record<string, unknown>;
  es_activa: boolean;
  requisitos?: Record<string, unknown>;
  orden_visualizacion: number;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface MisionUsuario {
  mision_usuario_id: string;
  usuario_id: string;
  mision_id: string;
  estado: EstadoMision;
  progreso_actual: number;
  fecha_asignacion: string;
  fecha_inicio?: string;
  fecha_completada?: string;
  fecha_reclamada?: string;
  fecha_expiracion?: string;
  metadata_progreso?: Record<string, unknown>;
  fecha_actualizacion: string;
}

export interface MisionUsuarioConDetalle extends MisionUsuario {
  mision: Mision;
}

export interface MisionesDisponibles {
  diarias: MisionUsuarioConDetalle[];
  semanales: MisionUsuarioConDetalle[];
  mensuales: MisionUsuarioConDetalle[];
  unicas: MisionUsuarioConDetalle[];
  total_disponibles: number;
  total_completadas_hoy: number;
}

export interface EstadisticasMisiones {
  total_completadas: number;
  total_en_progreso: number;
  racha_actual: number;
  racha_maxima: number;
  puntos_ganados_misiones: number;
  misiones_por_tipo: Record<string, number>;
  misiones_por_dificultad: Record<string, number>;
}

export interface ActualizarProgresoRequest {
  incremento: number;
  metadata?: Record<string, unknown>;
}

// ==================== Helpers ====================
/**
 * Obtiene el color de la dificultad de la misión
 */
export function obtenerColorDificultad(dificultad: DificultadMision): string {
  const colores: Record<DificultadMision, string> = {
    facil: 'text-green-600 dark:text-green-400',
    normal: 'text-blue-600 dark:text-blue-400',
    dificil: 'text-purple-600 dark:text-purple-400',
    epica: 'text-orange-600 dark:text-orange-400',
  };
  return colores[dificultad];
}

/**
 * Obtiene el color de fondo de la dificultad
 */
export function obtenerBgDificultad(dificultad: DificultadMision): string {
  const colores: Record<DificultadMision, string> = {
    facil: 'bg-green-100 dark:bg-green-900',
    normal: 'bg-blue-100 dark:bg-blue-900',
    dificil: 'bg-purple-100 dark:bg-purple-900',
    epica: 'bg-orange-100 dark:bg-orange-900',
  };
  return colores[dificultad];
}

/**
 * Obtiene el color del estado de la misión
 */
export function obtenerColorEstado(estado: EstadoMision): string {
  const colores: Record<EstadoMision, string> = {
    disponible: 'text-gray-600 dark:text-gray-400',
    en_progreso: 'text-blue-600 dark:text-blue-400',
    completada: 'text-green-600 dark:text-green-400',
    reclamada: 'text-violet-600 dark:text-violet-400',
    expirada: 'text-red-600 dark:text-red-400',
    bloqueada: 'text-gray-400 dark:text-gray-600',
  };
  return colores[estado];
}

/**
 * Obtiene el texto del estado de la misión
 */
export function obtenerTextoEstado(estado: EstadoMision): string {
  const textos: Record<EstadoMision, string> = {
    disponible: 'Disponible',
    en_progreso: 'En Progreso',
    completada: '¡Completada!',
    reclamada: 'Reclamada',
    expirada: 'Expirada',
    bloqueada: 'Bloqueada',
  };
  return textos[estado];
}

/**
 * Obtiene el icono del tipo de misión
 */
export function obtenerIconoTipo(tipo: TipoMision): string {
  const iconos: Record<TipoMision, string> = {
    participacion: '💬',
    entrega: '📝',
    evaluacion: '📊',
    racha: '🔥',
    social: '👥',
    logro: '🏆',
    puntos: '⭐',
  };
  return iconos[tipo];
}

/**
 * Calcula el progreso en porcentaje
 */
export function calcularPorcentajeProgreso(progreso: number, objetivo: number): number {
  if (objetivo === 0) return 0;
  return Math.min(100, Math.round((progreso / objetivo) * 100));
}

/**
 * Formatea el tiempo restante hasta la expiración
 */
export function formatearTiempoRestante(fechaExpiracion?: string): string {
  if (!fechaExpiracion) return '';
  
  const ahora = new Date();
  const expira = new Date(fechaExpiracion);
  const diff = expira.getTime() - ahora.getTime();
  
  if (diff <= 0) return 'Expirada';
  
  const horas = Math.floor(diff / (1000 * 60 * 60));
  const minutos = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  
  if (horas > 24) {
    const dias = Math.floor(horas / 24);
    return `${dias}d ${horas % 24}h`;
  }
  
  if (horas > 0) {
    return `${horas}h ${minutos}m`;
  }
  
  return `${minutos}m`;
}

// ==================== Servicio de API ====================
class MisionesService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token de autenticación
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  /**
   * Obtiene todas las misiones disponibles agrupadas por frecuencia
   */
  async obtenerMisionesDisponibles(): Promise<MisionesDisponibles> {
    const { data } = await this.client.get<MisionesDisponibles>('/api/misiones/disponibles');
    return data;
  }

  /**
   * Obtiene las misiones del usuario con filtros
   */
  async obtenerMisMisiones(params?: {
    estado?: EstadoMision;
    frecuencia?: FrecuenciaMision;
    skip?: number;
    limit?: number;
  }): Promise<MisionUsuarioConDetalle[]> {
    const { data } = await this.client.get<MisionUsuarioConDetalle[]>('/api/misiones/mis-misiones', {
      params,
    });
    return data;
  }

  /**
   * Obtiene una misión específica del usuario
   */
  async obtenerMision(misionUsuarioId: string): Promise<MisionUsuarioConDetalle> {
    const { data } = await this.client.get<MisionUsuarioConDetalle>(
      `/api/misiones/${misionUsuarioId}`
    );
    return data;
  }

  /**
   * Actualiza el progreso de una misión
   */
  async actualizarProgreso(
    misionUsuarioId: string,
    request: ActualizarProgresoRequest
  ): Promise<MisionUsuarioConDetalle> {
    const { data } = await this.client.patch<MisionUsuarioConDetalle>(
      `/api/misiones/${misionUsuarioId}/progreso`,
      request
    );
    return data;
  }

  /**
   * Reclama la recompensa de una misión completada
   */
  async reclamarRecompensa(misionUsuarioId: string): Promise<MisionUsuarioConDetalle> {
    const { data } = await this.client.post<MisionUsuarioConDetalle>(
      `/api/misiones/${misionUsuarioId}/reclamar`,
      {}
    );
    return data;
  }

  /**
   * Obtiene estadísticas de misiones del usuario
   */
  async obtenerEstadisticas(): Promise<EstadisticasMisiones> {
    const { data } = await this.client.get<EstadisticasMisiones>('/api/misiones/estadisticas');
    return data;
  }

  // ==================== Métodos Administrativos ====================
  /**
   * Obtiene todas las misiones del sistema (Admin)
   */
  async obtenerTodasMisiones(params?: {
    activas_solo?: boolean;
    frecuencia?: FrecuenciaMision;
    skip?: number;
    limit?: number;
  }): Promise<Mision[]> {
    const { data } = await this.client.get<Mision[]>('/api/misiones/admin/todas', { params });
    return data;
  }

  /**
   * Crea una nueva misión (Admin)
   */
  async crearMision(mision: Omit<Mision, 'mision_id' | 'fecha_creacion' | 'fecha_actualizacion'>): Promise<Mision> {
    const { data } = await this.client.post<Mision>('/api/misiones/admin', mision);
    return data;
  }

  /**
   * Actualiza una misión existente (Admin)
   */
  async actualizarMision(misionId: string, mision: Partial<Mision>): Promise<Mision> {
    const { data } = await this.client.put<Mision>(`/api/misiones/admin/${misionId}`, mision);
    return data;
  }

  /**
   * Elimina (desactiva) una misión (Admin)
   */
  async eliminarMision(misionId: string): Promise<void> {
    await this.client.delete(`/api/misiones/admin/${misionId}`);
  }
}

// Exportar instancia única del servicio
export const misionesService = new MisionesService();
export default misionesService;
