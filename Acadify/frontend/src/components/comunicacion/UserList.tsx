import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { 
  UserIcon,
  ShieldCheckIcon,
  StarIcon,
  ChatBubbleLeftIcon,
  AtSymbolIcon
} from '@heroicons/react/24/outline';
import { 
  UserIcon as UserIconSolid,
  ShieldCheckIcon as ShieldCheckIconSolid 
} from '@heroicons/react/24/solid';

interface Participante {
  id: string;
  usuario_id: string;
  nombre: string;
  avatar?: string;
  es_admin: boolean;
  es_moderador: boolean;
  esta_activo: boolean;
  ultimo_acceso?: string;
  puede_escribir: boolean;
}

interface UserListProps {
  participantes: Participante[];
  onlineUsers: string[];
  onMention: (usuario: string) => void;
  onPrivateMessage?: (usuarioId: string) => void;
  currentUserId?: string;
}

export const UserList: React.FC<UserListProps> = ({
  participantes,
  onlineUsers,
  onMention,
  onPrivateMessage,
  currentUserId
}) => {
  const [filter, setFilter] = useState<'todos' | 'conectados' | 'admins'>('conectados');

  // Filtrar y ordenar participantes
  const filteredParticipants = participantes
    .filter(p => {
      switch (filter) {
        case 'conectados':
          return onlineUsers.includes(p.usuario_id);
        case 'admins':
          return p.es_admin || p.es_moderador;
        case 'todos':
        default:
          return true;
      }
    })
    .sort((a, b) => {
      // Primero admins/moderadores
      if (a.es_admin && !b.es_admin) return -1;
      if (!a.es_admin && b.es_admin) return 1;
      if (a.es_moderador && !b.es_moderador) return -1;
      if (!a.es_moderador && b.es_moderador) return 1;
      
      // Luego por estado en línea
      const aOnline = onlineUsers.includes(a.usuario_id);
      const bOnline = onlineUsers.includes(b.usuario_id);
      if (aOnline && !bOnline) return -1;
      if (!aOnline && bOnline) return 1;
      
      // Finalmente por nombre
      return a.nombre.localeCompare(b.nombre);
    });

  // Contar diferentes tipos de usuarios
  const counts = {
    total: participantes.length,
    conectados: participantes.filter(p => onlineUsers.includes(p.usuario_id)).length,
    admins: participantes.filter(p => p.es_admin || p.es_moderador).length
  };

  const renderUserAvatar = (participante: Participante) => {
    const isOnline = onlineUsers.includes(participante.usuario_id);
    const isCurrentUser = participante.usuario_id === currentUserId;
    
    return (
      <div className="relative flex-shrink-0">
        <div className="w-10 h-10 rounded-full overflow-hidden bg-gray-200 flex items-center justify-center">
          {participante.avatar ? (
            <img 
              src={participante.avatar} 
              alt={participante.nombre}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-sm font-semibold text-gray-600">
              {participante.nombre.charAt(0).toUpperCase()}
            </span>
          )}
        </div>
        
        {/* Indicador de estado online */}
        <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
          isOnline ? 'bg-green-400' : 'bg-gray-300'
        }`}></div>
        
        {/* Indicador de usuario actual */}
        {isCurrentUser && (
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs">•</span>
          </div>
        )}
      </div>
    );
  };

  const renderUserBadges = (participante: Participante) => {
    return (
      <div className="flex items-center space-x-1 ml-2">
        {participante.es_admin && (
          <div className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium flex items-center">
            <ShieldCheckIconSolid className="h-3 w-3 mr-1" />
            Admin
          </div>
        )}
        {participante.es_moderador && !participante.es_admin && (
          <div className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full text-xs font-medium flex items-center">
            <StarIcon className="h-3 w-3 mr-1" />
            Mod
          </div>
        )}
        {!participante.puede_escribir && (
          <div className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs font-medium">
            Solo lectura
          </div>
        )}
      </div>
    );
  };

  const renderUserActions = (participante: Participante) => {
    if (participante.usuario_id === currentUserId) {
      return null;
    }

    return (
      <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={() => onMention(participante.nombre)}
          className="p-1 hover:bg-gray-100 rounded text-gray-500 hover:text-gray-700"
          title="Mencionar"
        >
          <AtSymbolIcon className="h-4 w-4" />
        </button>
        
        {onPrivateMessage && (
          <button
            onClick={() => onPrivateMessage(participante.usuario_id)}
            className="p-1 hover:bg-gray-100 rounded text-gray-500 hover:text-gray-700"
            title="Mensaje privado"
          >
            <ChatBubbleLeftIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Participantes</h3>
        
        {/* Filtros */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setFilter('conectados')}
            className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'conectados'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            En línea ({counts.conectados})
          </button>
          <button
            onClick={() => setFilter('todos')}
            className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'todos'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Todos ({counts.total})
          </button>
          {counts.admins > 0 && (
            <button
              onClick={() => setFilter('admins')}
              className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === 'admins'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Staff ({counts.admins})
            </button>
          )}
        </div>
      </div>

      {/* Lista de usuarios */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredParticipants.length === 0 ? (
          <div className="text-center py-8">
            <UserIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {filter === 'conectados' ? 'Nadie está conectado' : 'No hay participantes'}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredParticipants.map((participante) => {
              const isOnline = onlineUsers.includes(participante.usuario_id);
              const isCurrentUser = participante.usuario_id === currentUserId;
              
              return (
                <div
                  key={participante.id}
                  className={`group flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors ${
                    isCurrentUser ? 'bg-blue-50 border border-blue-200' : ''
                  }`}
                >
                  <div className="flex items-center flex-1 min-w-0">
                    {/* Avatar */}
                    {renderUserAvatar(participante)}
                    
                    {/* Info del usuario */}
                    <div className="ml-3 flex-1 min-w-0">
                      <div className="flex items-center">
                        <p className={`text-sm font-medium truncate ${
                          isCurrentUser ? 'text-blue-900' : 'text-gray-900'
                        }`}>
                          {participante.nombre}
                          {isCurrentUser && (
                            <span className="text-blue-600 ml-2 text-xs">(tú)</span>
                          )}
                        </p>
                        {renderUserBadges(participante)}
                      </div>
                      
                      {/* Estado */}
                      <p className="text-xs text-gray-500 mt-1">
                        {isOnline ? (
                          <span className="text-green-600 font-medium">En línea</span>
                        ) : participante.ultimo_acceso ? (
                          `Visto ${formatDistanceToNow(new Date(participante.ultimo_acceso), {
                            addSuffix: true,
                            locale: es,
                          })}`
                        ) : (
                          'Desconectado'
                        )}
                      </p>
                    </div>
                    
                    {/* Acciones */}
                    {renderUserActions(participante)}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer con estadísticas */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>{counts.conectados} de {counts.total} conectados</span>
          {counts.admins > 0 && (
            <span>{counts.admins} administradores</span>
          )}
        </div>
      </div>
    </div>
  );
};