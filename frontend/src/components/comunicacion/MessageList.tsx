import React, { useEffect, useRef, useState, memo, useMemo } from 'react';
import { formatRelativeTime } from '../../utils/dateUtils';
import { Paperclip, MessageCircle, Heart, CornerUpLeft, MoreHorizontal } from 'lucide-react';

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

interface MessageListProps {
  messages: Mensaje[];
  currentUserId: string;
  salaId: string;
  onMention: (tipo: 'rutilio' | 'usuario', usuario?: string) => string;
  onReply?: (mensaje: Mensaje) => void;
  onReaction?: (mensajeId: string, emoji: string) => void;
}

const MessageListComponent: React.FC<MessageListProps> = ({ 
  messages, 
  currentUserId, 
  salaId,
  onMention,
  onReply,
  onReaction
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(new Set());
  const [hoveredMessage, setHoveredMessage] = useState<string | null>(null);

  // Auto scroll a los nuevos mensajes
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Renderizar contenido del mensaje según el tipo
  const renderMessageContent = (mensaje: Mensaje) => {
    const { contenido, tipo_mensaje, archivos_urls } = mensaje;

    // Procesar menciones en el contenido
    const processedContent = contenido?.replace(
      /@(\w+)/g,
      '<span class="bg-blue-100 text-blue-800 px-1 rounded font-semibold">@$1</span>'
    );

    switch (tipo_mensaje) {
      case 'imagen':
        return (
          <div className="space-y-2">
            {contenido && (
              <p 
                dangerouslySetInnerHTML={{ __html: processedContent }} 
                className="text-gray-800"
              />
            )}
            {archivos_urls && archivos_urls.map((url, index) => (
              <img
                key={index}
                src={url}
                alt="Imagen compartida"
                className="max-w-sm max-h-64 rounded-lg object-cover cursor-pointer hover:opacity-90 transition-opacity"
                onClick={() => window.open(url, '_blank')}
              />
            ))}
          </div>
        );
      
      case 'archivo':
        return (
          <div className="space-y-2">
            {contenido && (
              <p 
                dangerouslySetInnerHTML={{ __html: processedContent }} 
                className="text-gray-800"
              />
            )}
            {archivos_urls && archivos_urls.map((url, index) => (
              <a
                key={index}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 bg-gray-100 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Paperclip className="h-4 w-4 text-gray-600" />
                <span className="text-sm text-gray-800">
                  {url.split('/').pop() || 'Archivo adjunto'}
                </span>
              </a>
            ))}
          </div>
        );
      
      case 'sistema':
        return (
          <div className="text-center">
            <span className="text-sm text-gray-500 italic">{contenido}</span>
          </div>
        );
      
      case 'ia':
        return (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded-lg border-l-4 border-blue-400">
            <div className="flex items-center mb-2">
              <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">🤖</span>
              </div>
              <span className="ml-2 text-sm font-semibold text-blue-700">Rutilio IA</span>
            </div>
            <p 
              dangerouslySetInnerHTML={{ __html: processedContent }} 
              className="text-gray-800"
            />
          </div>
        );
      
      default:
        return (
          <p 
            dangerouslySetInnerHTML={{ __html: processedContent }} 
            className="text-gray-800"
          />
        );
    }
  };

  // Renderizar reacciones
  const renderReactions = (mensaje: Mensaje) => {
    if (!mensaje.reacciones || Object.keys(mensaje.reacciones).length === 0) {
      return null;
    }

    return (
      <div className="flex flex-wrap gap-1 mt-2">
        {Object.entries(mensaje.reacciones).map(([emoji, usuarios]) => {
          const hasReacted = usuarios.includes(currentUserId);
          return (
            <button
              key={emoji}
              onClick={() => onReaction?.(mensaje.id, emoji)}
              className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium transition-colors ${
                hasReacted 
                  ? 'bg-blue-100 text-blue-800 border border-blue-200' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <span className="mr-1">{emoji}</span>
              <span>{usuarios.length}</span>
            </button>
          );
        })}
      </div>
    );
  };

  // Renderizar respuestas (hilos)
  const renderReplies = (mensaje: Mensaje) => {
    if (!mensaje.respuestas || mensaje.respuestas.length === 0) {
      return null;
    }

    const showAllReplies = expandedMessages.has(mensaje.id);
    const visibleReplies = showAllReplies ? mensaje.respuestas : mensaje.respuestas.slice(0, 2);
    const hiddenCount = mensaje.respuestas.length - visibleReplies.length;

    return (
      <div className="mt-3 ml-4 border-l-2 border-gray-200 pl-4 space-y-2">
        {visibleReplies.map(respuesta => (
          <div key={respuesta.id} className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-900">
                {respuesta.usuario?.nombre || 'Usuario'}
              </span>
              <span className="text-xs text-gray-500">
                {formatRelativeTime(respuesta.fecha_creacion)}
              </span>
            </div>
            {renderMessageContent(respuesta)}
            {renderReactions(respuesta)}
          </div>
        ))}
        
        {hiddenCount > 0 && (
          <button
            onClick={() => {
              const newExpanded = new Set(expandedMessages);
              if (showAllReplies) {
                newExpanded.delete(mensaje.id);
              } else {
                newExpanded.add(mensaje.id);
              }
              setExpandedMessages(newExpanded);
            }}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            {showAllReplies 
              ? 'Ocultar respuestas' 
              : `Ver ${hiddenCount} respuesta${hiddenCount > 1 ? 's' : ''} más`
            }
          </button>
        )}
      </div>
    );
  };

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No hay mensajes aún</p>
          <p className="text-sm text-gray-400 mt-1">¡Sé el primero en escribir!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
      {messages.map((mensaje) => {
        const isOwn = mensaje.usuario_id === currentUserId;
        const isSystem = mensaje.tipo_mensaje === 'sistema';
        
        if (isSystem) {
          return (
            <div key={mensaje.id} className="flex justify-center">
              <div className="bg-gray-100 px-3 py-1 rounded-full">
                {renderMessageContent(mensaje)}
              </div>
            </div>
          );
        }

        return (
          <div
            key={mensaje.id}
            className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
            onMouseEnter={() => setHoveredMessage(mensaje.id)}
            onMouseLeave={() => setHoveredMessage(null)}
          >
            <div className={`max-w-xs lg:max-w-md ${isOwn ? 'order-2' : 'order-1'}`}>
              {/* Avatar y nombre (solo para mensajes de otros) */}
              {!isOwn && (
                <div className="flex items-center mb-1">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold mr-2">
                    {mensaje.usuario?.avatar ? (
                      <img 
                        src={mensaje.usuario.avatar} 
                        alt={mensaje.usuario.nombre}
                        className="w-8 h-8 rounded-full object-cover"
                      />
                    ) : (
                      mensaje.usuario?.nombre?.charAt(0).toUpperCase() || 'U'
                    )}
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {mensaje.usuario?.nombre || 'Usuario'}
                  </span>
                </div>
              )}

              {/* Contenido del mensaje */}
              <div
                className={`relative px-4 py-2 rounded-lg ${
                  isOwn
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {renderMessageContent(mensaje)}

                {/* Hora del mensaje */}
                <div className={`text-xs mt-1 ${isOwn ? 'text-blue-100' : 'text-gray-500'}`}>
                  {formatRelativeTime(mensaje.fecha_creacion)}
                </div>

                {/* Botones de acción (aparecen al hover) */}
                {hoveredMessage === mensaje.id && (
                  <div className="absolute -top-8 right-0 flex space-x-1 bg-white border rounded-lg shadow-lg p-1">
                    <button
                      onClick={() => onReaction?.(mensaje.id, '👍')}
                      className="p-1 hover:bg-gray-100 rounded"
                      title="Me gusta"
                    >
                      <Heart className="h-4 w-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() => onReply?.(mensaje)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title="Responder"
                    >
                      <CornerUpLeft className="h-4 w-4 text-gray-600" />
                    </button>
                    <button
                      className="p-1 hover:bg-gray-100 rounded"
                      title="Más opciones"
                    >
                      <MoreHorizontal className="h-4 w-4 text-gray-600" />
                    </button>
                  </div>
                )}
              </div>

              {/* Reacciones */}
              {renderReactions(mensaje)}

              {/* Respuestas (hilos) */}
              {renderReplies(mensaje)}
            </div>
          </div>
        );
      })}
      <div ref={messagesEndRef} />
    </div>
  );
};

// Memoizar componente para evitar re-renders cuando messages no cambian
export const MessageList = memo(MessageListComponent);