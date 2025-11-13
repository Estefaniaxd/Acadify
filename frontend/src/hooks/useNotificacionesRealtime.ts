/**
 * Hook para detección de nuevas notificaciones en tiempo real
 * 
 * @module hooks/useNotificacionesRealtime
 * @description Detecta nuevas notificaciones y dispara efectos (sonido, browser notification)
 */

import { useEffect, useRef } from 'react';
import { useContadorNoLeidas, useNotificacionesPush, useSonidoNotificacion } from './useNotificaciones';

/**
 * Hook para manejar notificaciones en tiempo real
 * 
 * Características:
 * - Detecta incremento en contador de notificaciones no leídas
 * - Reproduce sonido cuando hay nuevas notificaciones
 * - Muestra notificación del navegador (si está habilitado)
 * - Auto-refetch cada 10 segundos
 */
export function useNotificacionesRealtime() {
  const { data: contador = 0 } = useContadorNoLeidas();
  const { reproducir } = useSonidoNotificacion();
  const { mostrarNotificacion, permiso } = useNotificacionesPush();
  
  // Ref para almacenar el contador anterior
  const contadorAnteriorRef = useRef<number | null>(null);

  useEffect(() => {
    // Si es la primera vez, solo guardamos el contador
    if (contadorAnteriorRef.current === null) {
      contadorAnteriorRef.current = contador;
      return;
    }

    // Si hay un incremento en el contador, hay nuevas notificaciones
    if (contador > contadorAnteriorRef.current) {
      const nuevasNotificaciones = contador - contadorAnteriorRef.current;
      
      // Reproducir sonido
      reproducir('mensaje');
      
      // Mostrar notificación del navegador (si está permitido)
      if (permiso === 'granted') {
        mostrarNotificacion({
          titulo: 'Nueva notificación',
          mensaje: nuevasNotificaciones === 1 
            ? 'Tienes 1 nueva notificación' 
            : `Tienes ${nuevasNotificaciones} nuevas notificaciones`,
          icono: '🔔',
          url: '/notificaciones'
        });
      }
    }

    // Actualizar el contador anterior
    contadorAnteriorRef.current = contador;
  }, [contador, reproducir, mostrarNotificacion, permiso]);

  return {
    contador,
    tieneNotificaciones: contador > 0,
  };
}
