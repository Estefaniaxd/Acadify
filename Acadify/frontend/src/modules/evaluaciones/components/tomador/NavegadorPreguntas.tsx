import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  XMarkIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { Card, CardHeader, CardContent } from '../common/LayoutComponents';
import { PreguntaExamen, RespuestaEstudiante, TipoPregunta, DificultadPregunta } from '../../types';

interface NavegadorPreguntasProps {
  preguntas: PreguntaExamen[];
  respuestas: RespuestaEstudiante[];
  preguntaActual: number;
  onIrAPregunta: (indice: number) => void;
  onCerrar: () => void;
  className?: string;
}

const TIPO_PREGUNTA_LABELS: Record<TipoPregunta, string> = {
  SELECCION_UNICA: 'Selección Única',
  SELECCION_MULTIPLE: 'Selección Múltiple',
  VERDADERO_FALSO: 'Verdadero/Falso',
  RESPUESTA_ABIERTA: 'Respuesta Abierta'
};

const DIFICULTAD_COLORS: Record<DificultadPregunta, string> = {
  FACIL: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  MEDIO: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  DIFICIL: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
};

export function NavegadorPreguntas({
  preguntas,
  respuestas,
  preguntaActual,
  onIrAPregunta,
  onCerrar,
  className = ''
}: NavegadorPreguntasProps) {
  
  const estadisticas = useMemo(() => {
    const total = preguntas.length;
    const respondidas = respuestas.length;
    const noRespondidas = total - respondidas;
    const porcentajeCompleto = Math.round((respondidas / total) * 100);

    return {
      total,
      respondidas,
      noRespondidas,
      porcentajeCompleto
    };
  }, [preguntas, respuestas]);

  const obtenerEstadoPregunta = (indice: number) => {
    const pregunta = preguntas[indice];
    const respuesta = respuestas.find(r => r.pregunta_id === pregunta.pregunta_id);
    const esActual = indice === preguntaActual;

    if (esActual) {
      return {
        estado: 'actual',
        color: 'bg-blue-500 text-white',
        icono: <ClockIcon className="h-4 w-4" />
      };
    } else if (respuesta) {
      return {
        estado: 'respondida',
        color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        icono: <CheckCircleIcon className="h-4 w-4" />
      };
    } else {
      return {
        estado: 'pendiente',
        color: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
        icono: <ExclamationCircleIcon className="h-4 w-4" />
      };
    }
  };

  const agruparPorTipo = useMemo(() => {
    const grupos: Record<string, { preguntas: PreguntaExamen[]; indices: number[] }> = {};

    preguntas.forEach((pregunta, indice) => {
      const tipo = pregunta.tipo_pregunta;
      if (!grupos[tipo]) {
        grupos[tipo] = { preguntas: [], indices: [] };
      }
      grupos[tipo].preguntas.push(pregunta);
      grupos[tipo].indices.push(indice);
    });

    return grupos;
  }, [preguntas]);

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Vista General del Examen
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Haz clic en cualquier pregunta para navegar directamente
          </p>
        </div>
        
        <button
          onClick={onCerrar}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <XMarkIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
        </button>
      </div>

      {/* Estadísticas */}
      <div className="p-6 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {estadisticas.total}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Total
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {estadisticas.respondidas}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Respondidas
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-500 dark:text-gray-400">
              {estadisticas.noRespondidas}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Pendientes
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {estadisticas.porcentajeCompleto}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Completado
            </div>
          </div>
        </div>

        {/* Barra de progreso */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Progreso general
            </span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {estadisticas.respondidas} / {estadisticas.total}
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-green-600 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${estadisticas.porcentajeCompleto}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </div>
      </div>

      {/* Lista de preguntas */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-6">
          {Object.entries(agruparPorTipo).map(([tipo, grupo]) => (
            <div key={tipo} className="space-y-3">
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {TIPO_PREGUNTA_LABELS[tipo as TipoPregunta]}
                </h3>
                <span className="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded-full text-sm font-medium">
                  {grupo.preguntas.length}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                {grupo.indices.map((indice) => {
                  const pregunta = preguntas[indice];
                  const estadoPregunta = obtenerEstadoPregunta(indice);
                  
                  return (
                    <motion.button
                      key={indice}
                      onClick={() => onIrAPregunta(indice)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={`
                        relative p-4 rounded-lg border-2 transition-all text-left
                        ${estadoPregunta.color}
                        ${estadoPregunta.estado === 'actual' 
                          ? 'border-blue-500 shadow-lg' 
                          : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
                        }
                      `}
                    >
                      {/* Número de pregunta */}
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-lg">
                          {indice + 1}
                        </span>
                        {estadoPregunta.icono}
                      </div>

                      {/* Información de la pregunta */}
                      <div className="space-y-1">
                        <div className="text-xs opacity-75">
                          {pregunta.tipo_pregunta}
                        </div>
                        
                        {pregunta.dificultad && (
                          <div className={`text-xs px-2 py-1 rounded ${DIFICULTAD_COLORS[pregunta.dificultad]}`}>
                            {pregunta.dificultad}
                          </div>
                        )}
                      </div>

                      {/* Indicador de contexto adicional */}
                      {pregunta.contexto_adicional && (
                        <div className="absolute top-2 right-2 w-2 h-2 bg-purple-500 rounded-full" />
                      )}
                    </motion.button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer con leyenda */}
      <div className="p-6 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded"></div>
            <span className="text-gray-600 dark:text-gray-400">Actual</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-100 dark:bg-green-900 rounded border border-green-300 dark:border-green-700"></div>
            <span className="text-gray-600 dark:text-gray-400">Respondida</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-gray-100 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600"></div>
            <span className="text-gray-600 dark:text-gray-400">Pendiente</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span className="text-gray-600 dark:text-gray-400">Con contexto</span>
          </div>
        </div>
      </div>
    </div>
  );
}