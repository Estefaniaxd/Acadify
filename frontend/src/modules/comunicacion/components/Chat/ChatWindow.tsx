/**
 * ChatWindow Component
 * ====================
 * Componente ventana de chat activa.
 * 
 * Responsabilidades:
 * - Mostrar header con info de la sala
 * - Lista de mensajes con scroll automático
 * - Indicador de usuarios escribiendo
 * - Integración con MessageInput y MessageBubble
 * - Manejo de carga de mensajes antiguos (scroll infinito)
 * 
 * @author Acadify Team
 */

import React, { useEffect, useRef, useState } from 'react';
import { X, Users, Video, Phone, MoreVertical, ArrowDown } from 'lucide-react';
import { SalaChat, Mensaje } from '../../../../types/communication';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from '../Common';

interface ChatWindowProps {
  sala: SalaChat;
  mensajes: Mensaje[];
  usuarioId: string;
  usuariosEscribiendo?: string[];
  usuariosOnline?: string[];
  onClose: () => void;
  onSendMessage: (contenido: string, archivos?: File[]) => void;
  onEditMessage?: (mensajeId: string, nuevoContenido: string) => void;
  onDeleteMessage?: (mensajeId: string) => void;
  onReactMessage?: (mensajeId: string, emoji: string) => void;
  onTyping?: (isTyping: boolean) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
  isLoading?: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  sala,
  mensajes,
  usuarioId,
  usuariosEscribiendo = [],
  usuariosOnline = [],
  onClose,
  onSendMessage,
  onEditMessage,
  onDeleteMessage,
  onReactMessage,
  onTyping,
  onLoadMore,
  hasMore = false,
  isLoading = false
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const prevScrollHeight = useRef(0);

  // Scroll al final
  const scrollToBottom = (smooth = true) => {
    messagesEndRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
  };

  // Manejar scroll
  const handleScroll = () => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

    // Mostrar botón si está lejos del final
    setShowScrollButton(distanceFromBottom > 200);

    // Activar auto-scroll si está cerca del final
    setAutoScroll(distanceFromBottom < 100);

    // Cargar más mensajes si está arriba
    if (scrollTop < 100 && hasMore && !isLoading && onLoadMore) {
      prevScrollHeight.current = scrollHeight;
      onLoadMore();
    }
  };

  // Auto-scroll en nuevos mensajes
  useEffect(() => {
    if (autoScroll) {
      scrollToBottom();
    }
  }, [mensajes, autoScroll]);

  // Mantener posición al cargar mensajes antiguos
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container && prevScrollHeight.current > 0) {
      const newScrollHeight = container.scrollHeight;
      const scrollDiff = newScrollHeight - prevScrollHeight.current;
      container.scrollTop = scrollDiff;
      prevScrollHeight.current = 0;
    }
  }, [mensajes.length]);

  // Obtener nombre de usuario
  const getNombreUsuario = (usuarioIdParam: string): string => {
    const participante = sala.participantes?.find(p => p.usuario_id === usuarioIdParam);
    return participante?.usuario?.nombre || 'Usuario';
  };

  // Filtrar usuarios escribiendo (excluir usuario actual)
  const nombresEscribiendo = usuariosEscribiendo
    .filter(uid => uid !== usuarioId)
    .map(uid => getNombreUsuario(uid));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-4 text-white flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          {/* Info de sala */}
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg truncate">{sala.nombre}</h3>
            <div className="flex items-center space-x-2 text-sm text-blue-100">
              <Users className="w-4 h-4" />
              <span>
                {sala.participantes?.length || 0} participante{sala.participantes?.length !== 1 ? 's' : ''}
              </span>
              {usuariosOnline.length > 0 && (
                <>
                  <span>•</span>
                  <span className="text-green-300">
                    {usuariosOnline.length} online
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex items-center space-x-2">
          <button
            className="p-2 hover:bg-white/10 rounded-full transition"
            aria-label="Llamada de voz"
          >
            <Phone className="w-5 h-5" />
          </button>
          <button
            className="p-2 hover:bg-white/10 rounded-full transition"
            aria-label="Videollamada"
          >
            <Video className="w-5 h-5" />
          </button>
          <button
            className="p-2 hover:bg-white/10 rounded-full transition"
            aria-label="Más opciones"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition"
            aria-label="Cerrar chat"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Área de mensajes */}
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 space-y-2 bg-gray-50 dark:bg-gray-900/50 relative"
      >
        {/* Indicador de carga (mensajes antiguos) */}
        {isLoading && (
          <div className="flex justify-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        )}

        {/* Mensaje de más antiguos disponibles */}
        {hasMore && !isLoading && (
          <div className="text-center py-2">
            <button
              onClick={onLoadMore}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Cargar mensajes anteriores
            </button>
          </div>
        )}

        {/* Lista de mensajes */}
        {mensajes.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="bg-white dark:bg-gray-800 rounded-full p-6 mb-4 shadow-lg">
              <Users className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
              ¡Inicia la conversación!
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
              Sé el primero en enviar un mensaje a {sala.nombre}
            </p>
          </div>
        ) : (
          <>
            {mensajes.map((mensaje) => (
              <MessageBubble
                key={mensaje.id}
                mensaje={mensaje}
                esPropio={mensaje.usuario_id === usuarioId}
                nombreAutor={getNombreUsuario(mensaje.usuario_id)}
                onEdit={onEditMessage}
                onDelete={onDeleteMessage}
                onReact={onReactMessage}
              />
            ))}
          </>
        )}

        {/* Indicador de usuarios escribiendo */}
        {nombresEscribiendo.length > 0 && (
          <TypingIndicator usuarios={nombresEscribiendo} />
        )}

        {/* Referencia para scroll */}
        <div ref={messagesEndRef} />

        {/* Botón de scroll al final */}
        {showScrollButton && (
          <button
            onClick={() => {
              scrollToBottom();
              setAutoScroll(true);
            }}
            className="fixed bottom-24 right-8 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-200 z-10"
            aria-label="Ir al final"
          >
            <ArrowDown className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Input de mensaje */}
      <MessageInput
        onSend={onSendMessage}
        onTyping={onTyping}
        placeholder={`Mensaje a ${sala.nombre}...`}
      />
    </div>
  );
};

export default ChatWindow;
