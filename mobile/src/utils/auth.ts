/**
 * Authentication Utilities
 * JWT parsing, validation, and user info extraction
 */

import { TokenStorage } from './api';

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  nombres?: string;
  apellidos?: string;
}

export interface AuthStatus {
  isAuthenticated: boolean;
  token: string | null;
  needsLogin: boolean;
  tokenExpired: boolean;
}

/**
 * Parse user information from JWT token
 * Handles UTF-8 payload correctly
 */
export const parseUserFromToken = (token: string): User | null => {
  try {
    if (!token || typeof token !== 'string') return null;
    
    const parts = token.split('.');
    if (parts.length < 2) return null;
    
    const payload = parts[1];
    
    // Decode base64 with proper UTF-8 handling
    const json = decodeURIComponent(
      Array.prototype.map
        .call(atob(payload), (c: string) => {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );
    
    const decoded: any = JSON.parse(json);
    
    return {
      id: decoded.sub || decoded.user_id || '',
      username: decoded.username || '',
      email: decoded.email || decoded.correo_institucional || '',
      role: decoded.role || decoded.rol || decoded.perfil || 'estudiante',
      nombres: decoded.nombres,
      apellidos: decoded.apellidos,
    };
  } catch (error) {
    console.warn('Error parsing token:', error);
    return null;
  }
};

/**
 * Check if token is expired
 */
export const isTokenExpired = (token: string): boolean => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    
    const payload = JSON.parse(atob(parts[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    
    return payload.exp && payload.exp < currentTime;
  } catch {
    return true;
  }
};

/**
 * Check authentication status
 */
export const checkAuthStatus = async (): Promise<AuthStatus> => {
  const token = await TokenStorage.getAccessToken();
  
  if (!token) {
    return {
      isAuthenticated: false,
      token: null,
      needsLogin: true,
      tokenExpired: false,
    };
  }
  
  // Verify token format
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      await TokenStorage.clearTokens();
      return {
        isAuthenticated: false,
        token: null,
        needsLogin: true,
        tokenExpired: false,
      };
    }
    
    // Check expiration
    const payload = JSON.parse(atob(parts[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    
    if (payload.exp && payload.exp < currentTime) {
      await TokenStorage.clearTokens();
      return {
        isAuthenticated: false,
        token: null,
        needsLogin: true,
        tokenExpired: true,
      };
    }
    
    return {
      isAuthenticated: true,
      token: token,
      needsLogin: false,
      tokenExpired: false,
    };
  } catch (error) {
    console.warn('Error checking auth status:', error);
    await TokenStorage.clearTokens();
    return {
      isAuthenticated: false,
      token: null,
      needsLogin: true,
      tokenExpired: false,
    };
  }
};

/**
 * Get user info from stored token
 */
export const getUserInfo = async (): Promise<User | null> => {
  const token = await TokenStorage.getAccessToken();
  if (!token) return null;
  
  return parseUserFromToken(token);
};

/**
 * Clear all authentication data
 */
export const clearAuth = async (): Promise<void> => {
  await TokenStorage.clearTokens();
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 * Minimum 6 characters
 */
export const isValidPassword = (password: string): boolean => {
  return password.length >= 6;
};

/**
 * Get user initials from name
 */
export const getUserInitials = (user: User | null): string => {
  if (!user) return '?';
  
  if (user.nombres && user.apellidos) {
    return `${user.nombres[0]}${user.apellidos[0]}`.toUpperCase();
  }
  
  if (user.username) {
    return user.username.slice(0, 2).toUpperCase();
  }
  
  return user.email.slice(0, 2).toUpperCase();
};

/**
 * Format user display name
 */
export const getUserDisplayName = (user: User | null): string => {
  if (!user) return 'Usuario';
  
  if (user.nombres && user.apellidos) {
    return `${user.nombres} ${user.apellidos}`;
  }
  
  return user.username || user.email;
};
