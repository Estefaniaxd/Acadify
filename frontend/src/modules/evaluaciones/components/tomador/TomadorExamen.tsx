import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
;
import { Card, CardContent } from '../common/LayoutComponents';
import { LoadingSpinner, ProgressBar } from '../common/LoadingComponents';
import { ConfirmDialog, useToast } from '../common/AlertComponents';
import { useTomarExamen } from '../../hooks';
import { 
  Examen, 
  IntentoExamen,
  RespuestaEstudiante,
  ConfiguracionProctoring,
  AlertaProctoring,
  SnapshotProctoring,
  EventoAudio
} from '../../types';
import { formatearTiempo, obtenerColorEstado } from '../../utils';
import { PantallaPregunta } from './PantallaPregunta';
import { NavegadorPreguntas } from './NavegadorPreguntas';
import { TimerExamen } from './TimerExamen';
import { ResumenFinal } from './ResumenFinal';
import { ProctoringCamera } from '../proctoring/ProctoringCamera';
import { ProctoringAudio } from '../proctoring/ProctoringAudio';
import { AlertasProctoring } from '../proctoring/AlertasProctoring';
import { proctoringService } from '../../services/proctoringService';
import { CheckCircle, ChevronRight, Eye, X, AlertTriangle } from 'lucide-react';

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
  
  // Estados para proctoring
  const [alertasProctoring, setAlertasProctoring] = useState<AlertaProctoring[]>([]);
  const [snapshotsCapturados, setSnapshotsCapturados] = useState<SnapshotProctoring[]>([]);
  const [eventosAudio, setEventosAudio] = useState<EventoAudio[]>([]);
  const [monitoreoActivo, setMonitoreoActivo] = useState(false);
  
  // Configuración de proctoring desde el examen
  const configuracionProctoring: ConfiguracionProctoring = {
    habilitarCamera: examen.configuracion_avanzada?.proctoring?.camera ?? false,
    habilitarMicrofono: examen.configuracion_avanzada?.proctoring?.audio ?? false,
    deteccionRostros: examen.configuracion_avanzada?.proctoring?.deteccionRostros ?? true,
    deteccionMultiplesRostros: examen.configuracion_avanzada?.proctoring?.deteccionMultiplesRostros ?? true,
    deteccionAudio: examen.configuracion_avanzada?.proctoring?.deteccionAudio ?? true,
    grabarVideo: examen.configuracion_avanzada?.proctoring?.grabarVideo ?? false,
    grabarAudio: examen.configuracion_avanzada?.proctoring?.grabarAudio ?? false,
    frecuenciaSnapshotsSegundos: examen.configuracion_avanzada?.proctoring?.frecuenciaSnapshotsSegundos ?? 30,
    umbralConfianzaRostro: examen.configuracion_avanzada?.proctoring?.umbralConfianzaRostro ?? 0.7,
    alertarSinRostro: examen.configuracion_avanzada?.proctoring?.alertarSinRostro ?? true,
    alertarMultiplesRostros: examen.configuracion_avanzada?.proctoring?.alertarMultiplesRostros ?? true,
    alertarRostroDesconocido: examen.configuracion_avanzada?.proctoring?.alertarRostroDesconocido ?? false,
    alertarMultiplesVoces: examen.configuracion_avanzada?.proctoring?.alertarMultiplesVoces ?? true,
  };
  
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
    preguntasExamen,
    respuestas,
    tiempoRestante,
    loading,
    error,
    iniciarIntento,
    enviarRespuesta,
    finalizarIntento: finalizarIntentoHook,
    navegarPregunta,
    siguientePregunta,
    preguntaAnterior
  } = useTomarExamen(examen.examen_id);

  // Callbacks para proctoring
  const handleAlertaProctoring = useCallback(async (alerta: AlertaProctoring) => {
    setAlertasProctoring(prev => [...prev, alerta]);
    
    // Mostrar toast según severidad
    if (alerta.severidad === 'critica' || alerta.severidad === 'alta') {
      showToast({
        type: 'error',
        title: 'Alerta de Seguridad',
        message: alerta.mensaje
      });
    }
    
    // Reportar al backend
    if (intento?.intento_id) {
      try {
        await proctoringService.registrarEvento(intento.intento_id, alerta);
      } catch (error) {
        console.error('Error al registrar evento de proctoring:', error);
      }
    }
  }, [showToast, intento?.intento_id]);

  const handleSnapshotProctoring = useCallback(async (snapshot: SnapshotProctoring) => {
    setSnapshotsCapturados(prev => [...prev, snapshot].slice(-20)); // Mantener últimos 20
    
    // Enviar snapshot al backend
    if (intento?.intento_id) {
      try {
        await proctoringService.subirSnapshot(intento.intento_id, snapshot);
      } catch (error) {
        console.error('Error al subir snapshot:', error);
      }
    }
  }, [intento?.intento_id]);

  const handleEventoAudio = useCallback(async (evento: EventoAudio) => {
    setEventosAudio(prev => [...prev, evento].slice(-50)); // Mantener últimos 50
    
    // Enviar evento al backend
    if (intento?.intento_id) {
      try {
        await proctoringService.registrarEventoAudio(intento.intento_id, evento);
      } catch (error) {
        console.error('Error al registrar evento de audio:', error);
      }
    }
  }, [intento?.intento_id]);

  const handleAlertaCritica = useCallback((contadorCriticas: number) => {
    // Si hay 3 o más alertas críticas, finalizar el examen automáticamente
    if (contadorCriticas >= 3) {
      showToast({
        type: 'error',
        title: 'Examen Finalizado',
        message: 'Se detectaron múltiples infracciones de seguridad. El examen se finalizará automáticamente.'
      });
      
      setTimeout(() => {
        manejarFinalizarExamen();
      }, 3000);
    }
  }, [showToast]);

  // Inicializar el examen
  useEffect(() => {
    const inicializar = async () => {
      try {
        setEstado('iniciando');
        await iniciarIntento();
        
        if (examen.modo_pantalla_completa) {
          await entrarFullscreen();
        }
        
        // Iniciar monitoreo de proctoring si está habilitado
        if (configuracionProctoring.habilitarCamera || configuracionProctoring.habilitarMicrofono) {
          setMonitoreoActivo(true);
        }
        
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
      setMonitoreoActivo(false);
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

  const entrarFullscreen = useCallback(async () => {
    try {
      await document.documentElement.requestFullscreen();
      setModoFullscreen(true);
      
      // Listener para detectar salida de pantalla completa
      const handleFullscreenChange = () => {
        if (!document.fullscreenElement) {
          setModoFullscreen(false);
          if (examen.detectar_cambio_pestana) {
            // TODO: Reportar evento cuando exista el servicio
            // reportarEvento({
            //   tipo: 'SALIDA_PANTALLA_COMPLETA',
            //   detalle: 'Usuario salió de pantalla completa'
            // });
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
  }, [examen.detectar_cambio_pestana]);

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
                tiempoRestante={tiempoRestante || 0}
                tiempoTotal={examen.tiempo_limite ? examen.tiempo_limite * 60 : 3600}
                onTiempoAgotado={manejarTiempoAgotado}
                onAutoSave={async () => {
                  // Auto-guardar respuesta actual si existe
                  if (preguntasExamen[preguntaActual] && respuestas.get(preguntasExamen[preguntaActual].pregunta_id)) {
                    try {
                      const respuestaActual = respuestas.get(preguntasExamen[preguntaActual].pregunta_id);
                      if (respuestaActual?.respuesta_texto) {
                        await enviarRespuesta(preguntasExamen[preguntaActual].pregunta_id, respuestaActual.respuesta_texto);
                      }
                    } catch (error) {
                      console.error('Error en auto-guardado:', error);
                    }
                  }
                }}
                pausado={estado === 'pausado'}
                habilitarNotificaciones={true}
                habilitarAutoSave={true}
                intervaloAutoSaveSegundos={30}
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
                <Eye className="h-4 w-4" />
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
                  <CheckCircle className="h-4 w-4" />
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
                <X className="h-5 w-5" />
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
            <ChevronRight className="h-4 w-4" />
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

      {/* Alertas anti-trampa - Sistema antiguo (deshabilitado temporalmente)
      {alertasActivas.length > 0 && (
        <div className="fixed bottom-4 right-4 z-40">
          <div className="bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded-lg p-4 shadow-lg max-w-sm">
            <div className="flex items-center">
              <AlertTriangle className="h-5 w-5 text-red-500 mr-3" />
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
      */}

      {/* Componentes de Proctoring */}
      {estado === 'en_progreso' && monitoreoActivo && (
        <>
          {configuracionProctoring.habilitarCamera && (
            <ProctoringCamera
              configuracion={configuracionProctoring}
              activo={monitoreoActivo}
              onAlerta={handleAlertaProctoring}
              onSnapshot={handleSnapshotProctoring}
            />
          )}
          
          {configuracionProctoring.habilitarMicrofono && (
            <ProctoringAudio
              configuracion={configuracionProctoring}
              activo={monitoreoActivo}
              onAlerta={handleAlertaProctoring}
              onEventoAudio={handleEventoAudio}
            />
          )}
          
          <AlertasProctoring
            alertas={alertasProctoring}
            onResolverAlerta={(id) => {
              setAlertasProctoring(prev => 
                prev.map(a => a.id === id ? { ...a, resuelta: true } : a)
              );
            }}
            onAlertaCritica={handleAlertaCritica}
          />
        </>
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