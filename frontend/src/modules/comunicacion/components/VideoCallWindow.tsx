/**
 * Componente VideoCallWindow
 * 
 * @module components/VideoCallWindow
 * @description Ventana completa de videollamada con controles,
 * lista de participantes y monitoreo de calidad de conexión.
 */

import { useState, useEffect } from 'react';
import { X, Users, Signal, Mic, MicOff, Video, VideoOff, PhoneOff } from 'lucide-react';
import JitsiMeeting from './JitsiMeeting';
import { useVideollamada, useCalidadConexion } from '../../../hooks/useVideollamada';
import type { Participante } from '../../../types/videollamada.types';
import { formatearDuracion, obtenerColorCalidad, obtenerIconoCalidad } from '../../../services/videollamadas.service';

// ==================== TIPOS ====================

interface VideoCallWindowProps {
  /** ID de la videollamada */
  videollamadaId: string;
  
  /** Nombre para mostrar del usuario */
  displayName: string;
  
  /** Email del usuario (opcional) */
  email?: string;
  
  /** Función al cerrar */
  onClose: () => void;
  
  /** Clase CSS adicional */
  className?: string;
}

// ==================== COMPONENTE ====================

export function VideoCallWindow({
  videollamadaId,
  displayName,
  email,
  onClose,
  className = '',
}: VideoCallWindowProps) {
  const [showParticipants, setShowParticipants] = useState(false);
  const [participanteId, setParticipanteId] = useState<string | null>(null);
  const [jitsiParticipantId, setJitsiParticipantId] = useState<string | null>(null);
  const [audioMuted, setAudioMuted] = useState(false);
  const [videoMuted, setVideoMuted] = useState(false);
  const [connectionQuality, setConnectionQuality] = useState<number>(100);
  const [duracionActual, setDuracionActual] = useState(0);

  // Hooks
  const {
    videollamada,
    participantes,
    isLoading,
    error,
    unirse,
    salir,
    finalizar,
    refetchParticipantes,
  } = useVideollamada(videollamadaId);

  const {
    calidad,
    metricas,
    reportarMetricas,
  } = useCalidadConexion(participanteId);

  // ==================== EFECTOS ====================

  // Unirse automáticamente al cargar
  useEffect(() => {
    const unirseAutomatico = async () => {
      try {
        const participante = await unirse(false);
        setParticipanteId(participante.id);
        console.log('✅ Unido a videollamada:', participante);
      } catch (err) {
        console.error('Error al unirse:', err);
      }
    };

    unirseAutomatico();
  }, [unirse]);

  // Actualizar duración cada segundo
  useEffect(() => {
    if (!videollamada?.fecha_inicio) return;

    const interval = setInterval(() => {
      const inicio = new Date(videollamada.fecha_inicio).getTime();
      const ahora = Date.now();
      const segundos = Math.floor((ahora - inicio) / 1000);
      setDuracionActual(segundos);
    }, 1000);

    return () => clearInterval(interval);
  }, [videollamada?.fecha_inicio]);

  // Refrescar participantes periódicamente
  useEffect(() => {
    const interval = setInterval(() => {
      refetchParticipantes();
    }, 10000); // cada 10 segundos

    return () => clearInterval(interval);
  }, [refetchParticipantes]);

  // ==================== HANDLERS ====================

  const handleClose = async () => {
    try {
      await salir();
      onClose();
    } catch (err) {
      console.error('Error al salir:', err);
      onClose();
    }
  };

  const handleJoin = (participantId: string) => {
    console.log('Usuario se unió a Jitsi:', participantId);
    setJitsiParticipantId(participantId);
  };

  const handleConnectionQualityChanged = (quality: { participantId: string; connectionQuality: number }) => {
    if (quality.participantId === jitsiParticipantId) {
      setConnectionQuality(quality.connectionQuality);
      
      // Calcular métricas aproximadas basadas en calidad (0-100)
      const latencia = Math.max(20, 300 - (quality.connectionQuality * 2.8));
      const perdida = Math.max(0, 5 - (quality.connectionQuality * 0.05));
      
      reportarMetricas(latencia, perdida);
    }
  };

  // ==================== RENDER ====================

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center h-screen bg-gray-900 ${className}`}>
        <div className="text-center text-white">
          <div className="animate-spin text-6xl mb-4">⏳</div>
          <p>Cargando videollamada...</p>
        </div>
      </div>
    );
  }

  if (error || !videollamada) {
    return (
      <div className={`flex items-center justify-center h-screen bg-gray-900 ${className}`}>
        <div className="text-center text-white">
          <div className="text-6xl mb-4">❌</div>
          <h3 className="text-xl font-bold mb-2">Error</h3>
          <p className="mb-4">{error?.message || 'Videollamada no encontrada'}</p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition"
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  }

  const esModerador = participantes.some(
    (p) => p.id === participanteId && p.es_moderador
  );

  return (
    <div className={`relative h-screen bg-gray-900 flex flex-col ${className}`}>
      {/* Header */}
      <div className="bg-gray-800 p-4 flex items-center justify-between shadow-lg z-10">
        <div className="flex items-center space-x-4">
          <h2 className="text-white text-lg font-semibold">
            {videollamada.jitsi_room_name}
          </h2>
          
          {/* Duración */}
          <div className="text-gray-300 text-sm">
            ⏱️ {formatearDuracion(duracionActual)}
          </div>

          {/* Calidad de conexión */}
          {calidad && (
            <div className="flex items-center space-x-2">
              <Signal className={`w-4 h-4 ${obtenerColorCalidad(calidad)}`} />
              <span className={`text-sm ${obtenerColorCalidad(calidad)}`}>
                {obtenerIconoCalidad(calidad)} {calidad.toUpperCase()}
              </span>
              {metricas && (
                <span className="text-xs text-gray-400">
                  ({Math.round(metricas.latencia)}ms, {metricas.perdidaPaquetes.toFixed(1)}%)
                </span>
              )}
            </div>
          )}

          {/* Badge moderador */}
          {esModerador && (
            <span className="px-2 py-1 bg-yellow-600 text-white text-xs rounded">
              ⭐ Moderador
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* Botón participantes */}
          <button
            onClick={() => setShowParticipants(!showParticipants)}
            className="p-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition flex items-center space-x-2"
          >
            <Users className="w-4 h-4" />
            <span>{participantes.length}</span>
          </button>

          {/* Botón cerrar */}
          <button
            onClick={handleClose}
            className="p-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            title="Salir de la videollamada"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex relative">
        {/* Jitsi Container */}
        <div className="flex-1">
          <JitsiMeeting
            roomName={videollamada.jitsi_room_name}
            userInfo={{
              displayName,
              email,
            }}
            width="100%"
            height="100%"
            onJoin={handleJoin}
            onLeave={handleClose}
            onAudioMuteStatusChanged={setAudioMuted}
            onVideoMuteStatusChanged={setVideoMuted}
            onConnectionQualityChanged={handleConnectionQualityChanged}
            onError={(err) => console.error('Jitsi Error:', err)}
          />
        </div>

        {/* Panel lateral de participantes */}
        {showParticipants && (
          <div className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
            <div className="p-4">
              <h3 className="text-white font-semibold mb-4 flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Participantes ({participantes.length})
              </h3>
              
              <div className="space-y-2">
                {participantes.map((participante) => (
                  <ParticipanteCard
                    key={participante.id}
                    participante={participante}
                    isCurrentUser={participante.id === participanteId}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer con controles (opcional, Jitsi ya tiene controles) */}
      <div className="bg-gray-800 p-2 flex items-center justify-center space-x-2 text-white text-xs">
        <span className={audioMuted ? 'text-red-400' : 'text-green-400'}>
          {audioMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </span>
        <span className={videoMuted ? 'text-red-400' : 'text-green-400'}>
          {videoMuted ? <VideoOff className="w-4 h-4" /> : <Video className="w-4 h-4" />}
        </span>
      </div>
    </div>
  );
}

// ==================== COMPONENTE PARTICIPANTE ====================

interface ParticipanteCardProps {
  participante: Participante;
  isCurrentUser: boolean;
}

function ParticipanteCard({ participante, isCurrentUser }: ParticipanteCardProps) {
  const duracion = participante.duracion_segundos || 0;

  return (
    <div className="bg-gray-700 rounded p-3 text-white">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm">
            👤
          </div>
          <div>
            <p className="font-medium text-sm">
              Usuario {participante.usuario_id.slice(0, 8)}
              {isCurrentUser && <span className="text-yellow-400 ml-1">(Tú)</span>}
            </p>
            {participante.es_moderador && (
              <span className="text-xs text-yellow-400">⭐ Moderador</span>
            )}
          </div>
        </div>
        
        {participante.calidad_conexion && (
          <span className={`text-xs ${obtenerColorCalidad(participante.calidad_conexion)}`}>
            {obtenerIconoCalidad(participante.calidad_conexion)}
          </span>
        )}
      </div>
      
      <p className="text-xs text-gray-400">
        En llamada: {formatearDuracion(duracion)}
      </p>
    </div>
  );
}

// ==================== EXPORTS ====================

export default VideoCallWindow;
