/**
 * Hooks de React Query para gestión de Invitaciones
 * Proporciona todas las operaciones con cache, revalidación automática y estados
 */

import { useMutation, useQuery, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import invitacionService from '../services/invitacionService';
import type {
  Invitacion,
  CrearInvitacionDTO,
  AceptarInvitacionDTO,
  RechazarInvitacionDTO,
  FiltrosInvitaciones,
  EstadisticasInvitaciones,
  ValidacionInvitacion,
  RespuestaPaginada,
  HistorialInvitacion,
  RespuestaEnvioInvitacion,
  NotificacionInvitacion,
} from '../types';

/**
 * Tipo para funciones de notificación toast
 * Compatible con el ToastContext del proyecto
 */
interface ToastFunctions {
  success: (title: string, message?: string, duration?: number) => void;
  error: (title: string, message?: string, duration?: number) => void;
  info: (title: string, message?: string, duration?: number) => void;
  warning: (title: string, message?: string, duration?: number) => void;
}

// ============================================
// QUERY KEYS - Centralización de claves
// ============================================

export const invitacionesKeys = {
  all: ['invitaciones'] as const,
  lists: () => [...invitacionesKeys.all, 'list'] as const,
  list: (filtros?: FiltrosInvitaciones) => 
    [...invitacionesKeys.lists(), filtros] as const,
  details: () => [...invitacionesKeys.all, 'detail'] as const,
  detail: (id: number) => [...invitacionesKeys.details(), id] as const,
  estadisticas: (institucionId?: number) => 
    [...invitacionesKeys.all, 'estadisticas', institucionId] as const,
  historial: (id: number) => [...invitacionesKeys.all, 'historial', id] as const,
  notificaciones: () => [...invitacionesKeys.all, 'notificaciones'] as const,
  validacion: (token: string) => [...invitacionesKeys.all, 'validacion', token] as const,
  porInstitucion: (institucionId: number, filtros?: FiltrosInvitaciones) =>
    [...invitacionesKeys.all, 'institucion', institucionId, filtros] as const,
};

// ============================================
// QUERIES - Obtención de datos
// ============================================

/**
 * Hook para obtener lista de invitaciones con filtros
 */
export function useInvitaciones(
  filtros?: FiltrosInvitaciones,
  options?: Omit<UseQueryOptions<RespuestaPaginada<Invitacion>>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: invitacionesKeys.list(filtros),
    queryFn: () => invitacionService.getAll(filtros),
    staleTime: 1000 * 60 * 2, // 2 minutos
    ...options,
  });
}

/**
 * Hook para obtener una invitación por ID
 */
export function useInvitacion(
  id: number,
  options?: Omit<UseQueryOptions<Invitacion>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: invitacionesKeys.detail(id),
    queryFn: () => invitacionService.getById(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutos
    ...options,
  });
}

/**
 * Hook para validar token de invitación (público)
 */
export function useValidarToken(
  token: string,
  options?: Omit<UseQueryOptions<ValidacionInvitacion>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: invitacionesKeys.validacion(token),
    queryFn: () => invitacionService.validarToken(token),
    enabled: !!token,
    retry: 1,
    staleTime: 0, // Siempre validar
    ...options,
  });
}

/**
 * Hook para obtener estadísticas de invitaciones
 */
export function useEstadisticasInvitaciones(
  institucionId?: number,
  options?: Omit<UseQueryOptions<EstadisticasInvitaciones>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: invitacionesKeys.estadisticas(institucionId),
    queryFn: () => invitacionService.getEstadisticas(institucionId),
    staleTime: 1000 * 60 * 5, // 5 minutos
    ...options,
  });
}

/**
 * Hook para obtener historial de una invitación
 */
export function useHistorialInvitacion(
  id: number,
  options?: Omit<UseQueryOptions<HistorialInvitacion[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: invitacionesKeys.historial(id),
    queryFn: () => invitacionService.getHistorial(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutos
    ...options,
  });
}

/**
 * Hook para obtener notificaciones de invitaciones del usuario
 */
export function useNotificacionesInvitacion(
  options?: Omit<UseQueryOptions<NotificacionInvitacion[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: invitacionesKeys.notificaciones(),
    queryFn: () => invitacionService.getMisInvitaciones(),
    staleTime: 1000 * 30, // 30 segundos
    refetchInterval: 1000 * 60, // Refetch cada minuto
    ...options,
  });
}

/**
 * Hook para obtener invitaciones de una institución
 */
export function useInvitacionesPorInstitucion(
  institucionId: number,
  filtros?: Omit<FiltrosInvitaciones, 'institucionId'>,
  options?: Omit<UseQueryOptions<RespuestaPaginada<Invitacion>>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: invitacionesKeys.porInstitucion(institucionId, filtros),
    queryFn: () => invitacionService.getPorInstitucion(institucionId, filtros),
    enabled: !!institucionId,
    staleTime: 1000 * 60 * 2, // 2 minutos
    ...options,
  });
}

// ============================================
// MUTATIONS - Modificación de datos
// ============================================

/**
 * Hook para crear nueva invitación
 */
export function useCrearInvitacion(toast: ToastFunctions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (dto: CrearInvitacionDTO) => invitacionService.crear(dto),
    onSuccess: (data: RespuestaEnvioInvitacion) => {
      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: invitacionesKeys.lists() });
      queryClient.invalidateQueries({ queryKey: invitacionesKeys.estadisticas() });

      // Mostrar notificación
      if (data.emailEnviado) {
        toast.success(
          'Invitación enviada',
          `Email enviado a ${data.invitacion.email}. Código: ${data.invitacion.codigo}`,
          5000
        );
      } else {
        toast.warning(
          'Invitación creada',
          `No se pudo enviar el email. Código: ${data.invitacion.codigo}`,
          7000
        );
      }
    },
    onError: (error: Error) => {
      toast.error('Error al crear invitación', error.message);
    },
  });
}

/**
 * Hook para reenviar invitación
 */
export function useReenviarInvitacion(toast: ToastFunctions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => invitacionService.reenviar(id),
    onSuccess: (data: RespuestaEnvioInvitacion, id: number) => {
      // Actualizar cache
      queryClient.invalidateQueries({ queryKey: invitacionesKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: invitacionesKeys.lists() });
      queryClient.invalidateQueries({ queryKey: invitacionesKeys.historial(id) });

      // Notificación
      if (data.emailEnviado) {
        toast.success(
          'Invitación reenviada',
          `Nuevo código: ${data.invitacion.codigo}`
        );
      } else {
        toast.error('Error', 'No se pudo reenviar el email');
      }
    },
    onError: (error: Error) => {
      toast.error('Error al reenviar', error.message);
    },
  });
}

/**
 * Hook para cancelar invitación
 */
export function useCancelarInvitacion(toast: ToastFunctions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => invitacionService.cancelar(id),
    onSuccess: (data: Invitacion) => {
      // Actualizar cache
      queryClient.setQueryData(invitacionesKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: invitacionesKeys.lists() });
      queryClient.invalidateQueries({ queryKey: invitacionesKeys.estadisticas() });

      toast.success('Invitación cancelada', 'La invitación ha sido cancelada exitosamente');
    },
    onError: (error: Error) => {
      toast.error('Error al cancelar', error.message);
    },
  });
}

/**
 * Hook para aceptar invitación (público)
 */
export function useAceptarInvitacion(toast: ToastFunctions) {
  return useMutation({
    mutationFn: (dto: AceptarInvitacionDTO) => invitacionService.aceptar(dto),
    onSuccess: (data) => {
      toast.success(
        '¡Bienvenido!',
        `${data.usuario.nombre}, tu cuenta ha sido creada exitosamente.`,
        5000
      );
      
      // Redirigir al dashboard después de un breve delay
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
    },
    onError: (error: Error) => {
      if (error.message.includes('código')) {
        toast.error('Código incorrecto', 'Verifica e intenta nuevamente.');
      } else if (error.message.includes('expirado')) {
        toast.error('Invitación expirada', 'Contacta al administrador.');
      } else {
        toast.error('Error', error.message);
      }
    },
  });
}

/**
 * Hook para rechazar invitación (público)
 */
export function useRechazarInvitacion(toast: ToastFunctions) {
  return useMutation({
    mutationFn: (dto: RechazarInvitacionDTO) => invitacionService.rechazar(dto),
    onSuccess: () => {
      toast.info('Invitación rechazada', 'Has rechazado la invitación');
      
      // Redirigir a home
      setTimeout(() => {
        window.location.href = '/';
      }, 1500);
    },
    onError: (error: Error) => {
      toast.error('Error al rechazar', error.message);
    },
  });
}

/**
 * Hook para marcar notificación como leída
 */
export function useMarcarNotificacionLeida() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificacionId: number) => 
      invitacionService.marcarLeida(notificacionId),
    onSuccess: () => {
      // Refetch notificaciones
      queryClient.invalidateQueries({ 
        queryKey: invitacionesKeys.notificaciones() 
      });
    },
    onError: (error: Error) => {
      console.error('Error al marcar notificación:', error);
    },
  });
}

// ============================================
// HOOK COMBINADO - Operaciones agrupadas
// ============================================

/**
 * Hook que agrupa todas las operaciones de invitaciones
 * Útil para componentes que necesitan múltiples operaciones
 */
export function useInvitacionOperations(toast: ToastFunctions) {
  const crear = useCrearInvitacion(toast);
  const reenviar = useReenviarInvitacion(toast);
  const cancelar = useCancelarInvitacion(toast);
  const aceptar = useAceptarInvitacion(toast);
  const rechazar = useRechazarInvitacion(toast);
  const marcarLeida = useMarcarNotificacionLeida();

  return {
    crear,
    reenviar,
    cancelar,
    aceptar,
    rechazar,
    marcarLeida,
    isLoading:
      crear.isPending ||
      reenviar.isPending ||
      cancelar.isPending ||
      aceptar.isPending ||
      rechazar.isPending ||
      marcarLeida.isPending,
  };
}

// ============================================
// HELPERS - Funciones auxiliares
// ============================================

/**
 * Hook para prefetch de invitaciones
 * Útil para mejorar UX al navegar
 */
export function usePrefetchInvitacion() {
  const queryClient = useQueryClient();

  return (id: number) => {
    queryClient.prefetchQuery({
      queryKey: invitacionesKeys.detail(id),
      queryFn: () => invitacionService.getById(id),
      staleTime: 1000 * 60 * 5,
    });
  };
}

/**
 * Hook para invalidar todas las queries de invitaciones
 * Útil después de operaciones masivas
 */
export function useInvalidateInvitaciones() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ 
      queryKey: invitacionesKeys.all 
    });
  };
}

export default {
  useInvitaciones,
  useInvitacion,
  useValidarToken,
  useEstadisticasInvitaciones,
  useHistorialInvitacion,
  useNotificacionesInvitacion,
  useInvitacionesPorInstitucion,
  useCrearInvitacion,
  useReenviarInvitacion,
  useCancelarInvitacion,
  useAceptarInvitacion,
  useRechazarInvitacion,
  useMarcarNotificacionLeida,
  useInvitacionOperations,
  usePrefetchInvitacion,
  useInvalidateInvitaciones,
};
