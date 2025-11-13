import { RefObject, useEffect } from 'react';

/**
 * Hook para detectar clicks fuera de un elemento
 * 
 * @param ref - Referencia al elemento
 * @param handler - Función a ejecutar cuando se hace click fuera
 * @param enabled - Si el hook está habilitado (default: true)
 * 
 * @example
 * ```tsx
 * const ref = useRef<HTMLDivElement>(null);
 * useClickOutside(ref, () => setIsOpen(false));
 * 
 * return <div ref={ref}>Contenido</div>
 * ```
 */
export function useClickOutside<T extends HTMLElement = HTMLElement>(
  ref: RefObject<T>,
  handler: (event: MouseEvent | TouchEvent) => void,
  enabled: boolean = true
): void {
  useEffect(() => {
    if (!enabled) return;

    const listener = (event: MouseEvent | TouchEvent) => {
      const element = ref.current;
      
      // No hacer nada si el elemento no existe o si se hizo click dentro
      if (!element || element.contains(event.target as Node)) {
        return;
      }

      handler(event);
    };

    // Usar capture phase para detectar antes que otros handlers
    document.addEventListener('mousedown', listener, true);
    document.addEventListener('touchstart', listener, true);

    return () => {
      document.removeEventListener('mousedown', listener, true);
      document.removeEventListener('touchstart', listener, true);
    };
  }, [ref, handler, enabled]);
}
