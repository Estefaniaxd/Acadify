import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, MessageCircle, Lock, Globe, Loader2 } from 'lucide-react';

interface Mensaje {
  id: string;
  autor: {
    id: string;
    nombre: string;
    rol: 'docente' | 'estudiante';
    avatar?: string;
  };
  contenido: string;
  privado: boolean;
  timestamp: string;
  reacciones?: Record<string, number>;
}

interface TareaChatProps {
  entregaId: string;
  tareaId: string;
  mensajesInicial?: Mensaje[];
  usuarioActual?: {
    id: string;
    nombre: string;
    rol: 'docente' | 'estudiante';
  };
  onMensajeEnviado?: (mensaje: string, privado: boolean) => void;
  readOnly?: boolean;
}

/**
 * 💬 TareaChat - Sistema de comunicación bidireccional entre profesor y estudiante
 * 
 * Características:
 * - Mensajes públicos (GENERAL) y privados
 * - Indicador visual de privacidad
 * - Reacciones con emojis
 * - Scroll automático al nuevo mensaje
 * - Timestamps legibles
 * - Estados: cargando, enviado, error
 */
export const TareaChat: React.FC<TareaChatProps> = ({
  entregaId,
  tareaId,
  mensajesInicial = [],
  usuarioActual,
  onMensajeEnviado,
  readOnly = false,
}) => {
  const [mensajes, setMensajes] = useState<Mensaje[]>(mensajesInicial);
  const [inputValue, setInputValue] = useState('');
  const [privado, setPrivado] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [filtroPrivacidad, setFiltroPrivacidad] = useState<'todos' | 'publicos' | 'privados'>('todos');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll automático al nuevo mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [mensajes]);

  const handleEnviarMensaje = async () => {
    if (!inputValue.trim() || !usuarioActual) return;

    const nuevoMensaje: Mensaje = {
      id: `msg-${Date.now()}`,
      autor: {
        id: usuarioActual.id,
        nombre: usuarioActual.nombre,
        rol: usuarioActual.rol,
      },
      contenido: inputValue.trim(),
      privado,
      timestamp: new Date().toISOString(),
    };

    setEnviando(true);

    try {
      // Simular envío al backend
      await new Promise((resolve) => setTimeout(resolve, 500));

      setMensajes([...mensajes, nuevoMensaje]);
      setInputValue('');
      onMensajeEnviado?.(inputValue, privado);
      console.log('✅ Mensaje enviado:', nuevoMensaje);
    } catch (err) {
      console.error('❌ Error enviando mensaje:', err);
    } finally {
      setEnviando(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleEnviarMensaje();
    }
  };

  const handleReaccion = (mensajeId: string, emoji: string) => {
    setMensajes(
      mensajes.map((msg) => {
        if (msg.id === mensajeId) {
          const reacciones = msg.reacciones || {};
          reacciones[emoji] = (reacciones[emoji] || 0) + 1;
          return { ...msg, reacciones };
        }
        return msg;
      })
    );
  };

  const mensajesFiltrados = mensajes.filter((msg) => {
    if (filtroPrivacidad === 'publicos') return !msg.privado;
    if (filtroPrivacidad === 'privados') return msg.privado;
    return true;
  });

  const formatoTiempo = (timestamp: string) => {
    const fecha = new Date(timestamp);
    return fecha.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="w-full h-full flex flex-col bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <MessageCircle size={24} className="text-blue-600" />
            <div>
              <h3 className="font-bold text-gray-800">Chat de Tarea</h3>
              <p className="text-xs text-gray-600">
                Tarea: <code className="bg-gray-100 px-1">{tareaId}</code>
              </p>
            </div>
          </div>
          <div className="text-2xl font-bold text-blue-600">{mensajes.length}</div>
        </div>

        {/* Filtros */}
        <div className="flex gap-2">
          {(['todos', 'publicos', 'privados'] as const).map((filtro) => (
            <button
              key={filtro}
              onClick={() => setFiltroPrivacidad(filtro)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filtroPrivacidad === filtro
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {filtro === 'publicos'
                ? '🌐 Públicos'
                : filtro === 'privados'
                ? '🔒 Privados'
                : '📋 Todos'}
            </button>
          ))}
        </div>
      </div>

      {/* Mensajes */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {mensajesFiltrados.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MessageCircle size={48} className="mx-auto text-gray-300 mb-3" />
              <p className="text-sm">No hay mensajes aún en esta vista</p>
            </div>
          </div>
        ) : (
          mensajesFiltrados.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${
                msg.autor.id === usuarioActual?.id ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.autor.id !== usuarioActual?.id && (
                <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0 text-xs font-bold">
                  {msg.autor.nombre.charAt(0).toUpperCase()}
                </div>
              )}

              <div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                  msg.autor.id === usuarioActual?.id
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
                }`}
              >
                {/* Header del Mensaje */}
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="text-xs font-semibold">
                    {msg.autor.nombre}
                    {msg.autor.rol === 'docente' && (
                      <span className="ml-1 bg-yellow-200 text-yellow-800 px-1 rounded text-xs">
                        👨‍🏫
                      </span>
                    )}
                  </span>
                  <span className={`text-xs ${msg.autor.id === usuarioActual?.id ? 'text-blue-100' : 'text-gray-500'}`}>
                    {formatoTiempo(msg.timestamp)}
                  </span>
                </div>

                {/* Contenido */}
                <p className="text-sm leading-relaxed break-words whitespace-pre-wrap">{msg.contenido}</p>

                {/* Indicador de Privacidad */}
                {msg.privado && (
                  <div className="mt-2 inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-red-100 text-red-700">
                    <Lock size={12} />
                    Privado
                  </div>
                )}

                {/* Reacciones */}
                {msg.reacciones && Object.keys(msg.reacciones).length > 0 && (
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {Object.entries(msg.reacciones).map(([emoji, count]) => (
                      <button
                        key={emoji}
                        onClick={() => handleReaccion(msg.id, emoji)}
                        className={`text-xs px-2 py-1 rounded-full flex items-center gap-1 ${
                          msg.autor.id === usuarioActual?.id
                            ? 'bg-blue-700 hover:bg-blue-800'
                            : 'bg-gray-200 hover:bg-gray-300'
                        }`}
                      >
                        {emoji}
                        <span className="font-semibold">{count}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Botones de Reacción */}
              {!readOnly && (
                <div className="flex gap-1 opacity-0 hover:opacity-100 transition-opacity">
                  {['👍', '❤️', '😂', '😮', '😢'].map((emoji) => (
                    <button
                      key={emoji}
                      onClick={() => handleReaccion(msg.id, emoji)}
                      className="text-lg hover:scale-125 transition-transform"
                      title={`Reaccionar con ${emoji}`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              )}
            </motion.div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {!readOnly && (
        <div className="px-6 py-4 bg-white border-t border-gray-200 shadow-lg space-y-3">
          {/* Privacidad Toggle */}
          <button
            onClick={() => setPrivado(!privado)}
            className={`text-xs px-3 py-1 rounded-full font-medium flex items-center gap-1 transition-all ${
              privado
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
          >
            {privado ? (
              <>
                <Lock size={14} />
                🔒 Privado (solo docente)
              </>
            ) : (
              <>
                <Globe size={14} />
                🌐 Público (GENERAL)
              </>
            )}
          </button>

          {/* Mensaje Input */}
          <div className="flex gap-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={enviando}
              rows={3}
              placeholder="Escribe tu mensaje aquí... (Ctrl+Enter para enviar)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-none disabled:bg-gray-100 disabled:text-gray-500"
            />

            <button
              onClick={handleEnviarMensaje}
              disabled={enviando || !inputValue.trim()}
              className={`flex-shrink-0 px-4 py-2 rounded-lg font-medium flex items-center justify-center gap-2 transition-all ${
                enviando || !inputValue.trim()
                  ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
              }`}
            >
              {enviando ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span className="hidden sm:inline">Enviando</span>
                </>
              ) : (
                <>
                  <Send size={16} />
                  <span className="hidden sm:inline">Enviar</span>
                </>
              )}
            </button>
          </div>

          {/* Ayuda */}
          <p className="text-xs text-gray-600 text-center">
            💡 Usa <kbd className="bg-gray-200 px-1 rounded">Ctrl</kbd> + <kbd className="bg-gray-200 px-1 rounded">Enter</kbd> para enviar
          </p>
        </div>
      )}
    </div>
  );
};

export default TareaChat;
