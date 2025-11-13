/**
 * Modal de bienvenida con información de racha diaria
 * Se muestra automáticamente al iniciar sesión cada día
 */
import React, { useState, useEffect } from 'react';
import { X, Flame, Trophy, Star, Zap, Gift } from 'lucide-react';

interface RachaData {
  ya_registrado_hoy: boolean;
  racha_actual: number;
  mejor_racha: number;
  dia_ciclo: number;
  puntos_obtenidos: number;
  mensaje: string;
  proxima_recompensa_dia: number;
  es_nuevo_record: boolean;
}

interface StreakWelcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  rachaData: RachaData | null;
}

const StreakWelcomeModal: React.FC<StreakWelcomeModalProps> = ({
  isOpen,
  onClose,
  rachaData
}) => {
  const [showAnimation, setShowAnimation] = useState(false);

  useEffect(() => {
    if (isOpen && rachaData && !rachaData.ya_registrado_hoy) {
      // Usar setTimeout para evitar setState síncrono
      const timer = setTimeout(() => {
        setShowAnimation(true);
      }, 0);
      
      return () => clearTimeout(timer);
    }
  }, [isOpen, rachaData]);

  if (!isOpen || !rachaData) return null;

  // Colores por día del ciclo
  const dayColors = {
    1: 'from-green-400 to-green-600',
    2: 'from-blue-400 to-blue-600',
    3: 'from-purple-400 to-purple-600',
    4: 'from-pink-400 to-pink-600',
    5: 'from-orange-400 to-orange-600',
    6: 'from-red-400 to-red-600',
    7: 'from-yellow-400 to-yellow-600'
  };

  const gradientColor = dayColors[rachaData.dia_ciclo as keyof typeof dayColors] || 'from-gray-400 to-gray-600';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div
        className={`
          relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl 
          max-w-md w-full mx-4 overflow-hidden
          transform transition-all duration-500
          ${showAnimation ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}
        `}
      >
        {/* Header con gradiente */}
        <div className={`bg-gradient-to-r ${gradientColor} p-6 text-white relative`}>
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 rounded-full mb-4 animate-bounce">
              <Flame size={40} className="text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-2">
              {rachaData.ya_registrado_hoy 
                ? '¡Bienvenido de vuelta! 👋' 
                : rachaData.es_nuevo_record 
                  ? '¡Nuevo Récord! 🎉' 
                  : '¡Excelente! 🔥'}
            </h2>
            <p className="text-white/90">
              {rachaData.ya_registrado_hoy 
                ? `Ya completaste tu registro hoy. ¡Sigue así!` 
                : rachaData.mensaje || '¡Continúa tu racha!'}
            </p>
          </div>
        </div>

        {/* Contenido principal */}
        <div className="p-6 space-y-6">
          {/* Racha actual */}
          <div className="text-center">
            <div className="text-6xl font-bold text-gray-800 dark:text-gray-100 mb-2">
              {rachaData.racha_actual}
            </div>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              {rachaData.racha_actual === 1 ? 'día consecutivo' : 'días consecutivos'}
            </p>
          </div>

          {/* Puntos obtenidos */}
          <div className={`${rachaData.puntos_obtenidos > 0 ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-700' : 'bg-gray-50 dark:bg-gray-700/20 border-gray-200 dark:border-gray-600'} rounded-xl p-4 border-2`}>
            <div className="flex items-center justify-center gap-3">
              <Star className={rachaData.puntos_obtenidos > 0 ? 'text-yellow-500' : 'text-gray-400'} size={28} />
              <div>
                <div className={`text-2xl font-bold ${rachaData.puntos_obtenidos > 0 ? 'text-yellow-700 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-400'}`}>
                  {rachaData.ya_registrado_hoy ? 'Ya registrado' : `+${rachaData.puntos_obtenidos} puntos`}
                </div>
                <div className={`text-sm ${rachaData.puntos_obtenidos > 0 ? 'text-yellow-600 dark:text-yellow-500' : 'text-gray-500 dark:text-gray-400'}`}>
                  Día {rachaData.dia_ciclo} del ciclo semanal
                </div>
              </div>
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-4">
            {/* Mejor racha */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 text-center">
              <Trophy className="text-orange-500 mx-auto mb-2" size={24} />
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                {rachaData.mejor_racha}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Mejor racha
              </div>
            </div>

            {/* Próxima recompensa */}
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 text-center">
              <Gift className="text-purple-500 mx-auto mb-2" size={24} />
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                Día {rachaData.proxima_recompensa_dia}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Próxima recompensa
              </div>
            </div>
          </div>

          {/* Mensaje motivacional */}
          {rachaData.racha_actual >= 7 && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-4 border border-purple-200 dark:border-purple-700">
              <div className="flex items-start gap-3">
                <Zap className="text-purple-500 flex-shrink-0 mt-1" size={20} />
                <div className="text-sm text-gray-700 dark:text-gray-300">
                  {rachaData.racha_actual >= 30
                    ? '¡Eres imparable! 🚀 Sigue así y alcanzarás el nivel legendario.'
                    : rachaData.racha_actual >= 14
                    ? '¡Vas por buen camino! 💪 Solo faltan unos días para el logro mensual.'
                    : '¡Una semana completa! 🎉 Sigue así para desbloquear más recompensas.'}
                </div>
              </div>
            </div>
          )}

          {/* Botón de cierre */}
          <button
            onClick={onClose}
            className={`
              w-full bg-gradient-to-r ${gradientColor}
              text-white font-semibold py-3 px-6 rounded-xl
              hover:shadow-lg transform hover:scale-105 transition-all
              focus:outline-none focus:ring-2 focus:ring-offset-2
            `}
          >
            ¡Continuar!
          </button>
        </div>
      </div>
    </div>
  );
};

export default StreakWelcomeModal;
