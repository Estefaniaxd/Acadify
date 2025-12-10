/**
 * Custom Hooks para Notificaciones
 * 
 * @module hooks/useNotificaciones
 * @description Hooks personalizados para gestionar el estado de notificaciones
 * con React Query. Incluye polling automático, SSE en tiempo real y actualizaciones.
 */

import { useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config/api.config';
import notificacionesService, {
  Notificacion,
  ConfiguracionNotificaciones,
  FiltrosNotificaciones,
} from '../services/notificaciones.service';

// ==================== QUERY KEYS ====================

export const NOTIFICACIONES_KEYS = {
  all: ['notificaciones'] as const,
  list: (filtros?: FiltrosNotificaciones) => [...NOTIFICACIONES_KEYS.all, 'list', filtros] as const,
  count: () => [...NOTIFICACIONES_KEYS.all, 'count'] as const,
  config: () => [...NOTIFICACIONES_KEYS.all, 'config'] as const,
};

// ==================== HOOKS - NOTIFICACIONES ====================

/**
 * Hook para obtener notificaciones con filtros opcionales
 * Incluye auto-refetch cada 30 segundos
 * ✨ NUEVO: Integración con SSE para actualizaciones en tiempo real
 */
export function useNotificaciones(
  filtros?: FiltrosNotificaciones
): UseQueryResult<Notificacion[], Error> {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);

  const query = useQuery({
    queryKey: ['notificaciones', 'list', filtros],
    queryFn: () => notificacionesService.obtenerNotificaciones(filtros),
    enabled: !!user,
    staleTime: 20000, // 20 segundos
    gcTime: 5 * 60 * 1000, // 5 minutos
    refetchInterval: 30000, // Auto-refetch cada 30 segundos
    refetchOnWindowFocus: true,
  });

  // Conectar a SSE para actualizaciones en tiempo real
  useEffect(() => {
    if (!user?.id) return;

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('No hay token disponible para conectar SSE de notificaciones');
        return;
      }

      const eventSource = new EventSource(
        `${API_BASE_URL}/api/communication/notificaciones/sse?usuario_id=${user.id}&token=${token}`
      );

      eventSource.onmessage = (event) => {
        try {
          const nuevaNotificacion: Notificacion = JSON.parse(event.data);
          console.log('📨 Nueva notificación en tiempo real:', nuevaNotificacion);

          // Invalidar query para refrescar
          queryClient.invalidateQueries({ queryKey: ['notificaciones'] });
        } catch (error) {
          console.error('Error procesando SSE:', error);
        }
      };

      eventSource.onerror = () => {
        console.warn('Conexión SSE cerrada, intentando reconectar...');
        eventSource.close();
      };

      eventSourceRef.current = eventSource;
    } catch (error) {
      console.error('Error conectando SSE:', error);
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [user?.id, queryClient]);

  return query;
}

/**
 * Hook para obtener el contador de notificaciones no leídas
 * Incluye auto-refetch cada 10 segundos para mantener actualizado el badge
 */
export function useContadorNoLeidas(): UseQueryResult<number, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: NOTIFICACIONES_KEYS.count(),
    queryFn: () => notificacionesService.obtenerContadorNoLeidas(),
    enabled: !!user,
    staleTime: 5000, // 5 segundos
    gcTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 10000, // Auto-refetch cada 10 segundos
    refetchOnWindowFocus: true,
  });
}

/**
 * Hook para marcar notificaciones como leídas
 */
export function useMarcarComoLeidas() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificacionesIds: string[]) =>
      notificacionesService.marcarComoLeidas(notificacionesIds),
    onSuccess: () => {
      // Invalidar todas las queries de notificaciones
      queryClient.invalidateQueries({ queryKey: NOTIFICACIONES_KEYS.all });
    },
  });
}

/**
 * Hook para marcar todas las notificaciones como leídas
 */
export function useMarcarTodasLeidas() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (tipoNotificacion?: string) =>
      notificacionesService.marcarTodasLeidas(tipoNotificacion as any),
    onSuccess: () => {
      // Invalidar todas las queries de notificaciones
      queryClient.invalidateQueries({ queryKey: NOTIFICACIONES_KEYS.all });
    },
  });
}

// ==================== HOOKS - CONFIGURACIÓN ====================

/**
 * Hook para obtener la configuración de notificaciones
 */
export function useConfiguracionNotificaciones(): UseQueryResult<
  ConfiguracionNotificaciones,
  Error
> {
  const { user } = useAuth();

  return useQuery({
    queryKey: NOTIFICACIONES_KEYS.config(),
    queryFn: () => notificacionesService.obtenerConfiguracion(),
    enabled: !!user,
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para actualizar la configuración de notificaciones
 */
export function useActualizarConfiguracion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Partial<ConfiguracionNotificaciones>) =>
      notificacionesService.actualizarConfiguracion(config),
    onSuccess: (data) => {
      // Actualizar cache con los nuevos datos
      queryClient.setQueryData(NOTIFICACIONES_KEYS.config(), data);
    },
  });
}

// ==================== HOOK COMBINADO ====================

/**
 * Hook que combina notificaciones y contador
 * Ideal para el centro de notificaciones
 */
export function useCentroNotificaciones(filtros?: FiltrosNotificaciones) {
  const notificaciones = useNotificaciones(filtros);
  const contador = useContadorNoLeidas();
  const marcarLeidas = useMarcarComoLeidas();
  const marcarTodasLeidas = useMarcarTodasLeidas();

  return {
    notificaciones: notificaciones.data || [],
    contador: contador.data || 0,
    isLoading: notificaciones.isLoading || contador.isLoading,
    isError: notificaciones.isError || contador.isError,
    error: notificaciones.error || contador.error,
    refetch: () => {
      notificaciones.refetch();
      contador.refetch();
    },
    marcarComoLeidas: marcarLeidas.mutate,
    marcarTodasLeidas: marcarTodasLeidas.mutate,
    isMarkingRead: marcarLeidas.isPending || marcarTodasLeidas.isPending,
  };
}

// ==================== HOOK DE NOTIFICACIONES PUSH ====================

/**
 * Hook para solicitar permisos de notificaciones push del navegador
 */
export function useNotificacionesPush() {
  const solicitarPermiso = async (): Promise<boolean> => {
    if (!('Notification' in window)) {
      console.warn('Este navegador no soporta notificaciones de escritorio');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }

    return false;
  };

  const mostrarNotificacion = (titulo: string, opciones?: NotificationOptions) => {
    if (Notification.permission === 'granted') {
      new Notification(titulo, {
        icon: '/logo.png',
        badge: '/badge.png',
        ...opciones,
      });
    }
  };

  return {
    permiso: typeof window !== 'undefined' && 'Notification' in window 
      ? Notification.permission 
      : 'denied',
    solicitarPermiso,
    mostrarNotificacion,
    soportado: typeof window !== 'undefined' && 'Notification' in window,
  };
}

// ==================== HOOK DE SONIDO ====================

/**
 * Hook para reproducir sonido de notificación
 */
export function useSonidoNotificacion() {
  const reproducir = (tipo: 'mensaje' | 'tarea' | 'logro' = 'mensaje') => {
    try {
      // Mapeo de tipos a archivos de sonido
      const sonidos = {
        mensaje: '/sounds/notification-message.mp3',
        tarea: '/sounds/notification-task.mp3',
        logro: '/sounds/notification-achievement.mp3',
      };

      const audio = new Audio(sonidos[tipo]);
      audio.volume = 0.5;
      audio.play().catch((error) => {
        console.warn('No se pudo reproducir el sonido:', error);
      });
    } catch (error) {
      console.error('Error al reproducir sonido:', error);
    }
  };

  return { reproducir };
}
