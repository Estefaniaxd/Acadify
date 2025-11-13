/**
 * Centro de Notificaciones - Dropdown Component
 * 
 * @module components/notificaciones/CentroNotificaciones
 * @description Panel dropdown de notificaciones con lista, filtros y acciones.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bell, Check, CheckCheck, X, Filter,
  Clock, ChevronRight
} from 'lucide-react';
import { useCentroNotificaciones } from '../../hooks/useNotificaciones';
import {
  obtenerIconoNotificacion,
  obtenerColorNotificacion,
  formatearTiempoRelativo,
  type TipoNotificacion,
  type Notificacion,
} from '../../services/notificaciones.service';

interface CentroNotificacionesProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CentroNotificaciones({ isOpen, onClose }: CentroNotificacionesProps) {
  const [_filtroTipo, _setFiltroTipo] = useState<TipoNotificacion | undefined>();
  const [soloNoLeidas, setSoloNoLeidas] = useState(false);

  const {
    notificaciones,
    contador,
    isLoading,
    marcarComoLeidas,
    marcarTodasLeidas,
    isMarkingRead,
  } = useCentroNotificaciones({
    tipo_notificacion: _filtroTipo,
    solo_no_leidas: soloNoLeidas,
    limite: 20,
  });

  const handleMarcarLeida = (id: string) => {
    marcarComoLeidas([id]);
  };

  const handleMarcarTodasLeidas = () => {
    // marcarTodasLeidas ya es la función mutate, no necesita .mutate()
    marcarTodasLeidas(undefined);
  };

  const handleClickNotificacion = (notif: Notificacion) => {
    // Marcar como leída
    if (!notif.leida) {
      handleMarcarLeida(notif.id);
    }

    // Navegar a la URL de acción si existe
    if (notif.url_accion) {
      window.open(notif.url_accion, '_self');
    }

    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ type: 'spring', duration: 0.3 }}
            className="fixed top-20 right-4 w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 max-h-[calc(100vh-6rem)] flex flex-col"
          >
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <Bell className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                      Notificaciones
                    </h2>
                    {contador > 0 && (
                      <p className="text-sm text-violet-600 dark:text-violet-400">
                        {contador} sin leer
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {contador > 0 && (
                    <button
                      onClick={handleMarcarTodasLeidas}
                      disabled={isMarkingRead}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
                      title="Marcar todas como leídas"
                    >
                      <CheckCheck className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                  )}
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Filtros */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSoloNoLeidas(!soloNoLeidas)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    soloNoLeidas
                      ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <Filter className="w-4 h-4 inline-block mr-1" />
                  {soloNoLeidas ? 'No leídas' : 'Todas'}
                </button>

                <button
                  onClick={() => {/* TODO: Abrir modal de filtros avanzados */}}
                  className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium transition-colors hover:bg-gray-200 dark:hover:bg-gray-600"
                >
                  <a href="/configuracion/notificaciones" className="flex items-center gap-1">
                    Configurar
                  </a>
                </button>
              </div>
            </div>

            {/* Lista de Notificaciones */}
            <div className="flex-1 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : notificaciones.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 px-4">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                    <Bell className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 text-center">
                    {soloNoLeidas
                      ? 'No tienes notificaciones sin leer'
                      : 'No tienes notificaciones'}
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {notificaciones.map((notif) => (
                    <motion.div
                      key={notif.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer ${
                        !notif.leida ? 'bg-violet-50/50 dark:bg-violet-900/10' : ''
                      }`}
                      onClick={() => handleClickNotificacion(notif)}
                    >
                      <div className="flex gap-3">
                        {/* Icono */}
                        <div
                          className={`flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br ${obtenerColorNotificacion(
                            notif.tipo_notificacion
                          )} flex items-center justify-center text-white`}
                        >
                          <span className="text-lg">
                            {notif.icono || obtenerIconoNotificacion(notif.tipo_notificacion)}
                          </span>
                        </div>

                        {/* Contenido */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white text-sm line-clamp-1">
                              {notif.titulo}
                            </h3>
                            {!notif.leida && (
                              <div className="flex-shrink-0 w-2 h-2 bg-violet-500 rounded-full mt-1"></div>
                            )}
                          </div>

                          {notif.mensaje && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
                              {notif.mensaje}
                            </p>
                          )}

                          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-500">
                            <Clock className="w-3 h-3" />
                            <span>{formatearTiempoRelativo(notif.fecha_creacion)}</span>
                          </div>
                        </div>

                        {/* Botón de acción */}
                        {notif.url_accion && (
                          <div className="flex-shrink-0">
                            <ChevronRight className="w-5 h-5 text-gray-400" />
                          </div>
                        )}
                      </div>

                      {/* Botón de marcar como leída (solo si no está leída) */}
                      {!notif.leida && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarcarLeida(notif.id);
                          }}
                          className="mt-2 text-xs text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 font-medium flex items-center gap-1"
                        >
                          <Check className="w-3 h-3" />
                          Marcar como leída
                        </button>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {notificaciones.length > 0 && (
              <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                <a
                  href="/notificaciones"
                  className="block text-center text-sm font-medium text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 transition-colors"
                  onClick={onClose}
                >
                  Ver todas las notificaciones
                </a>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
