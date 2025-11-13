/**
 * MessageInput Component
 * ======================
 * Componente para entrada de mensajes.
 * 
 * Responsabilidades:
 * - Capturar input de texto
 * - Adjuntar archivos
 * - Enviar mensajes
 * - Detección de escritura (typing indicators)
 * - Selector de emojis
 * 
 * @author Acadify Team
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Smile, X, FileText, Image as ImageIcon } from 'lucide-react';

interface MessageInputProps {
  onSend: (contenido: string, archivos?: File[]) => void;
  onTyping?: (isTyping: boolean) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSend,
  onTyping,
  disabled = false,
  placeholder = 'Escribe un mensaje...'
}) => {
  const [contenido, setContenido] = useState('');
  const [archivos, setArchivos] = useState<File[]>([]);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Emojis rápidos
  const emojisRapidos = ['😊', '😂', '❤️', '👍', '👏', '🎉', '🔥', '💯', '😍', '🤔', '😢', '🙏'];

  // Auto-resize textarea
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  // Manejar cambio de contenido
  const handleContenidoChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setContenido(newValue);
    adjustTextareaHeight();

    // Typing indicator
    if (onTyping) {
      // Si empieza a escribir, notificar
      if (newValue.length > 0 && contenido.length === 0) {
        onTyping(true);
      }

      // Reset timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }

      // Si hay contenido, programar stop
      if (newValue.length > 0) {
        typingTimeoutRef.current = setTimeout(() => {
          onTyping(false);
        }, 3000);
      } else {
        // Si borra todo, dejar de escribir inmediatamente
        onTyping(false);
      }
    }
  };

  // Manejar adjuntar archivos
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const newFiles = Array.from(files);
      setArchivos(prev => [...prev, ...newFiles]);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Remover archivo
  const removeFile = (index: number) => {
    setArchivos(prev => prev.filter((_, idx) => idx !== index));
  };

  // Insertar emoji
  const insertEmoji = (emoji: string) => {
    const textarea = textareaRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newContenido = contenido.substring(0, start) + emoji + contenido.substring(end);
      setContenido(newContenido);
      
      // Restaurar foco y posición del cursor
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + emoji.length, start + emoji.length);
        adjustTextareaHeight();
      }, 0);
    }
    setShowEmojiPicker(false);
  };

  // Enviar mensaje
  const handleSend = () => {
    const trimmedContent = contenido.trim();
    
    if (trimmedContent || archivos.length > 0) {
      onSend(trimmedContent, archivos.length > 0 ? archivos : undefined);
      setContenido('');
      setArchivos([]);
      
      // Stop typing
      if (onTyping) {
        onTyping(false);
      }
      
      // Clear timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  // Manejar teclas
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Cleanup en desmontaje
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      if (onTyping) {
        onTyping(false);
      }
    };
  }, [onTyping]);

  // Obtener icono según tipo de archivo
  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return ImageIcon;
    }
    return FileText;
  };

  return (
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
      {/* Preview de archivos adjuntos */}
      {archivos.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {archivos.map((file, idx) => {
            const Icon = getFileIcon(file);
            return (
              <div
                key={idx}
                className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-lg"
              >
                <Icon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                <span className="text-sm text-gray-700 dark:text-gray-300 truncate max-w-[200px]">
                  {file.name}
                </span>
                <button
                  onClick={() => removeFile(idx)}
                  className="text-gray-500 hover:text-red-600 transition"
                  aria-label="Eliminar archivo"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Input principal */}
      <div className="flex items-end space-x-2">
        {/* Botones laterales izquierdos */}
        <div className="flex items-center space-x-1 pb-2">
          {/* Adjuntar archivo */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Adjuntar archivo"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          {/* Emoji picker */}
          <div className="relative">
            <button
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              disabled={disabled}
              className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Insertar emoji"
            >
              <Smile className="w-5 h-5" />
            </button>

            {/* Panel de emojis */}
            {showEmojiPicker && (
              <div className="absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 p-3 z-10">
                <div className="grid grid-cols-6 gap-2">
                  {emojisRapidos.map((emoji, idx) => (
                    <button
                      key={idx}
                      onClick={() => insertEmoji(emoji)}
                      className="text-2xl hover:scale-125 transition-transform"
                      aria-label={`Insertar ${emoji}`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Textarea */}
        <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-2xl overflow-hidden">
          <textarea
            ref={textareaRef}
            value={contenido}
            onChange={handleContenidoChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-3 bg-transparent resize-none focus:outline-none dark:text-white text-sm"
            style={{ minHeight: '44px', maxHeight: '120px' }}
            aria-label="Mensaje"
          />
        </div>

        {/* Botón enviar */}
        <button
          onClick={handleSend}
          disabled={disabled || (!contenido.trim() && archivos.length === 0)}
          className={`
            p-3 rounded-full transition-all duration-200
            ${
              !disabled && (contenido.trim() || archivos.length > 0)
                ? 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl'
                : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }
          `}
          aria-label="Enviar mensaje"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>

      {/* Input de archivos oculto */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileSelect}
        className="hidden"
        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
      />

      {/* Hint */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
        Presiona Enter para enviar, Shift + Enter para nueva línea
      </div>
    </div>
  );
};

export default MessageInput;
