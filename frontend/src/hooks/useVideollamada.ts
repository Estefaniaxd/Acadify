/**
 * Custom Hook para Videollamadas
 * 
 * @module hooks/useVideollamada
 * @description Hook que maneja el estado y operaciones de videollamadas.
 * Incluye integración con React Query para caching y sincronización.
 */

import { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { videollamadasAPI, calcularCalidadConexion } from '../services/videollamadas.service';
import type {
  Videollamada,
  VideollamadaCreateRequest,
  Participante,
  CalidadConexion,
  ListarVideollamadasOptions,
} from '../types/videollamada.types';

// ==================== QUERY KEYS ====================

export const VIDEOLLAMADAS_KEYS = {
  all: ['videollamadas'] as const,
  lists: () => [...VIDEOLLAMADAS_KEYS.all, 'list'] as const,
  list: (filters: ListarVideollamadasOptions) => [...VIDEOLLAMADAS_KEYS.lists(), filters] as const,
  details: () => [...VIDEOLLAMADAS_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...VIDEOLLAMADAS_KEYS.details(), id] as const,
  participantes: (id: string) => [...VIDEOLLAMADAS_KEYS.detail(id), 'participantes'] as const,
  grabaciones: (id: string) => [...VIDEOLLAMADAS_KEYS.detail(id), 'grabaciones'] as const,
};

// ==================== HOOK PRINCIPAL ====================

/**
 * Hook para gestionar una videollamada específica
 */
export function useVideollamada(videollamadaId: string | null) {
  const queryClient = useQueryClient();

  // Query para obtener datos de videollamada
  const {
    data: videollamada,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: VIDEOLLAMADAS_KEYS.detail(videollamadaId!),
    queryFn: () => videollamadasAPI.obtenerVideollamada(videollamadaId!, true),
    enabled: !!videollamadaId,
    staleTime: 30000, // 30 segundos
    refetchInterval: 60000, // Refetch cada minuto
  });

  // Query para participantes activos
  const {
    data: participantes = [],
    refetch: refetchParticipantes,
  } = useQuery({
    queryKey: VIDEOLLAMADAS_KEYS.participantes(videollamadaId!),
    queryFn: () => videollamadasAPI.obtenerParticipantesActivos(videollamadaId!),
    enabled: !!videollamadaId,
    refetchInterval: 10000, // Refetch cada 10 segundos
  });

  // Mutation para unirse
  const unirse = useMutation({
    mutationFn: (esModerador: boolean = false) =>
      videollamadasAPI.unirseAVideollamada(videollamadaId!, esModerador),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VIDEOLLAMADAS_KEYS.detail(videollamadaId!) });
      queryClient.invalidateQueries({ queryKey: VIDEOLLAMADAS_KEYS.participantes(videollamadaId!) });
    },
  });

  // Mutation para salir
  const salir = useMutation({
    mutationFn: () => videollamadasAPI.salirDeVideollamada(videollamadaId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VIDEOLLAMADAS_KEYS.detail(videollamadaId!) });
      queryClient.invalidateQueries({ queryKey: VIDEOLLAMADAS_KEYS.participantes(videollamadaId!) });
    },
  });

  // Mutation para finalizar
  const finalizar = useMutation({
    mutationFn: (resumenIA?: string) =>
      videollamadasAPI.finalizarVideollamada(videollamadaId!, resumenIA),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VIDEOLLAMADAS_KEYS.detail(videollamadaId!) });
    },
  });

  return {
    videollamada,
    participantes,
    isLoading,
    error,
    refetch,
    refetchParticipantes,
    unirse: unirse.mutateAsync,
    salir: salir.mutateAsync,
    finalizar: finalizar.mutateAsync,
    isUniendo: unirse.isPending,
    isSaliendo: salir.isPending,
    isFinalizando: finalizar.isPending,
  };
}

// ==================== HOOK PARA LISTAR ====================

/**
 * Hook para listar videollamadas con filtros
 */
export function useVideollamadas(options: ListarVideollamadasOptions = {}) {
  const queryClient = useQueryClient();

  const {
    data: response,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: VIDEOLLAMADAS_KEYS.list(options),
    queryFn: () => videollamadasAPI.listarVideollamadas(options),
    staleTime: 60000, // 1 minuto
  });

  // Mutation para crear videollamada
  const crear = useMutation({
    mutationFn: (data: VideollamadaCreateRequest) =>
      videollamadasAPI.crearVideollamada(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VIDEOLLAMADAS_KEYS.lists() });
    },
  });

  return {
    videollamadas: response?.items || [],
    total: response?.total || 0,
    hasMore: response?.has_more || false,
    isLoading,
    error,
    refetch,
    crear: crear.mutateAsync,
    isCreando: crear.isPending,
  };
}

// ==================== HOOK PARA CALIDAD DE CONEXIÓN ====================

/**
 * Hook para monitorear y actualizar calidad de conexión
 */
export function useCalidadConexion(participanteId: string | null) {
  const [calidad, setCalidad] = useState<CalidadConexion | null>(null);
  const [metricas, setMetricas] = useState<{
    latencia: number;
    perdidaPaquetes: number;
  } | null>(null);

  const actualizarCalidad = useMutation({
    mutationFn: (data: { latencia_ms: number; perdida_paquetes_pct: number }) =>
      videollamadasAPI.actualizarCalidadConexion(participanteId!, data),
    onSuccess: (participante) => {
      if (participante.calidad_conexion) {
        setCalidad(participante.calidad_conexion);
      }
    },
  });

  const reportarMetricas = useCallback(
    (latenciaMs: number, perdidaPaquetes: number) => {
      setMetricas({ latencia: latenciaMs, perdidaPaquetes });
      
      // Calcular calidad
      const nuevaCalidad = calcularCalidadConexion(latenciaMs, perdidaPaquetes);
      setCalidad(nuevaCalidad as CalidadConexion);

      // Actualizar en servidor
      if (participanteId) {
        actualizarCalidad.mutate({
          latencia_ms: latenciaMs,
          perdida_paquetes_pct: perdidaPaquetes,
        });
      }
    },
    [participanteId, actualizarCalidad]
  );

  return {
    calidad,
    metricas,
    reportarMetricas,
    isActualizando: actualizarCalidad.isPending,
  };
}

// ==================== HOOK PARA VALIDACIÓN ====================

/**
 * Hook para validar acceso a videollamada
 */
export function useValidarAcceso(videollamadaId: string | null) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['videollamada-validacion', videollamadaId],
    queryFn: () => videollamadasAPI.validarPuedeUnirse(videollamadaId!),
    enabled: !!videollamadaId,
    staleTime: 10000, // 10 segundos
  });

  return {
    puedeUnirse: data?.can_join || false,
    razon: data?.reason,
    participantesActuales: data?.current_participants || 0,
    maxParticipantes: data?.max_participants || 0,
    isLoading,
    error,
    refetch,
  };
}

// ==================== HOOK PARA GRABACIONES ====================

/**
 * Hook para gestionar grabaciones de videollamada
 */
export function useGrabaciones(videollamadaId: string | null) {
  const queryClient = useQueryClient();

  const {
    data: grabaciones = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: VIDEOLLAMADAS_KEYS.grabaciones(videollamadaId!),
    queryFn: () => videollamadasAPI.obtenerGrabaciones(videollamadaId!),
    enabled: !!videollamadaId,
  });

  return {
    grabaciones,
    isLoading,
    error,
    refetch,
  };
}

// ==================== HOOK PARA JITSI ====================

/**
 * Hook para manejar configuración y estado de Jitsi Meet
 */
export function useJitsi(
  videollamada: Videollamada | undefined,
  participante: Participante | undefined
) {
  const [jitsiAPI, setJitsiAPI] = useState<any>(null);
  const [isJitsiReady, setIsJitsiReady] = useState(false);
  const [jitsiError, setJitsiError] = useState<Error | null>(null);

  // Generar JWT cuando sea necesario
  const generarToken = useCallback(
    async (displayName: string) => {
      if (!videollamada || !participante) {
        throw new Error('Videollamada o participante no disponibles');
      }

      try {
        const response = await videollamadasAPI.generarJitsiToken(
          videollamada.id,
          videollamada.jitsi_room_name,
          displayName,
          participante.es_moderador
        );
        return response.token;
      } catch (error) {
        console.error('Error generando JWT:', error);
        throw error;
      }
    },
    [videollamada, participante]
  );

  // Limpiar al desmontar
  useEffect(() => {
    return () => {
      if (jitsiAPI) {
        try {
          jitsiAPI.dispose();
        } catch (error) {
          console.error('Error disposing Jitsi API:', error);
        }
      }
    };
  }, [jitsiAPI]);

  return {
    jitsiAPI,
    setJitsiAPI,
    isJitsiReady,
    setIsJitsiReady,
    jitsiError,
    setJitsiError,
    generarToken,
  };
}

// ==================== HOOK PARA HEALTH CHECK ====================

/**
 * Hook para verificar estado del servicio
 */
export function useVideollamadasHealth() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['videollamadas-health'],
    queryFn: () => videollamadasAPI.healthCheck(),
    staleTime: 300000, // 5 minutos
    retry: 3,
  });

  return {
    isHealthy: data?.success || false,
    message: data?.message,
    isLoading,
    error,
  };
}
