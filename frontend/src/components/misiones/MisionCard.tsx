/**
 * MisionCard Component
 * 
 * @module components/misiones/MisionCard
 * @description Tarjeta visual para mostrar una misión individual con progreso,
 * dificultad, tiempo restante y botones de acción.
 */

import { motion } from 'framer-motion';
import { 
  Clock, 
  Trophy, 
  Zap, 
  CheckCircle, 
  Lock,
  Target,
  TrendingUp,
  Calendar,
  Flame
} from 'lucide-react';
import { MisionUsuarioConDetalle } from '../../services/misiones.service';
import {
  obtenerColorDificultad,
  obtenerBgDificultad,
  obtenerColorEstado,
  obtenerTextoEstado,
  obtenerIconoTipo,
  calcularPorcentajeProgreso,
  formatearTiempoRestante,
  MisionUsuarioConDetalle,
} from '../../services/misiones.service';

interface MisionCardProps {
  mision: MisionUsuarioConDetalle;
  onReclamar?: (misionUsuarioId: string) => void;
  onProgreso?: (misionUsuarioId: string) => void;
  variant?: 'default' | 'compact' | 'featured';
  isLoading?: boolean;
}

/**
 * Componente para mostrar una tarjeta de misión
 */
export default function MisionCard({
  mision,
  onReclamar,
  onProgreso,
  variant = 'default',
  isLoading = false,
}: MisionCardProps) {
  const porcentajeProgreso = calcularPorcentajeProgreso(
    mision.progreso_actual,
    mision.mision.objetivo
  );
  const tiempoRestante = mision.fecha_expiracion
    ? formatearTiempoRestante(mision.fecha_expiracion)
    : null;

  const isCompletada = mision.estado === 'completada';
  const isReclamada = mision.estado === 'reclamada';
  const isExpirada = mision.estado === 'expirada';
  const isBloqueada = mision.estado === 'bloqueada';
  const puedeReclamar = isCompletada && !isReclamada;

  // Variantes de tamaño
  const sizes = {
    default: 'p-6',
    compact: 'p-4',
    featured: 'p-8',
  };

  const iconSizes = {
    default: 'h-12 w-12',
    compact: 'h-8 w-8',
    featured: 'h-16 w-16',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={!isBloqueada && !isExpirada ? { y: -4, scale: 1.02 } : {}}
      transition={{ duration: 0.2 }}
      className={`
        relative overflow-hidden rounded-xl border-2 bg-white shadow-lg
        ${isBloqueada || isExpirada ? 'opacity-60 grayscale' : ''}
        ${isReclamada ? 'border-green-300 bg-green-50' : 'border-gray-200'}
        ${puedeReclamar ? 'border-yellow-400 shadow-yellow-100' : ''}
        ${sizes[variant]}
      `}
    >
      {/* Badge de dificultad */}
      <div className="absolute top-3 right-3 flex items-center gap-2">
        {/* Tiempo restante */}
        {tiempoRestante && !isReclamada && (
          <span className="flex items-center gap-1 rounded-full bg-orange-100 px-2 py-1 text-xs font-medium text-orange-700">
            <Clock className="h-3 w-3" />
            {tiempoRestante}
          </span>
        )}

        {/* Dificultad */}
        <span
          className={`
            rounded-full px-3 py-1 text-xs font-bold uppercase
            ${obtenerBgDificultad(mision.mision.dificultad)}
            ${obtenerColorDificultad(mision.mision.dificultad)}
          `}
        >
          {mision.mision.dificultad}
        </span>
      </div>

      {/* Icono de estado (bloqueada/completada) */}
      {(isBloqueada || isReclamada) && (
        <div className="absolute top-3 left-3">
          {isBloqueada && <Lock className="h-5 w-5 text-gray-400" />}
          {isReclamada && <CheckCircle className="h-5 w-5 text-green-500" />}
        </div>
      )}

      {/* Header - Icono y Título */}
      <div className="mb-4 flex items-start gap-4">
        <div
          className={`
            flex items-center justify-center rounded-full
            ${obtenerBgDificultad(mision.mision.dificultad)}
            ${iconSizes[variant]}
          `}
        >
          <span
            className={`
              ${variant === 'compact' ? 'text-base' : variant === 'featured' ? 'text-3xl' : 'text-2xl'}
            `}
          >
            {obtenerIconoTipo(mision.mision.tipo)}
          </span>
        </div>

        <div className="flex-1 min-w-0">
          <h3
            className={`
              font-bold text-gray-900 line-clamp-2
              ${variant === 'compact' ? 'text-sm' : variant === 'featured' ? 'text-2xl' : 'text-lg'}
            `}
          >
            {mision.mision.nombre}
          </h3>
          <p
            className={`
              mt-1 text-gray-600 line-clamp-2
              ${variant === 'compact' ? 'text-xs' : 'text-sm'}
            `}
          >
            {mision.mision.descripcion}
          </p>
        </div>
      </div>

      {/* Progreso */}
      {!isReclamada && !isBloqueada && (
        <div className="mb-4">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="flex items-center gap-1 text-gray-600">
              <Target className="h-4 w-4" />
              Progreso
            </span>
            <span className="font-bold text-gray-900">
              {mision.progreso_actual} / {mision.mision.objetivo} {mision.mision.unidad}
            </span>
          </div>

          {/* Barra de progreso */}
          <div className="relative h-3 overflow-hidden rounded-full bg-gray-200">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${porcentajeProgreso}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={`
                h-full rounded-full
                ${isCompletada ? 'bg-gradient-to-r from-green-400 to-green-600' : 'bg-gradient-to-r from-blue-400 to-blue-600'}
              `}
            />
            
            {/* Efecto de brillo */}
            {porcentajeProgreso > 0 && (
              <motion.div
                initial={{ x: '-100%' }}
                animate={{ x: '200%' }}
                transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 2 }}
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
              />
            )}
          </div>

          <div className="mt-1 text-right text-xs font-medium text-gray-500">
            {porcentajeProgreso.toFixed(0)}%
          </div>
        </div>
      )}

      {/* Recompensas */}
      <div className="mb-4 flex flex-wrap gap-3">
        {mision.mision.puntos_recompensa > 0 && (
          <div className="flex items-center gap-1.5 rounded-lg bg-amber-50 px-3 py-1.5 border border-amber-200">
            <Trophy className="h-4 w-4 text-amber-600" />
            <span className="text-sm font-bold text-amber-900">
              +{mision.mision.puntos_recompensa}
            </span>
            <span className="text-xs text-amber-700">pts</span>
          </div>
        )}

        {mision.mision.experiencia_recompensa > 0 && (
          <div className="flex items-center gap-1.5 rounded-lg bg-purple-50 px-3 py-1.5 border border-purple-200">
            <Zap className="h-4 w-4 text-purple-600" />
            <span className="text-sm font-bold text-purple-900">
              +{mision.mision.experiencia_recompensa}
            </span>
            <span className="text-xs text-purple-700">XP</span>
          </div>
        )}

        {mision.mision.frecuencia && (
          <div className="flex items-center gap-1.5 rounded-lg bg-blue-50 px-3 py-1.5 border border-blue-200">
            {mision.mision.frecuencia === 'diaria' ? (
              <Flame className="h-4 w-4 text-blue-600" />
            ) : (
              <Calendar className="h-4 w-4 text-blue-600" />
            )}
            <span className="text-xs font-medium text-blue-700 capitalize">
              {mision.mision.frecuencia}
            </span>
          </div>
        )}
      </div>

      {/* Estado */}
      <div className="mb-4">
        <span
          className={`
            inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium
            ${obtenerColorEstado(mision.estado)}
          `}
        >
          {mision.estado === 'completada' && <CheckCircle className="h-3.5 w-3.5" />}
          {mision.estado === 'en_progreso' && <TrendingUp className="h-3.5 w-3.5" />}
          {mision.estado === 'bloqueada' && <Lock className="h-3.5 w-3.5" />}
          {obtenerTextoEstado(mision.estado)}
        </span>
      </div>

      {/* Botones de acción */}
      <div className="flex gap-2">
        {puedeReclamar && onReclamar && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onReclamar(mision.mision_usuario_id)}
            disabled={isLoading}
            className="
              flex-1 flex items-center justify-center gap-2 rounded-lg
              bg-gradient-to-r from-yellow-400 to-orange-500
              px-4 py-3 font-bold text-white shadow-lg
              transition-all hover:shadow-xl
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            <Trophy className="h-5 w-5" />
            {isLoading ? 'Reclamando...' : 'Reclamar Recompensa'}
          </motion.button>
        )}

        {mision.estado === 'en_progreso' && onProgreso && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onProgreso(mision.mision_usuario_id)}
            disabled={isLoading}
            className="
              flex-1 flex items-center justify-center gap-2 rounded-lg
              bg-gradient-to-r from-blue-500 to-blue-600
              px-4 py-3 font-semibold text-white shadow-lg
              transition-all hover:shadow-xl
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            <TrendingUp className="h-5 w-5" />
            {isLoading ? 'Actualizando...' : 'Ver Progreso'}
          </motion.button>
        )}

        {isReclamada && (
          <div className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-green-100 px-4 py-3 text-green-800">
            <CheckCircle className="h-5 w-5" />
            <span className="font-semibold">Completada</span>
          </div>
        )}

        {isBloqueada && (
          <div className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-gray-100 px-4 py-3 text-gray-600">
            <Lock className="h-5 w-5" />
            <span className="font-semibold">Bloqueada</span>
          </div>
        )}

        {isExpirada && (
          <div className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-red-100 px-4 py-3 text-red-800">
            <Clock className="h-5 w-5" />
            <span className="font-semibold">Expirada</span>
          </div>
        )}
      </div>

      {/* Efecto de brillo para misiones completadas */}
      {puedeReclamar && (
        <motion.div
          animate={{
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute inset-0 rounded-xl bg-gradient-to-r from-yellow-400/10 via-orange-400/10 to-yellow-400/10 pointer-events-none"
        />
      )}
    </motion.div>
  );
}
