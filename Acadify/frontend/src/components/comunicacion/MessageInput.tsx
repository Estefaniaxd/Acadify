import React, { useState, useRef, useEffect } from 'react';
import { 
  PaperAirplaneIcon, 
  PaperClipIcon, 
  PhotoIcon,
  FaceSmileIcon,
  AtSymbolIcon,
  MicrophoneIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface Participante {
  id: string;
  usuario_id: string;
  nombre: string;
  avatar?: string;
  esta_activo: boolean;
}

interface MessageInputProps {
  onSendMessage: (contenido: string, archivos?: File[]) => void;
  onMention: (tipo: 'rutilio' | 'usuario', usuario?: string) => string;
  onTyping?: (typing: boolean) => void;
  participantes: Participante[];
  permiteMenciones?: boolean;
  permiteArchivos?: boolean;
  permiteHilos?: boolean;
  replyTo?: {
    id: string;
    usuario: string;
    contenido: string;
  };
  onCancelReply?: () => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  onMention,
  onTyping,
  participantes,
  permiteMenciones = true,
  permiteArchivos = true,
  permiteHilos = true,
  replyTo,
  onCancelReply,
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showMentions, setShowMentions] = useState(false);
  const [mentionQuery, setMentionQuery] = useState('');
  const [cursorPosition, setCursorPosition] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Manejar cambios en el textarea
  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setMessage(value);
    
    // Detectar menciones (@)
    const position = e.target.selectionStart;
    const textBeforeCursor = value.substring(0, position);
    const mentionMatch = textBeforeCursor.match(/@(\w*)$/);
    
    if (mentionMatch && permiteMenciones) {
      setMentionQuery(mentionMatch[1]);
      setShowMentions(true);
      setCursorPosition(position);
    } else {
      setShowMentions(false);
      setMentionQuery('');
    }

    // Indicar que el usuario está escribiendo
    if (onTyping) {
      onTyping(true);
      
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      typingTimeoutRef.current = setTimeout(() => {
        onTyping(false);
      }, 1000);
    }
  };

  // Auto-resize del textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  // Manejar envío de mensaje
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if ((!message.trim() && selectedFiles.length === 0) || disabled) {
      return;
    }

    onSendMessage(message.trim(), selectedFiles);
    setMessage('');
    setSelectedFiles([]);
    
    if (onTyping) {
      onTyping(false);
    }

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Manejar selección de archivos
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles(prev => [...prev, ...files]);
  };

  // Remover archivo seleccionado
  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Insertar mención en el texto
  const insertMention = (usuario: string) => {
    const textBefore = message.substring(0, cursorPosition - mentionQuery.length - 1);
    const textAfter = message.substring(cursorPosition);
    const newMessage = textBefore + onMention('usuario', usuario) + textAfter;
    
    setMessage(newMessage);
    setShowMentions(false);
    setMentionQuery('');
    
    // Focus back to textarea
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  };

  // Insertar emoji
  const insertEmoji = (emoji: string) => {
    const textarea = textareaRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newMessage = message.substring(0, start) + emoji + message.substring(end);
      setMessage(newMessage);
      
      // Mantener cursor después del emoji
      setTimeout(() => {
        textarea.setSelectionRange(start + emoji.length, start + emoji.length);
        textarea.focus();
      }, 0);
    }
    setShowEmojiPicker(false);
  };

  // Grabación de audio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const audioChunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioFile = new File([audioBlob], 'mensaje-audio.wav', { type: 'audio/wav' });
        setSelectedFiles(prev => [...prev, audioFile]);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error al acceder al micrófono:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Filtrar participantes para menciones
  const filteredParticipants = participantes.filter(p => 
    p.nombre.toLowerCase().includes(mentionQuery.toLowerCase()) && p.esta_activo
  );

  // Emojis comunes
  const commonEmojis = ['😊', '😂', '❤️', '👍', '👎', '😢', '😮', '😡', '🎉', '🔥', '💯', '✨'];

  return (
    <div className="border-t border-gray-200 bg-white">
      {/* Respuesta a mensaje */}
      {replyTo && (
        <div className="p-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="text-sm text-gray-600">
                Respondiendo a <span className="font-semibold">{replyTo.usuario}</span>
              </div>
              <div className="text-sm text-gray-800 truncate mt-1">
                {replyTo.contenido}
              </div>
            </div>
            <button
              onClick={onCancelReply}
              className="ml-2 p-1 hover:bg-gray-200 rounded"
            >
              <XMarkIcon className="h-4 w-4 text-gray-500" />
            </button>
          </div>
        </div>
      )}

      {/* Archivos seleccionados */}
      {selectedFiles.length > 0 && (
        <div className="p-3 border-b border-gray-200">
          <div className="flex flex-wrap gap-2">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center bg-blue-50 rounded-lg px-3 py-2">
                <span className="text-sm text-blue-800">{file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="ml-2 p-1 hover:bg-blue-100 rounded"
                >
                  <XMarkIcon className="h-3 w-3 text-blue-600" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lista de menciones */}
      {showMentions && filteredParticipants.length > 0 && (
        <div className="absolute bottom-full left-0 right-0 bg-white border border-gray-200 rounded-t-lg shadow-lg max-h-32 overflow-y-auto z-10">
          {/* Opción @rutilio */}
          {mentionQuery === '' || 'rutilio'.includes(mentionQuery.toLowerCase()) && (
            <button
              onClick={() => insertMention('rutilio')}
              className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center"
            >
              <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mr-3">
                <span className="text-white text-xs">🤖</span>
              </div>
              <span className="font-semibold text-blue-600">rutilio</span>
              <span className="text-gray-500 text-sm ml-2">(IA Asistente)</span>
            </button>
          )}
          
          {/* Participantes */}
          {filteredParticipants.map((participante) => (
            <button
              key={participante.id}
              onClick={() => insertMention(participante.nombre)}
              className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center"
            >
              <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center mr-3">
                {participante.avatar ? (
                  <img 
                    src={participante.avatar} 
                    alt={participante.nombre}
                    className="w-6 h-6 rounded-full object-cover"
                  />
                ) : (
                  <span className="text-xs font-semibold text-gray-600">
                    {participante.nombre.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <span>{participante.nombre}</span>
            </button>
          ))}
        </div>
      )}

      {/* Selector de emojis */}
      {showEmojiPicker && (
        <div className="absolute bottom-full left-0 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-10">
          <div className="grid grid-cols-6 gap-2">
            {commonEmojis.map((emoji) => (
              <button
                key={emoji}
                onClick={() => insertEmoji(emoji)}
                className="text-lg hover:bg-gray-100 rounded p-1"
              >
                {emoji}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input principal */}
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex items-end space-x-3">
          {/* Textarea */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleMessageChange}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder={
                replyTo 
                  ? "Escribe tu respuesta..." 
                  : permiteMenciones 
                    ? "Escribe un mensaje... (usa @ para menciones)"
                    : "Escribe un mensaje..."
              }
              disabled={disabled}
              className="w-full resize-none border border-gray-300 rounded-lg px-4 py-2 pr-12 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ minHeight: '2.5rem', maxHeight: '8rem' }}
            />
          </div>

          {/* Botones de acción */}
          <div className="flex items-center space-x-2">
            {/* Archivos */}
            {permiteArchivos && (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
                title="Adjuntar archivo"
              >
                <PaperClipIcon className="h-5 w-5" />
              </button>
            )}

            {/* Emojis */}
            <button
              type="button"
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              disabled={disabled}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
              title="Emojis"
            >
              <FaceSmileIcon className="h-5 w-5" />
            </button>

            {/* Audio */}
            <button
              type="button"
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={stopRecording}
              disabled={disabled}
              className={`p-2 rounded-full disabled:opacity-50 disabled:cursor-not-allowed ${
                isRecording 
                  ? 'text-red-600 bg-red-100' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
              title={isRecording ? 'Grabando... (suelta para enviar)' : 'Mantener para grabar audio'}
            >
              <MicrophoneIcon className="h-5 w-5" />
            </button>

            {/* Enviar */}
            <button
              type="submit"
              disabled={(!message.trim() && selectedFiles.length === 0) || disabled}
              className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Enviar mensaje"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Input file oculto */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept="image/*,application/pdf,.doc,.docx,.txt"
        />
      </form>
    </div>
  );
};