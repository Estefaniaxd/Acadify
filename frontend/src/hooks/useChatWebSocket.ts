/**
 * useChatWebSocket Hook
 * ======================
 * Custom hook para gestionar WebSocket de chat con eventos específicos.
 * 
 * Características:
 * - Conexión automática a sala de chat
 * - Manejo de mensajes en tiempo real
 * - Typing indicators
 * - Read receipts
 * - Reacciones
 * - Estado de usuarios online
 * 
 * @author Acadify Team
 * @version 1.0.0
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { useWebSocket } from './useWebSocket';
import { WebSocketEventType } from '../services/websocketService';
import {
  Mensaje,
  MessageNewEvent,
  MessageEditEvent,
  MessageDeleteEvent,
  MessageReactionEvent,
  TypingUpdateEvent,
  OnlineUsersEvent,
  CrearMensajeRequest
} from '../types/communication';

/**
 * Opciones del hook
 */
export interface UseChatWebSocketOptions {
  /** URL base del WebSocket */
  baseUrl: string;
  /** Token de autenticación */
  token: string;
  /** ID de la sala */
  salaId: string;
  /** ID del usuario actual */
  usuarioId: string;
  /** Auto-conectar */
  autoConnect?: boolean;
  /** Callbacks */
  onNuevoMensaje?: (mensaje: Mensaje) => void;
  onMensajeEditado?: (mensajeId: string, contenido: string) => void;
  onMensajeEliminado?: (mensajeId: string) => void;
  onReaccion?: (mensajeId: string, emoji: string, usuarioId: string) => void;
}

/**
 * Valor de retorno del hook
 */
export interface UseChatWebSocketReturn {
  /** Mensajes de la sala */
  mensajes: Mensaje[];
  /** Usuarios escribiendo */
  usuariosEscribiendo: string[];
  /** Usuarios online */
  usuariosOnline: string[];
  /** Estado de conexión */
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  /** Acciones */
  enviarMensaje: (data: CrearMensajeRequest) => void;
  editarMensaje: (mensajeId: string, contenido: string) => void;
  eliminarMensaje: (mensajeId: string) => void;
  añadirReaccion: (mensajeId: string, emoji: string) => void;
  marcarComoLeido: (mensajesIds: string[]) => void;
  setEscribiendo: (escribiendo: boolean) => void;
  /** Utilidades */
  limpiarMensajes: () => void;
}

/**
 * Hook principal
 */
export const useChatWebSocket = (
  options: UseChatWebSocketOptions
): UseChatWebSocketReturn => {
  const {
    baseUrl,
    token,
    salaId,
    usuarioId,
    autoConnect = true,
    onNuevoMensaje,
    onMensajeEditado,
    onMensajeEliminado,
    onReaccion
  } = options;
  
  // State
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [usuariosEscribiendo, setUsuariosEscribiendo] = useState<string[]>([]);
  const [usuariosOnline, setUsuariosOnline] = useState<string[]>([]);
  
  // Refs para timeouts
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // WebSocket connection
  const {
    isConnected,
    isConnecting,
    isReconnecting,
    send,
    on,
    off
  } = useWebSocket({
    baseUrl,
    token,
    salaId,
    autoConnect,
    debug: true,
    onConnected: () => {
      console.log('✅ Chat WebSocket conectado a sala:', salaId);
      // Solicitar usuarios online al conectar
      send('get.online_users', {});
    },
    onDisconnected: () => {
      console.log('❌ Chat WebSocket desconectado');
      setUsuariosEscribiendo([]);
    }
  });
  
  // ==================== Event Handlers ====================
  
  /**
   * Handler: Nuevo mensaje
   */
  const handleNuevoMensaje = useCallback((event: MessageNewEvent) => {
    console.log('📨 Nuevo mensaje:', event.mensaje);
    
    const nuevoMensaje: Mensaje = {
      ...event.mensaje,
      es_propio: event.mensaje.usuario_id === usuarioId
    };
    
    setMensajes(prev => {
      // Evitar duplicados
      if (prev.some(m => m.id === nuevoMensaje.id)) {
        return prev;
      }
      return [...prev, nuevoMensaje];
    });
    
    onNuevoMensaje?.(nuevoMensaje);
  }, [usuarioId, onNuevoMensaje]);
  
  /**
   * Handler: Mensaje editado
   */
  const handleMensajeEditado = useCallback((event: MessageEditEvent) => {
    console.log('✏️ Mensaje editado:', event.mensaje_id);
    
    setMensajes(prev => prev.map(mensaje =>
      mensaje.id === event.mensaje_id
        ? {
            ...mensaje,
            contenido: event.contenido,
            contenido_html: event.contenido_html,
            editado: true,
            fecha_edicion: event.fecha_edicion
          }
        : mensaje
    ));
    
    onMensajeEditado?.(event.mensaje_id, event.contenido);
  }, [onMensajeEditado]);
  
  /**
   * Handler: Mensaje eliminado
   */
  const handleMensajeEliminado = useCallback((event: MessageDeleteEvent) => {
    console.log('🗑️ Mensaje eliminado:', event.mensaje_id);
    
    setMensajes(prev => prev.map(mensaje =>
      mensaje.id === event.mensaje_id
        ? { ...mensaje, eliminado: true }
        : mensaje
    ));
    
    onMensajeEliminado?.(event.mensaje_id);
  }, [onMensajeEliminado]);
  
  /**
   * Handler: Reacción añadida
   */
  const handleReaccion = useCallback((event: MessageReactionEvent) => {
    console.log('👍 Reacción añadida:', event.emoji, 'a mensaje', event.mensaje_id);
    
    setMensajes(prev => prev.map(mensaje =>
      mensaje.id === event.mensaje_id
        ? { ...mensaje, reacciones: event.reacciones }
        : mensaje
    ));
    
    onReaccion?.(event.mensaje_id, event.emoji, event.usuario_id);
  }, [onReaccion]);
  
  /**
   * Handler: Usuario escribiendo
   */
  const handleTyping = useCallback((event: TypingUpdateEvent) => {
    if (event.usuario_id === usuarioId) return; // Ignorar propio
    
    if (event.is_typing) {
      setUsuariosEscribiendo(prev => {
        if (!prev.includes(event.usuario_nombre || event.usuario_id)) {
          return [...prev, event.usuario_nombre || event.usuario_id];
        }
        return prev;
      });
    } else {
      setUsuariosEscribiendo(prev =>
        prev.filter(u => u !== (event.usuario_nombre || event.usuario_id))
      );
    }
  }, [usuarioId]);
  
  /**
   * Handler: Usuarios online
   */
  const handleOnlineUsers = useCallback((event: OnlineUsersEvent) => {
    console.log('👥 Usuarios online:', event.count);
    setUsuariosOnline(event.usuarios);
  }, []);
  
  /**
   * Handler: Usuario conectado
   */
  const handleUserConnected = useCallback((event: any) => {
    console.log('➕ Usuario conectado:', event.usuario_id);
    setUsuariosOnline(prev => {
      if (!prev.includes(event.usuario_id)) {
        return [...prev, event.usuario_id];
      }
      return prev;
    });
  }, []);
  
  /**
   * Handler: Usuario desconectado
   */
  const handleUserDisconnected = useCallback((event: any) => {
    console.log('➖ Usuario desconectado:', event.usuario_id);
    setUsuariosOnline(prev => prev.filter(u => u !== event.usuario_id));
    setUsuariosEscribiendo(prev => prev.filter(u => u !== event.usuario_id));
  }, []);
  
  // ==================== Suscripciones a Eventos ====================
  
  useEffect(() => {
    if (!isConnected) return;
    
    // Suscribir a eventos
    on(WebSocketEventType.MESSAGE_NEW, handleNuevoMensaje);
    on(WebSocketEventType.MESSAGE_EDIT, handleMensajeEditado);
    on(WebSocketEventType.MESSAGE_DELETE, handleMensajeEliminado);
    on(WebSocketEventType.MESSAGE_REACTION, handleReaccion);
    on(WebSocketEventType.TYPING_UPDATE, handleTyping);
    on(WebSocketEventType.TYPING_STOP, handleTyping);
    on(WebSocketEventType.ONLINE_USERS, handleOnlineUsers);
    on(WebSocketEventType.USER_CONNECTED, handleUserConnected);
    on(WebSocketEventType.USER_DISCONNECTED, handleUserDisconnected);
    
    // Cleanup
    return () => {
      off(WebSocketEventType.MESSAGE_NEW, handleNuevoMensaje);
      off(WebSocketEventType.MESSAGE_EDIT, handleMensajeEditado);
      off(WebSocketEventType.MESSAGE_DELETE, handleMensajeEliminado);
      off(WebSocketEventType.MESSAGE_REACTION, handleReaccion);
      off(WebSocketEventType.TYPING_UPDATE, handleTyping);
      off(WebSocketEventType.TYPING_STOP, handleTyping);
      off(WebSocketEventType.ONLINE_USERS, handleOnlineUsers);
      off(WebSocketEventType.USER_CONNECTED, handleUserConnected);
      off(WebSocketEventType.USER_DISCONNECTED, handleUserDisconnected);
    };
  }, [
    isConnected,
    on,
    off,
    handleNuevoMensaje,
    handleMensajeEditado,
    handleMensajeEliminado,
    handleReaccion,
    handleTyping,
    handleOnlineUsers,
    handleUserConnected,
    handleUserDisconnected
  ]);
  
  // ==================== Acciones ====================
  
  /**
   * Envía un mensaje
   */
  const enviarMensaje = useCallback((data: CrearMensajeRequest) => {
    send('message.new', data);
    
    // Detener typing indicator
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
    send('typing.stop', {});
  }, [send]);
  
  /**
   * Edita un mensaje
   */
  const editarMensaje = useCallback((mensajeId: string, contenido: string) => {
    send('message.edit', { mensaje_id: mensajeId, contenido });
  }, [send]);
  
  /**
   * Elimina un mensaje
   */
  const eliminarMensaje = useCallback((mensajeId: string) => {
    send('message.delete', { mensaje_id: mensajeId });
  }, [send]);
  
  /**
   * Añade una reacción
   */
  const añadirReaccion = useCallback((mensajeId: string, emoji: string) => {
    send('message.reaction', { mensaje_id: mensajeId, emoji });
  }, [send]);
  
  /**
   * Marca mensajes como leídos
   */
  const marcarComoLeido = useCallback((mensajesIds: string[]) => {
    send('read.receipt', { mensajes_ids: mensajesIds });
  }, [send]);
  
  /**
   * Establece estado de escritura
   */
  const setEscribiendo = useCallback((escribiendo: boolean) => {
    if (escribiendo) {
      send('typing.start', {});
      
      // Auto-detener después de 3 segundos
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      typingTimeoutRef.current = setTimeout(() => {
        send('typing.stop', {});
      }, 3000);
    } else {
      send('typing.stop', {});
      
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
        typingTimeoutRef.current = null;
      }
    }
  }, [send]);
  
  /**
   * Limpia mensajes locales
   */
  const limpiarMensajes = useCallback(() => {
    setMensajes([]);
  }, []);
  
  // Cleanup de timeouts
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);
  
  return {
    mensajes,
    usuariosEscribiendo,
    usuariosOnline,
    isConnected,
    isConnecting,
    isReconnecting,
    enviarMensaje,
    editarMensaje,
    eliminarMensaje,
    añadirReaccion,
    marcarComoLeido,
    setEscribiendo,
    limpiarMensajes
  };
};

export default useChatWebSocket;
