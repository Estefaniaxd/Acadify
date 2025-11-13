/**
 * Widget Compacto de Puntos
 * 
 * @module components/gamificacion/widgets/PuntosWidget
 * @description Widget reutilizable que muestra puntos totales, nivel actual y progreso
 */

import { motion } from 'framer-motion';
import { Star, TrendingUp, Trophy } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useMisPuntos } from '../../../hooks/useGamificacion';
import { formatearPuntos, obtenerColorNivel } from '../../../services/gamificacion.service';

interface PuntosWidgetProps {
  className?: string;
  showDetails?: boolean;
  variant?: 'compact' | 'full';
}

export default function PuntosWidget({ 
  className = '', 
  showDetails = true,
  variant = 'compact' 
}: PuntosWidgetProps) {
  const { data: puntos, isLoading, isError } = useMisPuntos();

  if (isLoading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-4"></div>
          <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-40"></div>
        </div>
      </div>
    );
  }

  if (isError || !puntos) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="text-sm">Error al cargar puntos</p>
        </div>
      </div>
    );
  }

  const { puntos_acumulados, nivel_actual, nivel_info } = puntos;

  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -4, scale: 1.02 }}
        className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${className}`}
      >
        <Link to="/puntos" className="block p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
              Mis Puntos
            </h3>
            <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
              <Star className="w-5 h-5 text-white" />
            </div>
          </div>

          {/* Puntos totales */}
          <div className="mb-3">
            <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-orange-600">
              {formatearPuntos(puntos_acumulados)}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Puntos acumulados
            </p>
          </div>

          {/* Nivel */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 bg-gradient-to-br ${obtenerColorNivel(nivel_actual)} rounded-lg flex items-center justify-center`}>
                <Trophy className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-bold text-gray-900 dark:text-white">
                  {nivel_info.nombre}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Nivel {nivel_info.numero}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-violet-600 dark:text-violet-400">
                {nivel_info.progreso_porcentaje}%
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Progreso
              </p>
            </div>
          </div>

          {/* Barra de progreso */}
          {showDetails && (
            <div className="mt-4">
              <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${nivel_info.progreso_porcentaje}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-full bg-gradient-to-r ${obtenerColorNivel(nivel_actual)} rounded-full`}
                />
              </div>
              <div className="flex items-center justify-between mt-1">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {formatearPuntos(nivel_info.puntos_minimos)}
                </p>
                <p className="text-xs font-semibold text-violet-600 dark:text-violet-400">
                  {formatearPuntos(nivel_info.puntos_para_siguiente)} para subir
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {formatearPuntos(nivel_info.puntos_maximos)}
                </p>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Ver detalles →
            </span>
            <TrendingUp className="w-4 h-4 text-green-500" />
          </div>
        </Link>
      </motion.div>
    );
  }

  // Variant 'full'
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg p-8 ${className}`}
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            Mis Puntos
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Tu progreso y nivel actual
          </p>
        </div>
        <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-2xl flex items-center justify-center">
          <Star className="w-8 h-8 text-white" />
        </div>
      </div>

      {/* Grid de información */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Puntos Totales
          </p>
          <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-orange-600">
            {formatearPuntos(puntos_acumulados)}
          </p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Nivel Actual
          </p>
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 bg-gradient-to-br ${obtenerColorNivel(nivel_actual)} rounded-lg flex items-center justify-center`}>
              <Trophy className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {nivel_info.nombre}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Nivel {nivel_info.numero}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Barra de progreso al siguiente nivel */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Progreso al siguiente nivel
          </p>
          <p className="text-lg font-bold text-violet-600 dark:text-violet-400">
            {nivel_info.progreso_porcentaje}%
          </p>
        </div>
        <div className="relative w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${nivel_info.progreso_porcentaje}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className={`h-full bg-gradient-to-r ${obtenerColorNivel(nivel_actual)} rounded-full`}
          />
        </div>
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {formatearPuntos(nivel_info.puntos_minimos)} pts
          </p>
          <p className="text-xs font-semibold text-violet-600 dark:text-violet-400">
            {formatearPuntos(nivel_info.puntos_para_siguiente)} pts para subir
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {formatearPuntos(nivel_info.puntos_maximos)} pts
          </p>
        </div>
      </div>

      {/* Link a página completa */}
      <Link
        to="/puntos"
        className="block w-full py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white text-center font-semibold rounded-xl hover:shadow-lg transition-all duration-300"
      >
        Ver detalles completos
      </Link>
    </motion.div>
  );
}
