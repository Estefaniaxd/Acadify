/**
 * Módulo de Logros del Usuario
 * Visualización de logros completados y en progreso
 */

import { motion } from 'framer-motion';
import { 
  Trophy, Target, Star, Lock, Check,
  TrendingUp, Users, BookOpen, Zap, Heart
} from 'lucide-react';
import { useMisLogros } from '../../hooks/useGamificacion';
import { obtenerColorRareza, obtenerBgRareza } from '../../services/gamificacion.service';

// Iconos por tipo de logro
const iconosPorTipo: Record<string, any> = {
  tarea: BookOpen,
  participacion: Users,
  racha: Zap,
  examen: Target,
  social: Heart,
};

export default function LogrosUsuario() {
  const { data: logros, isLoading, isError } = useMisLogros();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando logros...</p>
        </div>
      </div>
    );
  }

  if (isError || !logros) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-red-600">Error al cargar los logros</p>
        </div>
      </div>
    );
  }

  const logrosCompletados = logros.filter(l => l.completado);
  const logrosEnProgreso = logros.filter(l => !l.completado);
  const porcentajeCompletado = logros.length > 0 
    ? Math.round((logrosCompletados.length / logros.length) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
            <Trophy className="w-10 h-10 text-yellow-500" />
            Mis Logros
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Desbloquea logros completando actividades y desafíos
          </p>
        </motion.div>

        {/* Estadísticas Generales */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Logros Completados
                </p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {logrosCompletados.length}
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Check className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  En Progreso
                </p>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {logrosEnProgreso.length}
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Progreso Total
                </p>
                <p className="text-3xl font-bold text-violet-600 dark:text-violet-400">
                  {porcentajeCompletado}%
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Star className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Tabs: Todos / Completados / En Progreso */}
        <div className="mb-6">
          <div className="flex gap-4 border-b border-gray-200 dark:border-gray-700">
            <button className="px-6 py-3 font-semibold text-violet-600 dark:text-violet-400 border-b-2 border-violet-600 dark:border-violet-400">
              Todos ({logros.length})
            </button>
            <button className="px-6 py-3 font-semibold text-gray-600 dark:text-gray-400 hover:text-violet-600 dark:hover:text-violet-400 transition-colors">
              Completados ({logrosCompletados.length})
            </button>
            <button className="px-6 py-3 font-semibold text-gray-600 dark:text-gray-400 hover:text-violet-600 dark:hover:text-violet-400 transition-colors">
              En Progreso ({logrosEnProgreso.length})
            </button>
          </div>
        </div>

        {/* Grid de Logros */}
        {logros.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {logros.map((logro, idx) => {
              const IconoTipo = iconosPorTipo[logro.tipo] || Target;
              const progresoPorcentaje = logro.objetivo > 0 
                ? Math.min(100, Math.round((logro.progreso_actual / logro.objetivo) * 100))
                : 0;

              return (
                <motion.div
                  key={logro.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.05 * idx }}
                  whileHover={{ scale: 1.02 }}
                  className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border-2 transition-all duration-300 ${
                    logro.completado
                      ? 'border-green-500 dark:border-green-600'
                      : 'border-gray-200 dark:border-gray-700'
                  }`}
                >
                  {/* Badge de completado */}
                  {logro.completado && (
                    <div className="absolute -top-3 -right-3 w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                      <Check className="w-6 h-6 text-white" />
                    </div>
                  )}

                  {/* Badge de rareza */}
                  <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold ${obtenerColorRareza(logro.rareza)} ${obtenerBgRareza(logro.rareza)}`}>
                    {logro.rareza}
                  </div>

                  {/* Icono del logro */}
                  <div className={`w-20 h-20 mb-4 rounded-2xl flex items-center justify-center ${
                    logro.completado
                      ? 'bg-gradient-to-br from-violet-500 to-purple-600'
                      : 'bg-gray-100 dark:bg-gray-700'
                  }`}>
                    {logro.completado ? (
                      <span className="text-4xl">{logro.icono}</span>
                    ) : (
                      <Lock className="w-10 h-10 text-gray-400" />
                    )}
                  </div>

                  {/* Título y descripción */}
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {logro.nombre}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {logro.descripcion}
                  </p>

                  {/* Progreso */}
                  {!logro.completado && (
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Progreso
                        </span>
                        <span className="text-sm font-bold text-violet-600 dark:text-violet-400">
                          {logro.progreso_actual} / {logro.objetivo}
                        </span>
                      </div>
                      <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${progresoPorcentaje}%` }}
                          transition={{ duration: 1, ease: 'easeOut' }}
                          className="h-full bg-gradient-to-r from-violet-500 to-purple-600 rounded-full"
                        />
                      </div>
                    </div>
                  )}

                  {/* Footer: Tipo y Puntos */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-2">
                      <IconoTipo className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {logro.tipo}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                      <Star className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                      <span className="text-sm font-bold text-yellow-700 dark:text-yellow-300">
                        {logro.puntos_recompensa} pts
                      </span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <Trophy className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
              No hay logros disponibles
            </h3>
            <p className="text-gray-500 dark:text-gray-500">
              ¡Comienza a participar para desbloquear logros!
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
