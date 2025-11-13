/**
 * Widget de Notificaciones Recientes
 * 
 * @module components/notificaciones/NotificacionesWidget
 * @description Widget compacto para mostrar últimas notificaciones en dashboard
 */

import { motion } from 'framer-motion';
import { Bell, ArrowRight, Circle } from 'lucide-react';
import { useNotificaciones } from '../../hooks/useNotificaciones';
import {
  obtenerIconoNotificacion,
  obtenerColorNotificacion,
  formatearTiempoRelativo,
} from '../../services/notificaciones.service';
import { Link } from 'react-router-dom';

export default function NotificacionesWidget() {
  const { data: notificaciones = [], isLoading } = useNotificaciones({
    limite: 5,
    solo_no_leidas: false,
  });

  const noLeidas = notificaciones.filter((n) => !n.leida).length;

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-center py-8">
          <div className="w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-lg"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Bell className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white">
              Notificaciones Recientes
            </h3>
            {noLeidas > 0 && (
              <p className="text-sm text-violet-600 dark:text-violet-400">
                {noLeidas} sin leer
              </p>
            )}
          </div>
        </div>
        <Link
          to="/notificaciones"
          className="text-sm font-medium text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 flex items-center gap-1"
        >
          Ver todas
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Lista de notificaciones */}
      {notificaciones.length === 0 ? (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
            <Bell className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            No tienes notificaciones
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {notificaciones.map((notif, index) => (
            <motion.div
              key={notif.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`flex gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer ${
                !notif.leida ? 'bg-violet-50/50 dark:bg-violet-900/10' : ''
              }`}
              onClick={() => {
                if (notif.url_accion) {
                  window.location.href = notif.url_accion;
                }
              }}
            >
              {/* Icono */}
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br ${obtenerColorNotificacion(
                  notif.tipo_notificacion
                )} flex items-center justify-center text-white text-sm`}
              >
                {notif.icono || obtenerIconoNotificacion(notif.tipo_notificacion)}
              </div>

              {/* Contenido */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-gray-900 dark:text-white line-clamp-1">
                    {notif.titulo}
                  </p>
                  {!notif.leida && (
                    <Circle className="w-2 h-2 fill-violet-500 text-violet-500 flex-shrink-0 mt-1" />
                  )}
                </div>
                {notif.mensaje && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mt-1">
                    {notif.mensaje}
                  </p>
                )}
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {formatearTiempoRelativo(notif.fecha_creacion)}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
