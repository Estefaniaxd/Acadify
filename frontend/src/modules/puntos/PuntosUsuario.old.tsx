/**
 * Módulo de Puntos del Usuario
 * Visualización completa de puntos, nivel, progreso y historial
 */

import { motion } from 'framer-motion';
import { 
  Star, TrendingUp, Award, Zap, 
  ChevronRight, ArrowUp, ArrowDown, 
  Trophy, Target, Clock
} from 'lucide-react';
import { useMisPuntos } from '../../hooks/useGamificacion';
import { obtenerColorNivel, formatearPuntos } from '../../services/gamificacion.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function PuntosUsuario() {
  const { data: puntos, isLoading, isError } = useMisPuntos();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando puntos...</p>
        </div>
      </div>
    );
  }

  if (isError || !puntos) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-red-600">Error al cargar los puntos</p>
        </div>
      </div>
    );
  }

  const { puntos_acumulados, nivel_actual, nivel_info, historial_reciente, insignias_obtenidas } = puntos;

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
            <Star className="w-10 h-10 text-yellow-500" />
            Mis Puntos
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Consulta tus puntos acumulados, nivel actual y progreso
          </p>
        </motion.div>

        {/* Grid principal */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Card de Puntos Totales */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="lg:col-span-1"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Puntos Totales
                </h2>
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                  <Star className="w-6 h-6 text-white" />
                </div>
              </div>
              <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-orange-600 mb-2">
                {formatearPuntos(puntos_acumulados)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Puntos acumulados
              </p>
            </div>
          </motion.div>

          {/* Card de Nivel Actual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-16 h-16 bg-gradient-to-br ${obtenerColorNivel(nivel_actual)} rounded-xl flex items-center justify-center`}>
                    <Trophy className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {nivel_info.nombre}
                    </h2>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Nivel {nivel_info.numero}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Progreso al siguiente nivel
                  </p>
                  <p className="text-2xl font-bold text-violet-600 dark:text-violet-400">
                    {nivel_info.progreso_porcentaje}%
                  </p>
                </div>
              </div>

              {/* Barra de progreso */}
              <div className="relative w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${nivel_info.progreso_porcentaje}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-full bg-gradient-to-r ${obtenerColorNivel(nivel_actual)} rounded-full`}
                />
              </div>

              <div className="flex items-center justify-between mt-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {formatearPuntos(nivel_info.puntos_minimos)} pts
                </p>
                <p className="text-sm font-semibold text-violet-600 dark:text-violet-400">
                  {formatearPuntos(nivel_info.puntos_para_siguiente)} pts para subir
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {formatearPuntos(nivel_info.puntos_maximos)} pts
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Grid secundario: Insignias e Historial */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Insignias Recientes */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <Award className="w-6 h-6 text-violet-600" />
                  Insignias Recientes
                </h2>
                <span className="px-3 py-1 bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300 rounded-full text-sm font-semibold">
                  {insignias_obtenidas.length} total
                </span>
              </div>

              {insignias_obtenidas.length > 0 ? (
                <div className="space-y-3">
                  {insignias_obtenidas.slice(0, 5).map((insignia, idx) => (
                    <motion.div
                      key={insignia.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx }}
                      className="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                    >
                      <div className="text-3xl">{insignia.icono}</div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {insignia.nombre}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {insignia.descripcion}
                        </p>
                      </div>
                      <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 rounded-lg text-xs font-semibold">
                        {insignia.rareza}
                      </span>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Award className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Aún no has obtenido insignias
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                    ¡Completa actividades para desbloquearlas!
                  </p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Historial Reciente */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <Clock className="w-6 h-6 text-blue-600" />
                  Actividad Reciente
                </h2>
              </div>

              {historial_reciente.length > 0 ? (
                <div className="space-y-3">
                  {historial_reciente.map((cambio, idx) => (
                    <motion.div
                      key={cambio.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx }}
                      className="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        cambio.tipo === 'ganado' 
                          ? 'bg-green-100 dark:bg-green-900' 
                          : 'bg-red-100 dark:bg-red-900'
                      }`}>
                        {cambio.tipo === 'ganado' ? (
                          <ArrowUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                        ) : (
                          <ArrowDown className="w-5 h-5 text-red-600 dark:text-red-400" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {cambio.tipo === 'ganado' ? '+' : '-'}{formatearPuntos(Math.abs(cambio.puntos))} pts
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {cambio.razon}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {format(new Date(cambio.fecha), "d 'de' MMMM, HH:mm", { locale: es })}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                    <TrendingUp className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    No hay actividad reciente
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
