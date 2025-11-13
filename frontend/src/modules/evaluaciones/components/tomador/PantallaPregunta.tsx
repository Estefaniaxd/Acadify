import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
;
import { Card, CardHeader, CardContent } from '../common/LayoutComponents';
import { LoadingSpinner } from '../common/LoadingComponents';
import { AlertMessage } from '../common/AlertComponents';
import { PreguntaExamen, RespuestaEstudiante, OpcionRespuesta } from '../../types';
import { formatearTexto, procesarMediaURL } from '../../utils';

interface PantallaPreguntaProps {
  pregunta: PreguntaExamen;
  respuestaActual?: RespuestaEstudiante;
  numero: number;
  total: number;
  onRespuesta: (respuesta: any) => void;
  deshabilitado?: boolean;
  className?: string;
}

interface EstadoMultimedia {
  cargando: boolean;
  error: string | null;
  duracion?: number;
  progreso?: number;
}

export function PantallaPregunta({
  pregunta,
  respuestaActual,
  numero,
  total,
  onRespuesta,
  deshabilitado = false,
  className = ''
}: PantallaPreguntaProps) {
  const [respuestaLocal, setRespuestaLocal] = useState<any>(null);
  const [multimedia, setMultimedia] = useState<EstadoMultimedia>({
    cargando: false,
    error: null
  });
  const [audioRef, setAudioRef] = useState<HTMLAudioElement | null>(null);
  const [reproduciendoAudio, setReproduciendoAudio] = useState(false);

  // Sincronizar respuesta actual con estado local
  useEffect(() => {
    if (respuestaActual) {
      setRespuestaLocal(respuestaActual.respuesta_data);
    } else {
      setRespuestaLocal(null);
    }
  }, [respuestaActual]);

  // Cargar multimedia si existe
  useEffect(() => {
    if (pregunta.multimedia_url) {
      cargarMultimedia();
    }

    return () => {
      if (audioRef) {
        audioRef.pause();
        audioRef.src = '';
      }
    };
  }, [pregunta.multimedia_url]);

  const cargarMultimedia = async () => {
    if (!pregunta.multimedia_url) return;

    setMultimedia({ cargando: true, error: null });

    try {
      const url = await procesarMediaURL(pregunta.multimedia_url);
      
      if (pregunta.multimedia_tipo === 'AUDIO') {
        const audio = new Audio(url);
        audio.preload = 'metadata';
        
        audio.onloadedmetadata = () => {
          setMultimedia({
            cargando: false,
            error: null,
            duracion: audio.duration
          });
        };

        audio.onerror = () => {
          setMultimedia({
            cargando: false,
            error: 'No se pudo cargar el audio'
          });
        };

        audio.ontimeupdate = () => {
          setMultimedia(prev => ({
            ...prev,
            progreso: (audio.currentTime / audio.duration) * 100
          }));
        };

        audio.onended = () => {
          setReproduciendoAudio(false);
        };

        setAudioRef(audio);
      } else {
        setMultimedia({ cargando: false, error: null });
      }
    } catch (error) {
      setMultimedia({
        cargando: false,
        error: 'Error al cargar el contenido multimedia'
      });
    }
  };

  const manejarCambioRespuesta = useCallback((nuevaRespuesta: any) => {
    setRespuestaLocal(nuevaRespuesta);
    
    // Guardar automáticamente después de un breve delay
    const timer = setTimeout(() => {
      onRespuesta(nuevaRespuesta);
    }, 500);

    return () => clearTimeout(timer);
  }, [onRespuesta]);

  const toggleAudio = () => {
    if (!audioRef) return;

    if (reproduciendoAudio) {
      audioRef.pause();
      setReproduciendoAudio(false);
    } else {
      audioRef.play();
      setReproduciendoAudio(true);
    }
  };

  const renderizarMultimedia = () => {
    if (!pregunta.multimedia_url) return null;

    return (
      <div className="mb-6">
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
          {multimedia.cargando ? (
            <div className="flex items-center justify-center h-32">
              <LoadingSpinner />
              <span className="ml-2 text-gray-600 dark:text-gray-400">
                Cargando multimedia...
              </span>
            </div>
          ) : multimedia.error ? (
            <div className="flex items-center justify-center h-32">
              <AlertMessage
                type="error"
                message={multimedia.error}
                className="mb-0"
              />
              <button
                onClick={cargarMultimedia}
                className="ml-4 p-2 text-blue-600 hover:text-blue-800 dark:text-blue-400"
              >
                <ArrowPathIcon className="h-5 w-5" />
              </button>
            </div>
          ) : pregunta.multimedia_tipo === 'IMAGE' ? (
            <div className="relative">
              <img
                src={pregunta.multimedia_url}
                alt="Imagen de la pregunta"
                className="max-w-full h-auto rounded-lg shadow-sm"
                loading="lazy"
              />
              <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                <PhotoIcon className="h-4 w-4 inline mr-1" />
                Imagen
              </div>
            </div>
          ) : pregunta.multimedia_tipo === 'AUDIO' ? (
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleAudio}
                className="flex items-center justify-center w-12 h-12 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors"
                disabled={!audioRef}
              >
                {reproduciendoAudio ? (
                  <PauseIcon className="h-6 w-6" />
                ) : (
                  <PlayIcon className="h-6 w-6" />
                )}
              </button>
              
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <SpeakerWaveIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Audio de la pregunta
                  </span>
                  {multimedia.duracion && (
                    <span className="text-xs text-gray-500">
                      {Math.floor(multimedia.duracion / 60)}:
                      {String(Math.floor(multimedia.duracion % 60)).padStart(2, '0')}
                    </span>
                  )}
                </div>
                
                {multimedia.progreso !== undefined && (
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${multimedia.progreso}%` }}
                    />
                  </div>
                )}
              </div>
            </div>
          ) : pregunta.multimedia_tipo === 'VIDEO' ? (
            <video
              src={pregunta.multimedia_url}
              controls
              className="w-full max-h-64 rounded-lg"
              preload="metadata"
            />
          ) : null}
        </div>
      </div>
    );
  };

  const renderizarOpcionesSeleccionMultiple = () => {
    const opciones = pregunta.opciones_respuesta as OpcionRespuesta[];
    const respuestasSeleccionadas = respuestaLocal || [];

    return (
      <div className="space-y-3">
        {opciones.map((opcion) => {
          const estaSeleccionada = respuestasSeleccionadas.includes(opcion.opcion_id);
          
          return (
            <motion.div
              key={opcion.opcion_id}
              whileHover={{ scale: deshabilitado ? 1 : 1.02 }}
              whileTap={{ scale: deshabilitado ? 1 : 0.98 }}
            >
              <label className={`
                flex items-start space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all
                ${estaSeleccionada
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }
                ${deshabilitado ? 'opacity-50 cursor-not-allowed' : ''}
              `}>
                <input
                  type="checkbox"
                  checked={estaSeleccionada}
                  onChange={(e) => {
                    if (deshabilitado) return;
                    
                    let nuevasRespuestas = [...respuestasSeleccionadas];
                    if (e.target.checked) {
                      nuevasRespuestas.push(opcion.opcion_id);
                    } else {
                      nuevasRespuestas = nuevasRespuestas.filter(id => id !== opcion.opcion_id);
                    }
                    manejarCambioRespuesta(nuevasRespuestas);
                  }}
                  disabled={deshabilitado}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div className="flex-1">
                  <div
                    className="text-gray-900 dark:text-white"
                    dangerouslySetInnerHTML={{ __html: formatearTexto(opcion.texto_opcion) }}
                  />
                  {opcion.explicacion && (
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      {opcion.explicacion}
                    </div>
                  )}
                </div>
              </label>
            </motion.div>
          );
        })}
      </div>
    );
  };

  const renderizarOpcionesSeleccionUnica = () => {
    const opciones = pregunta.opciones_respuesta as OpcionRespuesta[];
    const respuestaSeleccionada = respuestaLocal;

    return (
      <div className="space-y-3">
        {opciones.map((opcion) => {
          const estaSeleccionada = respuestaSeleccionada === opcion.opcion_id;
          
          return (
            <motion.div
              key={opcion.opcion_id}
              whileHover={{ scale: deshabilitado ? 1 : 1.02 }}
              whileTap={{ scale: deshabilitado ? 1 : 0.98 }}
            >
              <label className={`
                flex items-start space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all
                ${estaSeleccionada
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }
                ${deshabilitado ? 'opacity-50 cursor-not-allowed' : ''}
              `}>
                <input
                  type="radio"
                  name={`pregunta_${pregunta.pregunta_id}`}
                  checked={estaSeleccionada}
                  onChange={() => {
                    if (deshabilitado) return;
                    manejarCambioRespuesta(opcion.opcion_id);
                  }}
                  disabled={deshabilitado}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div className="flex-1">
                  <div
                    className="text-gray-900 dark:text-white"
                    dangerouslySetInnerHTML={{ __html: formatearTexto(opcion.texto_opcion) }}
                  />
                  {opcion.explicacion && (
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      {opcion.explicacion}
                    </div>
                  )}
                </div>
              </label>
            </motion.div>
          );
        })}
      </div>
    );
  };

  const renderizarRespuestaAbierta = () => {
    return (
      <div className="space-y-4">
        <textarea
          value={respuestaLocal || ''}
          onChange={(e) => {
            if (deshabilitado) return;
            manejarCambioRespuesta(e.target.value);
          }}
          disabled={deshabilitado}
          placeholder="Escribe tu respuesta aquí..."
          className="w-full h-32 p-4 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical disabled:opacity-50 disabled:cursor-not-allowed bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          maxLength={5000}
        />
        
        <div className="flex justify-between items-center text-sm text-gray-600 dark:text-gray-400">
          <span>
            {respuestaLocal?.length || 0} / 5000 caracteres
          </span>
          {respuestaLocal && (
            <span>
              Aproximadamente {Math.ceil((respuestaLocal.length || 0) / 5)} palabras
            </span>
          )}
        </div>
      </div>
    );
  };

  const renderizarVerdaderoFalso = () => {
    const opciones = [
      { id: 'true', label: 'Verdadero', valor: true },
      { id: 'false', label: 'Falso', valor: false }
    ];

    return (
      <div className="space-y-3">
        {opciones.map((opcion) => {
          const estaSeleccionada = respuestaLocal === opcion.valor;
          
          return (
            <motion.div
              key={opcion.id}
              whileHover={{ scale: deshabilitado ? 1 : 1.02 }}
              whileTap={{ scale: deshabilitado ? 1 : 0.98 }}
            >
              <label className={`
                flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all
                ${estaSeleccionada
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }
                ${deshabilitado ? 'opacity-50 cursor-not-allowed' : ''}
              `}>
                <input
                  type="radio"
                  name={`pregunta_${pregunta.pregunta_id}`}
                  checked={estaSeleccionada}
                  onChange={() => {
                    if (deshabilitado) return;
                    manejarCambioRespuesta(opcion.valor);
                  }}
                  disabled={deshabilitado}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="text-lg font-medium text-gray-900 dark:text-white">
                  {opcion.label}
                </span>
              </label>
            </motion.div>
          );
        })}
      </div>
    );
  };

  const renderizarRespuesta = () => {
    switch (pregunta.tipo_pregunta) {
      case 'SELECCION_MULTIPLE':
        return renderizarOpcionesSeleccionMultiple();
      case 'SELECCION_UNICA':
        return renderizarOpcionesSeleccionUnica();
      case 'RESPUESTA_ABIERTA':
        return renderizarRespuestaAbierta();
      case 'VERDADERO_FALSO':
        return renderizarVerdaderoFalso();
      default:
        return (
          <AlertMessage
            type="warning"
            message="Tipo de pregunta no soportado"
          />
        );
    }
  };

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      <Card className="shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm font-medium">
                Pregunta {numero} de {total}
              </div>
              
              {pregunta.puntos && (
                <div className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-3 py-1 rounded-full text-sm font-medium">
                  {pregunta.puntos} {pregunta.puntos === 1 ? 'punto' : 'puntos'}
                </div>
              )}
              
              {pregunta.dificultad && (
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  pregunta.dificultad === 'FACIL'
                    ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                    : pregunta.dificultad === 'MEDIO'
                    ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                    : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                }`}>
                  {pregunta.dificultad}
                </div>
              )}
            </div>

            {respuestaActual && (
              <div className="text-sm text-green-600 dark:text-green-400 font-medium">
                ✓ Respondida
              </div>
            )}
          </div>
        </CardHeader>

        <CardContent>
          {/* Texto de la pregunta */}
          <div className="mb-6">
            <div
              className="text-lg text-gray-900 dark:text-white leading-relaxed"
              dangerouslySetInnerHTML={{ __html: formatearTexto(pregunta.texto_pregunta) }}
            />
            
            {pregunta.contexto_adicional && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  Contexto adicional:
                </h4>
                <div
                  className="text-gray-700 dark:text-gray-300"
                  dangerouslySetInnerHTML={{ __html: formatearTexto(pregunta.contexto_adicional) }}
                />
              </div>
            )}
          </div>

          {/* Multimedia */}
          {renderizarMultimedia()}

          {/* Opciones de respuesta */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 dark:text-white">
              {pregunta.tipo_pregunta === 'SELECCION_MULTIPLE'
                ? 'Selecciona todas las opciones correctas:'
                : pregunta.tipo_pregunta === 'SELECCION_UNICA'
                ? 'Selecciona la opción correcta:'
                : pregunta.tipo_pregunta === 'VERDADERO_FALSO'
                ? 'Selecciona tu respuesta:'
                : 'Tu respuesta:'}
            </h4>
            
            <AnimatePresence mode="wait">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderizarRespuesta()}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Instrucciones adicionales */}
          {pregunta.instrucciones_adicionales && (
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h4 className="font-medium text-blue-900 dark:text-blue-200 mb-2">
                Instrucciones:
              </h4>
              <div
                className="text-blue-800 dark:text-blue-300 text-sm"
                dangerouslySetInnerHTML={{ __html: formatearTexto(pregunta.instrucciones_adicionales) }}
              />
            </div>
          )}

          {/* Estado de guardado automático */}
          {respuestaLocal && !deshabilitado && (
            <div className="mt-4 text-sm text-gray-500 dark:text-gray-400 italic">
              ✓ Respuesta guardada automáticamente
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}