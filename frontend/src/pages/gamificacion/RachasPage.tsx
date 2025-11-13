/**
 * Página de Rachas
 * 
 * @module pages/gamificacion/RachasPage
 * @description Página detallada del sistema de rachas con calendario completo
 */

import { motion } from 'framer-motion';
import { Flame, Calendar, TrendingUp, Award, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useRacha } from '../../hooks/useGamificacion';
import RachaTracker from '../../components/gamificacion/RachaTracker';

export default function RachasPage() {
  const { data: racha, isLoading, isError } = useRacha();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-8"></div>
            <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (isError || !racha) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-6">
            <p className="text-red-600 dark:text-red-400">Error al cargar información de rachas</p>
          </div>
        </div>
      </div>
    );
  }

  const isActiva = racha.activa;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header con navegación */}
        <div className="mb-8">
          <Link
            to="/gamificacion"
            className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Volver al Dashboard</span>
          </Link>

          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center">
              <Flame className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Sistema de Rachas
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Mantén tu racha activa estudiando cada día
              </p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Racha Actual */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-6 rounded-2xl ${
              isActiva
                ? 'bg-gradient-to-br from-orange-500 to-red-600'
                : 'bg-gray-200 dark:bg-gray-700'
            } text-white`}
          >
            <div className="flex items-center justify-between mb-4">
              <Calendar className="w-6 h-6" />
              {isActiva && (
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, 10, -10, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatDelay: 1,
                  }}
                >
                  <Flame className="w-6 h-6" />
                </motion.div>
              )}
            </div>
            <p className="text-sm opacity-90 mb-1">Racha Actual</p>
            <p className="text-4xl font-bold">{racha.dias_actuales}</p>
            <p className="text-sm opacity-90 mt-1">
              {racha.dias_actuales === 1 ? 'día' : 'días'}
            </p>
          </motion.div>

          {/* Mejor Racha */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-6 h-6" />
              <Award className="w-6 h-6" />
            </div>
            <p className="text-sm opacity-90 mb-1">Récord Personal</p>
            <p className="text-4xl font-bold">{racha.mejor_racha}</p>
            <p className="text-sm opacity-90 mt-1">
              {racha.mejor_racha === 1 ? 'día' : 'días'}
            </p>
          </motion.div>

          {/* Puntos por Día */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-6 rounded-2xl bg-gradient-to-br from-yellow-400 to-orange-500 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <Award className="w-6 h-6" />
            </div>
            <p className="text-sm opacity-90 mb-1">Puntos por Día</p>
            <p className="text-4xl font-bold">{racha.puntos_por_dia}</p>
            <p className="text-sm opacity-90 mt-1">puntos diarios</p>
          </motion.div>
        </div>

        {/* Información del sistema */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-8 mb-8"
        >
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            ¿Cómo funcionan las rachas?
          </h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-green-600 dark:text-green-400 font-bold">1</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  Inicia sesión cada día
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Ingresa a Acadify al menos una vez al día para mantener tu racha activa.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 dark:text-blue-400 font-bold">2</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  Gana puntos diarios
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Cada día que mantengas tu racha, ganarás {racha.puntos_por_dia} puntos de experiencia.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-orange-600 dark:text-orange-400 font-bold">3</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  Supera tu récord
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Intenta superar tu mejor racha de {racha.mejor_racha} días y desbloquea logros especiales.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Estado actual */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className={`rounded-2xl p-6 text-center mb-8 ${
            isActiva
              ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
              : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'
          }`}
        >
          {isActiva ? (
            <>
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <Flame className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-lg font-bold text-green-900 dark:text-green-100 mb-2">
                ¡Tu racha está activa! 🔥
              </h3>
              <p className="text-sm text-green-700 dark:text-green-300">
                Has iniciado sesión hoy. Vuelve mañana para continuar tu racha.
              </p>
            </>
          ) : (
            <>
              <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
              </div>
              <h3 className="text-lg font-bold text-yellow-900 dark:text-yellow-100 mb-2">
                Tu racha está inactiva
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                Inicia sesión hoy para comenzar una nueva racha.
              </p>
            </>
          )}
        </motion.div>

        {/* Calendario de Rachas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <RachaTracker />
        </motion.div>
      </div>
    </div>
  );
}
