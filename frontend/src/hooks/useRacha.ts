/**
 * Hook personalizado para gestionar el sistema de rachas
 */
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/api.config';

interface RachaState {
  usuario_id: string;
  racha_actual: number;
  mejor_racha: number;
  fecha_ultimo_dia: string | null;
  ya_registro_hoy: boolean;
  en_riesgo: boolean;
  dia_ciclo_actual: number;
  proxima_recompensa: {
    dia: number;
    puntos: number;
    mensaje: string;
  };
  recuperaciones_disponibles: number;
  dias_para_proxima_recuperacion: number;
  racha_congelada_hasta: string | null;
  esta_congelada: boolean;
}

interface RegistroRachaResponse {
  ya_registrado_hoy: boolean;
  racha_actual: number;
  mejor_racha: number;
  dia_ciclo: number;
  puntos_obtenidos: number;
  mensaje: string;
  proxima_recompensa_dia: number;
  es_nuevo_record: boolean;
}

interface UseRachaReturn {
  rachaState: RachaState | null;
  loading: boolean;
  error: string | null;
  registrarAccesoDiario: () => Promise<RegistroRachaResponse | null>;
  usarRecuperacion: () => Promise<void>;
  obtenerHistorial: () => Promise<any[]>;
  recargarEstado: () => Promise<void>;
}

export const useRacha = (): UseRachaReturn => {
  const [rachaState, setRachaState] = useState<RachaState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Obtiene el token de autenticación
   */
  const getAuthToken = (): string | null => {
    return localStorage.getItem('access_token');
  };

  /**
   * Obtiene el estado actual de la racha
   */
  const obtenerEstado = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = getAuthToken();
      if (!token) {
        throw new Error('No hay sesión activa');
      }

      const response = await axios.get(
        `${API_BASE_URL}/api/gamification/rachas/mi-racha`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setRachaState(response.data);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al obtener estado de racha';
      setError(errorMsg);
      console.error('Error obteniendo estado de racha:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Registra el acceso diario del usuario
   */
  const registrarAccesoDiario = useCallback(async (): Promise<RegistroRachaResponse | null> => {
    try {
      const token = getAuthToken();
      if (!token) {
        throw new Error('No hay sesión activa');
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/gamification/rachas/registrar`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      // Actualizar estado local
      await obtenerEstado();

      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al registrar acceso diario';
      setError(errorMsg);
      console.error('Error registrando acceso diario:', err);
      return null;
    }
  }, [obtenerEstado]);

  /**
   * Usa una recuperación de racha
   */
  const usarRecuperacion = useCallback(async (): Promise<void> => {
    try {
      const token = getAuthToken();
      if (!token) {
        throw new Error('No hay sesión activa');
      }

      await axios.post(
        `${API_BASE_URL}/api/gamification/rachas/usar-recuperacion`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      // Actualizar estado local
      await obtenerEstado();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al usar recuperación';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, [obtenerEstado]);

  /**
   * Obtiene el historial de rachas
   */
  const obtenerHistorial = useCallback(async (limite: number = 10): Promise<any[]> => {
    try {
      const token = getAuthToken();
      if (!token) {
        throw new Error('No hay sesión activa');
      }

      const response = await axios.get(
        `${API_BASE_URL}/api/gamification/rachas/historial`,
        {
          params: { limite },
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      return response.data.historial || [];
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al obtener historial';
      setError(errorMsg);
      console.error('Error obteniendo historial:', err);
      return [];
    }
  }, []);

  /**
   * Recarga el estado de la racha
   */
  const recargarEstado = useCallback(async (): Promise<void> => {
    await obtenerEstado();
  }, [obtenerEstado]);

  // Cargar estado inicial al montar el componente
  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      obtenerEstado();
    } else {
      setLoading(false);
    }
  }, [obtenerEstado]);

  return {
    rachaState,
    loading,
    error,
    registrarAccesoDiario,
    usarRecuperacion,
    obtenerHistorial,
    recargarEstado
  };
};

export default useRacha;
