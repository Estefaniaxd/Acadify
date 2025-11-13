/**
 * Custom Hooks for User API
 * React Query hooks for user profile and settings management
 * 
 * @module hooks/useUser
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { userService, type UserProfile, type UpdateProfileRequest, type ChangePasswordRequest, type UserStatistics, type UserPreferences } from '@/services';

// ==================== QUERY KEYS ====================

export const USER_QUERY_KEYS = {
  profile: ['user', 'profile'] as const,
  userById: (id: string) => ['user', 'profile', id] as const,
  statistics: ['user', 'statistics'] as const,
  preferences: ['user', 'preferences'] as const,
} as const;

// ==================== USER PROFILE ====================

/**
 * Hook para obtener perfil del usuario actual
 * 
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con perfil
 * 
 * @example
 * ```typescript
 * const { data: profile, isLoading } = useUserProfile();
 * console.log(profile?.nombres, profile?.apellidos);
 * ```
 */
export function useUserProfile(
  options?: Omit<UseQueryOptions<UserProfile>, 'queryKey' | 'queryFn'>
) {
  return useQuery<UserProfile>({
    queryKey: USER_QUERY_KEYS.profile,
    queryFn: () => userService.getProfile(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
}

/**
 * Hook para obtener perfil de un usuario por ID
 * 
 * @param {string} userId - ID del usuario
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con perfil
 * 
 * @example
 * ```typescript
 * const { data: user } = useUserById('user-123');
 * ```
 */
export function useUserById(
  userId: string,
  options?: Omit<UseQueryOptions<UserProfile>, 'queryKey' | 'queryFn'>
) {
  return useQuery<UserProfile>({
    queryKey: USER_QUERY_KEYS.userById(userId),
    queryFn: () => userService.getUserById(userId),
    enabled: !!userId,
    staleTime: 1000 * 60 * 5,
    ...options,
  });
}

/**
 * Hook para obtener estadísticas del usuario
 * 
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con estadísticas
 * 
 * @example
 * ```typescript
 * const { data: stats } = useUserStatistics();
 * console.log('Nivel:', stats?.nivel, 'Puntos:', stats?.puntos_totales);
 * ```
 */
export function useUserStatistics(
  options?: Omit<UseQueryOptions<UserStatistics>, 'queryKey' | 'queryFn'>
) {
  return useQuery<UserStatistics>({
    queryKey: USER_QUERY_KEYS.statistics,
    queryFn: () => userService.getStatistics(),
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
}

/**
 * Hook para obtener preferencias del usuario
 * 
 * @param {UseQueryOptions} options - Opciones de React Query
 * @returns Query result con preferencias
 * 
 * @example
 * ```typescript
 * const { data: preferences } = useUserPreferences();
 * console.log('Tema:', preferences?.tema);
 * ```
 */
export function useUserPreferences(
  options?: Omit<UseQueryOptions<UserPreferences>, 'queryKey' | 'queryFn'>
) {
  return useQuery<UserPreferences>({
    queryKey: USER_QUERY_KEYS.preferences,
    queryFn: () => userService.getPreferences(),
    staleTime: 1000 * 60 * 10, // 10 minutes
    ...options,
  });
}

// ==================== MUTATIONS ====================

/**
 * Hook para actualizar perfil del usuario
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: updateProfile, isLoading } = useUpdateProfile();
 * updateProfile({
 *   bio: 'Nueva biografía',
 *   ciudad: 'Bogotá'
 * });
 * ```
 */
export function useUpdateProfile(
  options?: UseMutationOptions<UserProfile, Error, UpdateProfileRequest>
) {
  const queryClient = useQueryClient();

  return useMutation<UserProfile, Error, UpdateProfileRequest>({
    mutationFn: (data: UpdateProfileRequest) => userService.updateProfile(data),
    onSuccess: (updatedProfile) => {
      // Update cache with new data
      queryClient.setQueryData(USER_QUERY_KEYS.profile, updatedProfile);
    },
    ...options,
  });
}

/**
 * Hook para cambiar contraseña
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: changePassword, isLoading } = useChangePassword();
 * changePassword({
 *   current_password: 'oldPass123',
 *   new_password: 'newSecure456'
 * });
 * ```
 */
export function useChangePassword(
  options?: UseMutationOptions<{ message: string }, Error, ChangePasswordRequest>
) {
  return useMutation<{ message: string }, Error, ChangePasswordRequest>({
    mutationFn: (data: ChangePasswordRequest) => userService.changePassword(data),
    ...options,
  });
}

/**
 * Hook para subir avatar
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: uploadAvatar, isLoading } = useUploadAvatar();
 * uploadAvatar(imageFile);
 * ```
 */
export function useUploadAvatar(
  options?: UseMutationOptions<any, Error, File | Blob>
) {
  const queryClient = useQueryClient();

  return useMutation<any, Error, File | Blob>({
    mutationFn: (file: File | Blob) => userService.uploadAvatar(file),
    onSuccess: () => {
      // Refetch profile to get new avatar URL
      queryClient.invalidateQueries({ queryKey: USER_QUERY_KEYS.profile });
    },
    ...options,
  });
}

/**
 * Hook para eliminar avatar
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteAvatar } = useDeleteAvatar();
 * deleteAvatar();
 * ```
 */
export function useDeleteAvatar(
  options?: UseMutationOptions<{ message: string }, Error, void>
) {
  const queryClient = useQueryClient();

  return useMutation<{ message: string }, Error, void>({
    mutationFn: () => userService.deleteAvatar(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: USER_QUERY_KEYS.profile });
    },
    ...options,
  });
}

/**
 * Hook para actualizar preferencias
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: updatePreferences } = useUpdatePreferences();
 * updatePreferences({
 *   tema: 'dark',
 *   notificaciones_push: true
 * });
 * ```
 */
export function useUpdatePreferences(
  options?: UseMutationOptions<UserPreferences, Error, Partial<UserPreferences>>
) {
  const queryClient = useQueryClient();

  return useMutation<UserPreferences, Error, Partial<UserPreferences>>({
    mutationFn: (preferences: Partial<UserPreferences>) => 
      userService.updatePreferences(preferences),
    onSuccess: (updatedPreferences) => {
      queryClient.setQueryData(USER_QUERY_KEYS.preferences, updatedPreferences);
    },
    ...options,
  });
}

/**
 * Hook para eliminar cuenta
 * 
 * @param {UseMutationOptions} options - Opciones de React Query
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteAccount } = useDeleteAccount();
 * deleteAccount('myPassword123');
 * ```
 */
export function useDeleteAccount(
  options?: UseMutationOptions<{ message: string }, Error, string>
) {
  return useMutation<{ message: string }, Error, string>({
    mutationFn: (password: string) => userService.deleteAccount(password),
    ...options,
  });
}
