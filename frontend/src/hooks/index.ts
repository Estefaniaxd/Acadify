/**
 * Custom Hooks Library
 * 
 * Hooks reutilizables siguiendo principios SOLID:
 * - Single Responsibility: Cada hook hace una cosa
 * - Open/Closed: Extensibles vía options
 * - Liskov Substitution: API consistente
 * - Interface Segregation: Hooks específicos
 * - Dependency Inversion: No dependen de componentes específicos
 */

export { useClickOutside } from './useClickOutside';
export { useKeyPress } from './useKeyPress';
export { 
  useMediaQuery, 
  useBreakpoint, 
  useIsMobile, 
  useIsTablet, 
  useIsDesktop,
  breakpoints 
} from './useMediaQuery';
export { useDebounce, useDebouncedCallback } from './useDebounce';
export { useLocalStorage, useLocalStorageBoolean } from './useLocalStorage';
export { useWebSocket } from './useWebSocket';
