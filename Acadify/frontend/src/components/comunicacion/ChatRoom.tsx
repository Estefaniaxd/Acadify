import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket.js';
import { MessageList } from './MessageList.js';
import { MessageInput } from './MessageInput.js';
import { UserList } from './UserList.js';
import { NotificationCenter } from './NotificationCenter.js';
import { 
  ChatBubbleLeftRightIcon, 
  UserGroupIcon, 
  BellIcon,
  Cog6ToothIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface SalaChat {
  id: string;
  nombre: string;
  descripcion?: string;
  tipo_sala: 'curso' | 'grupo' | 'tarea' | 'privado' | 'general';
  es_publica: boolean;
  permite_archivos: boolean;
  permite_menciones: boolean;
  permite_hilos: boolean;
  participantes_conectados: number;
  ultimo_mensaje_fecha?: string;
}

interface Participante {
  id: string;
  usuario_id: string;
  nombre: string;
  avatar?: string;
  es_admin: boolean;
  es_moderador: boolean;
  esta_activo: boolean;
  ultimo_acceso?: string;
}

interface ChatRoomProps {
  salaId: string;
  usuarioId: string;
  onClose?: () => void;
}

export const ChatRoom: React.FC<ChatRoomProps> = ({ 
  salaId, 
  usuarioId,
  onClose 
}) => {
  const [sala, setSala] = useState<SalaChat | null>(null);
  const [participantes, setParticipantes] = useState<Participante[]>([]);
  const [showUserList, setShowUserList] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // WebSocket connection para mensajes en tiempo real
  const { 
    messages, 
    sendMessage, 
    isConnected, 
    typing,
    onlineUsers 
  } = useWebSocket(`/chat/${salaId}`, usuarioId);

  // Cargar información de la sala
  useEffect(() => {
    const fetchSalaInfo = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/comunicacion/salas/${salaId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });
        
        if (!response.ok) {
          throw new Error('Error al cargar la sala');
        }
        
        const salaData = await response.json();
        setSala(salaData);
        
        // Cargar participantes
        const participantesResponse = await fetch(`/api/comunicacion/salas/${salaId}/participantes`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });
        
        if (participantesResponse.ok) {
          const participantesData = await participantesResponse.json();
          setParticipantes(participantesData);
        }
        
      } catch (error) {
        console.error('Error cargando sala:', error);
        setError('No se pudo cargar la información de la sala');
      } finally {
        setLoading(false);
      }
    };

    if (salaId) {
      fetchSalaInfo();
    }
  }, [salaId]);

  // Manejar envío de mensajes
  const handleSendMessage = async (contenido: string, archivos?: File[]) => {
    try {
      // Enviar mensaje través del WebSocket
      await sendMessage({
        contenido,
        tipo_mensaje: archivos?.length ? 'archivo' : 'texto',
        archivos
      });
    } catch (error) {
      console.error('Error enviando mensaje:', error);
    }
  };

  // Manejar menciones (@rutilio, @username)
  const handleMention = (tipo: 'rutilio' | 'usuario', usuario?: string) => {
    if (tipo === 'rutilio') {
      return '@rutilio ';
    } else if (usuario) {
      return `@${usuario} `;
    }
    return '';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Cargando chat...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <ChatBubbleLeftRightIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header de la sala */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-400' : 'bg-red-400'
            }`}></div>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{sala?.nombre}</h2>
            {sala?.descripcion && (
              <p className="text-sm text-gray-500">{sala.descripcion}</p>
            )}
            <div className="flex items-center space-x-4 text-xs text-gray-400">
              <span>{participantes.length} participantes</span>
              <span>{onlineUsers.length} en línea</span>
              {typing.length > 0 && (
                <span className="text-blue-500">
                  {typing.join(', ')} escribiendo...
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Botón de notificaciones */}
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
          >
            <BellIcon className="h-5 w-5" />
          </button>
          
          {/* Botón de lista de usuarios */}
          <button
            onClick={() => setShowUserList(!showUserList)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
          >
            <UserGroupIcon className="h-5 w-5" />
          </button>
          
          {/* Botón de configuración */}
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100">
            <Cog6ToothIcon className="h-5 w-5" />
          </button>
          
          {/* Botón de cerrar */}
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      {/* Contenido principal */}
      <div className="flex flex-1 overflow-hidden">
        {/* Lista de mensajes */}
        <div className="flex-1 flex flex-col">
          <MessageList
            messages={messages}
            currentUserId={usuarioId}
            salaId={salaId}
            onMention={handleMention}
          />
          
          <MessageInput
            onSendMessage={handleSendMessage}
            onMention={handleMention}
            participantes={participantes}
            permiteMenciones={sala?.permite_menciones ?? true}
            permiteArchivos={sala?.permite_archivos ?? true}
            permiteHilos={sala?.permite_hilos ?? true}
          />
        </div>

        {/* Panel lateral: Lista de usuarios */}
        {showUserList && (
          <div className="w-64 border-l border-gray-200 bg-gray-50">
            <UserList
              participantes={participantes}
              onlineUsers={onlineUsers}
              onMention={(usuario: any) => handleMention('usuario', usuario)}
            />
          </div>
        )}
      </div>

      {/* Notificaciones */}
      {showNotifications && (
        <div className="absolute top-16 right-4 w-80 z-50">
          <NotificationCenter
            usuarioId={usuarioId}
            salaId={salaId}
            onClose={() => setShowNotifications(false)}
          />
        </div>
      )}
    </div>
  );
};