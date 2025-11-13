/**
 * Componente VideollamadasList
 * 
 * @module components/VideollamadasList
 * @description Lista de videollamadas activas y recientes.
 * Permite crear, unirse y gestionar videollamadas.
 */

import { useState } from 'react';
import { Video, Plus, Users, Clock, Check, X } from 'lucide-react';
import { useVideollamadas } from '../../../hooks/useVideollamada';
import type { Videollamada, TipoLlamada, EstadoVideollamada } from '../../../types/videollamada.types';
import { formatearDuracion } from '../../../services/videollamadas.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

// ==================== TIPOS ====================

interface VideollamadasListProps {
  /** ID de sala de chat (filtro opcional) */
  salaChatId?: string;
  
  /** Solo mostrar activas */
  soloActivas?: boolean;
  
  /** Callback al seleccionar videollamada */
  onSelectVideollamada: (videollamada: Videollamada) => void;
  
  /** Clase CSS adicional */
  className?: string;
}

// ==================== COMPONENTE ====================

export function VideollamadasList({
  salaChatId,
  soloActivas = true,
  onSelectVideollamada,
  className = '',
}: VideollamadasListProps) {
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const {
    videollamadas,
    total,
    isLoading,
    error,
    refetch,
    crear,
    isCreando,
  } = useVideollamadas({
    sala_chat_id: salaChatId,
    solo_activas: soloActivas,
    limit: 20,
  });

  // ==================== HANDLERS ====================

  const handleCrearVideollamada = async (tipoLlamada: TipoLlamada) => {
    try {
      const nueva = await crear({
        tipo_llamada: tipoLlamada,
        sala_chat_id: salaChatId,
        configuracion: {
          max_participantes: 50,
          permitir_grabacion: true,
          permitir_chat: true,
          permitir_compartir_pantalla: true,
        },
      });
      
      setMostrarFormulario(false);
      onSelectVideollamada(nueva);
    } catch (err) {
      console.error('Error creando videollamada:', err);
      alert('Error al crear videollamada. Inténtalo de nuevo.');
    }
  };

  // ==================== RENDER ====================

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Video className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-800">
            Videollamadas
            {total > 0 && (
              <span className="ml-2 text-sm text-gray-500">
                ({total})
              </span>
            )}
          </h2>
        </div>

        <button
          onClick={() => setMostrarFormulario(!mostrarFormulario)}
          disabled={isCreando}
          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          title="Nueva videollamada"
        >
          {isCreando ? (
            <span className="animate-spin">⏳</span>
          ) : (
            <Plus className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Formulario crear */}
      {mostrarFormulario && (
        <div className="p-4 bg-blue-50 border-b border-blue-200">
          <p className="text-sm text-gray-700 mb-3">
            Selecciona el tipo de llamada:
          </p>
          <div className="flex space-x-2">
            <button
              onClick={() => handleCrearVideollamada('video' as TipoLlamada)}
              disabled={isCreando}
              className="flex-1 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              <Video className="w-5 h-5" />
              <span>Videollamada</span>
            </button>
            <button
              onClick={() => handleCrearVideollamada('voz' as TipoLlamada)}
              disabled={isCreando}
              className="flex-1 p-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              <span>🎙️</span>
              <span>Solo audio</span>
            </button>
          </div>
        </div>
      )}

      {/* Lista */}
      <div className="max-h-96 overflow-y-auto">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            <div className="animate-spin text-4xl mb-2">⏳</div>
            <p>Cargando videollamadas...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">
            <div className="text-4xl mb-2">❌</div>
            <p>Error al cargar videollamadas</p>
            <button
              onClick={() => refetch()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              Reintentar
            </button>
          </div>
        ) : videollamadas.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-2">📹</div>
            <p>No hay videollamadas {soloActivas ? 'activas' : 'disponibles'}</p>
            <p className="text-sm mt-2">
              Crea una nueva videollamada para comenzar
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {videollamadas.map((videollamada) => (
              <VideollamadaCard
                key={videollamada.id}
                videollamada={videollamada}
                onClick={() => onSelectVideollamada(videollamada)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== COMPONENTE CARD ====================

interface VideollamadaCardProps {
  videollamada: Videollamada;
  onClick: () => void;
}

function VideollamadaCard({ videollamada, onClick }: VideollamadaCardProps) {
  const esActiva = videollamada.estado === 'ACTIVA';
  const fechaInicio = new Date(videollamada.fecha_inicio);
  const participantes = videollamada.participantes?.length || 0;

  return (
    <div
      onClick={onClick}
      className="p-4 hover:bg-gray-50 cursor-pointer transition"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Título */}
          <div className="flex items-center space-x-2 mb-2">
            {videollamada.tipo_llamada === 'video' ? (
              <Video className="w-4 h-4 text-blue-600" />
            ) : (
              <span>🎙️</span>
            )}
            <h3 className="font-medium text-gray-800">
              {videollamada.jitsi_room_name}
            </h3>
            <EstadoBadge estado={videollamada.estado as EstadoVideollamada} />
          </div>

          {/* Info */}
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Users className="w-4 h-4" />
              <span>{participantes} participante{participantes !== 1 && 's'}</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4" />
              <span>
                {format(fechaInicio, 'HH:mm', { locale: es })}
              </span>
            </div>

            {videollamada.duracion_segundos && (
              <span>
                ⏱️ {formatearDuracion(videollamada.duracion_segundos)}
              </span>
            )}
          </div>
        </div>

        {/* Botón unirse */}
        {esActiva && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm"
          >
            Unirse
          </button>
        )}
      </div>
    </div>
  );
}

// ==================== BADGE ESTADO ====================

function EstadoBadge({ estado }: { estado: EstadoVideollamada }) {
  const configs = {
    ACTIVA: { color: 'bg-green-100 text-green-800', icon: '🟢', label: 'Activa' },
    PROGRAMADA: { color: 'bg-blue-100 text-blue-800', icon: '📅', label: 'Programada' },
    FINALIZADA: { color: 'bg-gray-100 text-gray-800', icon: '✅', label: 'Finalizada' },
    CANCELADA: { color: 'bg-red-100 text-red-800', icon: '❌', label: 'Cancelada' },
  };

  const config = configs[estado] || configs.FINALIZADA;

  return (
    <span className={`px-2 py-1 rounded text-xs ${config.color}`}>
      {config.icon} {config.label}
    </span>
  );
}

// ==================== EXPORTS ====================

export default VideollamadasList;
