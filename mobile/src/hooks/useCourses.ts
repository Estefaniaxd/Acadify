/**
 * Custom Hooks for API Integration
 * React Query hooks for data fetching with caching and optimization
 * 
 * @module hooks/useAPI
 * @follows Separation of Concerns
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { courseService, type Course, type CourseWithProgress, type Lesson, type LessonWithProgress, type CourseFilters, type PaginatedResponse, type CourseReview, type AddReviewRequest } from '@/services';
import { formatApiError } from '@/utils/api';

// ==================== QUERY KEYS ====================

/**
 * Query keys for React Query cache management
 * Follows a hierarchical structure for easy invalidation
 */
export const QUERY_KEYS = {
  // Courses
  courses: ['courses'] as const,
  coursesList: (filters?: CourseFilters) => ['courses', 'list', filters] as const,
  courseDetail: (id: string) => ['courses', 'detail', id] as const,
  courseLessons: (id: string) => ['courses', id, 'lessons'] as const,
  courseLesson: (courseId: string, lessonId: string) => ['courses', courseId, 'lessons', lessonId] as const,
  courseReviews: (id: string) => ['courses', id, 'reviews'] as const,
  enrolledCourses: ['courses', 'enrolled'] as const,
  courseCategories: ['courses', 'categories'] as const,
} as const;

// ==================== COURSES ====================

/**
 * Hook para obtener lista de cursos
 * 
 * @param {CourseFilters} filters - Filtros de búsqueda
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con lista de cursos
 * 
 * @example
 * ```typescript
 * const { data, isLoading, error } = useCourses({
 *   categoria: 'Programación',
 *   nivel: 'intermedio'
 * });
 * ```
 */
export function useCourses(
  filters?: CourseFilters,
  options?: Omit<UseQueryOptions<PaginatedResponse<Course>>, 'queryKey' | 'queryFn'>
) {
  return useQuery<PaginatedResponse<Course>>({
    queryKey: QUERY_KEYS.coursesList(filters),
    queryFn: () => courseService.getCourses(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
}

/**
 * Hook para obtener detalle de un curso
 * 
 * @param {string} courseId - ID del curso
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con detalle del curso
 * 
 * @example
 * ```typescript
 * const { data: course, isLoading } = useCourseDetail('course-123');
 * ```
 */
export function useCourseDetail(
  courseId: string,
  options?: Omit<UseQueryOptions<Course>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Course>({
    queryKey: QUERY_KEYS.courseDetail(courseId),
    queryFn: () => courseService.getCourseById(courseId),
    enabled: !!courseId,
    staleTime: 1000 * 60 * 5,
    ...options,
  });
}

/**
 * Hook para obtener cursos inscritos del usuario
 * 
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con cursos inscritos
 * 
 * @example
 * ```typescript
 * const { data: myCourses, isLoading } = useEnrolledCourses();
 * ```
 */
export function useEnrolledCourses(
  options?: Omit<UseQueryOptions<CourseWithProgress[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery<CourseWithProgress[]>({
    queryKey: QUERY_KEYS.enrolledCourses,
    queryFn: () => courseService.getEnrolledCourses(),
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
}

/**
 * Hook para obtener lecciones de un curso
 * 
 * @param {string} courseId - ID del curso
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con lecciones
 * 
 * @example
 * ```typescript
 * const { data: lessons } = useCourseLessons('course-123');
 * ```
 */
export function useCourseLessons(
  courseId: string,
  options?: Omit<UseQueryOptions<LessonWithProgress[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery<LessonWithProgress[]>({
    queryKey: QUERY_KEYS.courseLessons(courseId),
    queryFn: () => courseService.getCourseLessons(courseId),
    enabled: !!courseId,
    staleTime: 1000 * 60 * 5,
    ...options,
  });
}

/**
 * Hook para obtener detalle de una lección
 * 
 * @param {string} courseId - ID del curso
 * @param {string} lessonId - ID de la lección
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con detalle de la lección
 * 
 * @example
 * ```typescript
 * const { data: lesson } = useLessonDetail('course-123', 'lesson-456');
 * ```
 */
export function useLessonDetail(
  courseId: string,
  lessonId: string,
  options?: Omit<UseQueryOptions<LessonWithProgress>, 'queryKey' | 'queryFn'>
) {
  return useQuery<LessonWithProgress>({
    queryKey: QUERY_KEYS.courseLesson(courseId, lessonId),
    queryFn: () => courseService.getLessonById(courseId, lessonId),
    enabled: !!courseId && !!lessonId,
    staleTime: 1000 * 60 * 5,
    ...options,
  });
}

/**
 * Hook para obtener reseñas de un curso
 * 
 * @param {string} courseId - ID del curso
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con reseñas
 * 
 * @example
 * ```typescript
 * const { data: reviews } = useCourseReviews('course-123');
 * ```
 */
export function useCourseReviews(
  courseId: string,
  options?: Omit<UseQueryOptions<PaginatedResponse<CourseReview>>, 'queryKey' | 'queryFn'>
) {
  return useQuery<PaginatedResponse<CourseReview>>({
    queryKey: QUERY_KEYS.courseReviews(courseId),
    queryFn: () => courseService.getCourseReviews(courseId),
    enabled: !!courseId,
    staleTime: 1000 * 60 * 5,
    ...options,
  });
}

/**
 * Hook para obtener categorías de cursos
 * 
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con categorías
 * 
 * @example
 * ```typescript
 * const { data: categories } = useCourseCategories();
 * ```
 */
export function useCourseCategories(
  options?: Omit<UseQueryOptions<string[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery<string[]>({
    queryKey: QUERY_KEYS.courseCategories,
    queryFn: () => courseService.getCategories(),
    staleTime: 1000 * 60 * 60, // 1 hour
    ...options,
  });
}

// ==================== MUTATIONS ====================

/**
 * Hook para inscribirse en un curso
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: enrollCourse, isLoading } = useEnrollCourse();
 * enrollCourse('course-123', {
 *   onSuccess: () => alert('Inscrito exitosamente')
 * });
 * ```
 */
export function useEnrollCourse(options?: UseMutationOptions<any, Error, string>) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, string>({
    mutationFn: (courseId: string) => courseService.enrollCourse(courseId),
    onSuccess: (_, courseId) => {
      // Invalidate queries to refetch data
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.enrolledCourses });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseDetail(courseId) });
    },
    ...options,
  });
}

/**
 * Hook para marcar lección como completada
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: completeLesson } = useMarkLessonComplete();
 * completeLesson({ courseId: 'course-123', lessonId: 'lesson-456' });
 * ```
 */
export function useMarkLessonComplete(
  options?: UseMutationOptions<any, Error, { courseId: string; lessonId: string }>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, { courseId: string; lessonId: string }>({
    mutationFn: ({ courseId, lessonId }) => courseService.markLessonComplete(courseId, lessonId),
    onSuccess: (_, { courseId, lessonId }) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseLessons(courseId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseLesson(courseId, lessonId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.enrolledCourses });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseDetail(courseId) });
    },
    ...options,
  });
}

/**
 * Hook para actualizar progreso de lección
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: updateProgress } = useUpdateLessonProgress();
 * updateProgress({ courseId: 'course-123', lessonId: 'lesson-456', progress: 75 });
 * ```
 */
export function useUpdateLessonProgress(
  options?: UseMutationOptions<any, Error, { courseId: string; lessonId: string; progress: number }>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, { courseId: string; lessonId: string; progress: number }>({
    mutationFn: ({ courseId, lessonId, progress }) =>
      courseService.updateLessonProgress(courseId, lessonId, progress),
    onSuccess: (_, { courseId, lessonId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseLesson(courseId, lessonId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseLessons(courseId) });
    },
    ...options,
  });
}

/**
 * Hook para agregar reseña a un curso
 * 
 * @param {string} courseId - ID del curso
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: addReview } = useAddCourseReview('course-123');
 * addReview({ rating: 5, comentario: 'Excelente curso' });
 * ```
 */
export function useAddCourseReview(
  courseId: string,
  options?: UseMutationOptions<CourseReview, Error, AddReviewRequest>
) {
  const queryClient = useQueryClient();

  return useMutation<CourseReview, Error, AddReviewRequest>({
    mutationFn: (review: AddReviewRequest) => courseService.addCourseReview(courseId, review),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseReviews(courseId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseDetail(courseId) });
    },
    ...options,
  });
}

/**
 * Hook para desinscribirse de un curso
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: unenroll } = useUnenrollCourse();
 * unenroll('course-123');
 * ```
 */
export function useUnenrollCourse(options?: UseMutationOptions<any, Error, string>) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, string>({
    mutationFn: (courseId: string) => courseService.unenrollCourse(courseId),
    onSuccess: (_, courseId) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.enrolledCourses });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseDetail(courseId) });
    },
    ...options,
  });
}
