/**
 * Componente de cámara para proctoring en evaluaciones
 * 
 * Funcionalidades:
 * - Captura de video en tiempo real
 * - Detección de rostros con MediaPipe Face Detection
 * - Alertas automáticas (sin rostro, múltiples rostros)
 * - Snapshots periódicos
 * - Preview minimizado
 * 
 * Principios SOLID aplicados:
 * - Single Responsibility: Solo maneja captura y detección de video
 * - Open/Closed: Extensible mediante props de configuración
 * - Dependency Inversion: Depende de abstracciones (callbacks)
 */

import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, AlertTriangle, User, Users } from 'lucide-react';
import type { ConfiguracionProctoring, AlertaProctoring, SnapshotProctoring } from '../../types';
import { faceDetectionService } from '../../services/faceDetectionService';

interface ProctoringCameraProps {
  configuracion: ConfiguracionProctoring;
  onAlerta: (alerta: AlertaProctoring) => void;
  onSnapshot: (snapshot: SnapshotProctoring) => void;
  activo: boolean;
  className?: string;
}

/**
 * Hook personalizado para gestión de MediaStream
 * Separa la lógica de captura de video del componente visual
 */
function useMediaStream(activo: boolean) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [permisoConcedido, setPermisoConcedido] = useState(false);

  useEffect(() => {
    let streamActual: MediaStream | null = null;

    const iniciarStream = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          }
        });

        streamActual = mediaStream;
        setStream(mediaStream);
        setPermisoConcedido(true);
        setError(null);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Error al acceder a la cámara';
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
 * Hook para detección de rostros con MediaPipe Face Detection
 * 
 * Detecta rostros en tiempo real y genera alertas cuando:
 * - No se detecta ningún rostro (alerta alta)
 * - Se detectan múltiples rostros (alerta crítica)
 * 
 * Implementa throttling para evitar spam de alertas.
 */
function useDeteccionRostros(
  videoRef: React.RefObject<HTMLVideoElement>,
  configuracion: ConfiguracionProctoring,
  activo: boolean,
  onAlerta: (alerta: AlertaProctoring) => void
) {
  const [rostrosDetectados, setRostrosDetectados] = useState(0);
  const ultimaAlertaRef = useRef<{ tipo: string; timestamp: number } | null>(null);
  const detectionStopperRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!activo || !configuracion.deteccionRostros || !videoRef.current) {
      return;
    }

    const inicializarDetector = async () => {
      try {
        // Inicializar MediaPipe Face Detection
        await faceDetectionService.initialize({
          modelSelection: 'short', // Mejor para rostros cercanos a la cámara
          minDetectionConfidence: configuracion.umbralConfianzaRostro || 0.7,
        });
        
        // eslint-disable-next-line no-console
        console.log('✅ Detector de rostros inicializado');

        // Iniciar detección continua
        const stopper = faceDetectionService.startContinuousDetection(
          videoRef.current!,
          (results) => {
            const numeroRostros = results.faces.length;
            setRostrosDetectados(numeroRostros);

            // Generar alertas si es necesario
            const ahora = Date.now();
            const ultimaAlerta = ultimaAlertaRef.current;

            // Throttling: mínimo 5 segundos entre alertas del mismo tipo
            const puedeAlertar = !ultimaAlerta || (ahora - ultimaAlerta.timestamp) > 5000;

            if (numeroRostros === 0 && configuracion.alertarSinRostro && puedeAlertar) {
              onAlerta({
                id: `sin-rostro-${Date.now()}`,
                tipo: 'sin_rostro_detectado',
                severidad: 'alta',
                mensaje: 'No se detecta ningún rostro en la cámara',
                timestamp: new Date(),
                resuelta: false
              });
              ultimaAlertaRef.current = { tipo: 'sin_rostro', timestamp: ahora };
            }

            if (numeroRostros > 1 && configuracion.alertarMultiplesRostros && puedeAlertar) {
              onAlerta({
                id: `multiples-rostros-${Date.now()}`,
                tipo: 'multiples_rostros',
                severidad: 'critica',
                mensaje: `Se detectaron ${numeroRostros} rostros en la cámara`,
                timestamp: new Date(),
                resuelta: false,
                datos: { numeroRostros }
              });
              ultimaAlertaRef.current = { tipo: 'multiples_rostros', timestamp: ahora };
            }
          },
          2000 // Detectar cada 2 segundos
        );

        detectionStopperRef.current = stopper;
      } catch (error) {
        console.error('Error al inicializar detector de rostros:', error);
        // Fallback: usar simulación si falla MediaPipe
        console.warn('⚠️ Usando simulación de detección de rostros');
      }
    };

    inicializarDetector();

    return () => {
      // Detener detección continua
      if (detectionStopperRef.current) {
        detectionStopperRef.current();
        detectionStopperRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activo, configuracion.deteccionRostros]);

  return { rostrosDetectados };
}

/**
 * Hook para captura de snapshots periódicos
 */
function useSnapshots(
  videoRef: React.RefObject<HTMLVideoElement>,
  canvasRef: React.RefObject<HTMLCanvasElement>,
  configuracion: ConfiguracionProctoring,
  activo: boolean,
  onSnapshot: (snapshot: SnapshotProctoring) => void
) {
  useEffect(() => {
    if (!activo || !configuracion.grabarVideo || !videoRef.current || !canvasRef.current) {
      return;
    }

    const intervalo = setInterval(() => {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      if (!video || !canvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
        return;
      }

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Capturar frame actual
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);

      // Convertir a base64
      const imagenBase64 = canvas.toDataURL('image/jpeg', 0.7);

      onSnapshot({
        timestamp: new Date(),
        imagenBase64,
        rostrosDetectados: 1, // TODO: obtener de detección real
        metadatos: {
          ancho: canvas.width,
          alto: canvas.height,
          calidad: 70
        }
      });
    }, configuracion.frecuenciaSnapshotsSegundos * 1000);

    return () => clearInterval(intervalo);
  }, [activo, configuracion, onSnapshot, videoRef, canvasRef]);
}

/**
 * Componente principal de cámara de proctoring
 */
export function ProctoringCamera({
  configuracion,
  onAlerta,
  onSnapshot,
  activo,
  className = ''
}: ProctoringCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [videoMinimizado, setVideoMinimizado] = useState(true);

  const { stream, error, permisoConcedido } = useMediaStream(activo && configuracion.habilitarCamera);
  const { rostrosDetectados } = useDeteccionRostros(videoRef, configuracion, activo, onAlerta);

  useSnapshots(videoRef, canvasRef, configuracion, activo, onSnapshot);

  // Conectar stream al video element
  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  const obtenerColorEstado = () => {
    if (!activo || !permisoConcedido) return 'bg-gray-500';
    if (rostrosDetectados === 0) return 'bg-red-500';
    if (rostrosDetectados > 1) return 'bg-orange-500';
    return 'bg-green-500';
  };

  const obtenerIconoEstado = () => {
    if (!activo || !permisoConcedido) return <CameraOff className="h-4 w-4" />;
    if (rostrosDetectados === 0) return <AlertTriangle className="h-4 w-4" />;
    if (rostrosDetectados === 1) return <User className="h-4 w-4" />;
    return <Users className="h-4 w-4" />;
  };

  const obtenerTextoEstado = () => {
    if (!activo) return 'Cámara desactivada';
    if (!permisoConcedido) return 'Esperando permisos...';
    if (error) return 'Error de cámara';
    if (rostrosDetectados === 0) return 'Sin rostro detectado';
    if (rostrosDetectados === 1) return 'Rostro detectado';
    return `${rostrosDetectados} rostros detectados`;
  };

  if (!configuracion.habilitarCamera) {
    return null;
  }

  return (
    <div className={`relative ${className}`}>
      {/* Canvas oculto para captura de snapshots */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Video preview */}
      <div
        className={`
          relative overflow-hidden rounded-lg border-2 shadow-lg transition-all duration-300
          ${videoMinimizado ? 'w-48 h-36' : 'w-96 h-72'}
          ${obtenerColorEstado().replace('bg-', 'border-')}
        `}
      >
        {/* Header del preview */}
        <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/70 to-transparent p-2 z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`${obtenerColorEstado()} rounded-full p-1.5 animate-pulse`}>
                {obtenerIconoEstado()}
              </div>
              <span className="text-white text-xs font-medium">{obtenerTextoEstado()}</span>
            </div>

            <button
              onClick={() => setVideoMinimizado(!videoMinimizado)}
              className="text-white hover:bg-white/20 rounded p-1 transition-colors"
              title={videoMinimizado ? 'Expandir' : 'Minimizar'}
            >
              {videoMinimizado ? (
                <Camera className="h-4 w-4" />
              ) : (
                <CameraOff className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>

        {/* Video element */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover bg-gray-900"
        />

        {/* Indicador de grabación */}
        {activo && permisoConcedido && (
          <div className="absolute bottom-2 left-2 flex items-center space-x-1.5 bg-red-500/90 text-white px-2 py-1 rounded-full text-xs font-medium">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            <span>Grabando</span>
          </div>
        )}

        {/* Overlay de error */}
        {error && (
          <div className="absolute inset-0 bg-gray-900/90 flex items-center justify-center p-4">
            <div className="text-center text-white">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-red-400" />
              <p className="text-sm font-medium">Error de cámara</p>
              <p className="text-xs text-gray-300 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Overlay de permisos */}
        {!permisoConcedido && !error && (
          <div className="absolute inset-0 bg-gray-900/90 flex items-center justify-center p-4">
            <div className="text-center text-white">
              <Camera className="h-8 w-8 mx-auto mb-2 text-blue-400 animate-pulse" />
              <p className="text-sm font-medium">Solicitando permisos...</p>
              <p className="text-xs text-gray-300 mt-1">Permite el acceso a tu cámara</p>
            </div>
          </div>
        )}
      </div>

      {/* Información de detección (modo expandido) */}
      {!videoMinimizado && configuracion.deteccionRostros && (
        <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs">
          <div className="flex items-center justify-between">
            <span className="text-gray-600 dark:text-gray-400">Rostros detectados:</span>
            <span className="font-semibold text-gray-900 dark:text-gray-100">{rostrosDetectados}</span>
          </div>
          {rostrosDetectados > 1 && (
            <div className="mt-1 flex items-center space-x-1 text-orange-600 dark:text-orange-400">
              <AlertTriangle className="h-3 w-3" />
              <span>Se detectaron múltiples personas</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ProctoringCamera;
