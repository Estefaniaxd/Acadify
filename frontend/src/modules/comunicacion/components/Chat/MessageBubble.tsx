/**
 * MessageBubble Component
 * =======================
 * Componente para mostrar un mensaje individual.
 * 
 * Responsabilidades:
 * - Renderizar contenido del mensaje
 * - Mostrar metadata (autor, timestamp, reacciones)
 * - Acciones (editar, eliminar, reaccionar)
 * - Manejo de diferentes tipos de mensaje (texto, imagen, archivo, etc.)
 * 
 * @author Acadify Team
 */

import React, { useState } from 'react';
import { Edit2, Trash2, Smile, FileText, Download, CheckCheck } from 'lucide-react';
import { Mensaje, TipoMensaje } from '../../../../types/communication';

interface MessageBubbleProps {
  mensaje: Mensaje;
  esPropio: boolean;
  nombreAutor?: string;
  onEdit?: (mensajeId: string, nuevoContenido: string) => void;
  onDelete?: (mensajeId: string) => void;
  onReact?: (mensajeId: string, emoji: string) => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  mensaje,
  esPropio,
  nombreAutor,
  onEdit,
  onDelete,
  onReact
}) => {
  const [showActions, setShowActions] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState(mensaje.contenido);
  const [showReactions, setShowReactions] = useState(false);

  const reaccionesRapidas = ['👍', '❤️', '😂', '😮', '😢', '🎉'];

  // Formatear timestamp
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  };

  // Manejar guardado de edición
  const handleSaveEdit = () => {
    if (editContent.trim() && editContent !== mensaje.contenido && onEdit) {
      onEdit(mensaje.id, editContent.trim());
    }
    setEditing(false);
  };

  // Manejar cancelar edición
  const handleCancelEdit = () => {
    setEditContent(mensaje.contenido);
    setEditing(false);
  };

  // Manejar reacción
  const handleReaction = (emoji: string) => {
    if (onReact) {
      onReact(mensaje.id, emoji);
    }
    setShowReactions(false);
  };

  // Renderizar contenido según tipo
  const renderContent = () => {
    if (editing) {
      return (
        <div className="space-y-2">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm resize-none"
            rows={3}
            autoFocus
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSaveEdit();
              }
              if (e.key === 'Escape') {
                handleCancelEdit();
              }
            }}
          />
          <div className="flex justify-end space-x-2">
            <button
              onClick={handleCancelEdit}
              className="px-3 py-1 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition"
            >
              Cancelar
            </button>
            <button
              onClick={handleSaveEdit}
              disabled={!editContent.trim() || editContent === mensaje.contenido}
              className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              Guardar
            </button>
          </div>
        </div>
      );
    }

    switch (mensaje.tipo_mensaje) {
      case TipoMensaje.TEXTO:
        return (
          <p className="text-sm whitespace-pre-wrap break-words">
            {mensaje.contenido}
          </p>
        );

      case TipoMensaje.IMAGEN:
        return (
          <div className="space-y-2">
            {mensaje.contenido && <p className="text-sm">{mensaje.contenido}</p>}
            {mensaje.archivos_urls && mensaje.archivos_urls.length > 0 && (
              <div className="grid grid-cols-2 gap-2 max-w-md">
                {mensaje.archivos_urls.map((url, idx) => (
                  <img
                    key={idx}
                    src={url}
                    alt={`Imagen ${idx + 1}`}
                    className="rounded-lg cursor-pointer hover:opacity-90 transition"
                    onClick={() => window.open(url, '_blank')}
                  />
                ))}
              </div>
            )}
          </div>
        );

      case TipoMensaje.ARCHIVO:
        return (
          <div className="space-y-2">
            {mensaje.contenido && <p className="text-sm">{mensaje.contenido}</p>}
            {mensaje.archivos_urls && mensaje.archivos_urls.length > 0 && (
              <div className="space-y-2">
                {mensaje.archivos_urls.map((url, idx) => {
                  const fileName = url.split('/').pop() || `archivo-${idx + 1}`;
                  return (
                    <a
                      key={idx}
                      href={url}
                      download
                      className="flex items-center space-x-2 p-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
                    >
                      <FileText className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm flex-1 truncate">{fileName}</span>
                      <Download className="w-4 h-4 text-gray-500" />
                    </a>
                  );
                })}
              </div>
            )}
          </div>
        );

      case TipoMensaje.VIDEO:
        return (
          <div className="space-y-2">
            {mensaje.contenido && <p className="text-sm">{mensaje.contenido}</p>}
            {mensaje.archivos_urls && mensaje.archivos_urls.length > 0 && (
              <video
                src={mensaje.archivos_urls[0]}
                controls
                className="rounded-lg max-w-md"
              >
                Tu navegador no soporta video.
              </video>
            )}
          </div>
        );

      case TipoMensaje.AUDIO:
        return (
          <div className="space-y-2">
            {mensaje.contenido && <p className="text-sm">{mensaje.contenido}</p>}
            {mensaje.archivos_urls && mensaje.archivos_urls.length > 0 && (
              <audio src={mensaje.archivos_urls[0]} controls className="w-full max-w-md">
                Tu navegador no soporta audio.
              </audio>
            )}
          </div>
        );

      case TipoMensaje.SISTEMA:
        return (
          <p className="text-xs text-center text-gray-500 dark:text-gray-400 italic">
            {mensaje.contenido}
          </p>
        );

      default:
        return <p className="text-sm">{mensaje.contenido}</p>;
    }
  };

  // Mensajes de sistema tienen estilo especial
  if (mensaje.tipo_mensaje === TipoMensaje.SISTEMA) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-full">
          {renderContent()}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex ${esPropio ? 'justify-end' : 'justify-start'} mb-4 group`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div
        className={`max-w-[70%] ${
          esPropio
            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
        } rounded-2xl px-4 py-2 shadow-sm relative`}
      >
        {/* Autor (solo si no es propio y hay nombre) */}
        {!esPropio && nombreAutor && (
          <p className="text-xs font-semibold mb-1 text-gray-600 dark:text-gray-400">
            {nombreAutor}
          </p>
        )}

        {/* Contenido */}
        <div className={mensaje.eliminado ? 'opacity-50 italic' : ''}>
          {mensaje.eliminado ? (
            <p className="text-sm">Este mensaje fue eliminado</p>
          ) : (
            renderContent()
          )}
        </div>

        {/* Footer: timestamp, editado, leído */}
        <div className="flex items-center justify-end space-x-2 mt-1">
          {mensaje.editado && !mensaje.eliminado && (
            <span className="text-xs opacity-70">editado</span>
          )}
          <span className="text-xs opacity-70">
            {formatTime(mensaje.fecha_creacion)}
          </span>
          {esPropio && mensaje.es_importante && (
            <CheckCheck className="w-4 h-4 text-blue-200" />
          )}
        </div>

        {/* Reacciones */}
        {mensaje.reacciones && Object.keys(mensaje.reacciones).length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {Object.entries(mensaje.reacciones).map(([emoji, usuarios]) => (
              <button
                key={emoji}
                onClick={() => handleReaction(emoji)}
                className={`
                  flex items-center space-x-1 px-2 py-1 rounded-full text-xs
                  ${esPropio 
                    ? 'bg-white/20 hover:bg-white/30' 
                    : 'bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500'
                  }
                  transition
                `}
              >
                <span>{emoji}</span>
                <span className="font-medium">{usuarios.length}</span>
              </button>
            ))}
          </div>
        )}

        {/* Botones de acción */}
        {!mensaje.eliminado && showActions && (
          <div
            className={`absolute top-0 ${
              esPropio ? 'right-full mr-2' : 'left-full ml-2'
            } flex items-center space-x-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-1 border border-gray-200 dark:border-gray-700`}
          >
            {/* Reaccionar */}
            <div className="relative">
              <button
                onClick={() => setShowReactions(!showReactions)}
                className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition"
                aria-label="Reaccionar"
              >
                <Smile className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              </button>
              {showReactions && (
                <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-2 border border-gray-200 dark:border-gray-700 flex space-x-1 z-10">
                  {reaccionesRapidas.map((emoji) => (
                    <button
                      key={emoji}
                      onClick={() => handleReaction(emoji)}
                      className="text-xl hover:scale-125 transition-transform"
                      aria-label={`Reaccionar con ${emoji}`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Editar (solo mensajes propios de texto) */}
            {esPropio && mensaje.tipo_mensaje === TipoMensaje.TEXTO && onEdit && (
              <button
                onClick={() => setEditing(true)}
                className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition"
                aria-label="Editar mensaje"
              >
                <Edit2 className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              </button>
            )}

            {/* Eliminar (solo mensajes propios) */}
            {esPropio && onDelete && (
              <button
                onClick={() => onDelete(mensaje.id)}
                className="p-1.5 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition"
                aria-label="Eliminar mensaje"
              >
                <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
