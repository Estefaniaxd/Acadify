/**
 * Hooks para gestión de instituciones
 * Usa React Query para cache y actualizaciones
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import institucionesService, {
  InstitucionCreate,
  InstitucionUpdate,
  InvitacionCoordinador,
} from '../services/instituciones.service';
import { useToast } from '../context/ToastContext';

/**
 * Hook para obtener todas las instituciones
 */
export function useInstituciones() {
  return useQuery({
    queryKey: ['instituciones'],
    queryFn: () => institucionesService.getAll(),
    staleTime: 1000 * 60 * 5, // 5 minutos
    retry: 1, // Solo reintentar una vez
    retryDelay: 1000,
  });
}

/**
 * Hook para obtener una institución específica
 */
export function useInstitucion(id: string) {
  return useQuery({
    queryKey: ['instituciones', id],
    queryFn: () => institucionesService.getById(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

/**
 * Hook para crear institución
 */
export function useCrearInstitucion() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (data: InstitucionCreate) => institucionesService.create(data),
    onSuccess: (newInstitucion) => {
      // Invalidar query de instituciones para refrescar
      queryClient.invalidateQueries({ queryKey: ['instituciones'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
      toast.success('Institución creada', `"${newInstitucion.nombre}" creada exitosamente`);
    },
    onError: (error: Error) => {
      toast.error('Error', error.message || 'Error al crear institución');
    },
  });
}

/**
 * Hook para actualizar institución
 */
export function useActualizarInstitucion() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: InstitucionUpdate }) =>
      institucionesService.update(id, data),
    onSuccess: (updatedInstitucion) => {
      // Invalidar queries relevantes
      queryClient.invalidateQueries({ queryKey: ['instituciones'] });
      queryClient.invalidateQueries({ queryKey: ['instituciones', updatedInstitucion.institucion_id] });
      toast.success('Institución actualizada', `"${updatedInstitucion.nombre}" actualizada exitosamente`);
    },
    onError: (error: Error) => {
      toast.error('Error', error.message || 'Error al actualizar institución');
    },
  });
}

/**
 * Hook para eliminar institución
 */
export function useEliminarInstitucion() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (id: string) => institucionesService.delete(id),
    onSuccess: (result) => {
      // Invalidar query de instituciones para refrescar
      queryClient.invalidateQueries({ queryKey: ['instituciones'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
      toast.success('Institución eliminada', result.message);
    },
    onError: (error: Error) => {
      toast.error('Error', error.message || 'Error al eliminar institución');
    },
  });
}

/**
 * Hook para invitar coordinador
 */
export function useInvitarCoordinador() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ institucionId, data }: { institucionId: string; data: InvitacionCoordinador }) =>
      institucionesService.invitarCoordinador(institucionId, data),
    onSuccess: (result) => {
      // Invalidar queries relevantes
      queryClient.invalidateQueries({ queryKey: ['instituciones'] });
      toast.success(
        'Invitación enviada',
        `${result.message}. Código: ${result.codigo}`
      );
    },
    onError: (error: Error) => {
      toast.error('Error', error.message || 'Error al enviar invitación');
    },
  });
}

/**
 * Hook para obtener estadísticas de institución
 */
export function useInstitucionStats(id: string) {
  return useQuery({
    queryKey: ['instituciones', id, 'stats'],
    queryFn: () => institucionesService.getStats(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 2, // 2 minutos
  });
}
