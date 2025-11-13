/**
 * Hooks de React Query para el módulo de Programas Académicos
 * 
 * Implementa el patrón de hooks personalizados con React Query
 * para gestionar el estado y caché de programas.
 * 
 * @module useProgramas
 */

import { useQuery, useMutation, useQueryClient, type UseQueryResult } from '@tanstack/react-query';
import { programaService } from '../services/programaService';
import type {
  Programa,
  CrearProgramaDTO,
  ActualizarProgramaDTO,
  FiltrosProgramas,
  RespuestaPaginada,
  EstadisticasPrograma,
  AsignarCursosDTO,
  MallaCurricular,
  EstadoPrograma
} from '../types';

/**
 * Keys centralizadas para React Query
 * Facilita la invalidación y refetch de queries
 */
export const programaKeys = {
  all: ['programas'] as const,
  lists: () => [...programaKeys.all, 'list'] as const,
  list: (filtros?: FiltrosProgramas) => [...programaKeys.lists(), filtros] as const,
  details: () => [...programaKeys.all, 'detail'] as const,
  detail: (id: number) => [...programaKeys.details(), id] as const,
  estadisticas: (id: number) => [...programaKeys.all, 'estadisticas', id] as const,
  malla: (id: number) => [...programaKeys.all, 'malla', id] as const,
  porInstitucion: (institucionId: number) => 
    [...programaKeys.all, 'institucion', institucionId] as const,
};

/**
 * Hook para obtener lista de programas con filtros
 * 
 * @param filtros - Parámetros de búsqueda y filtrado
 * @returns Query con lista paginada de programas
 * 
 * @example
 * ```tsx
 * const { data, isLoading, error } = useProgramas({
 *   institucionId: 1,
 *   nivel: 'PROFESIONAL',
 *   pagina: 1,
 *   limite: 10
 * });
 * ```
 */
export function useProgramas(filtros?: FiltrosProgramas) {
  return useQuery({
    queryKey: programaKeys.list(filtros),
    queryFn: () => programaService.getAll(filtros),
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos (antes cacheTime)
  });
}

/**
 * Hook para obtener programas de una institución específica
 * 
 * @param institucionId - ID de la institución
 * @param filtros - Filtros adicionales
 * @returns Query con programas de la institución
 * 
 * @example
 * ```tsx
 * const { data } = useProgramasPorInstitucion(1, { estado: 'ACTIVO' });
 * ```
 */
export function useProgramasPorInstitucion(
  institucionId: number,
  filtros?: Omit<FiltrosProgramas, 'institucionId'>
) {
  return useQuery({
    queryKey: programaKeys.porInstitucion(institucionId),
    queryFn: () => programaService.getPorInstitucion(institucionId, filtros),
    enabled: !!institucionId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para obtener un programa específico por ID
 * 
 * @param id - ID del programa
 * @returns Query con datos del programa
 * 
 * @example
 * ```tsx
 * const { data: programa, isLoading } = usePrograma(5);
 * if (isLoading) return <Spinner />;
 * return <div>{programa.nombre}</div>;
 * ```
 */
export function usePrograma(id: number | undefined) {
  return useQuery({
    queryKey: programaKeys.detail(id!),
    queryFn: () => programaService.getById(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para obtener estadísticas de un programa
 * 
 * @param id - ID del programa
 * @returns Query con estadísticas
 * 
 * @example
 * ```tsx
 * const { data: stats } = useEstadisticasPrograma(5);
 * console.log(`Tasa graduación: ${stats?.tasaGraduacion}%`);
 * ```
 */
export function useEstadisticasPrograma(id: number | undefined) {
  return useQuery({
    queryKey: programaKeys.estadisticas(id!),
    queryFn: () => programaService.getEstadisticas(id!),
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutos (datos más dinámicos)
  });
}

/**
 * Hook para obtener malla curricular de un programa
 * 
 * @param id - ID del programa
 * @returns Query con malla curricular
 * 
 * @example
 * ```tsx
 * const { data: malla } = useMallaCurricular(5);
 * ```
 */
export function useMallaCurricular(id: number | undefined) {
  return useQuery({
    queryKey: programaKeys.malla(id!),
    queryFn: () => programaService.getMallaCurricular(id!),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutos (estructura estable)
  });
}

/**
 * Hook para buscar programas por término
 * 
 * @param termino - Término de búsqueda
 * @returns Query con resultados de búsqueda
 * 
 * @example
 * ```tsx
 * const [busqueda, setBusqueda] = useState('');
 * const { data: resultados } = useBuscarProgramas(busqueda);
 * ```
 */
export function useBuscarProgramas(termino: string) {
  return useQuery({
    queryKey: [...programaKeys.all, 'search', termino],
    queryFn: () => programaService.search(termino),
    enabled: termino.length >= 2,
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
}

/**
 * Hook para crear un nuevo programa
 * 
 * @returns Mutation para crear programa
 * 
 * @example
 * ```tsx
 * const crearPrograma = useCrearPrograma();
 * 
 * const handleSubmit = async (data: CrearProgramaDTO) => {
 *   await crearPrograma.mutateAsync(data);
 *   navigate('/admin/programas');
 * };
 * ```
 */
export function useCrearPrograma() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CrearProgramaDTO) => programaService.create(data),
    onSuccess: (nuevoPrograma) => {
      // Invalida todas las listas de programas
      queryClient.invalidateQueries({ queryKey: programaKeys.lists() });
      
      // Invalida programas de la institución
      queryClient.invalidateQueries({ 
        queryKey: programaKeys.porInstitucion(nuevoPrograma.institucionId) 
      });
      
      // Opcionalmente, agregar a caché
      queryClient.setQueryData(
        programaKeys.detail(nuevoPrograma.id),
        nuevoPrograma
      );
    },
  });
}

/**
 * Hook para actualizar un programa existente
 * 
 * @returns Mutation para actualizar programa
 * 
 * @example
 * ```tsx
 * const actualizarPrograma = useActualizarPrograma();
 * 
 * const handleUpdate = async () => {
 *   await actualizarPrograma.mutateAsync({
 *     id: 5,
 *     data: { nombre: 'Nuevo Nombre' }
 *   });
 * };
 * ```
 */
export function useActualizarPrograma() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ActualizarProgramaDTO }) =>
      programaService.update(id, data),
    onMutate: async ({ id, data }) => {
      // Cancelar queries en progreso
      await queryClient.cancelQueries({ queryKey: programaKeys.detail(id) });

      // Snapshot del valor anterior
      const previous = queryClient.getQueryData<Programa>(programaKeys.detail(id));

      // Actualización optimista
      if (previous) {
        queryClient.setQueryData<Programa>(programaKeys.detail(id), {
          ...previous,
          ...data,
        });
      }

      return { previous, id };
    },
    onError: (err, variables, context) => {
      // Rollback en caso de error
      if (context?.previous) {
        queryClient.setQueryData(
          programaKeys.detail(context.id),
          context.previous
        );
      }
    },
    onSuccess: (programaActualizado) => {
      // Actualizar caché del detalle
      queryClient.setQueryData(
        programaKeys.detail(programaActualizado.id),
        programaActualizado
      );

      // Invalidar listas para reflejar cambios
      queryClient.invalidateQueries({ queryKey: programaKeys.lists() });
      
      // Invalidar programas de la institución
      queryClient.invalidateQueries({ 
        queryKey: programaKeys.porInstitucion(programaActualizado.institucionId) 
      });
    },
  });
}

/**
 * Hook para eliminar un programa
 * 
 * @returns Mutation para eliminar programa
 * 
 * @example
 * ```tsx
 * const eliminarPrograma = useEliminarPrograma();
 * 
 * const handleDelete = async (id: number) => {
 *   if (confirm('¿Estás seguro?')) {
 *     await eliminarPrograma.mutateAsync(id);
 *   }
 * };
 * ```
 */
export function useEliminarPrograma() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => programaService.delete(id),
    onSuccess: (_, id) => {
      // Remover de caché
      queryClient.removeQueries({ queryKey: programaKeys.detail(id) });

      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: programaKeys.lists() });
      queryClient.invalidateQueries({ queryKey: programaKeys.all });
    },
  });
}

/**
 * Hook para cambiar el estado de un programa
 * 
 * @returns Mutation para cambiar estado
 * 
 * @example
 * ```tsx
 * const cambiarEstado = useCambiarEstadoPrograma();
 * 
 * const handleToggle = async (id: number, estado: EstadoPrograma) => {
 *   await cambiarEstado.mutateAsync({ id, estado });
 * };
 * ```
 */
export function useCambiarEstadoPrograma() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, estado }: { id: number; estado: EstadoPrograma }) =>
      programaService.cambiarEstado(id, estado),
    onSuccess: (programaActualizado) => {
      // Actualizar caché
      queryClient.setQueryData(
        programaKeys.detail(programaActualizado.id),
        programaActualizado
      );

      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: programaKeys.lists() });
    },
  });
}

/**
 * Hook para asignar cursos a un programa
 * 
 * @returns Mutation para asignar cursos
 * 
 * @example
 * ```tsx
 * const asignarCursos = useAsignarCursos();
 * 
 * const handleAssign = async () => {
 *   await asignarCursos.mutateAsync({
 *     programaId: 5,
 *     cursoIds: [1, 2, 3],
 *     nivel: 1,
 *     esObligatorio: true
 *   });
 * };
 * ```
 */
export function useAsignarCursos() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AsignarCursosDTO) => programaService.asignarCursos(data),
    onSuccess: (programaActualizado) => {
      // Actualizar caché del programa
      queryClient.setQueryData(
        programaKeys.detail(programaActualizado.id),
        programaActualizado
      );

      // Invalidar malla curricular
      queryClient.invalidateQueries({ 
        queryKey: programaKeys.malla(programaActualizado.id) 
      });

      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: programaKeys.lists() });
    },
  });
}

/**
 * Hook combinado que agrupa operaciones comunes
 * Útil para evitar múltiples declaraciones de hooks
 * 
 * @returns Objeto con todas las operaciones disponibles
 * 
 * @example
 * ```tsx
 * const { crear, actualizar, eliminar, cambiarEstado } = useProgramaOperations();
 * 
 * // Usar las operaciones
 * await crear.mutateAsync(data);
 * await actualizar.mutateAsync({ id, data });
 * await eliminar.mutateAsync(id);
 * ```
 */
export function useProgramaOperations() {
  return {
    crear: useCrearPrograma(),
    actualizar: useActualizarPrograma(),
    eliminar: useEliminarPrograma(),
    cambiarEstado: useCambiarEstadoPrograma(),
    asignarCursos: useAsignarCursos(),
  };
}
