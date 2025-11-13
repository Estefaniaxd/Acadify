import { useEffect, useState, useCallback } from 'react';

type KeyFilter = string | string[] | ((event: KeyboardEvent) => boolean);

/**
 * Hook para detectar cuando se presiona una tecla específica
 * 
 * @param targetKey - Tecla(s) a detectar o función de filtro
 * @param handler - Función a ejecutar cuando se presiona la tecla
 * @param options - Opciones adicionales
 * 
 * @example
 * ```tsx
 * // Detectar tecla Escape
 * useKeyPress('Escape', () => setIsOpen(false));
 * 
 * // Detectar múltiples teclas
 * useKeyPress(['Enter', 'Space'], handleSubmit);
 * 
 * // Con modificadores
 * useKeyPress('s', handleSave, { ctrlKey: true });
 * ```
 */
export function useKeyPress(
  targetKey: KeyFilter,
  handler?: (event: KeyboardEvent) => void,
  options: {
    ctrlKey?: boolean;
    shiftKey?: boolean;
    altKey?: boolean;
    metaKey?: boolean;
    enabled?: boolean;
  } = {}
): boolean {
  const [keyPressed, setKeyPressed] = useState(false);
  const { ctrlKey, shiftKey, altKey, metaKey, enabled = true } = options;

  const matchesKey = useCallback((event: KeyboardEvent): boolean => {
    if (typeof targetKey === 'function') {
      return targetKey(event);
    }

    const keys = Array.isArray(targetKey) ? targetKey : [targetKey];
    const keyMatch = keys.includes(event.key);

    const modifiersMatch = 
      (ctrlKey === undefined || event.ctrlKey === ctrlKey) &&
      (shiftKey === undefined || event.shiftKey === shiftKey) &&
      (altKey === undefined || event.altKey === altKey) &&
      (metaKey === undefined || event.metaKey === metaKey);

    return keyMatch && modifiersMatch;
  }, [targetKey, ctrlKey, shiftKey, altKey, metaKey]);

  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (matchesKey(event)) {
        setKeyPressed(true);
        handler?.(event);
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      if (matchesKey(event)) {
        setKeyPressed(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [matchesKey, handler, enabled]);

  return keyPressed;
}
