/**
 * NotificationCenter - Centro de notificaciones de invitaciones
 * Dropdown con badge contador, diseño profesional y actualización en tiempo real
 */

import React, { useState, useRef, useEffect, memo, useCallback } from 'react';
import { Bell, Mail, MailCheck, Check, X, Loader2, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { 
  useNotificacionesInvitacion, 
  useMarcarNotificacionLeida 
} from '../hooks/useInvitaciones';
import type { NotificacionInvitacion } from '../types';

function NotificationCenter() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { data: notificaciones, isLoading } = useNotificacionesInvitacion();
  const marcarLeidaMutation = useMarcarNotificacionLeida();

  const noLeidas = notificaciones?.filter(n => !n.leida).length || 0;

  // Cerrar al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Callbacks estables con useCallback
  const handleMarcarLeida = useCallback((notificacionId: number) => {
    marcarLeidaMutation.mutate(notificacionId);
  }, [marcarLeidaMutation]);

  const handleMarcarTodasLeidas = useCallback(() => {
    notificaciones
      ?.filter(n => !n.leida)
      .forEach(n => marcarLeidaMutation.mutate(n.id));
  }, [notificaciones, marcarLeidaMutation]);

  const handleClickNotificacion = useCallback((notificacion: NotificacionInvitacion) => {
    if (!notificacion.leida) {
      handleMarcarLeida(notificacion.id);
    }
    setIsOpen(false);
    navigate(`/admin/invitaciones`);
  }, [navigate, handleMarcarLeida]);

  const getTipoConfig = (tipo: NotificacionInvitacion['tipo']) => {
    const configs = {
      INVITACION_RECIBIDA: {
        icon: Mail,
        color: 'text-blue-600 dark:text-blue-400',
        bg: 'bg-blue-100 dark:bg-blue-900/30',
        label: 'Nueva invitación',
      },
      INVITACION_ACEPTADA: {
        icon: MailCheck,
        color: 'text-green-600 dark:text-green-400',
        bg: 'bg-green-100 dark:bg-green-900/30',
        label: 'Invitación aceptada',
      },
      INVITACION_RECHAZADA: {
        icon: X,
        color: 'text-red-600 dark:text-red-400',
        bg: 'bg-red-100 dark:bg-red-900/30',
        label: 'Invitación rechazada',
      },
      INVITACION_EXPIRADA: {
        icon: Mail,
        color: 'text-gray-600 dark:text-gray-400',
        bg: 'bg-gray-100 dark:bg-gray-900/30',
        label: 'Invitación expirada',
      },
      INVITACION_REENVIADA: {
        icon: Mail,
        color: 'text-indigo-600 dark:text-indigo-400',
        bg: 'bg-indigo-100 dark:bg-indigo-900/30',
        label: 'Invitación reenviada',
      },
    };
    return configs[tipo] || configs.INVITACION_RECIBIDA;
  };

  const formatearTiempo = (fecha: string) => {
    const ahora = new Date();
    const fechaNotif = new Date(fecha);
    const diffMs = ahora.getTime() - fechaNotif.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHoras = Math.floor(diffMs / 3600000);
    const diffDias = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Ahora mismo';
    if (diffMins < 60) return `Hace ${diffMins}m`;
    if (diffHoras < 24) return `Hace ${diffHoras}h`;
    if (diffDias === 1) return 'Ayer';
    if (diffDias < 7) return `Hace ${diffDias}d`;
    
    return fechaNotif.toLocaleDateString('es-ES', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Botón de campana con badge */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
        aria-label={`Notificaciones ${noLeidas > 0 ? `(${noLeidas} sin leer)` : ''}`}
      >
        <Bell className="w-6 h-6 text-gray-600 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors" />
        
        {/* Badge contador - Círculo morado profesional */}
        {noLeidas > 0 && (
          <span className="absolute -top-1 -right-1 flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-gradient-to-br from-purple-500 to-purple-600 text-white text-xs font-bold rounded-full shadow-lg shadow-purple-500/50 animate-pulse">
            {noLeidas > 99 ? '99+' : noLeidas}
          </span>
        )}

        {/* Indicador de pulsación cuando hay notificaciones */}
        {noLeidas > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-purple-500 rounded-full animate-ping opacity-75" />
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20">
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Bell className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                Notificaciones
              </h3>
              {noLeidas > 0 && (
                <button
                  onClick={handleMarcarTodasLeidas}
                  disabled={marcarLeidaMutation.isPending}
                  className="text-xs font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors disabled:opacity-50 flex items-center gap-1"
                >
                  <Check className="w-3 h-3" />
                  Marcar todas
                </button>
              )}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {noLeidas > 0 
                ? `Tienes ${noLeidas} notificación${noLeidas > 1 ? 'es' : ''} sin leer`
                : 'No tienes notificaciones sin leer'}
            </p>
          </div>

          {/* Lista de notificaciones */}
          <div className="max-h-[420px] overflow-y-auto">
            {isLoading ? (
              <div className="p-8 text-center">
                <Loader2 className="w-6 h-6 text-purple-600 dark:text-purple-400 animate-spin mx-auto mb-2" />
                <p className="text-sm text-gray-600 dark:text-gray-400">Cargando...</p>
              </div>
            ) : !notificaciones?.length ? (
              <div className="p-8 text-center">
                <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Bell className="w-8 h-8 text-gray-400" />
                </div>
                <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                  No hay notificaciones
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Te notificaremos cuando haya actividad en tus invitaciones
                </p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {notificaciones.map((notificacion) => {
                  const config = getTipoConfig(notificacion.tipo);
                  const Icon = config.icon;

                  return (
                    <button
                      key={notificacion.id}
                      onClick={() => handleClickNotificacion(notificacion)}
                      className={`w-full p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors text-left group relative ${
                        !notificacion.leida ? 'bg-purple-50/50 dark:bg-purple-900/10' : ''
                      }`}
                    >
                      {/* Indicador de no leída */}
                      {!notificacion.leida && (
                        <div className="absolute left-2 top-1/2 -translate-y-1/2 w-2 h-2 bg-purple-600 rounded-full" />
                      )}

                      <div className="flex gap-3 ml-2">
                        {/* Icono */}
                        <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center`}>
                          <Icon className={`w-5 h-5 ${config.color}`} />
                        </div>

                        {/* Contenido */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <p className="text-sm font-semibold text-gray-900 dark:text-white">
                              {config.label}
                            </p>
                            <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                              {formatearTiempo(notificacion.fechaCreacion)}
                            </span>
                          </div>

                          <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mb-1">
                            <span className="font-medium">{notificacion.invitacion.nombreInvitado}</span>
                            {notificacion.tipo === 'INVITACION_ACEPTADA' && ' ha aceptado la invitación'}
                            {notificacion.tipo === 'INVITACION_RECHAZADA' && ' ha rechazado la invitación'}
                            {notificacion.tipo === 'INVITACION_EXPIRADA' && ' - invitación expirada'}
                            {notificacion.tipo === 'INVITACION_RECIBIDA' && ' - nueva invitación enviada'}
                          </p>

                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {notificacion.invitacion.email}
                            </span>
                            <span className="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-gray-600 dark:text-gray-400">
                              {notificacion.invitacion.rol}
                            </span>
                          </div>
                        </div>

                        {/* Flecha al hover */}
                        <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-2" />
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          {notificaciones && notificaciones.length > 0 && (
            <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
              <button
                onClick={() => {
                  setIsOpen(false);
                  navigate('/admin/invitaciones');
                }}
                className="w-full px-4 py-2 text-sm font-medium text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30 rounded-lg transition-colors"
              >
                Ver todas las invitaciones
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Memoizar componente para evitar re-renders innecesarios
export default memo(NotificationCenter);
