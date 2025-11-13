/**
 * Widget Compacto de Ranking
 * 
 * @module components/gamificacion/widgets/RankingWidget
 * @description Widget reutilizable que muestra el top del ranking y posición del usuario
 */

import { motion } from 'framer-motion';
import { Trophy, Crown, Medal, ArrowUp, ArrowDown, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useRanking, useMiPosicionRanking } from '../../../hooks/useGamificacion';
import { formatearPuntos } from '../../../services/gamificacion.service';

interface RankingWidgetProps {
  className?: string;
  topCount?: number;
  variant?: 'compact' | 'full';
}

export default function RankingWidget({ 
  className = '', 
  topCount = 5,
  variant = 'compact' 
}: RankingWidgetProps) {
  const { data: ranking, isLoading: isLoadingRanking } = useRanking(topCount, 0);
  const { data: miPosicion, isLoading: isLoadingPosicion } = useMiPosicionRanking();

  const isLoading = isLoadingRanking || isLoadingPosicion;

  if (isLoading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-4"></div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              <div className="flex-1">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!ranking || !miPosicion) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="text-sm">Error al cargar ranking</p>
        </div>
      </div>
    );
  }

  const topUsuarios = ranking.usuarios.slice(0, topCount);
  
  // Iconos de posición
  const getPosicionIcon = (posicion: number) => {
    if (posicion === 1) return <Crown className="w-4 h-4 text-yellow-500" />;
    if (posicion === 2) return <Medal className="w-4 h-4 text-gray-400" />;
    if (posicion === 3) return <Medal className="w-4 h-4 text-orange-600" />;
    return <span className="text-xs font-bold text-gray-500">#{posicion}</span>;
  };

  const getPosicionColor = (posicion: number) => {
    if (posicion === 1) return 'from-yellow-400 to-orange-500';
    if (posicion === 2) return 'from-gray-300 to-gray-500';
    if (posicion === 3) return 'from-orange-400 to-red-600';
    return 'from-gray-200 to-gray-300';
  };

  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -4, scale: 1.02 }}
        className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden ${className}`}
      >
        <Link to="/niveles" className="block p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
              Ranking Global
            </h3>
            <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Trophy className="w-5 h-5 text-white" />
            </div>
          </div>

          {/* Mi posición destacada */}
          <div className="mb-4 p-3 bg-gradient-to-r from-violet-500 to-purple-600 rounded-xl">
            <div className="flex items-center justify-between text-white">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  <span className="text-sm font-bold">#{miPosicion.posicion}</span>
                </div>
                <div>
                  <p className="text-xs opacity-80">Tu posición</p>
                  <p className="text-sm font-bold">{formatearPuntos(miPosicion.puntos)} pts</p>
                </div>
              </div>
              {miPosicion.puntos_hasta_anterior > 0 && (
                <div className="flex items-center gap-1 text-xs bg-white/20 px-2 py-1 rounded-lg">
                  <ArrowUp className="w-3 h-3" />
                  <span>{formatearPuntos(miPosicion.puntos_hasta_anterior)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Top usuarios */}
          <div className="space-y-2 mb-4">
            {topUsuarios.map((usuario, idx) => (
              <motion.div
                key={usuario.usuario_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className={`w-8 h-8 bg-gradient-to-br ${getPosicionColor(usuario.posicion)} rounded-lg flex items-center justify-center`}>
                  {getPosicionIcon(usuario.posicion)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                    {usuario.nombre} {usuario.apellido}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatearPuntos(usuario.puntos)} pts
                  </p>
                </div>
                {usuario.insignias_count > 0 && (
                  <div className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 rounded text-xs font-semibold text-yellow-700 dark:text-yellow-300">
                    {usuario.insignias_count}
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* Footer */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Ver ranking completo →
            </span>
            <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
              <Users className="w-3 h-3" />
              <span>{miPosicion.total_usuarios}</span>
            </div>
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
            Ranking Global
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Top {topCount} estudiantes
          </p>
        </div>
        <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center">
          <Trophy className="w-8 h-8 text-white" />
        </div>
      </div>

      {/* Mi posición - Card grande */}
      <div className="mb-6 p-6 bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl text-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <span className="text-2xl font-bold">#{miPosicion.posicion}</span>
            </div>
            <div>
              <p className="text-white/80 text-sm mb-1">Tu Posición</p>
              <h3 className="text-2xl font-bold">{formatearPuntos(miPosicion.puntos)} puntos</h3>
              <p className="text-white/90 text-sm">{miPosicion.nivel}</p>
            </div>
          </div>
          
          <div className="text-right">
            {miPosicion.puntos_hasta_anterior > 0 && (
              <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg mb-2">
                <ArrowUp className="w-4 h-4" />
                <span className="text-sm font-semibold">
                  -{formatearPuntos(miPosicion.puntos_hasta_anterior)} pts
                </span>
              </div>
            )}
            {miPosicion.puntos_hasta_siguiente > 0 && (
              <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg">
                <ArrowDown className="w-4 h-4" />
                <span className="text-sm font-semibold">
                  +{formatearPuntos(miPosicion.puntos_hasta_siguiente)} pts
                </span>
              </div>
            )}
          </div>
        </div>
        <p className="text-white/80 text-sm">
          de {miPosicion.total_usuarios} estudiantes
        </p>
      </div>

      {/* Lista del top */}
      <div className="space-y-3 mb-6">
        {topUsuarios.map((usuario, idx) => (
          <motion.div
            key={usuario.usuario_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center gap-4 p-4 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div className={`w-12 h-12 bg-gradient-to-br ${getPosicionColor(usuario.posicion)} rounded-xl flex items-center justify-center shadow-lg`}>
              {usuario.posicion <= 3 ? (
                getPosicionIcon(usuario.posicion)
              ) : (
                <span className="text-sm font-bold text-gray-700">#{usuario.posicion}</span>
              )}
            </div>

            <div className="flex-1">
              <p className="text-base font-semibold text-gray-900 dark:text-white">
                {usuario.nombre} {usuario.apellido}
              </p>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <span>{usuario.nivel}</span>
                {usuario.insignias_count > 0 && (
                  <>
                    <span>•</span>
                    <div className="flex items-center gap-1">
                      <Trophy className="w-3 h-3" />
                      <span>{usuario.insignias_count} insignias</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="text-right">
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {formatearPuntos(usuario.puntos)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                puntos
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Link a página completa */}
      <Link
        to="/niveles"
        className="block w-full py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white text-center font-semibold rounded-xl hover:shadow-lg transition-all duration-300"
      >
        Ver ranking completo
      </Link>
    </motion.div>
  );
}
