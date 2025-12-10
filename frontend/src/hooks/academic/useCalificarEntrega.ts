import {
  useMutation,
  UseMutationResult,
  useQueryClient,
} from "@tanstack/react-query";
import { apiClient } from "@/services/apiClient";
import type { EntregaTarea } from "@/types";

// ============================================================================
// TYPES
// ============================================================================

export interface CalificarEntregaPayload {
  calificacion: number;
  comentarios_docente?: string;
  rubrica_calificacion?: Record<string, any>;
  puntos_otorgados?: number;
}

export interface CalificarEntregaConPuntosPayload extends CalificarEntregaPayload {
  // Points are calculated automatically, but can be overridden
  aplicar_penalizacion_tardia?: boolean;
  aplicar_penalizacion_intentos?: boolean;
}

export interface SubirArchivoPayload {
  archivo: File;
  nombre_archivo?: string;
}

export interface EntregarTareaPayload {
  comentarios_estudiante?: string;
  archivo?: File;
  enlaces_externos?: string[];
  contenido_texto?: string;
}

interface UseMutationOptions {
  onSuccess?: (data: EntregaTarea) => void;
  onError?: (error: Error) => void;
}

// ============================================================================
// MUTATION: Calificar Entrega (Basic Grading)
// ============================================================================

/**
 * Mutation to grade a submission with basic grading information.
 * Updates calificacion, comentarios_docente, and rubrica_calificacion.
 * Does NOT automatically calculate points (use calificar_entrega_con_puntos for that).
 *
 * @param options - Mutation options (onSuccess, onError callbacks)
 * @returns Mutation result with loading/error states
 *
 * @example
 * const { mutate: calificar, isPending } = useCalificarEntrega();
 *
 * calificar({
 *   entregaId: 123,
 *   payload: {
 *     calificacion: 4.5,
 *     comentarios_docente: "Buen trabajo",
 *     rubrica_calificacion: { presentacion: 5, contenido: 4 }
 *   }
 * });
 */
export function useCalificarEntrega(
  options: UseMutationOptions = {}
): UseMutationResult<
  EntregaTarea,
  Error,
  { entregaId: number; payload: CalificarEntregaPayload },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      entregaId,
      payload,
    }: {
      entregaId: number;
      payload: CalificarEntregaPayload;
    }) => {
      const response = await apiClient.patch<EntregaTarea>(
        `/api/academic/entregas/${entregaId}/calificar`,
        payload
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({
        queryKey: ["entregas", data.entrega_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["tareas", data.tarea_id, "entregas"],
      });
      queryClient.invalidateQueries({
        queryKey: ["entregas", "por-calificar"],
      });

      options.onSuccess?.(data);
    },
    onError: (error) => {
      options.onError?.(error);
    },
  });
}

// ============================================================================
// MUTATION: Calificar Entrega Con Puntos (Advanced Grading)
// ============================================================================

/**
 * Mutation to grade a submission WITH automatic points calculation.
 * Calculates points using formula: base + bonus - late_penalty - attempt_penalty
 * Updates calificacion, puntos_otorgados, and applies gamification logic.
 *
 * @param options - Mutation options
 * @returns Mutation result with loading/error states
 *
 * @example
 * const { mutate: calificarConPuntos } = useCalificarEntregaConPuntos();
 *
 * calificarConPuntos({
 *   entregaId: 123,
 *   payload: {
 *     calificacion: 4.5,
 *     comentarios_docente: "Excelente",
 *     aplicar_penalizacion_tardia: true,
 *     aplicar_penalizacion_intentos: true
 *   }
 * });
 */
export function useCalificarEntregaConPuntos(
  options: UseMutationOptions = {}
): UseMutationResult<
  EntregaTarea,
  Error,
  {
    entregaId: number;
    payload: CalificarEntregaConPuntosPayload;
  },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      entregaId,
      payload,
    }: {
      entregaId: number;
      payload: CalificarEntregaConPuntosPayload;
    }) => {
      const response = await apiClient.post<EntregaTarea>(
        `/api/academic/entregas/${entregaId}/calificar-con-puntos`,
        payload
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({
        queryKey: ["entregas", data.entrega_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["tareas", data.tarea_id, "entregas"],
      });
      queryClient.invalidateQueries({
        queryKey: ["entregas", "por-calificar"],
      });
      queryClient.invalidateQueries({
        queryKey: ["estudiantes", data.estudiante_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["puntos"],
      });

      options.onSuccess?.(data);
    },
    onError: (error) => {
      options.onError?.(error);
    },
  });
}

// ============================================================================
// MUTATION: Enviar/Entregar Tarea
// ============================================================================

/**
 * Mutation to submit a task (mark as ENTREGADA).
 * Transitions entrega from BORRADOR to ENTREGADA status.
 * Detects if submission is late and sets es_tardia flag.
 *
 * @param options - Mutation options
 * @returns Mutation result
 *
 * @example
 * const { mutate: entregar } = useEntregarTarea();
 *
 * entregar({
 *   entregaId: 123,
 *   payload: {
 *     comentarios_estudiante: "Aquí está mi entrega",
 *     archivo: fileObject,
 *     enlaces_externos: ["https://github.com/..."]
 *   }
 * });
 */
export function useEntregarTarea(
  options: UseMutationOptions = {}
): UseMutationResult<
  EntregaTarea,
  Error,
  {
    entregaId: number;
    payload: EntregarTareaPayload;
  },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      entregaId,
      payload,
    }: {
      entregaId: number;
      payload: EntregarTareaPayload;
    }) => {
      const formData = new FormData();

      // Add text fields
      if (payload.comentarios_estudiante) {
        formData.append("comentarios_estudiante", payload.comentarios_estudiante);
      }
      if (payload.contenido_texto) {
        formData.append("contenido_texto", payload.contenido_texto);
      }
      if (payload.enlaces_externos) {
        formData.append("enlaces_externos", JSON.stringify(payload.enlaces_externos));
      }

      // Add file
      if (payload.archivo) {
        formData.append("archivo", payload.archivo);
      }

      const response = await apiClient.patch<EntregaTarea>(
        `/api/academic/entregas/${entregaId}/entregar`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({
        queryKey: ["entregas", data.entrega_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["tareas", data.tarea_id, "entregas"],
      });
      queryClient.invalidateQueries({
        queryKey: ["tareas", data.tarea_id, "mi-entrega"],
      });
      queryClient.invalidateQueries({
        queryKey: ["entregas", "por-calificar"],
      });

      options.onSuccess?.(data);
    },
    onError: (error) => {
      options.onError?.(error);
    },
  });
}

// ============================================================================
// MUTATION: Crear Entrega (Initialize Submission)
// ============================================================================

/**
 * Mutation to create a new submission for a task.
 * Initializes entrega with BORRADOR status, auto-increments attempt number,
 * and detects if submission is late.
 *
 * @param options - Mutation options
 * @returns Mutation result
 *
 * @example
 * const { mutate: crearEntrega } = useCrearEntrega();
 *
 * crearEntrega({
 *   tareaId: 123,
 *   payload: {} // Empty payload for initial creation
 * });
 */
interface CrearEntregaPayload {
  comentarios_estudiante?: string;
}

export function useCrearEntrega(
  options: UseMutationOptions = {}
): UseMutationResult<
  EntregaTarea,
  Error,
  {
    tareaId: number;
    payload?: CrearEntregaPayload;
  },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      tareaId,
      payload = {},
    }: {
      tareaId: number;
      payload?: CrearEntregaPayload;
    }) => {
      const response = await apiClient.post<EntregaTarea>(
        `/api/academic/tareas/${tareaId}/entregas`,
        payload
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({
        queryKey: ["tareas", data.tarea_id, "entregas"],
      });
      queryClient.invalidateQueries({
        queryKey: ["tareas", data.tarea_id, "mi-entrega"],
      });
      queryClient.invalidateQueries({
        queryKey: ["entregas"],
      });

      options.onSuccess?.(data);
    },
    onError: (error) => {
      options.onError?.(error);
    },
  });
}

// ============================================================================
// MUTATION: Subir Archivo
// ============================================================================

/**
 * Mutation to upload a file to a submission.
 * Validates file type, size, and prevents path traversal attacks.
 * Can update existing file or add new one.
 *
 * @param options - Mutation options
 * @returns Mutation result
 *
 * @example
 * const { mutate: subirArchivo, isPending } = useSubirArchivoEntrega();
 *
 * const handleFileChange = (file: File) => {
 *   subirArchivo({
 *     entregaId: 123,
 *     payload: { archivo: file }
 *   });
 * };
 */
export function useSubirArchivoEntrega(
  options: UseMutationOptions = {}
): UseMutationResult<
  EntregaTarea,
  Error,
  {
    entregaId: number;
    payload: SubirArchivoPayload;
  },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      entregaId,
      payload,
    }: {
      entregaId: number;
      payload: SubirArchivoPayload;
    }) => {
      const formData = new FormData();
      formData.append("archivo", payload.archivo);

      if (payload.nombre_archivo) {
        formData.append("nombre_archivo", payload.nombre_archivo);
      }

      const response = await apiClient.post<EntregaTarea>(
        `/api/academic/entregas/${entregaId}/subir-archivo`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["entregas", data.entrega_id],
      });

      options.onSuccess?.(data);
    },
    onError: (error) => {
      options.onError?.(error);
    },
  });
}

// ============================================================================
// MUTATION: Eliminar Entrega
// ============================================================================

/**
 * Mutation to delete/soft-delete a submission.
 * Only allowed for students on their own BORRADOR submissions before deadline.
 * Teachers can soft-delete any submission for data cleanup.
 *
 * @param options - Mutation options
 * @returns Mutation result
 *
 * @example
 * const { mutate: eliminar } = useEliminarEntrega();
 *
 * eliminar({ entregaId: 123 });
 */
export function useEliminarEntrega(
  options: UseMutationOptions = {}
): UseMutationResult<
  { message: string },
  Error,
  { entregaId: number },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ entregaId }: { entregaId: number }) => {
      const response = await apiClient.delete<{ message: string }>(
        `/api/academic/entregas/${entregaId}`
      );
      return response.data;
    },
    onSuccess: (_, { entregaId }) => {
      queryClient.invalidateQueries({
        queryKey: ["entregas", entregaId],
      });
      queryClient.invalidateQueries({
        queryKey: ["entregas"],
      });

      options.onSuccess?.({} as EntregaTarea); // Empty object for compatibility
    },
    onError: (error) => {
      options.onError?.(error);
    },
  });
}

// ============================================================================
// MUTATION: Solicitar Revisión
// ============================================================================

/**
 * Mutation to request grade review from teacher.
 * Sets requiere_revision flag and creates audit trail.
 *
 * @param options - Mutation options
 * @returns Mutation result
 *
 * @example
 * const { mutate: solicitarRevision } = useSolicitarRevision();
 *
 * solicitarRevision({
 *   entregaId: 123,
 *   razon: "Creo que debería tener mejor calificación"
 * });
 */
interface SolicitarRevisionPayload {
  razon?: string;
}

export function useSolicitarRevision(
  options: UseMutationOptions = {}
): UseMutationResult<
  EntregaTarea,
  Error,
  {
    entregaId: number;
    payload?: SolicitarRevisionPayload;
  },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      entregaId,
      payload = {},
    }: {
      entregaId: number;
      payload?: SolicitarRevisionPayload;
    }) => {
      const response = await apiClient.post<EntregaTarea>(
        `/api/academic/entregas/${entregaId}/solicitar-revision`,
        payload
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["entregas", data.entrega_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["entregas", "por-calificar"],
      });

      options.onSuccess?.(data);
    },
    onError: (error) => {
      options.onError?.(error);
    },
  });
}
