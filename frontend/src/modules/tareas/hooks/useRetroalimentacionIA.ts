import { useState, useCallback } from 'react';
import { iaService, RetroalimentacionResponse } from '@/services/iaService';

/**
 * Hook para gestionar retroalimentación IA
 * Proporciona métodos para generar y obtener retroalimentación
 */
export function useRetroalimentacionIA() {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retroalimentacion, setRetroalimentacion] = useState<RetroalimentacionResponse | null>(null);

  const generarRetroalimentacion = useCallback(
    async (
      entregaId: string,
      modelo: string = 'gemini-2.5-flash',
      nivelDetalle: 'basico' | 'medio' | 'completo' = 'completo'
    ) => {
      setCargando(true);
      setError(null);

      try {
        const resultado = await iaService.generarRetroalimentacionIndividual(
          entregaId,
          modelo,
          nivelDetalle,
          true
        );
        setRetroalimentacion(resultado);
        return resultado;
      } catch (err: any) {
        const mensaje = err.response?.data?.detail || err.message || 'Error desconocido';
        setError(mensaje);
        throw err;
      } finally {
        setCargando(false);
      }
    },
    []
  );

  const obtenerRetroalimentacion = useCallback(async (entregaId: string) => {
    setCargando(true);
    setError(null);

    try {
      const resultado = await iaService.obtenerRetroalimentacion(entregaId);
      if (resultado) {
        setRetroalimentacion(resultado);
      }
      return resultado;
    } catch (err: any) {
      const mensaje = err.response?.data?.detail || err.message || 'Error desconocido';
      setError(mensaje);
      throw err;
    } finally {
      setCargando(false);
    }
  }, []);

  const limpiar = useCallback(() => {
    setRetroalimentacion(null);
    setError(null);
  }, []);

  return {
    cargando,
    error,
    retroalimentacion,
    generarRetroalimentacion,
    obtenerRetroalimentacion,
    limpiar,
  };
}
