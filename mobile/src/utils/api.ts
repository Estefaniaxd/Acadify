/**
 * API Configuration and Utilities
 * Base URL, error handling, and helpers for API calls
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

// Determine API base URL based on platform and environment
export const API_BASE_URL = __DEV__
  ? Platform.OS === 'android'
    ? 'http://10.0.2.2:8000' // Android emulator
    : 'http://localhost:8000' // iOS simulator / real device
  : 'https://your-api-domain.com'; // Production

export const AVATAR_ASSETS_BASE_URL = __DEV__
  ? `${API_BASE_URL}/static/assets`
  : 'https://your-api-domain.com/static/assets';

/**
 * Token Management with Expo SecureStore
 */
export const TokenStorage = {
  async getAccessToken(): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync('access_token');
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  },

  async setAccessToken(token: string): Promise<void> {
    try {
      await SecureStore.setItemAsync('access_token', token);
    } catch (error) {
      console.error('Error setting access token:', error);
    }
  },

  async getRefreshToken(): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync('refresh_token');
    } catch (error) {
      console.error('Error getting refresh token:', error);
      return null;
    }
  },

  async setRefreshToken(token: string): Promise<void> {
    try {
      await SecureStore.setItemAsync('refresh_token', token);
    } catch (error) {
      console.error('Error setting refresh token:', error);
    }
  },

  async clearTokens(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('access_token');
      await SecureStore.deleteItemAsync('refresh_token');
    } catch (error) {
      console.error('Error clearing tokens:', error);
    }
  },
};

/**
 * Create axios instance with default config
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

/**
 * Request interceptor to add authorization token
 */
apiClient.interceptors.request.use(
  async (config) => {
    const token = await TokenStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling and token refresh
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Token expired, try to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await TokenStorage.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Call refresh endpoint
        const response = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          }
        );

        const { access_token, refresh_token } = response.data;
        await TokenStorage.setAccessToken(access_token);
        
        if (refresh_token) {
          await TokenStorage.setRefreshToken(refresh_token);
        }

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        await TokenStorage.clearTokens();
        // Emit event for AuthContext to handle
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new Event('auth-token-expired'));
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Format API error messages
 */
export function formatApiError(error: any): string {
  // Axios error with response
  if (error.response) {
    const data = error.response.data;
    
    // FastAPI validation error
    if (data.detail && Array.isArray(data.detail)) {
      return data.detail
        .map((err: any) => {
          const field = err.loc?.join(' > ') || 'Campo';
          return `${field}: ${err.msg}`;
        })
        .join('\n');
    }
    
    // Simple error message
    if (typeof data.detail === 'string') {
      return data.detail;
    }
    
    if (typeof data.message === 'string') {
      return data.message;
    }
    
    // Status-based messages
    if (error.response.status === 401) {
      return 'Credenciales incorrectas';
    }
    if (error.response.status === 403) {
      return 'No tienes permisos para realizar esta acción';
    }
    if (error.response.status === 404) {
      return 'Recurso no encontrado';
    }
    if (error.response.status === 423) {
      return 'Cuenta bloqueada por intentos fallidos';
    }
    if (error.response.status >= 500) {
      return 'Error del servidor. Intenta de nuevo más tarde.';
    }
    
    return `Error ${error.response.status}: ${error.response.statusText}`;
  }
  
  // Network error
  if (error.request) {
    return 'No se pudo conectar al servidor. Verifica tu conexión a internet.';
  }
  
  // Other errors
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'Error desconocido. Intenta de nuevo.';
}

/**
 * API Endpoints
 */
export const API = {
  // Auth endpoints
  auth: {
    login: (data: { identifier: string; password: string; remember?: boolean; otp_code?: string }) =>
      apiClient.post('/auth/login', data),
    register: (data: any) => apiClient.post('/auth/register', data),
    logout: () => apiClient.post('/auth/logout'),
    refresh: () => apiClient.post('/auth/refresh'),
    recoverPassword: (email: string) => apiClient.post('/auth/recover', { email }),
    resetPassword: (token: string, password: string) =>
      apiClient.post('/auth/reset', { token, password }),
  },
  
  // User endpoints
  user: {
    getProfile: () => apiClient.get('/users/me'),
    updateProfile: (data: any) => apiClient.patch('/users/me', data),
  },
  
  // Add more endpoints as needed
};

export default apiClient;
