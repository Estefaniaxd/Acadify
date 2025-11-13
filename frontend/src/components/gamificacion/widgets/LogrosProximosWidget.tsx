/**
 * Widget de Logros Próximos a Completar
 * 
 * @module components/gamificacion/widgets/LogrosProximosWidget
 * @description Widget reutilizable que muestra los logros casi completados
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Target, Trophy, Star, Lock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useMisLogros } from '../../../hooks/useGamificacion';
import { obtenerColorRareza, obtenerBgRareza } from '../../../services/gamificacion.service';

interface LogrosProximosWidgetProps {
  className?: string;
  count?: number;
  variant?: 'compact' | 'full';
}

export default function LogrosProximosWidget({ 
  className = '', 
  count = 3,
  variant = 'compact' 
}: LogrosProximosWidgetProps) {
  const { data: logros, isLoading, isError } = useMisLogros();

  // Calcular logros próximos a completar (ordenados por % de progreso)
  const logrosProximos = useMemo(() => {
    if (!logros) return [];
    
    return logros
      .filter(l => !l.completado && l.progreso_actual > 0)
      .map(l => ({
        ...l,
        porcentaje: Math.round((l.progreso_actual / l.objetivo) * 100)
      }))
      .sort((a, b) => b.porcentaje - a.porcentaje)
      .slice(0, count);
  }, [logros, count]);

  if (isLoading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4"></div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="mb-3">
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !logros) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="text-sm">Error al cargar logros</p>
        </div>
      </div>
    );
  }

  if (logrosProximos.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg p-6 ${className}`}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
            Próximos Logros
          </h3>
          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
            <Trophy className="w-5 h-5 text-white" />
          </div>
        </div>
        <div className="text-center py-6">
          <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
            <Star className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            ¡Todos los logros iniciados están completos!
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500">
            Explora más actividades
          </p>
        </div>
        <Link
          to="/logros"
          className="block w-full py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-center text-sm font-medium rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          Ver todos los logros
        </Link>
      </motion.div>
    );
  }

  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -4, scale: 1.02 }}
        className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${className}`}
      >
        <Link to="/logros" className="block p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
              Próximos Logros
            </h3>
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
          </div>

          {/* Lista de logros */}
          <div className="space-y-3 mb-4">
            {logrosProximos.map((logro, idx) => (
              <motion.div
                key={logro.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="group"
              >
                {/* Header del logro */}
                <div className="flex items-start gap-3 mb-2">
                  <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Lock className="w-4 h-4 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                        {logro.nombre}
                      </p>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${obtenerColorRareza(logro.rareza)} ${obtenerBgRareza(logro.rareza)}`}>
                        {logro.rareza}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
                      <span>{logro.progreso_actual} / {logro.objetivo}</span>
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 text-yellow-500" />
                        <span className="font-semibold text-yellow-600 dark:text-yellow-400">
                          {logro.puntos_recompensa} pts
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Barra de progreso */}
                <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${logro.porcentaje}%` }}
                    transition={{ duration: 1, delay: idx * 0.1 }}
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-600 rounded-full relative"
                  >
                    {logro.porcentaje >= 50 && (
                      <span className="absolute right-2 top-1/2 transform -translate-y-1/2 text-[10px] font-bold text-white">
                        {logro.porcentaje}%
                      </span>
                    )}
                  </motion.div>
                </div>
                {logro.porcentaje < 50 && (
                  <p className="text-xs text-right text-gray-500 dark:text-gray-400 mt-1">
                    {logro.porcentaje}%
                  </p>
                )}
              </motion.div>
            ))}
          </div>

          {/* Footer */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Ver todos los logros →
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
            Logros en Progreso
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {logrosProximos.length} logros cerca de completarse
          </p>
        </div>
        <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center">
          <Target className="w-8 h-8 text-white" />
        </div>
      </div>

      {/* Lista de logros - Vista ampliada */}
      <div className="space-y-4 mb-6">
        {logrosProximos.map((logro, idx) => (
          <motion.div
            key={logro.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            {/* Header */}
            <div className="flex items-start gap-4 mb-3">
              <div className="w-12 h-12 bg-white dark:bg-gray-800 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                <Lock className="w-6 h-6 text-gray-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-base font-bold text-gray-900 dark:text-white">
                    {logro.nombre}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-bold ${obtenerColorRareza(logro.rareza)} ${obtenerBgRareza(logro.rareza)}`}>
                    {logro.rareza}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {logro.descripcion}
                </p>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <Trophy className="w-4 h-4 text-violet-600 dark:text-violet-400" />
                    <span className="text-gray-700 dark:text-gray-300">
                      {logro.tipo}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span className="font-semibold text-yellow-600 dark:text-yellow-400">
                      {logro.puntos_recompensa} pts
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Progreso */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Progreso: {logro.progreso_actual} / {logro.objetivo}
                </span>
                <span className="text-sm font-bold text-green-600 dark:text-green-400">
                  {logro.porcentaje}%
                </span>
              </div>
              <div className="relative w-full h-3 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${logro.porcentaje}%` }}
                  transition={{ duration: 1, delay: idx * 0.1 }}
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-600 rounded-full"
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Link a página completa */}
      <Link
        to="/logros"
        className="block w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white text-center font-semibold rounded-xl hover:shadow-lg transition-all duration-300"
      >
        Ver todos los logros
      </Link>
    </motion.div>
  );
}
