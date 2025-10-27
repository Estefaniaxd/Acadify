import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ClockIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FlagIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { Card, CardHeader, CardContent } from '../common/LayoutComponents';
import { LoadingSpinner, ProgressBar } from '../common/LoadingComponents';
import { ConfirmDialog, useToast } from '../common/AlertComponents';
import { useTomarExamen, useAntiTrampa } from '../../hooks';
import { 
  Examen, 
  PreguntaExamen, 
  IntentoExamen,
  RespuestaEstudiante 
} from '../../types';
import { formatearTiempo, obtenerColorEstado } from '../../utils';
import { PantallaPregunta } from './PantallaPregunta';
import { NavegadorPreguntas } from './NavegadorPreguntas';
import { TimerExamen } from './TimerExamen';
import { ResumenFinal } from './ResumenFinal';

interface TomadorExamenProps {
  examen: Examen;
  onFinalizarExamen: (intento: IntentoExamen) => void;
  onSalir: () => void;
  className?: string;
}

type EstadoTomador = 'cargando' | 'iniciando' | 'en_progreso' | 'pausado' | 'finalizando' | 'finalizado' | 'error';

export function TomadorExamen({ 
  examen, 
  onFinalizarExamen, 
  onSalir, 
  className = '' 
}: TomadorExamenProps) {
  const [estado, setEstado] = useState<EstadoTomador>('cargando');
  const [preguntaActual, setPreguntaActual] = useState(0);
  const [mostrarNavegador, setMostrarNavegador] = useState(false);
  const [mostrarResumen, setMostrarResumen] = useState(false);
  const [modoFullscreen, setModoFullscreen] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
  }>({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {}
  });

  const { showToast } = useToast();

  const {
    intento,
    preguntas,
    respuestas,
    tiempoRestante,
    loading,
    error,
    iniciarIntento,
    guardarRespuesta,
    finalizarIntento,
    pausarIntento,
    reanudarIntento,
    obtenerProgreso
  } = useTomarExamen(examen.examen_id);

  const {
    eventosAntiTrampa,
    alertasActivas,
    iniciarMonitoreo,
    detenerMonitoreo,
    reportarEvento,
    verificarIntegridad
  } = useAntiTrampa(intento?.intento_id);

  // Inicializar el examen
  useEffect(() => {
    const inicializar = async () => {
      try {
        setEstado('iniciando');
        await iniciarIntento();
        
        if (examen.modo_pantalla_completa) {
          await entrarFullscreen();
        }
        
        await iniciarMonitoreo();
        setEstado('en_progreso');
      } catch (error) {
        console.error('Error al inicializar examen:', error);
        setEstado('error');
        showToast({
          type: 'error',
          title: 'Error',
          message: 'No se pudo inicializar el examen'
        });
      }
    };

    inicializar();

    // Cleanup al desmontar
    return () => {
      detenerMonitoreo();
      if (modoFullscreen) {
        salirFullscreen();
      }
    };
  }, [examen.examen_id]);

  // Monitorear tiempo
  useEffect(() => {
    if (tiempoRestante === 0 && estado === 'en_progreso') {
      manejarTiempoAgotado();
    }
  }, [tiempoRestante, estado]);

  // Monitorear eventos anti-trampa
  useEffect(() => {
    if (alertasActivas.length > 0) {
      const ultimaAlerta = alertasActivas[alertasActivas.length - 1];
      
      showToast({
        type: 'warning',
        title: 'Advertencia de Seguridad',
        message: ultimaAlerta.mensaje,
        duration: 5000
      });

      // Si hay demasiadas infracciones, finalizar automáticamente
      if (alertasActivas.filter(a => a.severidad === 'CRITICA').length >= 3) {
        manejarFinalizacionForzada('Múltiples infracciones de seguridad detectadas');
      }
    }
  }, [alertasActivas]);

  const entrarFullscreen = useCallback(async () => {
    try {
      await document.documentElement.requestFullscreen();
      setModoFullscreen(true);
      
      // Listener para detectar salida de pantalla completa
      const handleFullscreenChange = () => {
        if (!document.fullscreenElement) {
          setModoFullscreen(false);
          if (examen.detectar_cambio_pestana) {
            reportarEvento({
              tipo: 'SALIDA_PANTALLA_COMPLETA',
              detalle: 'Usuario salió de pantalla completa'
            });
          }
        }
      };
      
      document.addEventListener('fullscreenchange', handleFullscreenChange);
      
      return () => {
        document.removeEventListener('fullscreenchange', handleFullscreenChange);
      };
    } catch (error) {
      console.error('Error al entrar en pantalla completa:', error);
    }
  }, [examen.detectar_cambio_pestana, reportarEvento]);

  const salirFullscreen = useCallback(async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      }
      setModoFullscreen(false);
    } catch (error) {
      console.error('Error al salir de pantalla completa:', error);
    }
  }, []);

  const manejarRespuesta = useCallback(async (respuesta: any) => {
    try {
      await guardarRespuesta(preguntas[preguntaActual].pregunta_id, respuesta);
      
      showToast({
        type: 'success',
        title: 'Respuesta guardada',
        message: 'Tu respuesta se ha guardado automáticamente',
        duration: 2000
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo guardar la respuesta. Inténtalo de nuevo.'
      });
    }
  }, [preguntaActual, preguntas, guardarRespuesta, showToast]);

  const manejarSiguientePregunta = useCallback(() => {
    if (preguntaActual < preguntas.length - 1) {
      setPreguntaActual(prev => prev + 1);
    }
  }, [preguntaActual, preguntas.length]);

  const manejarAnteriorPregunta = useCallback(() => {
    if (preguntaActual > 0) {
      setPreguntaActual(prev => prev - 1);
    }
  }, [preguntaActual]);

  const manejarIrAPregunta = useCallback((indicePregunta: number) => {
    if (indicePregunta >= 0 && indicePregunta < preguntas.length) {
      setPreguntaActual(indicePregunta);
      setMostrarNavegador(false);
    }
  }, [preguntas.length]);

  const manejarTiempoAgotado = useCallback(async () => {
    setConfirmDialog({
      isOpen: true,
      title: 'Tiempo Agotado',
      message: 'El tiempo del examen ha terminado. El examen se enviará automáticamente.',
      onConfirm: async () => {
        await manejarFinalizarExamen();
        setConfirmDialog(prev => ({ ...prev, isOpen: false }));
      }
    });
  }, []);

  const manejarFinalizacionForzada = useCallback(async (razon: string) => {
    try {
      setEstado('finalizando');
      const intentoFinalizado = await finalizarIntento(true, razon);
      onFinalizarExamen(intentoFinalizado);
      setEstado('finalizado');
    } catch (error) {
      console.error('Error en finalización forzada:', error);
      setEstado('error');
    }
  }, [finalizarIntento, onFinalizarExamen]);

  const manejarFinalizarExamen = useCallback(async () => {
    setConfirmDialog({
      isOpen: true,
      title: 'Confirmar Envío',
      message: '¿Estás seguro de que quieres enviar el examen? Esta acción no se puede deshacer.',
      onConfirm: async () => {
        try {
          setEstado('finalizando');
          detenerMonitoreo();
          
          const intentoFinalizado = await finalizarIntento();
          
          if (modoFullscreen) {
            await salirFullscreen();
          }
          
          onFinalizarExamen(intentoFinalizado);
          setEstado('finalizado');
        } catch (error) {
          console.error('Error al finalizar examen:', error);
          showToast({
            type: 'error',
            title: 'Error',
            message: 'Hubo un problema al enviar el examen'
          });
          setEstado('en_progreso');
        }
        setConfirmDialog(prev => ({ ...prev, isOpen: false }));
      }
    });
  }, [finalizarIntento, onFinalizarExamen, detenerMonitoreo, modoFullscreen, salirFullscreen, showToast]);

  const manejarPausar = useCallback(async () => {
    try {
      setEstado('pausado');
      await pausarIntento();
      showToast({
        type: 'info',
        title: 'Examen pausado',
        message: 'El cronómetro se ha detenido'
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo pausar el examen'
      });
      setEstado('en_progreso');
    }
  }, [pausarIntento, showToast]);

  const manejarReanudar = useCallback(async () => {
    try {
      await reanudarIntento();
      setEstado('en_progreso');
      showToast({
        type: 'success',
        title: 'Examen reanudado',
        message: 'El cronómetro ha continuado'
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo reanudar el examen'
      });
    }
  }, [reanudarIntento, showToast]);

  const manejarSalir = useCallback(() => {
    setConfirmDialog({
      isOpen: true,
      title: 'Confirmar Salida',
      message: '¿Estás seguro de que quieres salir? Se perderá todo el progreso no guardado.',
      onConfirm: () => {
        detenerMonitoreo();
        if (modoFullscreen) {
          salirFullscreen();
        }
        onSalir();
        setConfirmDialog(prev => ({ ...prev, isOpen: false }));
      }
    });
  }, [onSalir, detenerMonitoreo, modoFullscreen, salirFullscreen]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent>
            <div className="text-center">
              <ExclamationTriangleIcon className="w-16 h-16 mx-auto text-red-500 mb-4" />
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Error al cargar el examen
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {error}
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => window.location.reload()}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                >
                  <ArrowPathIcon className="h-4 w-4" />
                  <span>Reintentar</span>
                </button>
                <button
                  onClick={onSalir}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
                >
                  Salir
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (estado === 'cargando' || estado === 'iniciando' || loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            {estado === 'cargando' ? 'Cargando examen...' : 'Iniciando examen...'}
          </p>
        </div>
      </div>
    );
  }

  if (estado === 'finalizado') {
    return (
      <ResumenFinal
        intento={intento!}
        examen={examen}
        onSalir={onSalir}
      />
    );
  }

  const progreso = obtenerProgreso();
  const preguntaActualObj = preguntas[preguntaActual];
  const respuestaActual = respuestas.find(r => r.pregunta_id === preguntaActualObj?.pregunta_id);

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Header fijo */}
      <div className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Info del examen */}
            <div className="flex items-center space-x-4">
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                {examen.titulo}
              </h1>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorEstado(examen.estado_examen)}`}>
                {examen.estado_examen}
              </span>
            </div>

            {/* Controles centrales */}
            <div className="flex items-center space-x-6">
              {/* Timer */}
              <TimerExamen
                tiempoRestante={tiempoRestante}
                tiempoTotal={examen.tiempo_limite * 60}
                onTiempoAgotado={manejarTiempoAgotado}
                pausado={estado === 'pausado'}
              />

              {/* Progreso */}
              <div className="hidden sm:flex items-center space-x-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Pregunta {preguntaActual + 1} de {preguntas.length}
                </span>
                <div className="w-24">
                  <ProgressBar
                    value={(preguntaActual + 1) / preguntas.length * 100}
                    className="h-2"
                  />
                </div>
              </div>

              {/* Navegador de preguntas */}
              <button
                onClick={() => setMostrarNavegador(!mostrarNavegador)}
                className="flex items-center space-x-2 px-3 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <EyeIcon className="h-4 w-4" />
                <span className="hidden sm:inline">Vista general</span>
              </button>
            </div>

            {/* Controles de acción */}
            <div className="flex items-center space-x-3">
              {estado === 'pausado' ? (
                <button
                  onClick={manejarReanudar}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                >
                  <CheckCircleIcon className="h-4 w-4" />
                  <span>Reanudar</span>
                </button>
              ) : (
                <>
                  <button
                    onClick={manejarPausar}
                    className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg"
                  >
                    <ExclamationTriangleIcon className="h-4 w-4" />
                    <span>Pausar</span>
                  </button>
                  
                  <button
                    onClick={manejarFinalizarExamen}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                  >
                    <FlagIcon className="h-4 w-4" />
                    <span>Finalizar</span>
                  </button>
                </>
              )}

              <button
                onClick={manejarSalir}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {preguntaActualObj && (
            <motion.div
              key={preguntaActual}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <PantallaPregunta
                pregunta={preguntaActualObj}
                respuestaActual={respuestaActual}
                numero={preguntaActual + 1}
                total={preguntas.length}
                onRespuesta={manejarRespuesta}
                deshabilitado={estado !== 'en_progreso'}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navegación inferior */}
        <div className="flex items-center justify-between mt-8">
          <button
            onClick={manejarAnteriorPregunta}
            disabled={preguntaActual === 0 || estado !== 'en_progreso'}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            <ChevronLeftIcon className="h-4 w-4" />
            <span>Anterior</span>
          </button>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {progreso.respondidas} de {progreso.total} respondidas
            </span>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              ({Math.round(progreso.porcentaje)}% completo)
            </span>
          </div>

          <button
            onClick={manejarSiguientePregunta}
            disabled={preguntaActual === preguntas.length - 1 || estado !== 'en_progreso'}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            <span>Siguiente</span>
            <ChevronRightIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Navegador de preguntas overlay */}
      <AnimatePresence>
        {mostrarNavegador && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
            >
              <NavegadorPreguntas
                preguntas={preguntas}
                respuestas={respuestas}
                preguntaActual={preguntaActual}
                onIrAPregunta={manejarIrAPregunta}
                onCerrar={() => setMostrarNavegador(false)}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Alertas anti-trampa */}
      {alertasActivas.length > 0 && (
        <div className="fixed bottom-4 right-4 z-40">
          <div className="bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded-lg p-4 shadow-lg max-w-sm">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-3" />
              <div>
                <p className="font-medium text-red-800 dark:text-red-200">
                  Sistema de Seguridad Activo
                </p>
                <p className="text-sm text-red-700 dark:text-red-300">
                  {alertasActivas.length} evento{alertasActivas.length > 1 ? 's' : ''} detectado{alertasActivas.length > 1 ? 's' : ''}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog(prev => ({ ...prev, isOpen: false }))}
        type="warning"
      />
    </div>
  );
}