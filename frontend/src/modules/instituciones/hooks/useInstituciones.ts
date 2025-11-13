/**
 * Hooks personalizados para Instituciones
 * Implementan React Query para caché, sincronización y estados
 * Principio: Separation of Concerns - Los componentes no manejan lógica de data fetching
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { institucionService } from '../services/institucionService';
import type {
  Institucion,
  CrearInstitucionDTO,
  ActualizarInstitucionDTO,
  FiltrosInstitucion,
  PersonalizacionInstitucion,
} from '../types';

// Query Keys centralizadas
export const INSTITUCIONES_KEYS = {
  all: ['instituciones'] as const,
  lists: () => [...INSTITUCIONES_KEYS.all, 'list'] as const,
  list: (filtros?: FiltrosInstitucion) => [...INSTITUCIONES_KEYS.lists(), filtros] as const,
  details: () => [...INSTITUCIONES_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...INSTITUCIONES_KEYS.details(), id] as const,
  estadisticas: (id: string) => [...INSTITUCIONES_KEYS.detail(id), 'estadisticas'] as const,
  search: (termino: string) => [...INSTITUCIONES_KEYS.all, 'search', termino] as const,
};

/**
 * Hook para obtener lista de instituciones
 * Soporta filtros, paginación y caché automático
 */
export function useInstituciones(filtros?: FiltrosInstitucion) {
  return useQuery({
    queryKey: INSTITUCIONES_KEYS.list(filtros),
    queryFn: () => institucionService.getAll(filtros),
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos (antes cacheTime)
  });
}

/**
 * Hook para obtener una institución específica
 */
export function useInstitucion(id?: string) {
  return useQuery({
    queryKey: INSTITUCIONES_KEYS.detail(id!),
    queryFn: () => institucionService.getById(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para obtener estadísticas de una institución
 */
export function useEstadisticasInstitucion(id?: string) {
  return useQuery({
    queryKey: INSTITUCIONES_KEYS.estadisticas(id!),
    queryFn: () => institucionService.getEstadisticas(id!),
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutos (datos más volátiles)
  });
}

/**
 * Hook para buscar instituciones
 */
export function useBuscarInstituciones(termino: string) {
  return useQuery({
    queryKey: INSTITUCIONES_KEYS.search(termino),
    queryFn: () => institucionService.search(termino),
    enabled: termino.length >= 2,
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
}

/**
 * Hook para crear una institución
 * Invalida automáticamente el caché de listas
 */
export function useCrearInstitucion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CrearInstitucionDTO) => institucionService.create(data),
    onSuccess: (nuevaInstitucion) => {
      // Invalidar todas las listas
      queryClient.invalidateQueries({ queryKey: INSTITUCIONES_KEYS.lists() });
      
      // Agregar al caché de detalle
      queryClient.setQueryData(
        INSTITUCIONES_KEYS.detail(nuevaInstitucion.id),
        nuevaInstitucion
      );
    },
  });
}

/**
 * Hook para actualizar una institución
 */
export function useActualizarInstitucion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ActualizarInstitucionDTO }) =>
      institucionService.update(id, data),
    onSuccess: (institucionActualizada, variables) => {
      // Actualizar caché de detalle
      queryClient.setQueryData(
        INSTITUCIONES_KEYS.detail(variables.id),
        institucionActualizada
      );
      
      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: INSTITUCIONES_KEYS.lists() });
      
      // Invalidar estadísticas
      queryClient.invalidateQueries({
        queryKey: INSTITUCIONES_KEYS.estadisticas(variables.id),
      });
    },
  });
}

/**
 * Hook para eliminar una institución
 */
export function useEliminarInstitucion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => institucionService.delete(id),
    onSuccess: (_, id) => {
      // Remover del caché
      queryClient.removeQueries({ queryKey: INSTITUCIONES_KEYS.detail(id) });
      
      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: INSTITUCIONES_KEYS.lists() });
    },
  });
}

/**
 * Hook para activar/desactivar institución
 */
export function useToggleActivoInstitucion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, activo }: { id: string; activo: boolean }) =>
      institucionService.toggleActivo(id, activo),
    onSuccess: (institucionActualizada, variables) => {
      // Actualizar optimistamente
      queryClient.setQueryData(
        INSTITUCIONES_KEYS.detail(variables.id),
        institucionActualizada
      );
      
      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: INSTITUCIONES_KEYS.lists() });
    },
  });
}

/**
 * Hook para actualizar personalización visual
 */
export function useActualizarPersonalizacion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PersonalizacionInstitucion }) =>
      institucionService.updatePersonalizacion(id, data),
    onSuccess: (institucionActualizada, variables) => {
      queryClient.setQueryData(
        INSTITUCIONES_KEYS.detail(variables.id),
        institucionActualizada
      );
      
      queryClient.invalidateQueries({ queryKey: INSTITUCIONES_KEYS.lists() });
    },
  });
}

/**
 * Hook para subir logo
 */
export function useSubirLogo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) =>
      institucionService.uploadLogo(id, file),
    onSuccess: (url, variables) => {
      // Actualizar institución en caché con nuevo logo
      queryClient.setQueryData<Institucion>(
        INSTITUCIONES_KEYS.detail(variables.id),
        (old) => (old ? { ...old, logo: url } : undefined)
      );
      
      queryClient.invalidateQueries({ queryKey: INSTITUCIONES_KEYS.lists() });
    },
  });
}

/**
 * Hook combinado para operaciones comunes
 * Útil cuando necesitas múltiples operaciones en un componente
 */
export function useInstitucionOperations() {
  return {
    crear: useCrearInstitucion(),
    actualizar: useActualizarInstitucion(),
    eliminar: useEliminarInstitucion(),
    toggleActivo: useToggleActivoInstitucion(),
    actualizarPersonalizacion: useActualizarPersonalizacion(),
    subirLogo: useSubirLogo(),
  };
}
