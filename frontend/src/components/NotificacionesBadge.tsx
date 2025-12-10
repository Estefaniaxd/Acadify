import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, X, Archive, Check } from 'lucide-react';

interface Notificacion {
  id: string;
  titulo: string;
  mensaje: string;
  tipo: 'info' | 'exito' | 'advertencia' | 'error';
  fecha: string;
  leida: boolean;
  archivada: boolean;
}

/**
 * 🔔 Badge de Notificaciones
 * Muestra contador de notificaciones no leídas en la navbar
 */
export const NotificacionesBadge: React.FC = () => {
  const [abierto, setAbierto] = useState(false);
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [filtro, setFiltro] = useState<'todas' | 'no-leidas' | 'archivadas'>('todas');

  const noLeidas = notificaciones.filter((n) => !n.leida && !n.archivada).length;
  const notificacionesFiltradas = notificaciones.filter((n) => {
    if (filtro === 'no-leidas') return !n.leida && !n.archivada;
    if (filtro === 'archivadas') return n.archivada;
    return !n.archivada;
  });

  const getColorPorTipo = (tipo: string) => {
    const colores: Record<string, string> = {
      info: 'bg-blue-100 text-blue-700 border-blue-300',
      exito: 'bg-green-100 text-green-700 border-green-300',
      advertencia: 'bg-yellow-100 text-yellow-700 border-yellow-300',
      error: 'bg-red-100 text-red-700 border-red-300',
    };
    return colores[tipo] || colores.info;
  };

  const getIconoPorTipo = (tipo: string) => {
    const iconos: Record<string, string> = {
      info: '📢',
      exito: '✅',
      advertencia: '⚠️',
      error: '❌',
    };
    return iconos[tipo] || '📢';
  };

  return (
    <div className="relative">
      {/* Botón Badge */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setAbierto(!abierto)}
        className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <Bell size={24} className="text-gray-700" />
        {noLeidas > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center"
          >
            {noLeidas > 9 ? '9+' : noLeidas}
          </motion.span>
        )}
      </motion.button>

      {/* Panel de Notificaciones */}
      <AnimatePresence>
        {abierto && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className="absolute top-12 right-0 w-96 bg-white border border-gray-200 rounded-lg shadow-2xl z-50 max-h-96 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="font-bold text-gray-900">Notificaciones</h3>
              <button
                onClick={() => setAbierto(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X size={18} />
              </button>
            </div>

            {/* Filtros */}
            <div className="flex gap-2 px-4 py-2 border-b border-gray-200">
              {(['todas', 'no-leidas', 'archivadas'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFiltro(f)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    filtro === f
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {f === 'todas'
                    ? '📋 Todas'
                    : f === 'no-leidas'
                    ? '🔔 No leídas'
                    : '📁 Archivadas'}
                </button>
              ))}
            </div>

            {/* Lista de Notificaciones */}
            <div className="flex-1 overflow-y-auto space-y-2 p-3">
              {notificacionesFiltradas.length === 0 ? (
                <div className="py-8 text-center text-gray-500 text-sm">
                  <Bell size={32} className="mx-auto text-gray-400 mb-2" />
                  <p>No hay notificaciones</p>
                </div>
              ) : (
                notificacionesFiltradas.map((n) => (
                  <motion.div
                    key={n.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`p-3 rounded-lg border ${getColorPorTipo(
                      n.tipo
                    )} ${!n.leida ? 'font-semibold' : 'opacity-75'}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="text-sm">
                          {getIconoPorTipo(n.tipo)} {n.titulo}
                        </p>
                        <p className="text-xs mt-1 opacity-75">{n.mensaje}</p>
                      </div>
                      {!n.leida && (
                        <button
                          className="p-1 hover:opacity-70"
                          title="Marcar como leída"
                        >
                          <Check size={14} />
                        </button>
                      )}
                    </div>
                    <p className="text-xs mt-1 opacity-60">
                      {new Date(n.fecha).toLocaleTimeString()}
                    </p>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
