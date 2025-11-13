/**
 * Notificación Badge - Notification Bell Icon
 * 
 * @module components/notificaciones/NotificacionBadge
 * @description Icono de campanita con badge de contador de notificaciones no leídas.
 */

import { useState } from 'react';
import { Bell } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useContadorNoLeidas } from '../../hooks/useNotificaciones';
import { useNotificacionesRealtime } from '../../hooks/useNotificacionesRealtime';
import CentroNotificaciones from './CentroNotificaciones';

export default function NotificacionBadge() {
  const [isOpen, setIsOpen] = useState(false);
  const { data: contador = 0, isLoading } = useContadorNoLeidas();
  
  // Hook para detección en tiempo real y efectos de sonido/notificaciones
  useNotificacionesRealtime();

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <>
      <div className="relative">
        <button
          onClick={handleToggle}
          className={`relative p-2 rounded-xl transition-all duration-200 ${
            isOpen
              ? 'bg-violet-100 dark:bg-violet-900 text-violet-600 dark:text-violet-400'
              : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400'
          }`}
          aria-label={`Notificaciones${contador > 0 ? ` (${contador} sin leer)` : ''}`}
        >
          {/* Icono de campanita */}
          <Bell className="w-6 h-6" />

          {/* Badge con contador */}
          <AnimatePresence>
            {contador > 0 && !isLoading && (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                className="absolute -top-1 -right-1 min-w-[20px] h-5 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center px-1.5 shadow-lg"
              >
                <span className="text-[10px] font-bold text-white">
                  {contador > 99 ? '99+' : contador}
                </span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Indicador de carga */}
          {isLoading && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-gray-300 dark:bg-gray-600 rounded-full animate-pulse"></div>
          )}

          {/* Animación de ping cuando hay notificaciones */}
          {contador > 0 && !isLoading && (
            <motion.span
              initial={{ scale: 1, opacity: 0.75 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full"
            />
          )}
        </button>
      </div>

      {/* Panel de Notificaciones */}
      <CentroNotificaciones isOpen={isOpen} onClose={handleClose} />
    </>
  );
}
