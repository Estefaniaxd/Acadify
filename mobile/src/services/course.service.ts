/**
 * Course Service
 * Handles all course-related API calls
 * 
 * @module services/course
 * @implements Repository Pattern
 * @follows Single Responsibility Principle
 */

import { apiClient } from '@/utils/api';
import { AxiosResponse } from 'axios';

// ==================== TYPES ====================

/**
 * Course data
 */
export interface Course {
  id: string;
  titulo: string;
  descripcion: string;
  instructor_id: string;
  instructor_nombre: string;
  categoria: string;
  nivel: 'principiante' | 'intermedio' | 'avanzado';
  duracion_horas: number;
  thumbnail_url?: string;
  precio: number;
  rating: number;
  total_estudiantes: number;
  total_lecciones: number;
  estado: 'borrador' | 'publicado' | 'archivado';
  created_at: string;
  updated_at: string;
}

/**
 * Course with progress
 */
export interface CourseWithProgress extends Course {
  progreso: number;
  ultima_leccion_id?: string;
  fecha_inscripcion: string;
  fecha_ultimo_acceso?: string;
}

/**
 * Lesson data
 */
export interface Lesson {
  id: string;
  curso_id: string;
  titulo: string;
  descripcion?: string;
  contenido: string;
  orden: number;
  duracion_minutos: number;
  tipo: 'video' | 'texto' | 'quiz' | 'practica';
  video_url?: string;
  recursos_urls?: string[];
  es_gratuito: boolean;
  created_at: string;
}

/**
 * Lesson with progress
 */
export interface LessonWithProgress extends Lesson {
  completada: boolean;
  progreso: number;
  fecha_completado?: string;
}

/**
 * Course enrollment request
 */
export interface EnrollCourseRequest {
  curso_id: string;
}

/**
 * Course enrollment response
 */
export interface EnrollCourseResponse {
  message: string;
  inscripcion_id: string;
  curso_id: string;
}

/**
 * Mark lesson complete request
 */
export interface MarkLessonCompleteRequest {
  leccion_id: string;
}

/**
 * Course filters
 */
export interface CourseFilters {
  categoria?: string;
  nivel?: 'principiante' | 'intermedio' | 'avanzado';
  search?: string;
  instructor_id?: string;
  limit?: number;
  offset?: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

/**
 * Course review
 */
export interface CourseReview {
  id: string;
  curso_id: string;
  usuario_id: string;
  usuario_nombre: string;
  usuario_avatar?: string;
  rating: number;
  comentario?: string;
  created_at: string;
}

/**
 * Add review request
 */
export interface AddReviewRequest {
  rating: number;
  comentario?: string;
}

// ==================== SERVICE ====================

/**
 * Course Service
 * Provides methods for course and lesson management
 * 
 * @class CourseService
 * @implements Repository Pattern
 */
class CourseService {
  private readonly baseUrl = '/courses';

  /**
   * Get all available courses
   * 
   * @param {CourseFilters} filters - Filter criteria
   * @returns {Promise<PaginatedResponse<Course>>} List of courses
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const response = await courseService.getCourses({
   *   categoria: 'Programación',
   *   nivel: 'intermedio',
   *   limit: 10
   * });
   * ```
   */
  async getCourses(filters?: CourseFilters): Promise<PaginatedResponse<Course>> {
    const response: AxiosResponse<PaginatedResponse<Course>> = await apiClient.get(
      this.baseUrl,
      { params: filters }
    );
    return response.data;
  }

  /**
   * Get course by ID
   * 
   * @param {string} courseId - Course ID
   * @returns {Promise<Course>} Course details
   * @throws {AxiosError} If course not found
   * 
   * @example
   * ```typescript
   * const course = await courseService.getCourseById('course-123');
   * ```
   */
  async getCourseById(courseId: string): Promise<Course> {
    const response: AxiosResponse<Course> = await apiClient.get(`${this.baseUrl}/${courseId}`);
    return response.data;
  }

  /**
   * Get user's enrolled courses
   * 
   * @returns {Promise<CourseWithProgress[]>} List of enrolled courses with progress
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const myCourses = await courseService.getEnrolledCourses();
   * ```
   */
  async getEnrolledCourses(): Promise<CourseWithProgress[]> {
    const response: AxiosResponse<CourseWithProgress[]> = await apiClient.get(
      `${this.baseUrl}/enrolled`
    );
    return response.data;
  }

  /**
   * Enroll in a course
   * 
   * @param {string} courseId - Course ID to enroll in
   * @returns {Promise<EnrollCourseResponse>} Enrollment confirmation
   * @throws {AxiosError} If already enrolled or course not found
   * 
   * @example
   * ```typescript
   * const result = await courseService.enrollCourse('course-123');
   * ```
   */
  async enrollCourse(courseId: string): Promise<EnrollCourseResponse> {
    const response: AxiosResponse<EnrollCourseResponse> = await apiClient.post(
      `${this.baseUrl}/${courseId}/enroll`
    );
    return response.data;
  }

  /**
   * Unenroll from a course
   * 
   * @param {string} courseId - Course ID to unenroll from
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If not enrolled or request fails
   * 
   * @example
   * ```typescript
   * await courseService.unenrollCourse('course-123');
   * ```
   */
  async unenrollCourse(courseId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.post(
      `${this.baseUrl}/${courseId}/unenroll`
    );
    return response.data;
  }

  /**
   * Get course lessons
   * 
   * @param {string} courseId - Course ID
   * @returns {Promise<LessonWithProgress[]>} List of lessons with progress
   * @throws {AxiosError} If course not found or not enrolled
   * 
   * @example
   * ```typescript
   * const lessons = await courseService.getCourseLessons('course-123');
   * ```
   */
  async getCourseLessons(courseId: string): Promise<LessonWithProgress[]> {
    const response: AxiosResponse<LessonWithProgress[]> = await apiClient.get(
      `${this.baseUrl}/${courseId}/lessons`
    );
    return response.data;
  }

  /**
   * Get lesson by ID
   * 
   * @param {string} courseId - Course ID
   * @param {string} lessonId - Lesson ID
   * @returns {Promise<LessonWithProgress>} Lesson details with progress
   * @throws {AxiosError} If lesson not found or not enrolled
   * 
   * @example
   * ```typescript
   * const lesson = await courseService.getLessonById('course-123', 'lesson-456');
   * ```
   */
  async getLessonById(courseId: string, lessonId: string): Promise<LessonWithProgress> {
    const response: AxiosResponse<LessonWithProgress> = await apiClient.get(
      `${this.baseUrl}/${courseId}/lessons/${lessonId}`
    );
    return response.data;
  }

  /**
   * Mark lesson as complete
   * 
   * @param {string} courseId - Course ID
   * @param {string} lessonId - Lesson ID
   * @returns {Promise<{message: string; puntos_ganados: number}>} Success message
   * @throws {AxiosError} If lesson not found or already completed
   * 
   * @example
   * ```typescript
   * const result = await courseService.markLessonComplete('course-123', 'lesson-456');
   * console.log('Ganaste', result.puntos_ganados, 'puntos');
   * ```
   */
  async markLessonComplete(
    courseId: string,
    lessonId: string
  ): Promise<{ message: string; puntos_ganados: number }> {
    const response: AxiosResponse<{ message: string; puntos_ganados: number }> =
      await apiClient.post(`${this.baseUrl}/${courseId}/lessons/${lessonId}/complete`);
    return response.data;
  }

  /**
   * Update lesson progress
   * 
   * @param {string} courseId - Course ID
   * @param {string} lessonId - Lesson ID
   * @param {number} progress - Progress percentage (0-100)
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If lesson not found
   * 
   * @example
   * ```typescript
   * await courseService.updateLessonProgress('course-123', 'lesson-456', 75);
   * ```
   */
  async updateLessonProgress(
    courseId: string,
    lessonId: string,
    progress: number
  ): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.patch(
      `${this.baseUrl}/${courseId}/lessons/${lessonId}/progress`,
      { progreso: progress }
    );
    return response.data;
  }

  /**
   * Get course reviews
   * 
   * @param {string} courseId - Course ID
   * @param {number} limit - Max reviews to return
   * @param {number} offset - Offset for pagination
   * @returns {Promise<PaginatedResponse<CourseReview>>} List of reviews
   * @throws {AxiosError} If course not found
   * 
   * @example
   * ```typescript
   * const reviews = await courseService.getCourseReviews('course-123', 10, 0);
   * ```
   */
  async getCourseReviews(
    courseId: string,
    limit = 10,
    offset = 0
  ): Promise<PaginatedResponse<CourseReview>> {
    const response: AxiosResponse<PaginatedResponse<CourseReview>> = await apiClient.get(
      `${this.baseUrl}/${courseId}/reviews`,
      { params: { limit, offset } }
    );
    return response.data;
  }

  /**
   * Add course review
   * 
   * @param {string} courseId - Course ID
   * @param {AddReviewRequest} review - Review data
   * @returns {Promise<CourseReview>} Created review
   * @throws {AxiosError} If not enrolled or already reviewed
   * 
   * @example
   * ```typescript
   * const review = await courseService.addCourseReview('course-123', {
   *   rating: 5,
   *   comentario: 'Excelente curso, muy completo'
   * });
   * ```
   */
  async addCourseReview(courseId: string, review: AddReviewRequest): Promise<CourseReview> {
    const response: AxiosResponse<CourseReview> = await apiClient.post(
      `${this.baseUrl}/${courseId}/reviews`,
      review
    );
    return response.data;
  }

  /**
   * Update course review
   * 
   * @param {string} courseId - Course ID
   * @param {string} reviewId - Review ID
   * @param {AddReviewRequest} review - Updated review data
   * @returns {Promise<CourseReview>} Updated review
   * @throws {AxiosError} If review not found or not owner
   * 
   * @example
   * ```typescript
   * await courseService.updateCourseReview('course-123', 'review-456', {
   *   rating: 4,
   *   comentario: 'Muy buen curso'
   * });
   * ```
   */
  async updateCourseReview(
    courseId: string,
    reviewId: string,
    review: AddReviewRequest
  ): Promise<CourseReview> {
    const response: AxiosResponse<CourseReview> = await apiClient.patch(
      `${this.baseUrl}/${courseId}/reviews/${reviewId}`,
      review
    );
    return response.data;
  }

  /**
   * Delete course review
   * 
   * @param {string} courseId - Course ID
   * @param {string} reviewId - Review ID
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If review not found or not owner
   * 
   * @example
   * ```typescript
   * await courseService.deleteCourseReview('course-123', 'review-456');
   * ```
   */
  async deleteCourseReview(courseId: string, reviewId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${this.baseUrl}/${courseId}/reviews/${reviewId}`
    );
    return response.data;
  }

  /**
   * Get course categories
   * 
   * @returns {Promise<string[]>} List of categories
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const categories = await courseService.getCategories();
   * ```
   */
  async getCategories(): Promise<string[]> {
    const response: AxiosResponse<string[]> = await apiClient.get(`${this.baseUrl}/categories`);
    return response.data;
  }
}

// Export singleton instance
export const courseService = new CourseService();
export default courseService;
