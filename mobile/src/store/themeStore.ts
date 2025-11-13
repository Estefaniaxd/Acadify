/**
 * Theme Store
 * Global theme management with Zustand
 * 
 * @module store/themeStore
 * @follows Single Responsibility Principle
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Appearance } from 'react-native';

// ==================== TYPES ====================

export type ThemeMode = 'light' | 'dark' | 'auto';

export interface ThemeState {
  // State
  mode: ThemeMode;
  isDark: boolean;
  
  // Actions
  setTheme: (mode: ThemeMode) => void;
  toggleTheme: () => void;
  initializeTheme: () => void;
}

// ==================== STORE ====================

/**
 * Theme Store
 * Manages app theme (light/dark mode) with persistence
 * 
 * @example
 * ```typescript
 * const { mode, isDark, setTheme } = useThemeStore();
 * 
 * // Change theme
 * setTheme('dark');
 * 
 * // Toggle between light/dark
 * toggleTheme();
 * ```
 */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      // Initial state
      mode: 'auto',
      isDark: Appearance.getColorScheme() === 'dark',

      /**
       * Set theme mode
       * @param {ThemeMode} mode - Theme mode (light, dark, auto)
       */
      setTheme: (mode: ThemeMode) => {
        set({ mode });

        if (mode === 'auto') {
          const systemTheme = Appearance.getColorScheme();
          set({ isDark: systemTheme === 'dark' });
        } else {
          set({ isDark: mode === 'dark' });
        }
      },

      /**
       * Toggle between light and dark themes
       */
      toggleTheme: () => {
        const { mode } = get();
        const newMode: ThemeMode = mode === 'dark' ? 'light' : 'dark';
        get().setTheme(newMode);
      },

      /**
       * Initialize theme based on stored preference or system
       */
      initializeTheme: () => {
        const { mode } = get();

        if (mode === 'auto') {
          // Listen to system theme changes
          const listener = Appearance.addChangeListener((preferences) => {
            set({ isDark: preferences.colorScheme === 'dark' });
          });

          return () => listener.remove();
        }
      },
    }),
    {
      name: 'acadify-theme-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
