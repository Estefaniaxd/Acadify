/**
 * Custom Hooks para Sistema de Misiones
 * 
 * @module hooks/useMisiones
 * @description Hooks personalizados para gestionar misiones diarias, semanales,
 * mensuales y únicas con React Query.
 */

import { useMutation, useQuery, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import misionesService, {
  ActualizarProgresoRequest,
  EstadisticasMisiones,
  MisionesDisponibles,
  MisionUsuarioConDetalle,
  EstadoMision,
  FrecuenciaMision,
} from '../services/misiones.service';

// ==================== QUERY KEYS ====================

export const MISIONES_KEYS = {
  all: ['misiones'] as const,
  disponibles: () => [...MISIONES_KEYS.all, 'disponibles'] as const,
  misMisiones: (estado?: EstadoMision, frecuencia?: FrecuenciaMision) =>
    [...MISIONES_KEYS.all, 'mis-misiones', estado, frecuencia] as const,
  mision: (misionUsuarioId: string) => [...MISIONES_KEYS.all, 'mision', misionUsuarioId] as const,
  estadisticas: () => [...MISIONES_KEYS.all, 'estadisticas'] as const,
};

// ==================== HOOKS - CONSULTAS ====================

/**
 * Hook para obtener todas las misiones disponibles agrupadas por frecuencia
 * @returns Misiones diarias, semanales, mensuales y únicas disponibles
 */
export function useMisionesDisponibles(): UseQueryResult<MisionesDisponibles, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: MISIONES_KEYS.disponibles(),
    queryFn: () => misionesService.obtenerMisionesDisponibles(),
    enabled: !!user,
    staleTime: 30000, // 30 segundos - se actualiza con frecuencia
    gcTime: 5 * 60 * 1000, // 5 minutos
    refetchInterval: 60000, // Auto-refetch cada minuto
    refetchOnWindowFocus: true,
  });
}

/**
 * Hook para obtener las misiones del usuario con filtros
 * @param estado - Filtrar por estado de misión
 * @param frecuencia - Filtrar por frecuencia de misión
 */
export function useMisMisiones(
  estado?: EstadoMision,
  frecuencia?: FrecuenciaMision
): UseQueryResult<MisionUsuarioConDetalle[], Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: MISIONES_KEYS.misMisiones(estado, frecuencia),
    queryFn: () => misionesService.obtenerMisMisiones({ estado, frecuencia }),
    enabled: !!user,
    staleTime: 20000, // 20 segundos
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para obtener misiones diarias
 */
export function useMisionesDiarias(): UseQueryResult<MisionUsuarioConDetalle[], Error> {
  return useMisMisiones(undefined, 'diaria');
}

/**
 * Hook para obtener misiones semanales
 */
export function useMisionesSemanales(): UseQueryResult<MisionUsuarioConDetalle[], Error> {
  return useMisMisiones(undefined, 'semanal');
}

/**
 * Hook para obtener misiones mensuales
 */
export function useMisionesMensuales(): UseQueryResult<MisionUsuarioConDetalle[], Error> {
  return useMisMisiones(undefined, 'mensual');
}

/**
 * Hook para obtener misiones completadas
 */
export function useMisionesCompletadas(): UseQueryResult<MisionUsuarioConDetalle[], Error> {
  return useMisMisiones('completada');
}

/**
 * Hook para obtener misiones en progreso
 */
export function useMisionesEnProgreso(): UseQueryResult<MisionUsuarioConDetalle[], Error> {
  return useMisMisiones('en_progreso');
}

/**
 * Hook para obtener una misión específica
 * @param misionUsuarioId - ID de la misión del usuario
 */
export function useMision(misionUsuarioId: string | null): UseQueryResult<MisionUsuarioConDetalle, Error> {
  return useQuery({
    queryKey: MISIONES_KEYS.mision(misionUsuarioId || ''),
    queryFn: () => misionesService.obtenerMision(misionUsuarioId!),
    enabled: !!misionUsuarioId,
    staleTime: 10000, // 10 segundos
    gcTime: 2 * 60 * 1000,
  });
}

/**
 * Hook para obtener estadísticas de misiones del usuario
 */
export function useEstadisticasMisiones(): UseQueryResult<EstadisticasMisiones, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: MISIONES_KEYS.estadisticas(),
    queryFn: () => misionesService.obtenerEstadisticas(),
    enabled: !!user,
    staleTime: 60000, // 1 minuto
    gcTime: 10 * 60 * 1000,
  });
}

// ==================== HOOKS - MUTACIONES ====================

/**
 * Hook para actualizar el progreso de una misión
 */
export function useActualizarProgreso() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      misionUsuarioId,
      request,
    }: {
      misionUsuarioId: string;
      request: ActualizarProgresoRequest;
    }) => misionesService.actualizarProgreso(misionUsuarioId, request),

    onSuccess: (data) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.disponibles() });
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.misMisiones() });
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.mision(data.mision_usuario_id) });
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.estadisticas() });

      // Notificar al usuario
      if (data.estado === 'completada') {
        toast.success(
          `🎉 ¡Misión completada! "${data.mision.nombre}"`,
          {
            duration: 4000,
            icon: '🏆',
          }
        );
      } else {
        toast.success('Progreso actualizado', {
          duration: 2000,
        });
      }
    },

    onError: (error: Error) => {
      toast.error(`Error al actualizar progreso: ${error.message}`);
    },
  });
}

/**
 * Hook para reclamar la recompensa de una misión completada
 */
export function useReclamarRecompensa() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (misionUsuarioId: string) =>
      misionesService.reclamarRecompensa(misionUsuarioId),

    onSuccess: (data) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.disponibles() });
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.misMisiones() });
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.mision(data.mision_usuario_id) });
      queryClient.invalidateQueries({ queryKey: MISIONES_KEYS.estadisticas() });

      // También invalidar puntos y gamificación general
      queryClient.invalidateQueries({ queryKey: ['gamificacion', 'mis-puntos'] });
      queryClient.invalidateQueries({ queryKey: ['gamificacion', 'estadisticas'] });

      // Notificar al usuario
      const { puntos_recompensa, experiencia_recompensa } = data.mision;
      const recompensas = [];
      
      if (puntos_recompensa > 0) {
        recompensas.push(`+${puntos_recompensa} puntos`);
      }
      if (experiencia_recompensa > 0) {
        recompensas.push(`+${experiencia_recompensa} XP`);
      }

      toast.success(
        `✨ ¡Recompensa reclamada!\n${recompensas.join(' | ')}`,
        {
          duration: 5000,
          icon: '💎',
        }
      );
    },

    onError: (error: Error) => {
      toast.error(`Error al reclamar recompensa: ${error.message}`);
    },
  });
}

// ==================== HOOKS COMBINADOS ====================

/**
 * Hook combinado que obtiene toda la información de misiones necesaria
 * para la página principal de misiones
 */
export function useResumenMisiones() {
  const disponibles = useMisionesDisponibles();
  const estadisticas = useEstadisticasMisiones();

  return {
    disponibles: disponibles.data,
    estadisticas: estadisticas.data,
    isLoading: disponibles.isLoading || estadisticas.isLoading,
    isError: disponibles.isError || estadisticas.isError,
    error: disponibles.error || estadisticas.error,
    refetch: () => {
      disponibles.refetch();
      estadisticas.refetch();
    },
  };
}

/**
 * Hook para verificar si hay misiones completadas pendientes de reclamar
 */
export function useMisionesPendientesReclamar() {
  const misiones = useMisMisiones('completada');

  return {
    cantidad: misiones.data?.length || 0,
    misiones: misiones.data || [],
    isLoading: misiones.isLoading,
  };
}

/**
 * Hook para obtener el conteo de misiones por estado
 */
export function useConteoMisiones() {
  const disponibles = useMisionesDisponibles();
  const enProgreso = useMisionesEnProgreso();
  const completadas = useMisionesCompletadas();

  return {
    disponibles: disponibles.data?.total_disponibles || 0,
    enProgreso: enProgreso.data?.length || 0,
    completadas: completadas.data?.length || 0,
    completadasHoy: disponibles.data?.total_completadas_hoy || 0,
    isLoading: disponibles.isLoading || enProgreso.isLoading || completadas.isLoading,
  };
}

// ==================== EXPORTS ====================

export default {
  useMisionesDisponibles,
  useMisMisiones,
  useMisionesDiarias,
  useMisionesSemanales,
  useMisionesMensuales,
  useMisionesCompletadas,
  useMisionesEnProgreso,
  useMision,
  useEstadisticasMisiones,
  useActualizarProgreso,
  useReclamarRecompensa,
  useResumenMisiones,
  useMisionesPendientesReclamar,
  useConteoMisiones,
};
