/**
 * Configuración de React Query (TanStack Query)
 * Implementa caching inteligente y manejo optimizado de estado del servidor
 * Con persistencia en localStorage para mejor UX offline
 */

import { QueryClient } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/react-query-persist-client';

// Persister personalizado para localStorage
const createLocalStoragePersister = () => {
  return {
    persistClient: (client: any) => {
      try {
        localStorage.setItem('ACADIFY_REACT_QUERY_CACHE', JSON.stringify(client));
      } catch (error) {
        console.warn('Error persisting React Query cache:', error);
      }
    },
    restoreClient: () => {
      try {
        const stored = localStorage.getItem('ACADIFY_REACT_QUERY_CACHE');
        return stored ? JSON.parse(stored) : undefined;
      } catch (error) {
        console.warn('Error restoring React Query cache:', error);
        return undefined;
      }
    },
    removeClient: () => {
      try {
        localStorage.removeItem('ACADIFY_REACT_QUERY_CACHE');
      } catch (error) {
        console.warn('Error removing React Query cache:', error);
      }
    },
  };
};

/**
 * Cliente de React Query con configuración optimizada
 * 
 * Principios aplicados:
 * - Caching agresivo para reducir requests innecesarios
 * - Refetch automático solo cuando tiene sentido
 * - Manejo de errores consistente
 * - Retry con backoff exponencial
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Tiempo que los datos se consideran frescos (sin refetch automático)
      staleTime: 1000 * 60 * 5, // 5 minutos
      
      // Tiempo que los datos permanecen en cache
      gcTime: 1000 * 60 * 30, // 30 minutos (antes cacheTime)
      
      // Refetch solo cuando el usuario vuelve a la ventana y los datos están stale
      refetchOnWindowFocus: true,
      refetchOnMount: true,
      refetchOnReconnect: true,
      
      // Retry con backoff exponencial
      retry: (failureCount, error: any) => {
        // No reintentar en errores 4xx (excepto 408 - Request Timeout)
        if (error?.response?.status >= 400 && error?.response?.status < 500 && error?.response?.status !== 408) {
          return false;
        }
        // Máximo 3 reintentos para otros errores
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      // Retry para mutaciones críticas
      retry: 1,
      retryDelay: 1000,
    },
  },
});

/**
 * Claves de consulta centralizadas
 * Facilita la invalidación y prefetching
 */
export const queryKeys = {
  // Autenticación
  auth: {
    user: ['auth', 'user'] as const,
  },
  
  // Cursos
  courses: {
    all: ['courses'] as const,
    lists: () => [...queryKeys.courses.all, 'list'] as const,
    list: (filters?: any) => [...queryKeys.courses.lists(), filters] as const,
    details: () => [...queryKeys.courses.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.courses.details(), id] as const,
    mine: () => [...queryKeys.courses.all, 'mine'] as const,
  },
  
  // Comentarios
  comments: {
    all: ['comments'] as const,
    lists: () => [...queryKeys.comments.all, 'list'] as const,
    list: (courseId: string, filters?: any) => [...queryKeys.comments.lists(), courseId, filters] as const,
  },
  
  // Tareas
  tasks: {
    all: ['tasks'] as const,
    lists: () => [...queryKeys.tasks.all, 'list'] as const,
    list: (courseId: string) => [...queryKeys.tasks.lists(), courseId] as const,
  },
  
  // Avatar
  avatar: {
    all: ['avatar'] as const,
    mine: () => [...queryKeys.avatar.all, 'mine'] as const,
    gallery: (filters?: any) => [...queryKeys.avatar.all, 'gallery', filters] as const,
  },
  
  // Notificaciones
  notifications: {
    all: ['notifications'] as const,
    unread: () => [...queryKeys.notifications.all, 'unread'] as const,
  },
} as const;

/**
 * Helper para invalidar queries relacionadas con cursos
 */
export const invalidateCourseQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.courses.all });
};

/**
 * Helper para invalidar queries relacionadas con comentarios de un curso
 */
export const invalidateCourseComments = (courseId: string) => {
  queryClient.invalidateQueries({ queryKey: queryKeys.comments.list(courseId) });
};

/**
 * Helper para actualizar optimistamente un curso
 */
export const updateCourseOptimistically = (courseId: string, updater: (old: any) => any) => {
  queryClient.setQueryData(queryKeys.courses.detail(courseId), updater);
};

/**
 * Configuración de persistencia en localStorage
 * Mantiene el cache entre sesiones para mejor UX
 */
const localStoragePersister = createLocalStoragePersister();

/**
 * Activar persistencia del cache
 * Los datos se guardan en localStorage y se recuperan al recargar
 */
if (typeof window !== 'undefined') {
  persistQueryClient({
    queryClient,
    persister: localStoragePersister,
    maxAge: 1000 * 60 * 60 * 24, // 24 horas
    hydrateOptions: {
      // Solo hidratar queries que no estén stale
      defaultOptions: {
        queries: {
          gcTime: 1000 * 60 * 60 * 24, // 24 horas
        },
      },
    },
    dehydrateOptions: {
      // No persistir queries con errores
      shouldDehydrateQuery: (query) => {
        return query.state.status === 'success';
      },
    },
  });
}
