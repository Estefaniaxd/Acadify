import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
;
import { Card, CardHeader, CardContent } from '../common/LayoutComponents';
import { ProgressBar } from '../common/LoadingComponents';
import { IntentoExamen, Examen } from '../../types';
import { formatearTiempo, formatearFecha } from '../../utils';
import { ArrowRight, BarChart, CheckCircle, FileText } from 'lucide-react';

interface ResumenFinalProps {
  intento: IntentoExamen;
  examen: Examen;
  onSalir: () => void;
  className?: string;
}

const calcularPorcentaje = (valor: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((valor / total) * 100);
};

export function ResumenFinal({
  intento,
  examen,
  onSalir,
  className = ''
}: ResumenFinalProps) {
  const [mostrarDetalles, setMostrarDetalles] = useState(false);
  const [animacionCompleta, setAnimacionCompleta] = useState(false);

  useEffect(() => {
    // Iniciar animación después de un delay
    const timer = setTimeout(() => {
      setAnimacionCompleta(true);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  // Calcular estadísticas
  const tiempoUtilizado = intento.fecha_inicio && intento.fecha_fin
    ? new Date(intento.fecha_fin).getTime() - new Date(intento.fecha_inicio).getTime()
    : 0;
  
  const tiempoUtilizadoSegundos = Math.floor(tiempoUtilizado / 1000);
  const tiempoLimiteSegundos = examen.tiempo_limite * 60;
  const porcentajeTiempoUtilizado = (tiempoUtilizadoSegundos / tiempoLimiteSegundos) * 100;

  const obtenerColorCalificacion = (puntuacion: number, puntuacionMaxima: number) => {
    const porcentaje = calcularPorcentaje(puntuacion, puntuacionMaxima);
    if (porcentaje >= 90) return 'text-green-600';
    if (porcentaje >= 80) return 'text-blue-600';
    if (porcentaje >= 70) return 'text-yellow-600';
    if (porcentaje >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  const obtenerMensajeFelicitacion = (puntuacion: number, puntuacionMaxima: number) => {
    const porcentaje = calcularPorcentaje(puntuacion, puntuacionMaxima);
    if (porcentaje >= 95) return '¡Excelente trabajo! 🌟';
    if (porcentaje >= 90) return '¡Muy bien hecho! 🎉';
    if (porcentaje >= 80) return '¡Buen trabajo! 👏';
    if (porcentaje >= 70) return '¡Bien! Sigue practicando 💪';
    if (porcentaje >= 60) return 'Puedes mejorar 📚';
    return 'Sigue estudiando 📖';
  };

  const obtenerIconoRendimiento = (puntuacion: number, puntuacionMaxima: number) => {
    const porcentaje = calcularPorcentaje(puntuacion, puntuacionMaxima);
    if (porcentaje >= 90) return <TrophyIcon className="h-12 w-12 text-yellow-500" />;
    if (porcentaje >= 80) return <StarIcon className="h-12 w-12 text-blue-500" />;
    if (porcentaje >= 60) return <CheckCircle className="h-12 w-12 text-green-500" />;
    return <XCircleIcon className="h-12 w-12 text-red-500" />;
  };

  const preguntasRespondidas = intento.preguntas_respondidas || 0;
  const totalPreguntas = intento.total_preguntas || 0;
  const preguntasIncorrectas = totalPreguntas - preguntasRespondidas;
  const preguntasSinResponder = totalPreguntas - preguntasRespondidas;

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 p-4 ${className}`}>
      <div className="max-w-4xl mx-auto">
        {/* Header animado */}
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <div className="mb-4">
            {obtenerIconoRendimiento(intento.puntuacion_obtenida, intento.puntuacion_maxima)}
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            ¡Examen Completado!
          </h1>
          
          <p className="text-xl text-gray-600 dark:text-gray-300">
            {examen.titulo}
          </p>
          
          <div className="mt-4">
            <span className="inline-block bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-200 px-4 py-2 rounded-full text-sm font-medium">
              {obtenerMensajeFelicitacion(intento.puntuacion_obtenida, intento.puntuacion_maxima)}
            </span>
          </div>
        </motion.div>

        {/* Tarjeta principal de resultados */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="shadow-xl mb-6">
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Puntuación */}
                <div className="text-center">
                  <div className="mb-4">
                    <div className={`text-6xl font-bold ${obtenerColorCalificacion(intento.puntuacion_obtenida, intento.puntuacion_maxima)}`}>
                      {intento.puntuacion_obtenida}
                    </div>
                    <div className="text-2xl text-gray-600 dark:text-gray-400">
                      / {intento.puntuacion_maxima}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Puntuación Final
                    </h3>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                      <motion.div
                        className={`h-3 rounded-full transition-colors ${
                          calcularPorcentaje(intento.puntuacion_obtenida, intento.puntuacion_maxima) >= 60
                            ? 'bg-green-500'
                            : 'bg-red-500'
                        }`}
                        initial={{ width: 0 }}
                        animate={{ 
                          width: animacionCompleta 
                            ? `${calcularPorcentaje(intento.puntuacion_obtenida, intento.puntuacion_maxima)}%` 
                            : 0 
                        }}
                        transition={{ duration: 1, delay: 0.8 }}
                      />
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {calcularPorcentaje(intento.puntuacion_obtenida, intento.puntuacion_maxima)}% de aciertos
                    </div>
                  </div>
                </div>

                {/* Tiempo */}
                <div className="text-center">
                  <div className="mb-4">
                    <ClockIcon className="h-16 w-16 mx-auto text-blue-500 mb-2" />
                    <div className="text-3xl font-bold text-gray-900 dark:text-white">
                      {formatearTiempo(tiempoUtilizadoSegundos)}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Tiempo Utilizado
                    </h3>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                      <motion.div
                        className="bg-blue-500 h-3 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ 
                          width: animacionCompleta 
                            ? `${Math.min(porcentajeTiempoUtilizado, 100)}%` 
                            : 0 
                        }}
                        transition={{ duration: 1, delay: 1.2 }}
                      />
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      de {formatearTiempo(tiempoLimiteSegundos)} disponibles
                    </div>
                  </div>
                </div>

                {/* Estado */}
                <div className="text-center">
                  <div className="mb-4">
                    <CheckCircle className="h-16 w-16 mx-auto text-green-500 mb-2" />
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                      COMPLETADO
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Estado del Examen
                    </h3>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Finalizado el {formatearFecha(intento.fecha_fin || new Date().toISOString())}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-500">
                      ID: {intento.intento_id}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Estadísticas detalladas */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="shadow-lg mb-6">
            <CardHeader title="Resumen de Respuestas" />
            <CardContent>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Resumen de Respuestas
                </h2>
                <button
                  onClick={() => setMostrarDetalles(!mostrarDetalles)}
                  className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 transition-colors"
                >
                  <span>{mostrarDetalles ? 'Ocultar' : 'Ver'} detalles</span>
                  <motion.div
                    animate={{ rotate: mostrarDetalles ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ArrowRight className="h-4 w-4" />
                  </motion.div>
                </button>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                    {totalPreguntas}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Total Preguntas
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                    {preguntasRespondidas}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Respondidas
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600 dark:text-red-400">
                    {preguntasIncorrectas}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Incorrectas
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-600 dark:text-gray-400">
                    {preguntasSinResponder}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Sin Responder
                  </div>
                </div>
              </div>

              {/* Detalles expandibles */}
              {mostrarDetalles && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700"
                >
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                        Información del Intento
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Inicio:</span>
                          <span className="text-gray-900 dark:text-white">
                            {formatearFecha(intento.fecha_inicio)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Finalización:</span>
                          <span className="text-gray-900 dark:text-white">
                            {formatearFecha(intento.fecha_fin || new Date().toISOString())}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Estado:</span>
                          <span className="text-green-600 dark:text-green-400 font-medium">
                            {intento.estado_intento}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                        Configuración del Examen
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Tiempo límite:</span>
                          <span className="text-gray-900 dark:text-white">
                            {formatearTiempo(tiempoLimiteSegundos)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Intentos permitidos:</span>
                          <span className="text-gray-900 dark:text-white">
                            {examen.intentos_permitidos}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Pantalla completa:</span>
                          <span className="text-gray-900 dark:text-white">
                            {examen.modo_pantalla_completa ? 'Sí' : 'No'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Acciones finales */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="text-center"
        >
          <div className="space-y-4">
            <p className="text-gray-600 dark:text-gray-400">
              ¿Qué te gustaría hacer a continuación?
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={onSalir}
                className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                <FileText className="h-5 w-5" />
                <span>Regresar al Dashboard</span>
              </button>
              
              <button
                onClick={() => window.print()}
                className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
              >
                <BarChart className="h-5 w-5" />
                <span>Imprimir Resultados</span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}