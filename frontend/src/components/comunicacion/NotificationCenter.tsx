import React, { useState, useEffect, useRef } from 'react';
import { formatRelativeTime } from '../../utils/dateUtils';
import { AlertTriangle, Bell, Check, EyeOff, FileText, Info, MessageSquare, Settings, Users, X } from 'lucide-react';

interface Notificacion {
  id: string;
  titulo: string;
  mensaje: string;
  tipo_notificacion: string;
  leida: boolean;
  fecha_creacion: string;
  url_accion?: string;
  icono?: string;
  color?: string;
  datos_adicionales?: {
    usuario_nombre?: string;
    sala_nombre?: string;
    tarea_nombre?: string;
  };
}

interface NotificationCenterProps {
  usuarioId: string;
  salaId?: string;
  onClose: () => void;
  onNotificationClick?: (notification: Notificacion) => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  usuarioId,
  salaId,
  onClose,
  onNotificationClick
}) => {
  const [notifications, setNotifications] = useState<Notificacion[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'todas' | 'no_leidas' | 'chat' | 'tareas'>('no_leidas');
  const [error, setError] = useState<string | null>(null);

  // Cargar notificaciones
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          usuario_id: usuarioId,
          ...(salaId && { sala_id: salaId }),
          limit: '50'
        });

        const response = await fetch(`/api/comunicacion/notificaciones?${params}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Error al cargar notificaciones');
        }

        const data = await response.json();
        setNotifications(data.notificaciones || []);
      } catch (error) {
        console.error('Error cargando notificaciones:', error);
        setError('No se pudieron cargar las notificaciones');
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, [usuarioId, salaId]);

  // Marcar notificación como leída
  const markAsRead = async (notificationId: string) => {
    try {
      const response = await fetch(`/api/comunicacion/notificaciones/${notificationId}/leer`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setNotifications(prev =>
          prev.map(n =>
            n.id === notificationId ? { ...n, leida: true } : n
          )
        );
      }
    } catch (error) {
      console.error('Error marcando notificación como leída:', error);
    }
  };

  // Marcar todas como leídas
  const markAllAsRead = async () => {
    try {
      const response = await fetch(`/api/comunicacion/notificaciones/leer-todas`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ usuario_id: usuarioId }),
      });

      if (response.ok) {
        setNotifications(prev =>
          prev.map(n => ({ ...n, leida: true }))
        );
      }
    } catch (error) {
      console.error('Error marcando todas las notificaciones como leídas:', error);
    }
  };

  // Eliminar notificación
  const deleteNotification = async (notificationId: string) => {
    try {
      const response = await fetch(`/api/comunicacion/notificaciones/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        setNotifications(prev =>
          prev.filter(n => n.id !== notificationId)
        );
      }
    } catch (error) {
      console.error('Error eliminando notificación:', error);
    }
  };

  // Filtrar notificaciones
  const filteredNotifications = notifications.filter(notification => {
    switch (filter) {
      case 'no_leidas':
        return !notification.leida;
      case 'chat':
        return ['mensaje_directo', 'mencion', 'respuesta_hilo', 'mensaje_importante'].includes(notification.tipo_notificacion);
      case 'tareas':
        return ['tarea_nueva', 'tarea_vencimiento', 'tarea_calificada', 'tarea_comentario'].includes(notification.tipo_notificacion);
      case 'todas':
      default:
        return true;
    }
  });

  // Obtener icono según tipo de notificación
  const getNotificationIcon = (tipo: string, icono?: string) => {
    if (icono) {
      return <span className="text-lg">{icono}</span>;
    }

    switch (tipo) {
      case 'mensaje_directo':
      case 'mencion':
      case 'respuesta_hilo':
        return <MessageSquare className="h-5 w-5" />;
      case 'tarea_nueva':
      case 'tarea_vencimiento':
      case 'tarea_calificada':
        return <FileText className="h-5 w-5" />;
      case 'usuario_unido':
        return <Users className="h-5 w-5" />;
      case 'sistema':
        return <Settings className="h-5 w-5" />;
      case 'error':
        return <AlertTriangle className="h-5 w-5" />;
      default:
        return <Info className="h-5 w-5" />;
    }
  };

  // Obtener color según tipo
  const getNotificationColor = (tipo: string, color?: string) => {
    if (color) return color;

    switch (tipo) {
      case 'mensaje_directo':
      case 'mencion':
        return 'blue';
      case 'tarea_vencimiento':
      case 'advertencia':
        return 'red';
      case 'tarea_calificada':
        return 'green';
      case 'tarea_nueva':
        return 'purple';
      default:
        return 'gray';
    }
  };

  const handleNotificationClick = (notification: Notificacion) => {
    if (!notification.leida) {
      markAsRead(notification.id);
    }
    
    if (onNotificationClick) {
      onNotificationClick(notification);
    } else if (notification.url_accion) {
      window.location.href = notification.url_accion;
    }
  };

  const unreadCount = notifications.filter(n => !n.leida).length;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 w-80 max-h-96">
        <div className="p-4 flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Cargando...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 w-80 max-h-96 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Bell className="h-5 w-5 text-blue-600 mr-2 fill-current" />
            <h3 className="text-lg font-semibold text-gray-900">Notificaciones</h3>
            {unreadCount > 0 && (
              <span className="ml-2 bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
                {unreadCount}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 rounded-full p-1 hover:bg-gray-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Filtros */}
        <div className="mt-3 flex space-x-1 bg-white rounded-lg p-1">
          {[
            { key: 'no_leidas', label: 'No leídas', count: unreadCount },
            { key: 'todas', label: 'Todas', count: notifications.length },
            { key: 'chat', label: 'Chat' },
            { key: 'tareas', label: 'Tareas' }
          ].map(({ key, label, count }) => (
            <button
              key={key}
              onClick={() => setFilter(key as any)}
              className={`flex-1 px-2 py-1 rounded text-xs font-medium transition-colors ${
                filter === key
                  ? 'bg-blue-100 text-blue-800'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {label}
              {count !== undefined && (
                <span className="ml-1">({count})</span>
              )}
            </button>
          ))}
        </div>

        {/* Acciones */}
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="mt-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Marcar todas como leídas
          </button>
        )}
      </div>

      {/* Lista de notificaciones */}
      <div className="max-h-64 overflow-y-auto">
        {error ? (
          <div className="p-4 text-center">
            <AlertTriangle className="h-8 w-8 text-red-400 mx-auto mb-2" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="p-8 text-center">
            <Bell className="h-8 w-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-500">
              {filter === 'no_leidas' ? 'No tienes notificaciones sin leer' : 'No hay notificaciones'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredNotifications.map((notification) => {
              const color = getNotificationColor(notification.tipo_notificacion, notification.color);
              
              return (
                <div
                  key={notification.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                    !notification.leida ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className="flex items-start">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mr-3 bg-${color}-100 text-${color}-600`}>
                      {getNotificationIcon(notification.tipo_notificacion, notification.icono)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className={`text-sm font-medium ${
                          notification.leida ? 'text-gray-900' : 'text-gray-900 font-semibold'
                        }`}>
                          {notification.titulo}
                        </p>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                          className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                      
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {notification.mensaje}
                      </p>
                      
                      {/* Información adicional */}
                      {notification.datos_adicionales && (
                        <div className="mt-2 text-xs text-gray-500">
                          {notification.datos_adicionales.sala_nombre && (
                            <span>en {notification.datos_adicionales.sala_nombre}</span>
                          )}
                          {notification.datos_adicionales.usuario_nombre && (
                            <span> • por {notification.datos_adicionales.usuario_nombre}</span>
                          )}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500">
                          {formatRelativeTime(notification.fecha_creacion)}
                        </span>
                        
                        {!notification.leida && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              markAsRead(notification.id);
                            }}
                            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                            title="Marcar como leída"
                          >
                            <Check className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 bg-gray-50">
        <button
          className="w-full text-sm text-blue-600 hover:text-blue-800 font-medium"
          onClick={() => {
            // Ir a página completa de notificaciones
            window.location.href = '/notificaciones';
          }}
        >
          Ver todas las notificaciones
        </button>
      </div>
    </div>
  );
};