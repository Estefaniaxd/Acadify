/**
 * Context para gestión de temas (Dark/Light mode)
 * Implementa persistencia, detección de preferencias del sistema y actualización global
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

export type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
}

/**
 * Provider de tema con soporte para:
 * - Persistencia en localStorage
 * - Detección de preferencias del sistema
 * - Sincronización entre pestañas
 * - Actualizaciones reactivas
 */
export function ThemeProvider({ children, defaultTheme }: Readonly<ThemeProviderProps>) {
  // Inicializar tema desde localStorage o preferencias del sistema
  const [theme, setTheme] = useState<Theme>(() => {
    // Intentar obtener del localStorage
    try {
      const stored = localStorage.getItem('theme');
      if (stored === 'dark' || stored === 'light') {
        return stored;
      }
    } catch (error) {
      console.warn('Error reading theme from localStorage:', error);
    }

    // Si hay defaultTheme, usarlo
    if (defaultTheme) {
      return defaultTheme;
    }

    // Detectar preferencia del sistema
    if (globalThis.window?.matchMedia?.('(prefers-color-scheme: dark)')?.matches) {
      return 'dark';
    }

    return 'light';
  });

  const isDark = theme === 'dark';

  /**
   * Función para cambiar el tema
   * - Actualiza el estado
   * - Persiste en localStorage
   * - Aplica clase CSS al documento
   * - Dispara evento personalizado para sincronización
   */
  const changeTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    
    // Persistir en localStorage
    try {
      localStorage.setItem('theme', newTheme);
    } catch (error) {
      console.warn('Error saving theme to localStorage:', error);
    }

    // Aplicar clase CSS
    const root = document.documentElement;
    if (newTheme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Disparar evento personalizado para sincronización entre componentes
    globalThis.window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme: newTheme } }));
  };

  /**
   * Toggle entre light y dark
   */
  const toggleTheme = () => {
    changeTheme(theme === 'dark' ? 'light' : 'dark');
  };

  // Aplicar tema inicial
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, []);

  // Escuchar cambios en preferencias del sistema
  useEffect(() => {
    const mediaQuery = globalThis.window?.matchMedia?.('(prefers-color-scheme: dark)');
    if (!mediaQuery) return;
    
    const handleChange = (e: MediaQueryListEvent) => {
      // Solo auto-cambiar si no hay preferencia guardada
      try {
        const stored = localStorage.getItem('theme');
        if (!stored) {
          changeTheme(e.matches ? 'dark' : 'light');
        }
      } catch (error) {
        console.warn('Error handling system theme change:', error);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  // Sincronizar tema entre pestañas
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'theme' && (e.newValue === 'dark' || e.newValue === 'light')) {
        setTheme(e.newValue);
        
        // Aplicar clase CSS
        const root = document.documentElement;
        if (e.newValue === 'dark') {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      }
    };

    globalThis.window.addEventListener('storage', handleStorageChange);
    
    return () => {
      globalThis.window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Memorizar el valor del contexto para evitar re-renders innecesarios
  const value: ThemeContextType = React.useMemo(() => ({
    theme,
    setTheme: changeTheme,
    toggleTheme,
    isDark,
  }), [theme, changeTheme, toggleTheme, isDark]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook para usar el contexto de tema
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
}

/**
 * HOC para componentes que necesitan acceso al tema
 */
export function withTheme<P extends object>(
  Component: React.ComponentType<P & { theme: Theme; isDark: boolean }>
) {
  return function ThemedComponent(props: P) {
    const { theme, isDark } = useTheme();
    return <Component {...props} theme={theme} isDark={isDark} />;
  };
}
