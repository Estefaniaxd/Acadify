import { useQuery, UseQueryResult } from "@tanstack/react-query";
import { apiClient } from "@/services/apiClient";
import type { EntregaTarea } from "@/types";

interface UseEntregaTareaOptions {
  enabled?: boolean;
  staleTime?: number;
  cacheTime?: number;
}

/**
 * Hook to fetch a single submission (entrega) with all relationships.
 * Implements caching and real-time update strategy.
 *
 * @param entregaId - ID of the submission to fetch
 * @param options - Query options (enabled, staleTime, cacheTime)
 * @returns Query result with entrega data and loading/error states
 *
 * @example
 * const { data: entrega, isLoading, error } = useEntregaTarea(123);
 *
 * @example
 * // With custom cache settings
 * const { data: entrega } = useEntregaTarea(123, {
 *   staleTime: 10 * 60 * 1000, // 10 minutes
 *   cacheTime: 30 * 60 * 1000, // 30 minutes
 * });
 */
export function useEntregaTarea(
  entregaId: number | undefined | null,
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea, Error> {
  const {
    enabled = !!entregaId,
    staleTime = 2 * 60 * 1000, // 2 minutes default
    cacheTime = 10 * 60 * 1000, // 10 minutes default
  } = options;

  return useQuery<EntregaTarea, Error>({
    queryKey: ["entregas", entregaId],
    queryFn: async () => {
      if (!entregaId) {
        throw new Error("Entrega ID is required");
      }

      const response = await apiClient.get<EntregaTarea>(
        `/api/academic/entregas/${entregaId}`
      );
      return response.data;
    },
    enabled,
    staleTime,
    gcTime: cacheTime, // Renamed from cacheTime in React Query 5
  });
}

/**
 * Hook to fetch all submissions for a specific task.
 * Used by teachers to view all student submissions.
 *
 * @param tareaId - ID of the task
 * @param filters - Optional filters (status, estudiante_id)
 * @param options - Query options
 * @returns Query result with array of entregas
 *
 * @example
 * const { data: entregas } = useEntregasPorTarea(123);
 *
 * @example
 * // With filters
 * const { data: entregas } = useEntregasPorTarea(123, {
 *   status: "ENTREGADA",
 *   estudiante_id: 456
 * });
 */
interface EntregaFilters {
  status?: "BORRADOR" | "ENTREGADA" | "CALIFICADA" | "REVISIÓN";
  estudiante_id?: number;
  skip?: number;
  limit?: number;
}

export function useEntregasPorTarea(
  tareaId: number | undefined | null,
  filters?: EntregaFilters,
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea[], Error> {
  const { enabled = !!tareaId, staleTime = 2 * 60 * 1000 } = options;

  return useQuery<EntregaTarea[], Error>({
    queryKey: ["tareas", tareaId, "entregas", filters],
    queryFn: async () => {
      if (!tareaId) {
        throw new Error("Tarea ID is required");
      }

      const response = await apiClient.get<EntregaTarea[]>(
        `/api/academic/tareas/${tareaId}/entregas`,
        { params: filters }
      );
      return response.data;
    },
    enabled,
    staleTime,
  });
}

/**
 * Hook to fetch current user's submission for a specific task.
 * Used by students to view their own submission.
 *
 * @param tareaId - ID of the task
 * @param options - Query options
 * @returns Query result with user's entrega (or null if not submitted)
 *
 * @example
 * const { data: miEntrega } = useMiEntrega(123);
 * if (!miEntrega) {
 *   return <p>No has entregado esta tarea aún</p>;
 * }
 */
export function useMiEntrega(
  tareaId: number | undefined | null,
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea | null, Error> {
  const { enabled = !!tareaId, staleTime = 1 * 60 * 1000 } = options; // 1 minute for personal data

  return useQuery<EntregaTarea | null, Error>({
    queryKey: ["tareas", tareaId, "mi-entrega"],
    queryFn: async () => {
      if (!tareaId) {
        throw new Error("Tarea ID is required");
      }

      try {
        const response = await apiClient.get<EntregaTarea>(
          `/api/academic/tareas/${tareaId}/mi-entrega`
        );
        return response.data;
      } catch (error: any) {
        // 404 means no submission yet (not an error)
        if (error.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
    enabled,
    staleTime,
  });
}

/**
 * Hook to fetch submissions by a specific student.
 * Used by teachers to view all submissions from one student.
 *
 * @param estudianteId - ID of the student
 * @param options - Query options
 * @returns Query result with array of entregas
 *
 * @example
 * const { data: entregasEstudiante } = useEntregasPorEstudiante(789);
 */
export function useEntregasPorEstudiante(
  estudianteId: number | undefined | null,
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea[], Error> {
  const { enabled = !!estudianteId, staleTime = 5 * 60 * 1000 } = options;

  return useQuery<EntregaTarea[], Error>({
    queryKey: ["estudiantes", estudianteId, "entregas"],
    queryFn: async () => {
      if (!estudianteId) {
        throw new Error("Estudiante ID is required");
      }

      const response = await apiClient.get<EntregaTarea[]>(
        `/api/academic/estudiantes/${estudianteId}/entregas`
      );
      return response.data;
    },
    enabled,
    staleTime,
  });
}

/**
 * Hook to fetch submissions with a specific status.
 * Used for filtering and dashboard views.
 *
 * @param status - Status filter (BORRADOR, ENTREGADA, CALIFICADA, REVISIÓN)
 * @param options - Query options
 * @returns Query result with array of entregas
 *
 * @example
 * const { data: entregasPendientes } = useEntregasPorEstatus("ENTREGADA");
 */
export function useEntregasPorEstatus(
  status: "BORRADOR" | "ENTREGADA" | "CALIFICADA" | "REVISIÓN",
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea[], Error> {
  const { enabled = true, staleTime = 3 * 60 * 1000 } = options;

  return useQuery<EntregaTarea[], Error>({
    queryKey: ["entregas", "status", status],
    queryFn: async () => {
      const response = await apiClient.get<EntregaTarea[]>(
        `/api/academic/entregas`,
        { params: { status } }
      );
      return response.data;
    },
    enabled,
    staleTime,
  });
}

/**
 * Hook to fetch detailed entrega with all relationships and metadata.
 * Includes student info, task info, grade info, and IA feedback.
 *
 * @param entregaId - ID of the submission
 * @param options - Query options
 * @returns Query result with detailed entrega data
 *
 * @example
 * const { data: entregaDetallada } = useEntregaDetallada(123);
 */
export function useEntregaDetallada(
  entregaId: number | undefined | null,
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea & { tarea: any; estudiante: any }, Error> {
  const { enabled = !!entregaId, staleTime = 2 * 60 * 1000 } = options;

  return useQuery<EntregaTarea & { tarea: any; estudiante: any }, Error>({
    queryKey: ["entregas", entregaId, "detallada"],
    queryFn: async () => {
      if (!entregaId) {
        throw new Error("Entrega ID is required");
      }

      const response = await apiClient.get<
        EntregaTarea & { tarea: any; estudiante: any }
      >(`/api/academic/entregas/${entregaId}/detallada`);
      return response.data;
    },
    enabled,
    staleTime,
  });
}

/**
 * Hook to fetch submissions with pending grading.
 * Used by teachers on their dashboard.
 *
 * @param tareaId - Optional filter by task ID
 * @param options - Query options
 * @returns Query result with array of entregas pending grading
 *
 * @example
 * const { data: porCalificar } = useEntregasPorCalificar(123);
 */
export function useEntregasPorCalificar(
  tareaId?: number,
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea[], Error> {
  const { enabled = true, staleTime = 2 * 60 * 1000 } = options;

  return useQuery<EntregaTarea[], Error>({
    queryKey: ["entregas", "por-calificar", tareaId],
    queryFn: async () => {
      const response = await apiClient.get<EntregaTarea[]>(
        `/api/academic/entregas/por-calificar`,
        { params: tareaId ? { tarea_id: tareaId } : {} }
      );
      return response.data;
    },
    enabled,
    staleTime,
  });
}

/**
 * Hook to fetch late submissions.
 * Used by teachers to identify submissions that need penalty application.
 *
 * @param tareaId - Optional filter by task ID
 * @param options - Query options
 * @returns Query result with array of late entregas
 *
 * @example
 * const { data: tardia } = useEntregasTardia(123);
 */
export function useEntregasTardia(
  tareaId?: number,
  options: UseEntregaTareaOptions = {}
): UseQueryResult<EntregaTarea[], Error> {
  const { enabled = true, staleTime = 2 * 60 * 1000 } = options;

  return useQuery<EntregaTarea[], Error>({
    queryKey: ["entregas", "tardia", tareaId],
    queryFn: async () => {
      const response = await apiClient.get<EntregaTarea[]>(
        `/api/academic/entregas/tardia`,
        { params: tareaId ? { tarea_id: tareaId } : {} }
      );
      return response.data;
    },
    enabled,
    staleTime,
  });
}
