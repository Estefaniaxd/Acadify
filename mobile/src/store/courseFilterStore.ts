/**
 * Course Filter Store
 * Manages course filtering and search state
 * 
 * @module store/courseFilterStore
 * @follows Single Responsibility Principle
 */

import { create } from 'zustand';
import type { CourseFilters } from '@/services';

// ==================== TYPES ====================

export interface CourseFilterState {
  // State
  filters: CourseFilters;
  searchQuery: string;
  
  // Actions
  setFilters: (filters: Partial<CourseFilters>) => void;
  setSearchQuery: (query: string) => void;
  setCategory: (categoria?: string) => void;
  setLevel: (nivel?: 'principiante' | 'intermedio' | 'avanzado') => void;
  resetFilters: () => void;
  
  // Computed
  hasActiveFilters: () => boolean;
}

// ==================== INITIAL STATE ====================

const initialFilters: CourseFilters = {
  categoria: undefined,
  nivel: undefined,
  search: undefined,
  limit: 10,
  offset: 0,
};

// ==================== STORE ====================

/**
 * Course Filter Store
 * Manages filtering state for courses list
 * 
 * @example
 * ```typescript
 * const { filters, setCategory, setSearchQuery, resetFilters } = useCourseFilterStore();
 * 
 * // Set category
 * setCategory('Programación');
 * 
 * // Set search
 * setSearchQuery('React Native');
 * 
 * // Reset all
 * resetFilters();
 * ```
 */
export const useCourseFilterStore = create<CourseFilterState>((set, get) => ({
  // Initial state
  filters: initialFilters,
  searchQuery: '',

  /**
   * Set multiple filters at once
   * @param {Partial<CourseFilters>} filters - Filters to set
   */
  setFilters: (filters) => {
    set((state) => ({
      filters: { ...state.filters, ...filters },
    }));
  },

  /**
   * Set search query
   * @param {string} query - Search query
   */
  setSearchQuery: (query) => {
    set((state) => ({
      searchQuery: query,
      filters: { ...state.filters, search: query || undefined },
    }));
  },

  /**
   * Set category filter
   * @param {string} categoria - Category name
   */
  setCategory: (categoria) => {
    set((state) => ({
      filters: { ...state.filters, categoria, offset: 0 },
    }));
  },

  /**
   * Set level filter
   * @param {string} nivel - Level (principiante, intermedio, avanzado)
   */
  setLevel: (nivel) => {
    set((state) => ({
      filters: { ...state.filters, nivel, offset: 0 },
    }));
  },

  /**
   * Reset all filters to initial state
   */
  resetFilters: () => {
    set({
      filters: initialFilters,
      searchQuery: '',
    });
  },

  /**
   * Check if any filter is active
   * @returns {boolean} True if any filter is active
   */
  hasActiveFilters: () => {
    const { filters, searchQuery } = get();
    return !!(
      filters.categoria ||
      filters.nivel ||
      searchQuery
    );
  },
}));
