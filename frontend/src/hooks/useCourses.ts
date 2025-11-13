/**
 * Custom hooks para gestión de cursos con React Query
 * Implementa patrones de caching, optimistic updates y manejo de errores
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import courseService from '../modules/academico/services/courseService';
import { queryKeys, invalidateCourseComments } from '../lib/queryClient';
import { useToast } from '../context/ToastContext';

/**
 * Hook para obtener todos los cursos disponibles
 */
export function useCourses() {
  return useQuery({
    queryKey: queryKeys.courses.list(),
    queryFn: () => courseService.getCourses(),
    select: (data) => data, // Transformar datos si es necesario
    staleTime: 1000 * 60 * 5, // 5 minutos - los cursos no cambian tan seguido
  });
}

/**
 * Hook para obtener los cursos del usuario actual
 */
export function useMyCourses() {
  return useQuery({
    queryKey: queryKeys.courses.mine(),
    queryFn: () => courseService.getMyCourses(),
    staleTime: 1000 * 60 * 2, // 2 minutos - más dinámico que todos los cursos
  });
}

/**
 * Hook para obtener detalle de un curso específico
 */
export function useCourse(courseId: string | undefined, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.courses.detail(courseId || ''),
    queryFn: () => {
      if (!courseId) throw new Error('Course ID is required');
      return courseService.getCourseById(courseId);
    },
    enabled: !!courseId && enabled, // Solo ejecutar si hay ID
    staleTime: 1000 * 60 * 3, // 3 minutos
    retry: 2, // Reintentar 2 veces si falla
  });
}

/**
 * Hook para inscribirse a un curso
 */
export function useJoinCourse() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (codigo: string) => courseService.joinCourse(codigo),
    onSuccess: (data) => {
      // Invalidar la lista de mis cursos para refrescarla
      queryClient.invalidateQueries({ queryKey: queryKeys.courses.mine() });
      
      toast.success(
        data.message || '¡Te has inscrito exitosamente al curso!'
      );
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al inscribirse al curso';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para obtener todos los grupos disponibles
 */
export function useCourseGroups() {
  return useQuery({
    queryKey: [...queryKeys.courses.all, 'groups'],
    queryFn: () => courseService.getGroups(),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

/**
 * Hook para auto-vincular perfil de estudiante
 */
export function useAutoLinkStudent() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: () => courseService.autoLinkStudentProfile(),
    onSuccess: (data) => {
      // Invalidar cursos y perfil
      queryClient.invalidateQueries({ queryKey: queryKeys.courses.mine() });
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
      
      toast.success(
        data.message || 'Perfil vinculado exitosamente'
      );
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al vincular perfil';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para vincular por código de invitación
 */
export function useLinkByInvitationCode() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (codigo: string) => courseService.linkByInvitationCode(codigo),
    onSuccess: (data) => {
      // Invalidar cursos y perfil
      queryClient.invalidateQueries({ queryKey: queryKeys.courses.mine() });
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.user });
      
      toast.success(
        data.message || 'Vinculación exitosa con código de invitación'
      );
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Código de invitación inválido';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para generar código de invitación (coordinadores)
 */
export function useGenerateInvitationCode() {
  const toast = useToast();

  return useMutation({
    mutationFn: ({ programaId, descripcion }: { programaId: string; descripcion?: string }) => 
      courseService.generateInvitationCode(programaId, descripcion),
    onSuccess: (data) => {
      toast.success('Código de invitación generado exitosamente');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al generar código';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para obtener comentarios de un curso
 */
export function useCourseComments(courseId: string | undefined, limit: number = 20, offset: number = 0) {
  return useQuery({
    queryKey: queryKeys.comments.list(courseId || '', { limit, offset }),
    queryFn: () => {
      if (!courseId) throw new Error('Course ID is required');
      return courseService.getCourseComments(courseId, limit, offset);
    },
    enabled: !!courseId,
    staleTime: 1000 * 60 * 1, // 1 minuto - comentarios más dinámicos
  });
}

/**
 * Hook para crear comentario
 */
export function useCreateComment() {
  const toast = useToast();

  return useMutation({
    mutationFn: ({ courseId, commentData }: { courseId: string; commentData: any }) => 
      courseService.createComment(courseId, commentData),
    onSuccess: (data, variables) => {
      // Invalidar comentarios del curso
      invalidateCourseComments(variables.courseId);
      
      toast.success('Comentario publicado exitosamente');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al publicar comentario';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para obtener tareas de un curso
 */
export function useCourseTasks(courseId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.tasks.list(courseId || ''),
    queryFn: () => {
      if (!courseId) throw new Error('Course ID is required');
      return courseService.getCourseTasks(courseId);
    },
    enabled: !!courseId,
    staleTime: 1000 * 60 * 2, // 2 minutos
  });
}

/**
 * Hook para crear tarea
 */
export function useCreateTask() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ courseId, taskData }: { courseId: string; taskData: any }) => 
      courseService.createTask(courseId, taskData),
    onSuccess: (data, variables) => {
      // Invalidar tareas del curso
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.list(variables.courseId) });
      
      toast.success('Tarea creada exitosamente');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al crear tarea';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para subir archivo
 */
export function useUploadFile() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ courseId, file, tipo }: { courseId: string; file: File; tipo: string }) => 
      courseService.uploadFile(courseId, file, tipo),
    onSuccess: (data, variables) => {
      // Invalidar datos del curso
      queryClient.invalidateQueries({ queryKey: queryKeys.courses.detail(variables.courseId) });
      
      toast.success('Archivo subido exitosamente');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al subir archivo';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para agregar reacción
 */
export function useAddReaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ comentarioId, emoji, tipo }: { comentarioId: string; emoji: string; tipo?: string }) => 
      courseService.addReaction(comentarioId, emoji, tipo || 'like'),
    onSuccess: (data, variables) => {
      // Invalidar reacciones
      queryClient.invalidateQueries({ 
        queryKey: ['reactions', variables.comentarioId] 
      });
    },
  });
}

/**
 * Hook para crear respuesta
 */
export function useCreateReply() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ comentarioId, contenido }: { comentarioId: string; contenido: string }) => 
      courseService.createReply(comentarioId, { contenido }),
    onSuccess: (data, variables) => {
      // Invalidar respuestas del comentario
      queryClient.invalidateQueries({ 
        queryKey: ['replies', variables.comentarioId] 
      });
      
      toast.success('Respuesta publicada');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al publicar respuesta';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para actualizar comentario
 */
export function useUpdateComment() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ comentarioId, contenido }: { comentarioId: string; contenido: string }) => 
      courseService.updateComment(comentarioId, { contenido }),
    onSuccess: () => {
      // Invalidar todos los comentarios
      queryClient.invalidateQueries({ queryKey: queryKeys.comments.all });
      
      toast.success('Comentario actualizado');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al actualizar comentario';
      toast.error(errorMessage);
    },
  });
}

/**
 * Hook para eliminar comentario
 */
export function useDeleteComment() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (comentarioId: string) => courseService.deleteComment(comentarioId),
    onSuccess: () => {
      // Invalidar todos los comentarios
      queryClient.invalidateQueries({ queryKey: queryKeys.comments.all });
      
      toast.success('Comentario eliminado');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          'Error al eliminar comentario';
      toast.error(errorMessage);
    },
  });
}
