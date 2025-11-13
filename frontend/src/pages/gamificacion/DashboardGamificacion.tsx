/**
 * Dashboard Unificado de Gamificación
 * 
 * @module pages/gamificacion/DashboardGamificacion
 * @description Página principal que integra todos los widgets de gamificación
 */

import { motion } from 'framer-motion';
import { Trophy, Sparkles, ArrowRight, Store, Target, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';
import { 
  PuntosWidget, 
  RachaWidget, 
  RankingWidget, 
  LogrosProximosWidget, 
  EstadisticasWidget 
} from '../../components/gamificacion/widgets';
import { useResumenGamificacion } from '../../hooks/useGamificacion';

export default function DashboardGamificacion() {
  const { data: resumen, isLoading } = useResumenGamificacion();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header Hero */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 rounded-3xl p-8 shadow-2xl overflow-hidden relative">
            {/* Decoración de fondo */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
            
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <Trophy className="w-7 h-7 text-white" />
                </div>
                <h1 className="text-3xl md:text-4xl font-bold text-white">
                  Dashboard de Gamificación
                </h1>
              </div>
              
              {isLoading ? (
                <div className="animate-pulse">
                  <div className="h-6 bg-white/20 rounded w-64 mb-2"></div>
                  <div className="h-4 bg-white/20 rounded w-48"></div>
                </div>
              ) : resumen ? (
                <div className="text-white/90">
                  <p className="text-lg mb-2">
                    ¡Sigue adelante! Estás en el nivel{' '}
                    <span className="font-bold text-white">{resumen.puntos?.nivel || 'Novato'}</span>
                    {resumen.ranking && (
                      <> y ocupas el puesto{' '}
                        <span className="font-bold text-white">#{resumen.ranking.posicion}</span>
                      </>
                    )}
                  </p>
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-yellow-300" />
                    <p className="text-sm text-white/80">
                      {resumen.logros?.completados || 0} logros desbloqueados • {' '}
                      {resumen.racha?.activa ? (
                        <span className="font-semibold text-orange-300">
                          🔥 Racha de {resumen.racha.dias_actuales} días activa
                        </span>
                      ) : (
                        <span>Racha inactiva</span>
                      )}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-white/90">
                  Comienza tu aventura de aprendizaje gamificado
                </p>
              )}
            </div>
          </div>
        </motion.div>

        {/* Grid principal de widgets */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          
          {/* Columna izquierda - 2 widgets */}
          <div className="lg:col-span-1 space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
            >
              <PuntosWidget variant="compact" />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <RachaWidget variant="compact" showMiniCalendar={true} />
            </motion.div>
          </div>

          {/* Columna central - Widget grande de ranking */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="h-full"
            >
              <RankingWidget variant="compact" topCount={5} className="h-full" />
            </motion.div>
          </div>

          {/* Columna derecha - 2 widgets */}
          <div className="lg:col-span-1 space-y-6">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.25 }}
            >
              <LogrosProximosWidget variant="compact" count={3} />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <EstadisticasWidget variant="compact" />
            </motion.div>
          </div>
        </div>

        {/* Sección de acciones rápidas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Target className="w-6 h-6 text-violet-600 dark:text-violet-400" />
            Acciones Rápidas
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Card: Ver todos los logros */}
            <Link
              to="/logros"
              className="group p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Trophy className="w-6 h-6 text-white" />
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                Ver Todos los Logros
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Explora todos los desafíos disponibles
              </p>
            </Link>

            {/* Card: Ir a la tienda */}
            <Link
              to="/tienda"
              className="group p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:border-yellow-500 dark:hover:border-yellow-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Store className="w-6 h-6 text-white" />
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-yellow-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                Tienda de Puntos
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Canjea tus puntos por recompensas
              </p>
            </Link>

            {/* Card: Ver ranking completo */}
            <Link
              to="/niveles"
              className="group p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:border-violet-500 dark:hover:border-violet-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Trophy className="w-6 h-6 text-white" />
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-violet-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                Ranking Completo
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Mira tu posición en el top global
              </p>
            </Link>
          </div>
        </motion.div>

        {/* Sistema de Misiones */}
        <Link to="/misiones">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-r from-indigo-100 to-purple-100 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-2xl p-8 border border-indigo-200 dark:border-indigo-800 hover:shadow-2xl hover:border-indigo-400 dark:hover:border-indigo-600 transition-all cursor-pointer"
          >
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <Target className="w-7 h-7 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                    Sistema de Misiones
                  </h3>
                  <span className="px-2 py-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs font-bold rounded-full">
                    NUEVO
                  </span>
                </div>
                <p className="text-gray-700 dark:text-gray-300 mb-3">
                  Completa misiones diarias, semanales y mensuales para ganar puntos extra,
                  experiencia y desbloquear recompensas exclusivas.
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-white/50 dark:bg-gray-800/50 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300">
                    🎯 Misiones Diarias
                  </span>
                  <span className="px-3 py-1 bg-white/50 dark:bg-gray-800/50 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300">
                    📅 Desafíos Semanales
                  </span>
                  <span className="px-3 py-1 bg-white/50 dark:bg-gray-800/50 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300">
                    🏆 Recompensas Especiales
                  </span>
                  <span className="px-3 py-1 bg-white/50 dark:bg-gray-800/50 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300">
                    ⚡ Experiencia Extra
                  </span>
                </div>
              </div>
              <ArrowRight className="w-6 h-6 text-indigo-600 dark:text-indigo-400 flex-shrink-0 group-hover:translate-x-1 transition-transform" />
            </div>
          </motion.div>
        </Link>

      </div>
    </div>
  );
}
