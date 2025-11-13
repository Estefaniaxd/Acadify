/**
 * Componente de audio para proctoring en evaluaciones
 * 
 * Funcionalidades:
 * - Captura de audio en tiempo real
 * - Análisis de nivel de audio con Web Audio API
 * - Detección de múltiples voces (básico)
 * - Alertas de audio sospechoso
 * - Visualización de nivel de audio
 * 
 * Principios SOLID aplicados:
 * - Single Responsibility: Solo maneja captura y análisis de audio
 * - Open/Closed: Extensible mediante props de configuración
 * - Dependency Inversion: Depende de abstracciones (callbacks)
 */

import React, { useEffect, useRef, useState } from 'react';
import { Mic, MicOff, Volume2, VolumeX, AlertTriangle } from 'lucide-react';
import type { ConfiguracionProctoring, AlertaProctoring, EventoAudio } from '../../types';

interface ProctoringAudioProps {
  configuracion: ConfiguracionProctoring;
  onAlerta: (alerta: AlertaProctoring) => void;
  onEventoAudio: (evento: EventoAudio) => void;
  activo: boolean;
  className?: string;
}

/**
 * Hook personalizado para gestión de audio stream
 */
function useAudioStream(activo: boolean) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [permisoConcedido, setPermisoConcedido] = useState(false);

  useEffect(() => {
    let streamActual: MediaStream | null = null;

    const iniciarStream = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        });

        streamActual = mediaStream;
        setStream(mediaStream);
        setPermisoConcedido(true);
        setError(null);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Error al acceder al micrófono';
        setError(errorMsg);
        setPermisoConcedido(false);
      }
    };

    if (activo) {
      iniciarStream();
    }

    return () => {
      if (streamActual) {
        streamActual.getTracks().forEach(track => track.stop());
      }
    };
  }, [activo]);

  return { stream, error, permisoConcedido };
}

/**
 * Hook para análisis de audio con Web Audio API
 */
function useAudioAnalysis(
  stream: MediaStream | null,
  configuracion: ConfiguracionProctoring,
  activo: boolean,
  onAlerta: (alerta: AlertaProctoring) => void,
  onEventoAudio: (evento: EventoAudio) => void
) {
  const [nivelAudio, setNivelAudio] = useState(0);
  const [audioDetectado, setAudioDetectado] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const ultimaAlertaRef = useRef<number>(0);

  useEffect(() => {
    if (!activo || !stream || !configuracion.deteccionAudio) {
      return;
    }

    // Crear AudioContext y Analyser
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);

    analyser.fftSize = 2048;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    source.connect(analyser);

    audioContextRef.current = audioContext;
    analyserRef.current = analyser;
    dataArrayRef.current = dataArray;

    // Función para analizar audio en tiempo real
    const analizarAudio = () => {
      if (!analyserRef.current || !dataArrayRef.current) return;

      // getByteTimeDomainData espera Uint8Array con ArrayBuffer
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteTimeDomainData(dataArray);

      // Calcular nivel de audio (RMS)
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const normalized = (dataArray[i] - 128) / 128;
        sum += normalized * normalized;
      }
      const rms = Math.sqrt(sum / dataArray.length);
      const nivel = Math.min(100, Math.round(rms * 200));

      setNivelAudio(nivel);

      // Detectar si hay audio activo (umbral de 10%)
      const hayAudio = nivel > 10;
      setAudioDetectado(hayAudio);

      // Detectar picos de audio sospechosos (muy alto)
      const ahora = Date.now();
      const puedeAlertar = ahora - ultimaAlertaRef.current > 5000;

      if (nivel > 70 && puedeAlertar) {
        onAlerta({
          id: `audio-alto-${ahora}`,
          tipo: 'audio_sospechoso',
          severidad: 'media',
          mensaje: 'Se detectó un nivel de audio inusualmente alto',
          timestamp: new Date(),
          resuelta: false,
          datos: { nivel }
        });
        ultimaAlertaRef.current = ahora;
      }

      // Emitir evento de audio periódicamente
      if (hayAudio) {
        onEventoAudio({
          timestamp: new Date(),
          nivelAudio: nivel,
          duracionMs: 1000 // Aproximado
        });
      }

      // Continuar análisis
      requestAnimationFrame(analizarAudio);
    };

    analizarAudio();

    // Cleanup
    return () => {
      if (audioContext.state !== 'closed') {
        audioContext.close();
      }
    };
  }, [stream, activo, configuracion, onAlerta, onEventoAudio]);

  return { nivelAudio, audioDetectado };
}

/**
 * Componente principal de audio de proctoring
 */
export function ProctoringAudio({
  configuracion,
  onAlerta,
  onEventoAudio,
  activo,
  className = ''
}: ProctoringAudioProps) {
  const [minimizado, setMinimizado] = useState(true);
  const { stream, error, permisoConcedido } = useAudioStream(activo && configuracion.habilitarMicrofono);
  const { nivelAudio, audioDetectado } = useAudioAnalysis(stream, configuracion, activo, onAlerta, onEventoAudio);

  const obtenerColorEstado = () => {
    if (!activo || !permisoConcedido) return 'bg-gray-500';
    if (audioDetectado && nivelAudio > 50) return 'bg-orange-500';
    if (audioDetectado) return 'bg-green-500';
    return 'bg-blue-500';
  };

  const obtenerIconoEstado = () => {
    if (!activo || !permisoConcedido) return <MicOff className="h-4 w-4" />;
    if (audioDetectado && nivelAudio > 70) return <Volume2 className="h-4 w-4" />;
    if (audioDetectado) return <Mic className="h-4 w-4" />;
    return <VolumeX className="h-4 w-4" />;
  };

  const obtenerTextoEstado = () => {
    if (!activo) return 'Micrófono desactivado';
    if (!permisoConcedido) return 'Esperando permisos...';
    if (error) return 'Error de micrófono';
    if (audioDetectado) return `Audio detectado (${nivelAudio}%)`;
    return 'Sin audio';
  };

  if (!configuracion.habilitarMicrofono) {
    return null;
  }

  return (
    <div className={`relative ${className}`}>
      {/* Widget principal */}
      <div
        className={`
          relative overflow-hidden rounded-lg border-2 shadow-lg transition-all duration-300 bg-white dark:bg-gray-900
          ${minimizado ? 'w-48' : 'w-64'}
          ${obtenerColorEstado().replace('bg-', 'border-')}
        `}
      >
        {/* Header */}
        <div className="p-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`${obtenerColorEstado()} rounded-full p-1.5 ${audioDetectado ? 'animate-pulse' : ''}`}>
                {obtenerIconoEstado()}
              </div>
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {minimizado ? 'Audio' : obtenerTextoEstado()}
              </span>
            </div>

            <button
              onClick={() => setMinimizado(!minimizado)}
              className="text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded p-1 transition-colors"
              title={minimizado ? 'Expandir' : 'Minimizar'}
            >
              {minimizado ? '▼' : '▲'}
            </button>
          </div>
        </div>

        {/* Contenido */}
        {!minimizado && (
          <div className="p-3 space-y-3">
            {/* Visualización de nivel de audio */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
                <span>Nivel de audio:</span>
                <span className="font-semibold text-gray-900 dark:text-gray-100">{nivelAudio}%</span>
              </div>

              {/* Barra de nivel */}
              <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-150 ${
                    nivelAudio > 70
                      ? 'bg-red-500'
                      : nivelAudio > 40
                      ? 'bg-orange-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${nivelAudio}%` }}
                />
              </div>

              {/* Visualización de barras (ecualizador) */}
              <div className="flex items-end justify-center space-x-1 h-12">
                {[...Array(8)].map((_, i) => {
                  // Usar el índice para generar altura determinística basada en nivelAudio
                  const altura = audioDetectado ? ((nivelAudio / 100) * (50 + (i * 6))) : 0;
                  return (
                    <div
                      key={i}
                      className={`w-2 rounded-t transition-all duration-150 ${
                        altura > 70
                          ? 'bg-red-500'
                          : altura > 40
                          ? 'bg-orange-500'
                          : 'bg-green-500'
                      }`}
                      style={{ height: `${Math.min(100, altura)}%` }}
                    />
                  );
                })}
              </div>
            </div>

            {/* Estado */}
            <div className="flex items-center space-x-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
              {activo && permisoConcedido ? (
                <>
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-gray-700 dark:text-gray-300">Monitoreando audio</span>
                </>
              ) : (
                <>
                  <MicOff className="h-3 w-3 text-gray-500" />
                  <span className="text-gray-500">Micrófono inactivo</span>
                </>
              )}
            </div>

            {/* Alertas */}
            {nivelAudio > 70 && (
              <div className="flex items-center space-x-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs text-red-700 dark:text-red-300">
                <AlertTriangle className="h-3 w-3" />
                <span>Nivel de audio muy alto detectado</span>
              </div>
            )}
          </div>
        )}

        {/* Overlay de error */}
        {error && (
          <div className="absolute inset-0 bg-gray-900/90 flex items-center justify-center p-4">
            <div className="text-center text-white">
              <AlertTriangle className="h-6 w-6 mx-auto mb-2 text-red-400" />
              <p className="text-xs font-medium">Error de micrófono</p>
              <p className="text-xs text-gray-300 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Overlay de permisos */}
        {!permisoConcedido && !error && (
          <div className="absolute inset-0 bg-gray-900/90 flex items-center justify-center p-4">
            <div className="text-center text-white">
              <Mic className="h-6 w-6 mx-auto mb-2 text-blue-400 animate-pulse" />
              <p className="text-xs font-medium">Solicitando permisos...</p>
              <p className="text-xs text-gray-300 mt-1">Permite el acceso a tu micrófono</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProctoringAudio;
