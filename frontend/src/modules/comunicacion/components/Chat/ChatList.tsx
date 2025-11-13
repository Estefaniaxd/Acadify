/**
 * ChatList Component
 * ==================
 * Componente para mostrar la lista de salas de chat.
 * 
 * Responsabilidades:
 * - Mostrar lista de salas
 * - Búsqueda y filtrado
 * - Indicadores visuales (no leídos, último mensaje, estado online)
 * - Selección de sala activa
 * 
 * @author Acadify Team
 */

import React, { useState } from 'react';
import { Search, MessageSquare, Users, Video } from 'lucide-react';
import { SalaChat, TipoSala } from '../../../../types/communication';

interface ChatListProps {
  salas: SalaChat[];
  salaActiva: string | null;
  onSelectSala: (salaId: string) => void;
  usuariosOnline?: string[];
}

export const ChatList: React.FC<ChatListProps> = ({
  salas,
  salaActiva,
  onSelectSala,
  usuariosOnline: _usuariosOnline = []
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Filtrar salas por término de búsqueda
  const salasFiltradas = salas.filter(sala =>
    sala.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sala.ultimo_mensaje?.contenido.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Obtener ícono según tipo de sala
  const getTipoIcon = (tipo: TipoSala) => {
    switch (tipo) {
      case TipoSala.INDIVIDUAL:
        return MessageSquare;
      case TipoSala.GRUPO:
        return Users;
      case TipoSala.CLASE:
      case TipoSala.CURSO:
        return Video;
      default:
        return MessageSquare;
    }
  };

  // Obtener color del badge según tipo
  const getTipoColor = (tipo: TipoSala) => {
    switch (tipo) {
      case TipoSala.INDIVIDUAL:
        return 'from-blue-500 to-indigo-600';
      case TipoSala.GRUPO:
        return 'from-purple-500 to-pink-600';
      case TipoSala.CLASE:
      case TipoSala.CURSO:
        return 'from-green-500 to-teal-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  // Formatear timestamp
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    // Menos de 1 día: mostrar hora
    if (diff < 24 * 60 * 60 * 1000) {
      return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    }
    
    // Menos de 7 días: mostrar día de la semana
    if (diff < 7 * 24 * 60 * 60 * 1000) {
      return date.toLocaleDateString('es-ES', { weekday: 'short' });
    }
    
    // Más de 7 días: mostrar fecha
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col h-full">
      {/* Header con búsqueda */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Buscar chats..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm transition-all"
            aria-label="Buscar salas de chat"
          />
        </div>
      </div>

      {/* Lista de salas */}
      <div className="overflow-y-auto flex-1">
        {salasFiltradas.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <MessageSquare className="w-12 h-12 text-gray-400 mb-3" />
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              {searchTerm ? 'No se encontraron chats' : 'No tienes chats aún'}
            </p>
          </div>
        ) : (
          salasFiltradas.map((sala) => {
            const TipoIcon = getTipoIcon(sala.tipo);
            const colorClass = getTipoColor(sala.tipo);
            const isActiva = salaActiva === sala.id;
            const hasUnread = (sala.no_leidos ?? 0) > 0;

            return (
              <button
                key={sala.id}
                onClick={() => onSelectSala(sala.id)}
                className={`
                  w-full p-4 text-left transition-all duration-200
                  hover:bg-gray-50 dark:hover:bg-gray-700/50
                  ${isActiva 
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-r-4 border-blue-500' 
                    : 'border-r-4 border-transparent'
                  }
                  ${hasUnread ? 'font-medium' : ''}
                `}
                aria-label={`Chat con ${sala.nombre}`}
                aria-current={isActiva ? 'true' : 'false'}
              >
                <div className="flex items-start space-x-3">
                  {/* Avatar/Icon */}
                  <div className={`
                    w-12 h-12 bg-gradient-to-r ${colorClass} 
                    rounded-full flex items-center justify-center flex-shrink-0
                    ${hasUnread ? 'ring-2 ring-blue-400' : ''}
                  `}>
                    <TipoIcon className="w-6 h-6 text-white" />
                  </div>

                  {/* Contenido */}
                  <div className="flex-1 min-w-0">
                    {/* Header: nombre + timestamp */}
                    <div className="flex items-center justify-between mb-1">
                      <p className={`
                        text-sm truncate
                        ${hasUnread 
                          ? 'font-semibold text-gray-900 dark:text-white' 
                          : 'font-medium text-gray-700 dark:text-gray-300'
                        }
                      `}>
                        {sala.nombre}
                      </p>
                      <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {sala.ultima_actividad && formatTimestamp(sala.ultima_actividad)}
                        </span>
                        {hasUnread && (
                          <span className="bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                            {sala.no_leidos! > 9 ? '9+' : sala.no_leidos}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Último mensaje */}
                    {sala.ultimo_mensaje && (
                      <p className={`
                        text-xs truncate
                        ${hasUnread 
                          ? 'text-gray-600 dark:text-gray-400' 
                          : 'text-gray-500 dark:text-gray-500'
                        }
                      `}>
                        {sala.ultimo_mensaje.contenido}
                      </p>
                    )}

                    {/* Usuarios escribiendo */}
                    {sala.usuarios_escribiendo && sala.usuarios_escribiendo.length > 0 && (
                      <p className="text-xs text-blue-600 dark:text-blue-400 mt-1 flex items-center space-x-1">
                        <span className="animate-pulse">●</span>
                        <span>
                          {sala.usuarios_escribiendo.length === 1
                            ? 'escribiendo...'
                            : `${sala.usuarios_escribiendo.length} escribiendo...`
                          }
                        </span>
                      </p>
                    )}

                    {/* Participantes (para grupos/clases) */}
                    {(sala.tipo === TipoSala.GRUPO || sala.tipo === TipoSala.CLASE) && 
                     sala.participantes && sala.participantes.length > 0 && (
                      <p className="text-xs text-gray-400 dark:text-gray-500 truncate mt-1">
                        {sala.participantes.length} participante{sala.participantes.length !== 1 ? 's' : ''}
                        {sala.usuarios_online && sala.usuarios_online > 0 && (
                          <span className="text-green-500 ml-1">
                            • {sala.usuarios_online} online
                          </span>
                        )}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ChatList;
