/**
 * Widget Compacto de Racha
 * 
 * @module components/gamificacion/widgets/RachaWidget
 * @description Widget reutilizable que muestra la racha actual del usuario
 */

import { motion } from 'framer-motion';
import { Zap, Flame, TrendingUp, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useRacha } from '../../../hooks/useGamificacion';

interface RachaWidgetProps {
  className?: string;
  showMiniCalendar?: boolean;
  variant?: 'compact' | 'full';
}

export default function RachaWidget({ 
  className = '', 
  showMiniCalendar = true,
  variant = 'compact' 
}: RachaWidgetProps) {
  const { data: racha, isLoading, isError } = useRacha();

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

  if (isError || !racha) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="text-sm">Error al cargar racha</p>
        </div>
      </div>
    );
  }

  const { dias_actuales, mejor_racha, activa, puntos_por_dia } = racha;

  // Generar mini calendario de últimos 7 días
  const generateMiniCalendar = () => {
    const days = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dayName = date.toLocaleDateString('es-ES', { weekday: 'short' })[0].toUpperCase();
      const isActive = i < dias_actuales; // Simplificación: últimos N días activos
      days.push({ dayName, isActive, date });
    }
    return days;
  };

  const miniCalendar = generateMiniCalendar();

  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -4, scale: 1.02 }}
        className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${className}`}
      >
        <Link to="/rachas" className="block p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
              Racha Actual
            </h3>
            <motion.div 
              className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                activa 
                  ? 'bg-gradient-to-br from-orange-500 to-red-600' 
                  : 'bg-gray-400'
              }`}
              animate={activa ? {
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              } : {}}
              transition={{ 
                duration: 2, 
                repeat: activa ? Infinity : 0,
                repeatDelay: 1 
              }}
            >
              <Flame className="w-5 h-5 text-white" />
            </motion.div>
          </div>

          {/* Contador principal */}
          <div className="mb-3">
            <div className="flex items-baseline gap-2">
              <p className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-red-600">
                {dias_actuales}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {dias_actuales === 1 ? 'día' : 'días'}
              </p>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {activa ? '¡Racha activa!' : 'Racha inactiva'}
            </p>
          </div>

          {/* Mini calendario */}
          {showMiniCalendar && (
            <div className="mb-4">
              <div className="flex gap-1 justify-between">
                {miniCalendar.map((day, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex flex-col items-center"
                  >
                    <span className="text-[10px] text-gray-400 dark:text-gray-500 mb-1">
                      {day.dayName}
                    </span>
                    <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                      day.isActive 
                        ? 'bg-gradient-to-br from-orange-500 to-red-600' 
                        : 'bg-gray-200 dark:bg-gray-700'
                    }`}>
                      {day.isActive && (
                        <Flame className="w-3 h-3 text-white" />
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-2">
              <div className="flex items-center gap-1 mb-1">
                <TrendingUp className="w-3 h-3 text-violet-600 dark:text-violet-400" />
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Mejor
                </p>
              </div>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {mejor_racha}
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-2">
              <div className="flex items-center gap-1 mb-1">
                <Zap className="w-3 h-3 text-yellow-600 dark:text-yellow-400" />
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Puntos/día
                </p>
              </div>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {puntos_por_dia}
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Ver historial →
            </span>
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
            Tu Racha
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {activa ? 'Mantén el ritmo!' : 'Reactiva tu racha hoy'}
          </p>
        </div>
        <motion.div 
          className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
            activa 
              ? 'bg-gradient-to-br from-orange-500 to-red-600' 
              : 'bg-gray-400'
          }`}
          animate={activa ? {
            scale: [1, 1.1, 1],
            rotate: [0, 10, -10, 0]
          } : {}}
          transition={{ 
            duration: 2, 
            repeat: activa ? Infinity : 0,
            repeatDelay: 1 
          }}
        >
          <Flame className="w-8 h-8 text-white" />
        </motion.div>
      </div>

      {/* Contador grande */}
      <div className="text-center mb-8">
        <div className="flex items-baseline justify-center gap-3">
          <p className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-red-600">
            {dias_actuales}
          </p>
          <p className="text-xl text-gray-500 dark:text-gray-400">
            {dias_actuales === 1 ? 'día consecutivo' : 'días consecutivos'}
          </p>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
          {activa ? '¡Excelente trabajo! Sigue así' : 'Participa hoy para reactivar tu racha'}
        </p>
      </div>

      {/* Calendario completo de 7 días */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Últimos 7 días
        </h3>
        <div className="flex gap-2 justify-between">
          {miniCalendar.map((day, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="flex flex-col items-center flex-1"
            >
              <span className="text-xs text-gray-400 dark:text-gray-500 mb-2">
                {day.dayName}
              </span>
              <div className={`w-full aspect-square rounded-xl flex items-center justify-center ${
                day.isActive 
                  ? 'bg-gradient-to-br from-orange-500 to-red-600 shadow-lg' 
                  : 'bg-gray-200 dark:bg-gray-700'
              }`}>
                {day.isActive && (
                  <Flame className="w-6 h-6 text-white" />
                )}
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {day.date.getDate()}
              </span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Grid de estadísticas */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <Calendar className="w-5 h-5 text-violet-600 dark:text-violet-400" />
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {dias_actuales}
          </p>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Actual
          </p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {mejor_racha}
          </p>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Récord
          </p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <Zap className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {puntos_por_dia}
          </p>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Pts/día
          </p>
        </div>
      </div>

      {/* Link a página completa */}
      <Link
        to="/rachas"
        className="block w-full py-3 bg-gradient-to-r from-orange-600 to-red-600 text-white text-center font-semibold rounded-xl hover:shadow-lg transition-all duration-300"
      >
        Ver historial completo
      </Link>
    </motion.div>
  );
}
