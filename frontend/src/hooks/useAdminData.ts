/**
 * Hooks para datos de administración
 * Usa React Query para cache y actualizaciones
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import adminService, { AprobarUsuarioRequest, RechazarUsuarioRequest } from '../services/admin.service';
import { useToast } from '../context/ToastContext';

/**
 * Hook para obtener estadísticas del admin
 */
export function useAdminStats() {
  return useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: () => adminService.getStats(),
    staleTime: 1000 * 60 * 5, // 5 minutos
    refetchInterval: 1000 * 60 * 2, // Refrescar cada 2 minutos
  });
}

/**
 * Hook para obtener alertas del sistema
 */
export function useSystemAlerts() {
  return useQuery({
    queryKey: ['admin', 'alerts'],
    queryFn: () => adminService.getAlerts(),
    staleTime: 1000 * 60, // 1 minuto
    refetchInterval: 1000 * 30, // Refrescar cada 30 segundos
  });
}

/**
 * Hook para obtener usuarios pendientes
 */
export function useUsuariosPendientes() {
  return useQuery({
    queryKey: ['admin', 'usuarios-pendientes'],
    queryFn: () => adminService.getUsuariosPendientes(),
    staleTime: 1000 * 60 * 2, // 2 minutos
  });
}

/**
 * Hook para aprobar usuario
 */
export function useAprobarUsuario() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: (data: AprobarUsuarioRequest) => adminService.aprobarUsuario(data),
    onSuccess: (result) => {
      // Invalidar query de usuarios pendientes para refrescar
      queryClient.invalidateQueries({ queryKey: ['admin', 'usuarios-pendientes'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
      showToast(result.message, 'success');
    },
    onError: (error: Error) => {
      showToast(error.message || 'Error al aprobar usuario', 'error');
    },
  });
}

/**
 * Hook para rechazar usuario
 */
export function useRechazarUsuario() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: (data: RechazarUsuarioRequest) => adminService.rechazarUsuario(data),
    onSuccess: (result) => {
      // Invalidar query de usuarios pendientes para refrescar
      queryClient.invalidateQueries({ queryKey: ['admin', 'usuarios-pendientes'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
      showToast(result.message, 'success');
    },
    onError: (error: Error) => {
      showToast(error.message || 'Error al rechazar usuario', 'error');
    },
  });
}

/**
 * Hook para obtener reportes
 */
export function useReportes() {
  return useQuery({
    queryKey: ['admin', 'reportes'],
    queryFn: () => adminService.getReportes(),
    staleTime: 1000 * 60 * 10, // 10 minutos
  });
}

/**
 * Hook para obtener métricas del sistema
 */
export function useSystemMetrics() {
  return useQuery({
    queryKey: ['admin', 'system-metrics'],
    queryFn: () => adminService.getSystemMetrics(),
    staleTime: 1000 * 30, // 30 segundos
    refetchInterval: 1000 * 60, // Refrescar cada minuto
  });
}
