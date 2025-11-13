/**
 * Servicio de Gamificación - API Client
 * 
 * @module services/gamificacion
 * @description Cliente HTTP para interactuar con la API de gamificación.
 * Maneja puntos, niveles, ranking, logros e insignias.
 */

import axios, { AxiosInstance } from 'axios';

// ==================== TIPOS ====================

export interface PuntosUsuario {
  puntos_acumulados: number;
  nivel_actual: string;
  nivel_info: NivelInfo;
  historial_reciente: CambioPuntos[];
  insignias_obtenidas: Insignia[];
}

export interface NivelInfo {
  nombre: string;
  numero: number;
  puntos_minimos: number;
  puntos_maximos: number;
  progreso_porcentaje: number;
  puntos_para_siguiente: number;
  color: string;
  icono: string;
}

export interface CambioPuntos {
  id: string;
  puntos: number;
  razon: string;
  fecha: string;
  tipo: 'ganado' | 'perdido';
}

export interface Insignia {
  id: string;
  nombre: string;
  descripcion: string;
  icono: string;
  rareza: RarezaLogro;
  fecha_obtencion: string;
  progreso?: number;
  objetivo?: number;
}

export interface UsuarioRanking {
  posicion: number;
  usuario_id: string;
  nombre: string;
  apellido: string;
  puntos: number;
  nivel: string;
  avatar?: string;
  insignias_count: number;
}

export interface Ranking {
  usuarios: UsuarioRanking[];
  total: number;
  pagina_actual: number;
  total_paginas: number;
}

export interface PosicionRanking {
  posicion: number;
  puntos: number;
  nivel: string;
  puntos_hasta_anterior: number;
  puntos_hasta_siguiente: number;
  total_usuarios: number;
}

export type RarezaLogro = 'común' | 'raro' | 'épico' | 'legendario';

export interface Logro {
  id: string;
  nombre: string;
  descripcion: string;
  icono: string;
  puntos_recompensa: number;
  tipo: 'tarea' | 'participacion' | 'racha' | 'examen' | 'social';
  objetivo: number;
  progreso_actual: number;
  completado: boolean;
  fecha_completado?: string;
  rareza: RarezaLogro;
}

export interface Racha {
  dias_actuales: number;
  mejor_racha: number;
  fecha_inicio: string;
  activa: boolean;
  proxima_actividad: string;
  puntos_por_dia: number;
}

export interface EstadisticasGamificacion {
  puntos_totales: number;
  nivel_actual: string;
  posicion_ranking: number;
  logros_completados: number;
  logros_totales: number;
  insignias_obtenidas: number;
  racha_actual: number;
  tareas_completadas: number;
  participaciones: number;
}

// ==================== CONFIGURACIÓN ====================

const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const GAMIFICACION_PATH = '/api';

/**
 * Cliente de API configurado para gamificación
 */
class GamificacionAPIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${GAMIFICACION_PATH}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token JWT
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para manejar errores
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('Error en API de gamificación:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ==================== PUNTOS ====================

  /**
   * Obtiene los puntos y nivel de un usuario
   */
  async obtenerPuntosUsuario(usuarioId: string): Promise<PuntosUsuario> {
    const { data } = await this.client.get(`/usuarios/${usuarioId}/puntos`);
    return data;
  }

  /**
   * Obtiene los puntos del usuario actual
   */
  async obtenerMisPuntos(): Promise<PuntosUsuario> {
    const { data } = await this.client.get('/usuarios/me/puntos');
    return data;
  }

  // ==================== RANKING ====================

  /**
   * Obtiene el ranking global
   */
  async obtenerRanking(limite: number = 50, offset: number = 0): Promise<Ranking> {
    const { data } = await this.client.get('/usuarios/ranking', {
      params: { limite, offset },
    });
    return data;
  }

  /**
   * Obtiene la posición del usuario actual en el ranking
   */
  async obtenerMiPosicionRanking(): Promise<PosicionRanking> {
    const { data } = await this.client.get('/usuarios/mi-ranking');
    return data.data;
  }

  // ==================== LOGROS ====================

  /**
   * Obtiene todos los logros disponibles
   */
  async obtenerLogros(): Promise<Logro[]> {
    const { data } = await this.client.get('/logros');
    return data;
  }

  /**
   * Obtiene los logros de un usuario
   */
  async obtenerLogrosUsuario(usuarioId: string): Promise<Logro[]> {
    const { data } = await this.client.get(`/usuarios/${usuarioId}/logros`);
    return data;
  }

  /**
   * Obtiene los logros del usuario actual
   */
  async obtenerMisLogros(): Promise<Logro[]> {
    const { data } = await this.client.get('/usuarios/me/logros');
    return data;
  }

  // ==================== INSIGNIAS ====================

  /**
   * Obtiene todas las insignias disponibles
   */
  async obtenerInsignias(): Promise<Insignia[]> {
    const { data } = await this.client.get('/insignias');
    return data;
  }

  /**
   * Obtiene las insignias de un usuario
   */
  async obtenerInsigniasUsuario(usuarioId: string): Promise<Insignia[]> {
    const { data } = await this.client.get(`/usuarios/${usuarioId}/insignias`);
    return data;
  }

  /**
   * Obtiene las insignias del usuario actual
   */
  async obtenerMisInsignias(): Promise<Insignia[]> {
    const { data } = await this.client.get('/usuarios/me/insignias');
    return data;
  }

  // ==================== RACHA ====================

  /**
   * Obtiene la racha actual del usuario
   */
  async obtenerRacha(): Promise<Racha> {
    const { data } = await this.client.get('/usuarios/me/racha');
    return data;
  }

  // ==================== ESTADÍSTICAS ====================

  /**
   * Obtiene las estadísticas generales de gamificación del usuario
   */
  async obtenerEstadisticas(): Promise<EstadisticasGamificacion> {
    const { data } = await this.client.get('/usuarios/me/estadisticas-gamificacion');
    return data;
  }
}

// ==================== EXPORTAR INSTANCIA ÚNICA ====================

export const gamificacionService = new GamificacionAPIClient();
export default gamificacionService;

// ==================== UTILIDADES ====================

/**
 * Obtiene el color asociado a una rareza
 */
export function obtenerColorRareza(rareza: RarezaLogro): string {
  const colores: Record<RarezaLogro, string> = {
    'común': 'text-gray-600',
    'raro': 'text-blue-600',
    'épico': 'text-purple-600',
    'legendario': 'text-yellow-600',
  };
  return colores[rareza] || 'text-gray-600';
}

/**
 * Obtiene el color de fondo asociado a una rareza
 */
export function obtenerBgRareza(rareza: RarezaLogro): string {
  const colores: Record<RarezaLogro, string> = {
    'común': 'bg-gray-100',
    'raro': 'bg-blue-100',
    'épico': 'bg-purple-100',
    'legendario': 'bg-yellow-100',
  };
  return colores[rareza] || 'bg-gray-100';
}

/**
 * Obtiene el color asociado a un nivel
 */
export function obtenerColorNivel(nivel: string): string {
  if (nivel.includes('Platino')) return 'from-cyan-500 to-blue-600';
  if (nivel.includes('Oro')) return 'from-yellow-500 to-orange-600';
  if (nivel.includes('Plata')) return 'from-gray-400 to-gray-600';
  if (nivel.includes('Bronce')) return 'from-orange-700 to-red-800';
  return 'from-gray-500 to-gray-700';
}

/**
 * Formatea puntos con separadores de miles
 */
export function formatearPuntos(puntos: number): string {
  return new Intl.NumberFormat('es-ES').format(puntos);
}
