/**
 * Custom Hooks para Gamificación
 * 
 * @module hooks/useGamificacion
 * @description Hooks personalizados para gestionar el estado de gamificación
 * con React Query. Incluye puntos, ranking, logros, insignias y rachas.
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import gamificacionService, {
  PuntosUsuario,
  Ranking,
  PosicionRanking,
  Logro,
  Insignia,
  Racha,
  EstadisticasGamificacion,
} from '../services/gamificacion.service';

// ==================== QUERY KEYS ====================

export const GAMIFICACION_KEYS = {
  all: ['gamificacion'] as const,
  puntos: (usuarioId?: string) => [...GAMIFICACION_KEYS.all, 'puntos', usuarioId] as const,
  misPuntos: () => [...GAMIFICACION_KEYS.all, 'mis-puntos'] as const,
  ranking: (limite: number, offset: number) => [...GAMIFICACION_KEYS.all, 'ranking', limite, offset] as const,
  miPosicion: () => [...GAMIFICACION_KEYS.all, 'mi-posicion'] as const,
  logros: (usuarioId?: string) => [...GAMIFICACION_KEYS.all, 'logros', usuarioId] as const,
  misLogros: () => [...GAMIFICACION_KEYS.all, 'mis-logros'] as const,
  insignias: (usuarioId?: string) => [...GAMIFICACION_KEYS.all, 'insignias', usuarioId] as const,
  misInsignias: () => [...GAMIFICACION_KEYS.all, 'mis-insignias'] as const,
  racha: () => [...GAMIFICACION_KEYS.all, 'racha'] as const,
  estadisticas: () => [...GAMIFICACION_KEYS.all, 'estadisticas'] as const,
};

// ==================== HOOKS - PUNTOS ====================

/**
 * Hook para obtener los puntos de un usuario específico
 */
export function usePuntosUsuario(usuarioId: string): UseQueryResult<PuntosUsuario, Error> {
  return useQuery({
    queryKey: GAMIFICACION_KEYS.puntos(usuarioId),
    queryFn: () => gamificacionService.obtenerPuntosUsuario(usuarioId),
    staleTime: 30000, // 30 segundos
    gcTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para obtener los puntos del usuario actual
 */
export function useMisPuntos(): UseQueryResult<PuntosUsuario, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: GAMIFICACION_KEYS.misPuntos(),
    queryFn: () => gamificacionService.obtenerMisPuntos(),
    enabled: !!user,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
    refetchInterval: 60000, // Auto-refetch cada minuto
  });
}

// ==================== HOOKS - RANKING ====================

/**
 * Hook para obtener el ranking global
 */
export function useRanking(limite: number = 50, offset: number = 0): UseQueryResult<Ranking, Error> {
  return useQuery({
    queryKey: GAMIFICACION_KEYS.ranking(limite, offset),
    queryFn: () => gamificacionService.obtenerRanking(limite, offset),
    staleTime: 60000, // 1 minuto
    gcTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para obtener la posición del usuario actual en el ranking
 */
export function useMiPosicionRanking(): UseQueryResult<PosicionRanking, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: GAMIFICACION_KEYS.miPosicion(),
    queryFn: () => gamificacionService.obtenerMiPosicionRanking(),
    enabled: !!user,
    staleTime: 60000,
    gcTime: 10 * 60 * 1000,
    refetchInterval: 120000, // Auto-refetch cada 2 minutos
  });
}

// ==================== HOOKS - LOGROS ====================

/**
 * Hook para obtener los logros de un usuario específico
 */
export function useLogrosUsuario(usuarioId: string): UseQueryResult<Logro[], Error> {
  return useQuery({
    queryKey: GAMIFICACION_KEYS.logros(usuarioId),
    queryFn: () => gamificacionService.obtenerLogrosUsuario(usuarioId),
    staleTime: 60000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para obtener los logros del usuario actual
 */
export function useMisLogros(): UseQueryResult<Logro[], Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: GAMIFICACION_KEYS.misLogros(),
    queryFn: () => gamificacionService.obtenerMisLogros(),
    enabled: !!user,
    staleTime: 60000,
    gcTime: 10 * 60 * 1000,
  });
}

// ==================== HOOKS - INSIGNIAS ====================

/**
 * Hook para obtener las insignias de un usuario específico
 */
export function useInsigniasUsuario(usuarioId: string): UseQueryResult<Insignia[], Error> {
  return useQuery({
    queryKey: GAMIFICACION_KEYS.insignias(usuarioId),
    queryFn: () => gamificacionService.obtenerInsigniasUsuario(usuarioId),
    staleTime: 60000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para obtener las insignias del usuario actual
 */
export function useMisInsignias(): UseQueryResult<Insignia[], Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: GAMIFICACION_KEYS.misInsignias(),
    queryFn: () => gamificacionService.obtenerMisInsignias(),
    enabled: !!user,
    staleTime: 60000,
    gcTime: 10 * 60 * 1000,
  });
}

// ==================== HOOKS - RACHA ====================

/**
 * Hook para obtener la racha actual del usuario
 */
export function useRacha(): UseQueryResult<Racha, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: GAMIFICACION_KEYS.racha(),
    queryFn: () => gamificacionService.obtenerRacha(),
    enabled: !!user,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
    refetchInterval: 60000, // Auto-refetch cada minuto
  });
}

// ==================== HOOKS - ESTADÍSTICAS ====================

/**
 * Hook para obtener las estadísticas generales de gamificación
 */
export function useEstadisticasGamificacion(): UseQueryResult<EstadisticasGamificacion, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: GAMIFICACION_KEYS.estadisticas(),
    queryFn: () => gamificacionService.obtenerEstadisticas(),
    enabled: !!user,
    staleTime: 60000,
    gcTime: 10 * 60 * 1000,
  });
}

// ==================== HOOK COMBINADO ====================

/**
 * Hook que combina puntos, posición en ranking y racha
 * Ideal para dashboards y vistas resumidas
 */
export function useResumenGamificacion() {
  const puntos = useMisPuntos();
  const posicion = useMiPosicionRanking();
  const racha = useRacha();

  return {
    puntos: puntos.data,
    posicion: posicion.data,
    racha: racha.data,
    isLoading: puntos.isLoading || posicion.isLoading || racha.isLoading,
    isError: puntos.isError || posicion.isError || racha.isError,
    error: puntos.error || posicion.error || racha.error,
  };
}
