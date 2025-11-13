/**
 * User Service
 * Handles all user-related API calls
 * 
 * @module services/user
 * @implements Repository Pattern
 * @follows Single Responsibility Principle
 */

import { apiClient } from '@/utils/api';
import { AxiosResponse } from 'axios';

// ==================== TYPES ====================

/**
 * User profile data
 */
export interface UserProfile {
  id: string;
  username: string;
  nombres: string;
  apellidos: string;
  correo_institucional: string;
  tipo_documento: string;
  numero_documento: string;
  rol: 'estudiante' | 'docente' | 'admin';
  avatar_url?: string;
  bio?: string;
  telefono?: string;
  fecha_nacimiento?: string;
  genero?: 'masculino' | 'femenino' | 'otro';
  ciudad?: string;
  pais?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Update profile request
 */
export interface UpdateProfileRequest {
  nombres?: string;
  apellidos?: string;
  bio?: string;
  telefono?: string;
  fecha_nacimiento?: string;
  genero?: 'masculino' | 'femenino' | 'otro';
  ciudad?: string;
  pais?: string;
}

/**
 * Change password request
 */
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

/**
 * Upload avatar response
 */
export interface UploadAvatarResponse {
  message: string;
  avatar_url: string;
}

/**
 * User statistics
 */
export interface UserStatistics {
  cursos_inscritos: number;
  cursos_completados: number;
  puntos_totales: number;
  nivel: number;
  racha_dias: number;
  logros_desbloqueados: number;
  insignias_obtenidas: number;
  posicion_ranking: number;
}

/**
 * User preferences
 */
export interface UserPreferences {
  tema: 'light' | 'dark' | 'auto';
  idioma: string;
  notificaciones_push: boolean;
  notificaciones_email: boolean;
  notificaciones_mensajes: boolean;
  notificaciones_cursos: boolean;
  notificaciones_logros: boolean;
  sonido_notificaciones: boolean;
}

// ==================== SERVICE ====================

/**
 * User Service
 * Provides methods for user profile and settings management
 * 
 * @class UserService
 * @implements Repository Pattern
 */
class UserService {
  private readonly baseUrl = '/users';

  /**
   * Get current user profile
   * 
   * @returns {Promise<UserProfile>} User profile data
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const profile = await userService.getProfile();
   * console.log(profile.nombres, profile.apellidos);
   * ```
   */
  async getProfile(): Promise<UserProfile> {
    const response: AxiosResponse<UserProfile> = await apiClient.get(`${this.baseUrl}/me`);
    return response.data;
  }

  /**
   * Get user profile by ID
   * 
   * @param {string} userId - User ID
   * @returns {Promise<UserProfile>} User profile data
   * @throws {AxiosError} If user not found or request fails
   * 
   * @example
   * ```typescript
   * const profile = await userService.getUserById('user-123');
   * ```
   */
  async getUserById(userId: string): Promise<UserProfile> {
    const response: AxiosResponse<UserProfile> = await apiClient.get(`${this.baseUrl}/${userId}`);
    return response.data;
  }

  /**
   * Update current user profile
   * 
   * @param {UpdateProfileRequest} data - Profile data to update
   * @returns {Promise<UserProfile>} Updated profile
   * @throws {AxiosError} If validation fails or request fails
   * 
   * @example
   * ```typescript
   * const updatedProfile = await userService.updateProfile({
   *   bio: 'Estudiante apasionado por la tecnología',
   *   ciudad: 'Bogotá',
   *   telefono: '+57 300 1234567'
   * });
   * ```
   */
  async updateProfile(data: UpdateProfileRequest): Promise<UserProfile> {
    const response: AxiosResponse<UserProfile> = await apiClient.patch(`${this.baseUrl}/me`, data);
    return response.data;
  }

  /**
   * Change user password
   * 
   * @param {ChangePasswordRequest} data - Current and new password
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If current password incorrect or validation fails
   * 
   * @example
   * ```typescript
   * await userService.changePassword({
   *   current_password: 'oldPassword123',
   *   new_password: 'newSecurePassword456'
   * });
   * ```
   */
  async changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.post(
      `${this.baseUrl}/me/change-password`,
      data
    );
    return response.data;
  }

  /**
   * Upload user avatar
   * 
   * @param {File | Blob} file - Avatar image file
   * @returns {Promise<UploadAvatarResponse>} Avatar URL
   * @throws {AxiosError} If file too large or invalid format
   * 
   * @example
   * ```typescript
   * const result = await userService.uploadAvatar(imageFile);
   * console.log('Avatar URL:', result.avatar_url);
   * ```
   */
  async uploadAvatar(file: File | Blob): Promise<UploadAvatarResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<UploadAvatarResponse> = await apiClient.post(
      `${this.baseUrl}/me/avatar`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Delete user avatar (revert to default)
   * 
   * @returns {Promise<{message: string}>} Success message
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * await userService.deleteAvatar();
   * ```
   */
  async deleteAvatar(): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${this.baseUrl}/me/avatar`
    );
    return response.data;
  }

  /**
   * Get user statistics
   * 
   * @returns {Promise<UserStatistics>} User stats
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const stats = await userService.getStatistics();
   * console.log('Nivel:', stats.nivel, 'Puntos:', stats.puntos_totales);
   * ```
   */
  async getStatistics(): Promise<UserStatistics> {
    const response: AxiosResponse<UserStatistics> = await apiClient.get(
      `${this.baseUrl}/me/statistics`
    );
    return response.data;
  }

  /**
   * Get user preferences
   * 
   * @returns {Promise<UserPreferences>} User preferences
   * @throws {AxiosError} If request fails
   * 
   * @example
   * ```typescript
   * const prefs = await userService.getPreferences();
   * console.log('Tema:', prefs.tema);
   * ```
   */
  async getPreferences(): Promise<UserPreferences> {
    const response: AxiosResponse<UserPreferences> = await apiClient.get(
      `${this.baseUrl}/me/preferences`
    );
    return response.data;
  }

  /**
   * Update user preferences
   * 
   * @param {Partial<UserPreferences>} preferences - Preferences to update
   * @returns {Promise<UserPreferences>} Updated preferences
   * @throws {AxiosError} If validation fails
   * 
   * @example
   * ```typescript
   * await userService.updatePreferences({
   *   tema: 'dark',
   *   notificaciones_push: true
   * });
   * ```
   */
  async updatePreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    const response: AxiosResponse<UserPreferences> = await apiClient.patch(
      `${this.baseUrl}/me/preferences`,
      preferences
    );
    return response.data;
  }

  /**
   * Delete user account
   * 
   * @param {string} password - User password for confirmation
   * @returns {Promise<{message: string}>} Confirmation message
   * @throws {AxiosError} If password incorrect
   * 
   * @example
   * ```typescript
   * await userService.deleteAccount('myPassword123');
   * ```
   */
  async deleteAccount(password: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${this.baseUrl}/me`,
      {
        data: { password },
      }
    );
    return response.data;
  }
}

// Export singleton instance
export const userService = new UserService();
export default userService;
