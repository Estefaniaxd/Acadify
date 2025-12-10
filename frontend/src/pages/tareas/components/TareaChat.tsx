import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Clock, User, Lock, Globe } from 'lucide-react';
import { UserAvatar } from '../../../utils/avatarHelpers';

// ====================================
// TIPOS
// ====================================

export enum TipoCanalChat {
  GENERAL = 'general', // Todos ven
  PRIVADO = 'privado', // Solo profesor y estudiante
}

export interface MensajeChat {
  id: string;
  autor_id: string;
  autor_nombre: string;
  contenido: string;
  timestamp: string;
  tipo_canal: TipoCanalChat;
  archivo_url?: string;
}

interface TareaChatProps {
  tareaId: string;
  usuarioActualId: string;
  usuarioActualNombre: string;
  esProfesor: boolean;
  mensajes: MensajeChat[];
  onEnviarMensaje: (contenido: string, tipoCanal: TipoCanalChat) => Promise<void>;
  loading?: boolean;
}

// ====================================
// COMPONENTE
// ====================================

export const TareaChat: React.FC<TareaChatProps> = ({
  tareaId,
  usuarioActualId,
  usuarioActualNombre,
  esProfesor,
  mensajes,
  onEnviarMensaje,
  loading = false,
}) => {
  const [contenido, setContenido] = useState('');
  const [tipoCanal, setTipoCanal] = useState<TipoCanalChat>(TipoCanalChat.GENERAL);
  const [enviando, setEnviando] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [mensajes]);

  const handleEnviar = async () => {
    if (!contenido.trim()) return;

    try {
      setEnviando(true);
      await onEnviarMensaje(contenido, tipoCanal);
      setContenido('');
    } catch (error) {
      console.error('Error enviando mensaje:', error);
    } finally {
      setEnviando(false);
    }
  };

  // Filtrar mensajes según el tipo de canal
  const mensajesVisibles = mensajes.filter(m => {
    if (m.tipo_canal === TipoCanalChat.GENERAL) return true;
    if (m.tipo_canal === TipoCanalChat.PRIVADO && esProfesor) return true;
    if (m.tipo_canal === TipoCanalChat.PRIVADO && m.autor_id === usuarioActualId) return true;
    return false;
  });

  // Agrupar mensajes por fecha
  const mensajesPorFecha = React.useMemo(() => {
    const grupos: Record<string, MensajeChat[]> = {};
    mensajesVisibles.forEach(msg => {
      const fecha = new Date(msg.timestamp).toLocaleDateString('es-ES');
      if (!grupos[fecha]) grupos[fecha] = [];
      grupos[fecha].push(msg);
    });
    return grupos;
  }, [mensajesVisibles]);

  return (
    <div className="flex flex-col h-[500px] bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
      {/* Selector de canal */}
      <div className="flex gap-2 p-4 border-b border-slate-200 dark:border-slate-700">
        <button
          onClick={() => setTipoCanal(TipoCanalChat.GENERAL)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            tipoCanal === TipoCanalChat.GENERAL
              ? 'bg-blue-600 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          <Globe size={16} />
          <span>General</span>
        </button>

        {esProfesor && (
          <button
            onClick={() => setTipoCanal(TipoCanalChat.PRIVADO)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              tipoCanal === TipoCanalChat.PRIVADO
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            }`}
          >
            <Lock size={16} />
            <span>Privado</span>
          </button>
        )}
      </div>

      {/* Área de mensajes */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {Object.entries(mensajesPorFecha).map(([fecha, msgs]) => (
            <div key={fecha}>
              {/* Divisor de fecha */}
              <div className="flex items-center justify-center my-4">
                <div className="h-px bg-slate-200 dark:bg-slate-700 flex-1"></div>
                <span className="px-3 text-xs text-slate-500 dark:text-slate-400">{fecha}</span>
                <div className="h-px bg-slate-200 dark:bg-slate-700 flex-1"></div>
              </div>

              {/* Mensajes */}
              <motion.div className="space-y-3">
                {msgs.map((msg, idx) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`flex gap-3 ${msg.autor_id === usuarioActualId ? 'flex-row-reverse' : ''}`}
                  >
                    {/* Avatar */}
                    <UserAvatar
                      userId={msg.autor_id}
                      nombres={msg.autor_nombre.split(' ')[0]}
                      apellidos={msg.autor_nombre.split(' ')[1] || ''}
                      size="sm"
                    />

                    {/* Mensaje */}
                    <div
                      className={`flex-1 max-w-xs ${
                        msg.autor_id === usuarioActualId ? 'items-end flex flex-col' : ''
                      }`}
                    >
                      <div
                        className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                          msg.autor_id === usuarioActualId
                            ? 'bg-blue-600 text-white rounded-br-none'
                            : 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white rounded-bl-none'
                        }`}
                      >
                        {msg.tipo_canal === TipoCanalChat.PRIVADO && !esProfesor && (
                          <Lock size={14} className="flex-shrink-0" />
                        )}
                        <span className="break-words text-sm">{msg.contenido}</span>
                      </div>
                      <span className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        {new Date(msg.timestamp).toLocaleTimeString('es-ES', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Área de entrada */}
      <div className="border-t border-slate-200 dark:border-slate-700 p-4 flex gap-2">
        <textarea
          value={contenido}
          onChange={(e) => setContenido(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleEnviar();
            }
          }}
          placeholder={tipoCanal === TipoCanalChat.PRIVADO ? 'Mensaje privado...' : 'Escribe un mensaje...'}
          className="flex-1 p-2 border border-slate-200 dark:border-slate-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
          rows={2}
          disabled={loading || enviando}
        />
        <button
          onClick={handleEnviar}
          disabled={!contenido.trim() || loading || enviando}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};
