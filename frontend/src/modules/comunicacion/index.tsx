/**
 * Módulo de Comunicación - Refactorizado
 * =======================================
 * Centro de comunicación con chat en tiempo real.
 * 
 * Funcionalidades:
 * - Chat en tiempo real con WebSocket
 * - Gestión de salas (individuales, grupos, clases)
 * - Indicadores de escritura y presencia
 * - Archivos adjuntos y reacciones
 * 
 * Arquitectura:
 * - Componentes modulares (ChatList, ChatWindow, MessageBubble, MessageInput)
 * - Hooks personalizados (useChatWebSocket)
 * - Servicios de comunicación (chatService)
 * 
 * @author Acadify Team
 * @version 2.0 - Refactorizado con SOLID principles
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Video, Bell } from 'lucide-react';
import { ChatList, ChatWindow } from './components/Chat';
import { useChatWebSocket } from '../../hooks/useChatWebSocket';
import { getChatService } from '../../services/chatService';
import { SalaChat, TipoMensaje } from '../../types/communication';

// TODO: Obtener del contexto de autenticación
const USUARIO_ID_TEMP = 'user-123';
const TOKEN_TEMP = localStorage.getItem('token') || '';


export default function ModuloComunicacion() {
  // ========================================
  // Estado
  // ========================================
  const [activeTab, setActiveTab] = useState<'chats' | 'videollamadas' | 'notificaciones'>('chats');
  const [salas, setSalas] = useState<SalaChat[]>([]);
  const [salaActiva, setSalaActiva] = useState<string | null>(null);
  const [isLoadingSalas, setIsLoadingSalas] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ========================================
  // WebSocket Hook (solo si hay sala activa)
  // ========================================
  const chatWebSocketEnabled = !!salaActiva;
  const {
    mensajes,
    usuariosEscribiendo,
    usuariosOnline,
    isConnected,
    enviarMensaje,
    editarMensaje,
    eliminarMensaje,
    añadirReaccion,
    setEscribiendo
  } = useChatWebSocket({
    baseUrl: 'ws://localhost:8000',
    salaId: salaActiva || '',
    usuarioId: USUARIO_ID_TEMP,
    token: TOKEN_TEMP,
    autoConnect: chatWebSocketEnabled
  });

  // ========================================
  // Cargar salas al montar
  // ========================================
  useEffect(() => {
    cargarSalas();
  }, []);

  const cargarSalas = async () => {
    try {
      setIsLoadingSalas(true);
      setError(null);
      const chatService = getChatService();
      const salasData = await chatService.getSalas();
      setSalas(salasData);
    } catch (err) {
      console.error('Error al cargar salas:', err);
      setError('No se pudieron cargar los chats. Intenta de nuevo.');
    } finally {
      setIsLoadingSalas(false);
    }
  };

  // ========================================
  // Handlers
  // ========================================
  const handleSelectSala = (salaId: string) => {
    setSalaActiva(salaId);
  };

  const handleCloseSala = () => {
    setSalaActiva(null);
  };

  const handleSendMessage = async (contenido: string, archivos?: File[]) => {
    if (!salaActiva) return;

    try {
      if (archivos && archivos.length > 0) {
        // Si hay archivos, subir primero y luego enviar mensaje con URLs
        const chatService = getChatService();
        const urls = await chatService.subirArchivos(archivos, salaActiva);
        
        await enviarMensaje({
          contenido,
          tipo_mensaje: archivos[0].type.startsWith('image/') ? TipoMensaje.IMAGEN : TipoMensaje.ARCHIVO,
          archivos_urls: urls
        });
      } else {
        // Solo texto, usar WebSocket
        await enviarMensaje({
          contenido,
          tipo_mensaje: TipoMensaje.TEXTO
        });
      }
    } catch (err) {
      console.error('Error al enviar mensaje:', err);
    }
  };

  const handleEditMessage = async (mensajeId: string, nuevoContenido: string) => {
    try {
      await editarMensaje(mensajeId, nuevoContenido);
    } catch (err) {
      console.error('Error al editar mensaje:', err);
    }
  };

  const handleDeleteMessage = async (mensajeId: string) => {
    if (window.confirm('¿Estás seguro de eliminar este mensaje?')) {
      try {
        await eliminarMensaje(mensajeId);
      } catch (err) {
        console.error('Error al eliminar mensaje:', err);
      }
    }
  };

  const handleReactMessage = async (mensajeId: string, emoji: string) => {
    try {
      await añadirReaccion(mensajeId, emoji);
    } catch (err) {
      console.error('Error al reaccionar:', err);
    }
  };

  const handleTyping = (isTyping: boolean) => {
    setEscribiendo(isTyping);
  };

  // ========================================
  // Obtener sala activa
  // ========================================
  const salaActivaData = salas.find(s => s.id === salaActiva);

  // ========================================
  // Render
  // ========================================
  return (
    <div className="bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 min-h-screen">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Centro de Comunicación
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Chats, videollamadas y notificaciones en tiempo real
          </p>
          
          {/* Estado de conexión */}
          {salaActiva && (
            <div className="mt-2 flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {isConnected ? 'Conectado' : 'Desconectado'}
              </span>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap bg-white dark:bg-gray-800 rounded-xl p-2 mb-6 border border-gray-200 dark:border-gray-700">
          {[
            { key: 'chats', label: 'Chats', icon: MessageSquare },
            { key: 'videollamadas', label: 'Videollamadas', icon: Video },
            { key: 'notificaciones', label: 'Notificaciones', icon: Bell }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as 'chats' | 'videollamadas' | 'notificaciones')}
              className={`
                flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${activeTab === tab.key
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'chats' && (
            <motion.div
              key="chats"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-300px)]"
            >
              {/* Lista de Salas */}
              <div className="h-full">
                {isLoadingSalas ? (
                  <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                      <p className="text-gray-600 dark:text-gray-400">Cargando chats...</p>
                    </div>
                  </div>
                ) : error ? (
                  <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 flex items-center justify-center h-full">
                    <div className="text-center">
                      <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                      <button
                        onClick={cargarSalas}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                      >
                        Reintentar
                      </button>
                    </div>
                  </div>
                ) : (
                  <ChatList
                    salas={salas}
                    salaActiva={salaActiva}
                    onSelectSala={handleSelectSala}
                    usuariosOnline={usuariosOnline}
                  />
                )}
              </div>

              {/* Chat Activo */}
              <div className="lg:col-span-2 h-full">
                {salaActivaData ? (
                  <ChatWindow
                    sala={salaActivaData}
                    mensajes={mensajes}
                    usuarioId={USUARIO_ID_TEMP}
                    usuariosEscribiendo={usuariosEscribiendo}
                    usuariosOnline={usuariosOnline}
                    onClose={handleCloseSala}
                    onSendMessage={handleSendMessage}
                    onEditMessage={handleEditMessage}
                    onDeleteMessage={handleDeleteMessage}
                    onReactMessage={handleReactMessage}
                    onTyping={handleTyping}
                  />
                ) : (
                  <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 flex items-center justify-center h-full">
                    <div className="text-center p-8">
                      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full p-6 mb-4 inline-block">
                        <MessageSquare className="w-12 h-12 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        Selecciona un chat
                      </h3>
                      <p className="text-gray-500 dark:text-gray-400 max-w-sm">
                        Elige una conversación de la lista para comenzar a chatear
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'videollamadas' && (
            <motion.div
              key="videollamadas"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700 text-center"
            >
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full p-6 mb-4 inline-block">
                <Video className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Videollamadas
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Sistema de videollamadas en desarrollo (Fase 2)
              </p>
              <button
                disabled
                className="px-6 py-3 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
              >
                Próximamente
              </button>
            </motion.div>
          )}

          {activeTab === 'notificaciones' && (
            <motion.div
              key="notificaciones"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700 text-center"
            >
              <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-full p-6 mb-4 inline-block">
                <Bell className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Notificaciones
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Sistema de notificaciones en desarrollo (Fase 3)
              </p>
              <button
                disabled
                className="px-6 py-3 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
              >
                Próximamente
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}