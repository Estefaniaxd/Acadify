import React, { useState, useCallback } from 'react';
import {
  Bell,
  CheckCircle,
  AlertCircle,
  Trash2,
  ChevronDown,
  GraduationCap,
  MessageCircle,
  Zap,
  Calendar,
  X,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNotificaciones, useContadorNoLeidas, useMarcarTodasLeidas } from '@/hooks/useNotificaciones';
import { Notificacion, TipoNotificacion } from '@/services/notificaciones.service';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

// ====================================
// TIPOS
// ====================================

interface NotificacionesPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

// ====================================
// COMPONENTE PRINCIPAL
// ====================================

export function NotificacionesPanel({ isOpen, onClose }: NotificacionesPanelProps) {
  const { notificaciones = [], isLoading, error } = useNotificaciones({ solo_no_leidas: true });
  const { contador } = useContadorNoLeidas();
  const marcarTodasLeidas = useMarcarTodasLeidas();
  const [filtroActivo, setFiltroActivo] = useState<TipoNotificacion | 'todas'>('todas');

  // Filtrar notificaciones
  const notificacionesFiltradas =
    filtroActivo === 'todas'
      ? notificaciones
      : notificaciones.filter((n) => n.tipo === filtroActivo);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Panel */}
          <motion.div
            className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 flex flex-col"
            initial={{ x: 400 }}
            animate={{ x: 0 }}
            exit={{ x: 400 }}
            transition={{ duration: 0.3 }}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 border-b">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Bell className="w-6 h-6" />
                  <h2 className="text-xl font-bold">Notificaciones</h2>
                </div>
                <button
                  onClick={onClose}
                  className="hover:bg-blue-600 p-2 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Contador */}
              {contador > 0 && (
                <div className="flex items-center justify-between bg-white/20 px-3 py-2 rounded-lg">
                  <span className="text-sm font-medium">{contador} sin leer</span>
                  <button
                    onClick={() => marcarTodasLeidas.mutate()}
                    className="text-xs font-semibold hover:bg-white/10 px-3 py-1 rounded transition-colors"
                  >
                    Marcar todas como leídas
                  </button>
                </div>
              )}
            </div>

            {/* Filtros */}
            <div className="bg-gray-50 px-6 py-4 border-b flex gap-2 overflow-x-auto">
              {[
                { tipo: 'todas', label: 'Todas', icon: Bell },
                { tipo: TipoNotificacion.TAREA_CALIFICADA, label: 'Tareas', icon: GraduationCap },
                { tipo: TipoNotificacion.NUEVO_MENSAJE, label: 'Mensajes', icon: MessageCircle },
                { tipo: TipoNotificacion.RETROALIMENTACION_IA, label: 'IA', icon: Zap },
              ].map(({ tipo, label, icon: Icon }) => (
                <button
                  key={tipo}
                  onClick={() => setFiltroActivo(tipo as any)}
                  className={`flex items-center gap-1 px-3 py-2 rounded-lg whitespace-nowrap transition-colors ${
                    filtroActivo === tipo
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-xs font-medium">{label}</span>
                </button>
              ))}
            </div>

            {/* Lista de Notificaciones */}
            <div className="flex-1 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-spin mb-3">
                      <Bell className="w-8 h-8 text-gray-400" />
                    </div>
                    <p className="text-gray-500 text-sm">Cargando notificaciones...</p>
                  </div>
                </div>
              ) : error ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    <AlertCircle className="w-8 h-8 mx-auto mb-2" />
                    <p className="text-sm">Error cargando notificaciones</p>
                  </div>
                </div>
              ) : notificacionesFiltradas.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No hay notificaciones</p>
                  </div>
                </div>
              ) : (
                <AnimatePresence mode="popLayout">
                  {notificacionesFiltradas.map((notificacion) => (
                    <NotificacionItem
                      key={notificacion.id}
                      notificacion={notificacion}
                      onClose={onClose}
                    />
                  ))}
                </AnimatePresence>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// ====================================
// COMPONENTE ITEM
// ====================================

interface NotificacionItemProps {
  notificacion: Notificacion;
  onClose: () => void;
}

function NotificacionItem({ notificacion, onClose }: NotificacionItemProps) {
  const { marcarComoLeida, eliminarNotificacion } = useNotificaciones();
  const [isHovering, setIsHovering] = useState(false);

  // Determinar icono por tipo
  const getIconoTipo = () => {
    switch (notificacion.tipo) {
      case TipoNotificacion.TAREA_CALIFICADA:
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case TipoNotificacion.RETROALIMENTACION_IA:
        return <Zap className="w-5 h-5 text-yellow-500" />;
      case TipoNotificacion.NUEVO_MENSAJE:
        return <MessageCircle className="w-5 h-5 text-blue-500" />;
      case TipoNotificacion.RECORDATORIO_VENCIMIENTO:
        return <Calendar className="w-5 h-5 text-orange-500" />;
      default:
        return <Bell className="w-5 h-5 text-purple-500" />;
    }
  };

  // Determinar color de fondo
  const getColorFondo = () => {
    switch (notificacion.tipo) {
      case TipoNotificacion.TAREA_CALIFICADA:
        return 'bg-green-50';
      case TipoNotificacion.RETROALIMENTACION_IA:
        return 'bg-yellow-50';
      case TipoNotificacion.NUEVO_MENSAJE:
        return 'bg-blue-50';
      case TipoNotificacion.RECORDATORIO_VENCIMIENTO:
        return 'bg-orange-50';
      default:
        return 'bg-purple-50';
    }
  };

  const handleMarcarLeida = () => {
    marcarComoLeida.mutate(notificacion.id);
  };

  const handleEliminar = () => {
    eliminarNotificacion.mutate(notificacion.id);
  };

  const handleAccion = (accion: any) => {
    if (accion.tipo === 'link') {
      window.location.href = accion.url;
      onClose();
    }
  };

  const tiempo = formatDistanceToNow(new Date(notificacion.fecha_creacion), {
    addSuffix: true,
    locale: es,
  });

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      className={`border-b px-4 py-3 hover:bg-gray-50 transition-colors cursor-pointer ${getColorFondo()}`}
      onClick={handleMarcarLeida}
    >
      <div className="flex gap-3">
        {/* Icono */}
        <div className="flex-shrink-0 mt-1">{getIconoTipo()}</div>

        {/* Contenido */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-gray-900 text-sm pr-2 line-clamp-2">
              {notificacion.titulo}
            </h3>
            {isHovering && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleEliminar();
                }}
                className="flex-shrink-0 text-gray-400 hover:text-red-500 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <p className="text-gray-600 text-xs mt-1 line-clamp-2">{notificacion.mensaje}</p>
          <p className="text-gray-400 text-xs mt-2">{tiempo}</p>

          {/* Acciones */}
          {notificacion.acciones && notificacion.acciones.length > 0 && (
            <div className="flex gap-2 mt-3">
              {notificacion.acciones.map((accion, idx) => (
                <button
                  key={idx}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAccion(accion);
                  }}
                  className="px-3 py-1.5 rounded text-xs font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                >
                  {accion.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Indicador no leído */}
        {!notificacion.leida && (
          <div className="flex-shrink-0">
            <div className="w-2 h-2 rounded-full bg-blue-600 mt-1" />
          </div>
        )}
      </div>
    </motion.div>
  );
}

// ====================================
// COMPONENTE BADGE NOTIFICACIONES
// ====================================

export function NotificacionesBadge() {
  const { contador } = useContadorNoLeidas();
  const [panelAbierto, setPanelAbierto] = React.useState(false);

  return (
    <>
      <button
        onClick={() => setPanelAbierto(!panelAbierto)}
        className="relative p-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        title="Notificaciones"
      >
        <Bell className="w-6 h-6" />
        {contador > 0 && (
          <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
            {contador > 9 ? '9+' : contador}
          </span>
        )}
      </button>

      <NotificacionesPanel isOpen={panelAbierto} onClose={() => setPanelAbierto(false)} />
    </>
  );
}
