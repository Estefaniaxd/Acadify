import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  ClockIcon,
  ExclamationTriangleIcon,
  PauseIcon,
  PlayIcon
} from '@heroicons/react/24/outline';

interface TimerExamenProps {
  tiempoRestante: number; // en segundos
  tiempoTotal: number; // en segundos
  onTiempoAgotado: () => void;
  pausado?: boolean;
  className?: string;
}

export function TimerExamen({
  tiempoRestante,
  tiempoTotal,
  onTiempoAgotado,
  pausado = false,
  className = ''
}: TimerExamenProps) {
  const [ultimoTiempo, setUltimoTiempo] = useState(tiempoRestante);
  const [pulsando, setPulsando] = useState(false);

  // Detectar cuando el tiempo se agota
  useEffect(() => {
    if (tiempoRestante <= 0 && ultimoTiempo > 0) {
      onTiempoAgotado();
    }
    setUltimoTiempo(tiempoRestante);
  }, [tiempoRestante, ultimoTiempo, onTiempoAgotado]);

  // Efecto de pulsación cuando queda poco tiempo
  useEffect(() => {
    if (tiempoRestante <= 300 && tiempoRestante > 0 && !pausado) { // Últimos 5 minutos
      const intervalo = setInterval(() => {
        setPulsando(prev => !prev);
      }, 1000);

      return () => clearInterval(intervalo);
    } else {
      setPulsando(false);
    }
  }, [tiempoRestante, pausado]);

  const formatearTiempo = useCallback((segundos: number) => {
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const segs = segundos % 60;

    if (horas > 0) {
      return `${horas}:${String(minutos).padStart(2, '0')}:${String(segs).padStart(2, '0')}`;
    }
    return `${minutos}:${String(segs).padStart(2, '0')}`;
  }, []);

  const obtenerColorTimer = () => {
    if (pausado) {
      return 'text-gray-600 dark:text-gray-400';
    } else if (tiempoRestante <= 60) { // Último minuto
      return 'text-red-600 dark:text-red-400';
    } else if (tiempoRestante <= 300) { // Últimos 5 minutos
      return 'text-yellow-600 dark:text-yellow-400';
    } else if (tiempoRestante <= 900) { // Últimos 15 minutos
      return 'text-orange-600 dark:text-orange-400';
    }
    return 'text-gray-900 dark:text-white';
  };

  const obtenerColorFondo = () => {
    if (pausado) {
      return 'bg-gray-100 dark:bg-gray-700';
    } else if (tiempoRestante <= 60) {
      return 'bg-red-100 dark:bg-red-900/20';
    } else if (tiempoRestante <= 300) {
      return 'bg-yellow-100 dark:bg-yellow-900/20';
    } else if (tiempoRestante <= 900) {
      return 'bg-orange-100 dark:bg-orange-900/20';
    }
    return 'bg-white dark:bg-gray-800';
  };

  const porcentajeTiempo = (tiempoRestante / tiempoTotal) * 100;

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Indicador visual circular */}
      <div className="relative w-12 h-12">
        <svg className="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
          {/* Círculo de fondo */}
          <circle
            cx="18"
            cy="18"
            r="16"
            fill="none"
            className="stroke-gray-200 dark:stroke-gray-700"
            strokeWidth="3"
          />
          {/* Círculo de progreso */}
          <motion.circle
            cx="18"
            cy="18"
            r="16"
            fill="none"
            strokeWidth="3"
            strokeLinecap="round"
            className={`${
              pausado
                ? 'stroke-gray-400'
                : tiempoRestante <= 60
                ? 'stroke-red-500'
                : tiempoRestante <= 300
                ? 'stroke-yellow-500'
                : tiempoRestante <= 900
                ? 'stroke-orange-500'
                : 'stroke-green-500'
            }`}
            strokeDasharray="100.53 100.53"
            initial={{ strokeDashoffset: 100.53 }}
            animate={{ 
              strokeDashoffset: 100.53 - (porcentajeTiempo / 100) * 100.53
            }}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
          />
        </svg>
        
        {/* Icono central */}
        <div className="absolute inset-0 flex items-center justify-center">
          {pausado ? (
            <PauseIcon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
          ) : (
            <ClockIcon className={`h-4 w-4 ${obtenerColorTimer()}`} />
          )}
        </div>
      </div>

      {/* Timer display */}
      <motion.div
        animate={pulsando && !pausado ? { scale: [1, 1.05, 1] } : { scale: 1 }}
        transition={{ duration: 0.5, repeat: pulsando ? Infinity : 0 }}
        className={`
          px-4 py-2 rounded-lg border-2 transition-all
          ${obtenerColorFondo()}
          ${pausado 
            ? 'border-gray-300 dark:border-gray-600' 
            : tiempoRestante <= 300 
            ? 'border-red-300 dark:border-red-700' 
            : 'border-gray-200 dark:border-gray-700'
          }
        `}
      >
        <div className="flex items-center space-x-2">
          {tiempoRestante <= 300 && !pausado && (
            <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
          )}
          
          <div className="font-mono text-lg font-semibold">
            <span className={obtenerColorTimer()}>
              {formatearTiempo(Math.max(0, tiempoRestante))}
            </span>
          </div>
        </div>

        {/* Etiqueta de estado */}
        <div className="text-xs text-center mt-1">
          {pausado ? (
            <span className="text-gray-500 dark:text-gray-400">
              Pausado
            </span>
          ) : tiempoRestante <= 0 ? (
            <span className="text-red-500 font-medium">
              Tiempo agotado
            </span>
          ) : tiempoRestante <= 60 ? (
            <span className="text-red-500 font-medium">
              ¡Último minuto!
            </span>
          ) : tiempoRestante <= 300 ? (
            <span className="text-yellow-600 dark:text-yellow-400 font-medium">
              Quedan 5 min
            </span>
          ) : tiempoRestante <= 900 ? (
            <span className="text-orange-600 dark:text-orange-400">
              Quedan 15 min
            </span>
          ) : (
            <span className="text-gray-600 dark:text-gray-400">
              Tiempo restante
            </span>
          )}
        </div>
      </motion.div>

      {/* Barra de progreso horizontal (opcional) */}
      {tiempoRestante <= 900 && !pausado && (
        <div className="hidden sm:flex flex-col space-y-1">
          <div className="text-xs text-gray-600 dark:text-gray-400">
            {Math.round(porcentajeTiempo)}%
          </div>
          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <motion.div
              className={`h-2 rounded-full transition-colors ${
                tiempoRestante <= 60
                  ? 'bg-red-500'
                  : tiempoRestante <= 300
                  ? 'bg-yellow-500'
                  : 'bg-orange-500'
              }`}
              initial={{ width: '100%' }}
              animate={{ width: `${porcentajeTiempo}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      )}
    </div>
  );
}