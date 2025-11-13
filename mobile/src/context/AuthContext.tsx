/**
 * Authentication Context
 * Manages user authentication state, login, logout, and token handling
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter, useSegments } from 'expo-router';
import { TokenStorage } from '@/utils/api';
import { User, parseUserFromToken, checkAuthStatus } from '@/utils/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (accessToken: string, refreshToken?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const segments = useSegments();

  /**
   * Initialize auth state from stored tokens
   */
  useEffect(() => {
    initializeAuth();
  }, []);

  /**
   * Protected route navigation
   */
  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === '(auth)';
    const inAppGroup = segments[0] === '(app)';

    // Only redirect if user tries to access protected app routes without auth
    if (!isAuthenticated && inAppGroup) {
      // User not authenticated, trying to access protected routes
      router.replace('/(auth)/login');
    } else if (isAuthenticated && inAuthGroup) {
      // User authenticated but in auth screens, redirect to app
      router.replace('/(app)');
    }
  }, [isAuthenticated, segments, isLoading]);

  /**
   * Listen for token expiration events
   * Note: In React Native, we don't use window events
   * Token expiration is handled by the API client interceptor
   */

  /**
   * Initialize authentication from stored tokens
   */
  const initializeAuth = async () => {
    try {
      const authStatus = await checkAuthStatus();

      if (authStatus.isAuthenticated && authStatus.token) {
        const userData = parseUserFromToken(authStatus.token);
        if (userData) {
          setUser(userData);
          setIsAuthenticated(true);
        }
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Login with tokens
   */
  const login = async (accessToken: string, refreshToken?: string) => {
    try {
      // Store tokens
      await TokenStorage.setAccessToken(accessToken);
      if (refreshToken) {
        await TokenStorage.setRefreshToken(refreshToken);
      }

      // Parse user from token
      const userData = parseUserFromToken(accessToken);
      if (userData) {
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Error logging in:', error);
      throw error;
    }
  };

  /**
   * Logout and clear tokens
   */
  const logout = async () => {
    try {
      // Clear tokens
      await TokenStorage.clearTokens();

      // Clear state
      setUser(null);
      setIsAuthenticated(false);

      // Redirect to login
      router.replace('/(auth)/login');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  /**
   * Refresh user data from token
   */
  const refreshUser = async () => {
    try {
      const token = await TokenStorage.getAccessToken();
      if (token) {
        const userData = parseUserFromToken(token);
        if (userData) {
          setUser(userData);
        }
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
