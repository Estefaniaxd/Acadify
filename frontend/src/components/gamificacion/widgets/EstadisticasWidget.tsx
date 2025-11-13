/**
 * Widget de Estadísticas Generales
 * 
 * @module components/gamificacion/widgets/EstadisticasWidget
 * @description Widget reutilizable que muestra métricas clave de gamificación
 */

import { motion } from 'framer-motion';
import { TrendingUp, Trophy, Award, Flame, Star, Target } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useResumenGamificacion } from '../../../hooks/useGamificacion';
import { formatearPuntos } from '../../../services/gamificacion.service';

interface EstadisticasWidgetProps {
  className?: string;
  variant?: 'compact' | 'full';
}

export default function EstadisticasWidget({ 
  className = '', 
  variant = 'compact' 
}: EstadisticasWidgetProps) {
  const { puntos, posicion, racha, isLoading } = useResumenGamificacion();
  const { data: logros } = useMisLogros();
  const { data: insignias } = useMisInsignias();

  if (isLoading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4"></div>
          <div className="grid grid-cols-2 gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i}>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-2"></div>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!puntos && !posicion && !racha) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="text-sm">Error al cargar estadísticas</p>
        </div>
      </div>
    );
  }

  const logrosCompletados = logros?.filter(l => l.completado).length || 0;
  const insigniasDesbloqueadas = insignias?.filter(i => i.desbloqueada).length || 0;

  const estadisticas = [
    {
      icon: Star,
      label: 'Total Puntos',
      value: formatearPuntos(puntos?.total || 0),
      color: 'from-yellow-400 to-orange-500',
      bgColor: 'bg-yellow-100 dark:bg-yellow-900',
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      link: '/puntos'
    },
    {
      icon: Trophy,
      label: 'Logros',
      value: `${data.logros?.completados || 0}/${data.logros?.total || 0}`,
      color: 'from-green-400 to-emerald-500',
      bgColor: 'bg-green-100 dark:bg-green-900',
      iconColor: 'text-green-600 dark:text-green-400',
      link: '/logros'
    },
    {
      icon: TrendingUp,
      label: 'Ranking',
      value: `#${data.ranking?.posicion || '-'}`,
      color: 'from-violet-400 to-purple-500',
      bgColor: 'bg-violet-100 dark:bg-violet-900',
      iconColor: 'text-violet-600 dark:text-violet-400',
      link: '/niveles'
    },
    {
      icon: Flame,
      label: 'Racha',
      value: `${data.racha?.dias_actuales || 0} días`,
      color: 'from-orange-400 to-red-500',
      bgColor: 'bg-orange-100 dark:bg-orange-900',
      iconColor: 'text-orange-600 dark:text-orange-400',
      link: '/rachas'
    }
  ];

  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -4, scale: 1.02 }}
        className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${className}`}
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
              Resumen General
            </h3>
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
          </div>

          {/* Grid de estadísticas - 2x2 */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {estadisticas.map((stat, idx) => {
              const IconComponent = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`w-8 h-8 ${stat.bgColor} rounded-lg flex items-center justify-center`}>
                      <IconComponent className={`w-4 h-4 ${stat.iconColor}`} />
                    </div>
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                    {stat.label}
                  </p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                </motion.div>
              );
            })}
          </div>

          {/* Footer */}
          <Link
            to="/gamificacion"
            className="block w-full py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-center text-sm font-semibold rounded-lg hover:shadow-lg transition-all duration-300"
          >
            Ver dashboard completo
          </Link>
        </div>
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
            Estadísticas Generales
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Resumen de tu progreso
          </p>
        </div>
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center">
          <Target className="w-8 h-8 text-white" />
        </div>
      </div>

      {/* Grid de estadísticas - 2x2 expandido */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {estadisticas.map((stat, idx) => {
          const IconComponent = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <Link
                to={stat.link}
                className="block p-6 rounded-xl bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-all duration-300"
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-14 h-14 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center shadow-lg`}>
                    <IconComponent className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      {stat.label}
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {stat.value}
                    </p>
                  </div>
                </div>

                {/* Info adicional según la estadística */}
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {stat.label === 'Total Puntos' && data.puntos && (
                    <div className="flex items-center justify-between">
                      <span>Nivel: {data.puntos.nivel}</span>
                      <span className="font-semibold text-violet-600 dark:text-violet-400">
                        {data.puntos.progreso_porcentaje}%
                      </span>
                    </div>
                  )}
                  {stat.label === 'Logros' && data.logros && (
                    <div className="flex items-center justify-between">
                      <span>En progreso: {data.logros.en_progreso}</span>
                      <span className="font-semibold text-green-600 dark:text-green-400">
                        {Math.round((data.logros.completados / data.logros.total) * 100)}% completado
                      </span>
                    </div>
                  )}
                  {stat.label === 'Ranking' && data.ranking && (
                    <div className="flex items-center justify-between">
                      <span>de {data.ranking.total_usuarios} usuarios</span>
                      <span className="font-semibold text-violet-600 dark:text-violet-400">
                        Top {Math.round((data.ranking.posicion / data.ranking.total_usuarios) * 100)}%
                      </span>
                    </div>
                  )}
                  {stat.label === 'Racha' && data.racha && (
                    <div className="flex items-center justify-between">
                      <span>Récord: {data.racha.mejor_racha} días</span>
                      {data.racha.activa ? (
                        <span className="font-semibold text-orange-600 dark:text-orange-400">
                          🔥 ¡Activa!
                        </span>
                      ) : (
                        <span className="text-gray-400">Inactiva</span>
                      )}
                    </div>
                  )}
                </div>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {/* Sección de insignias */}
      {data.insignias && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center">
                <Award className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                  Insignias Desbloqueadas
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {data.insignias.desbloqueadas} de {data.insignias.total} insignias obtenidas
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {data.insignias.desbloqueadas}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {Math.round((data.insignias.desbloqueadas / data.insignias.total) * 100)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Link al dashboard */}
      <Link
        to="/gamificacion"
        className="block w-full py-3 mt-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-center font-semibold rounded-xl hover:shadow-lg transition-all duration-300"
      >
        Ver dashboard completo
      </Link>
    </motion.div>
  );
}
