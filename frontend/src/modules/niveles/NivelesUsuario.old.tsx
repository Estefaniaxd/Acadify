/**
 * Módulo de Niveles y Ranking
 * Visualización del ranking global y posición del usuario
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Trophy, TrendingUp, Medal, Crown, 
  ChevronUp, ChevronDown, Award, Users,
  Star, Target, Zap
} from 'lucide-react';
import { useRanking, useMiPosicionRanking } from '../../hooks/useGamificacion';
import { obtenerColorNivel, formatearPuntos } from '../../services/gamificacion.service';

// Iconos para el podio
const iconosPodio = {
  1: <Crown className="w-8 h-8 text-yellow-500" />,
  2: <Medal className="w-7 h-7 text-gray-400" />,
  3: <Medal className="w-6 h-6 text-orange-600" />,
};

export default function NivelesUsuario() {
  const [limite] = useState(50);
  const [offset] = useState(0);
  
  const { data: ranking, isLoading: isLoadingRanking, isError: isErrorRanking } = useRanking(limite, offset);
  const { data: miPosicion, isLoading: isLoadingPosicion, isError: isErrorPosicion } = useMiPosicionRanking();

  const isLoading = isLoadingRanking || isLoadingPosicion;
  const isError = isErrorRanking || isErrorPosicion;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando ranking...</p>
        </div>
      </div>
    );
  }

  if (isError || !ranking || !miPosicion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-red-600">Error al cargar el ranking</p>
        </div>
      </div>
    );
  }

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
            Ranking Global
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Compite con otros estudiantes y sube de nivel
          </p>
        </motion.div>

        {/* Mi Posición */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <span className="text-3xl font-bold">#{miPosicion.posicion}</span>
                </div>
                <div>
                  <p className="text-white/80 text-sm mb-1">Tu Posición</p>
                  <h2 className="text-3xl font-bold mb-1">{formatearPuntos(miPosicion.puntos)} puntos</h2>
                  <p className="text-white/90 font-medium">{miPosicion.nivel}</p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center gap-4 mb-2">
                  {miPosicion.puntos_hasta_anterior > 0 && (
                    <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg">
                      <ChevronUp className="w-4 h-4" />
                      <span className="text-sm font-semibold">
                        -{formatearPuntos(miPosicion.puntos_hasta_anterior)} pts
                      </span>
                    </div>
                  )}
                  {miPosicion.puntos_hasta_siguiente > 0 && (
                    <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg">
                      <ChevronDown className="w-4 h-4" />
                      <span className="text-sm font-semibold">
                        +{formatearPuntos(miPosicion.puntos_hasta_siguiente)} pts
                      </span>
                    </div>
                  )}
                </div>
                <p className="text-white/80 text-sm">
                  de {miPosicion.total_usuarios} estudiantes
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Podio Top 3 */}
        {ranking.usuarios.length >= 3 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <div className="grid grid-cols-3 gap-4 max-w-4xl mx-auto">
              {/* 2do Lugar */}
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex flex-col items-center pt-8"
              >
                <div className="relative mb-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-gray-300 to-gray-500 rounded-full flex items-center justify-center">
                    <span className="text-3xl">🥈</span>
                  </div>
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-10 h-10 bg-gray-500 rounded-full flex items-center justify-center text-white font-bold">
                    2
                  </div>
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white mb-1">
                  {ranking.usuarios[1].nombre} {ranking.usuarios[1].apellido}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {ranking.usuarios[1].nivel}
                </p>
                <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Star className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                  <span className="font-bold text-yellow-700 dark:text-yellow-300">
                    {formatearPuntos(ranking.usuarios[1].puntos)}
                  </span>
                </div>
              </motion.div>

              {/* 1er Lugar */}
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="flex flex-col items-center"
              >
                <div className="relative mb-4">
                  <div className="w-28 h-28 bg-gradient-to-br from-yellow-300 to-yellow-600 rounded-full flex items-center justify-center shadow-lg">
                    <span className="text-5xl">👑</span>
                  </div>
                  <div className="absolute -bottom-3 left-1/2 transform -translate-x-1/2 w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    1
                  </div>
                </div>
                <h3 className="font-bold text-xl text-gray-900 dark:text-white mb-1">
                  {ranking.usuarios[0].nombre} {ranking.usuarios[0].apellido}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {ranking.usuarios[0].nivel}
                </p>
                <div className="flex items-center gap-1 px-4 py-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Star className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                  <span className="font-bold text-lg text-yellow-700 dark:text-yellow-300">
                    {formatearPuntos(ranking.usuarios[0].puntos)}
                  </span>
                </div>
              </motion.div>

              {/* 3er Lugar */}
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex flex-col items-center pt-12"
              >
                <div className="relative mb-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-orange-400 to-orange-700 rounded-full flex items-center justify-center">
                    <span className="text-3xl">🥉</span>
                  </div>
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-10 h-10 bg-orange-600 rounded-full flex items-center justify-center text-white font-bold">
                    3
                  </div>
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white mb-1">
                  {ranking.usuarios[2].nombre} {ranking.usuarios[2].apellido}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {ranking.usuarios[2].nivel}
                </p>
                <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Star className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                  <span className="font-bold text-yellow-700 dark:text-yellow-300">
                    {formatearPuntos(ranking.usuarios[2].puntos)}
                  </span>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}

        {/* Lista del Ranking */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Users className="w-6 h-6 text-violet-600" />
                Ranking Completo
              </h2>
            </div>

            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {ranking.usuarios.slice(3).map((usuario, idx) => {
                const posicion = idx + 4; // +4 porque los primeros 3 están en el podio
                
                return (
                  <motion.div
                    key={usuario.usuario_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.05 * idx }}
                    className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 rounded-xl flex items-center justify-center">
                        <span className="font-bold text-gray-700 dark:text-gray-300">
                          #{posicion}
                        </span>
                      </div>

                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {usuario.nombre} {usuario.apellido}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {usuario.nivel}
                        </p>
                      </div>

                      <div className="flex items-center gap-4">
                        {usuario.insignias_count > 0 && (
                          <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900 rounded-lg">
                            <Award className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                            <span className="text-sm font-semibold text-purple-700 dark:text-purple-300">
                              {usuario.insignias_count}
                            </span>
                          </div>
                        )}

                        <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                          <Star className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                          <span className="font-bold text-yellow-700 dark:text-yellow-300">
                            {formatearPuntos(usuario.puntos)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
