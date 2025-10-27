import { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

interface Mensaje {
  id: string;
  usuario_id: string;
  contenido: string;
  tipo_mensaje: string;
  fecha_creacion: string;
  menciones_usuarios?: string[];
  menciones_ia: boolean;
  reacciones?: { [key: string]: string[] };
  archivos_urls?: string[];
  mensaje_padre_id?: string;
  respuestas?: Mensaje[];
  usuario?: {
    id: string;
    nombre: string;
    avatar?: string;
  };
}

interface SendMessageData {
  contenido: string;
  tipo_mensaje: string;
  archivos?: File[];
  mensaje_padre_id?: string;
  menciones_usuarios?: string[];
  menciones_ia?: boolean;
}

interface TypingData {
  usuario_id: string;
  nombre: string;
  escribiendo: boolean;
}

export const useWebSocket = (endpoint: string, usuarioId: string) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Mensaje[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [typing, setTyping] = useState<string[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!endpoint || !usuarioId) return;

    const token = localStorage.getItem('token');
    
    // Crear conexión WebSocket
    const newSocket = io(`http://localhost:8000${endpoint}`, {
      auth: {
        token: token,
        usuario_id: usuarioId,
      },
      transports: ['websocket', 'polling'],
    });

    // Event listeners
    newSocket.on('connect', () => {
      console.log('✅ WebSocket conectado');
      setIsConnected(true);
      setError(null);
    });

    newSocket.on('disconnect', (reason) => {
      console.log('❌ WebSocket desconectado:', reason);
      setIsConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('❌ Error de conexión WebSocket:', error);
      setError('Error de conexión al chat');
      setIsConnected(false);
    });

    // Recibir mensaje nuevo
    newSocket.on('nuevo_mensaje', (mensaje: Mensaje) => {
      console.log('📨 Nuevo mensaje recibido:', mensaje);
      setMessages(prevMessages => [...prevMessages, mensaje]);
    });

    // Recibir historial de mensajes
    newSocket.on('historial_mensajes', (mensajes: Mensaje[]) => {
      console.log('📚 Historial de mensajes cargado:', mensajes.length);
      setMessages(mensajes);
    });

    // Respuesta de @rutilio IA
    newSocket.on('respuesta_ia', (respuesta: Mensaje) => {
      console.log('🤖 Respuesta de IA recibida:', respuesta);
      setMessages(prevMessages => [...prevMessages, respuesta]);
    });

    // Usuario escribiendo
    newSocket.on('usuario_escribiendo', (data: TypingData) => {
      if (data.usuario_id !== usuarioId) {
        setTyping(prev => {
          if (data.escribiendo) {
            return [...prev.filter(u => u !== data.nombre), data.nombre];
          } else {
            return prev.filter(u => u !== data.nombre);
          }
        });
      }
    });

    // Usuarios conectados
    newSocket.on('usuarios_conectados', (usuarios: string[]) => {
      console.log('👥 Usuarios conectados:', usuarios);
      setOnlineUsers(usuarios);
    });

    // Usuario se unió
    newSocket.on('usuario_unido', (usuario: string) => {
      console.log('➕ Usuario se unió:', usuario);
      setOnlineUsers(prev => [...prev, usuario]);
    });

    // Usuario se fue
    newSocket.on('usuario_desconectado', (usuario: string) => {
      console.log('➖ Usuario se desconectó:', usuario);
      setOnlineUsers(prev => prev.filter(u => u !== usuario));
    });

    // Error del servidor
    newSocket.on('error', (error: string) => {
      console.error('❌ Error del servidor:', error);
      setError(error);
    });

    setSocket(newSocket);

    return () => {
      console.log('🔌 Desconectando WebSocket...');
      newSocket.disconnect();
    };
  }, [endpoint, usuarioId]);

  // Función para enviar mensaje
  const sendMessage = async (data: SendMessageData) => {
    if (!socket || !isConnected) {
      throw new Error('WebSocket no conectado');
    }

    try {
      // Si hay archivos, primero los subimos
      let archivos_urls: string[] = [];
      if (data.archivos && data.archivos.length > 0) {
        const formData = new FormData();
        data.archivos.forEach((archivo, index) => {
          formData.append(`archivo_${index}`, archivo);
        });

        const response = await fetch('/api/comunicacion/upload', {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const { urls } = await response.json();
          archivos_urls = urls;
        }
      }

      // Enviar mensaje através de WebSocket
      const mensajeData = {
        contenido: data.contenido,
        tipo_mensaje: data.tipo_mensaje,
        archivos_urls,
        mensaje_padre_id: data.mensaje_padre_id,
        menciones_usuarios: data.menciones_usuarios || [],
        menciones_ia: data.menciones_ia || false,
      };

      socket.emit('enviar_mensaje', mensajeData);
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      throw error;
    }
  };

  // Función para indicar que el usuario está escribiendo
  const setUserTyping = (typing: boolean) => {
    if (!socket || !isConnected) return;

    socket.emit('escribiendo', { escribiendo: typing });

    // Auto-stop typing después de 3 segundos
    if (typing) {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      typingTimeoutRef.current = setTimeout(() => {
        socket.emit('escribiendo', { escribiendo: false });
      }, 3000);
    }
  };

  // Función para reaccionar a un mensaje
  const addReaction = (mensajeId: string, emoji: string) => {
    if (!socket || !isConnected) return;

    socket.emit('reaccionar_mensaje', {
      mensaje_id: mensajeId,
      reaccion: emoji,
    });
  };

  // Función para marcar mensaje como leído
  const markAsRead = (mensajeId: string) => {
    if (!socket || !isConnected) return;

    socket.emit('marcar_leido', {
      mensaje_id: mensajeId,
    });
  };

  return {
    socket,
    messages,
    isConnected,
    typing,
    onlineUsers,
    error,
    sendMessage,
    setUserTyping,
    addReaction,
    markAsRead,
  };
};