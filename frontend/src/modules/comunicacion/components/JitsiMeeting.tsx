/**
 * Componente JitsiMeeting
 * 
 * @module components/JitsiMeeting
 * @description Componente wrapper para Jitsi Meet External API.
 * Maneja la inicialización, configuración y eventos de Jitsi.
 * 
 * Requiere: Script de Jitsi Meet External API cargado globalmente
 * <script src='https://meet.jit.si/external_api.js'></script>
 */

import { useEffect, useState, useRef } from 'react';
import type {
  JitsiMeetConfig,
  JitsiConfigOverwrite,
  JitsiInterfaceConfig,
  JitsiUserInfo,
  JitsiConnectionQuality
} from '../../../types/videollamada.types';

// ==================== TIPOS ====================

interface JitsiMeetingProps {
  /** Nombre de la sala Jitsi */
  roomName: string;
  
  /** Token JWT para autenticación */
  jwt?: string;
  
  /** Información del usuario */
  userInfo?: {
    displayName: string;
    email?: string;
    avatarURL?: string;
  };
  
  /** Configuración personalizada de Jitsi */
  configOverwrite?: JitsiMeetConfig['configOverwrite'];
  
  /** Configuración de interfaz personalizada */
  interfaceConfigOverwrite?: JitsiMeetConfig['interfaceConfigOverwrite'];
  
  /** Dominio de Jitsi (default: meet.jit.si) */
  domain?: string;
  
  /** Ancho del contenedor (default: 100%) */
  width?: string | number;
  
  /** Alto del contenedor (default: 100%) */
  height?: string | number;
  
  /** Clase CSS adicional */
  className?: string;
  
  // ==================== EVENTOS ====================
  
  /** Se ejecuta cuando la conferencia está lista */
  onReady?: () => void;
  
  /** Se ejecuta cuando el usuario se une a la conferencia */
  onJoin?: (participantId: string) => void;
  
  /** Se ejecuta cuando el usuario sale de la conferencia */
  onLeave?: () => void;
  
  /** Se ejecuta cuando un participante se une */
  onParticipantJoined?: (participant: { id: string; displayName: string }) => void;
  
  /** Se ejecuta cuando un participante sale */
  onParticipantLeft?: (participantId: string) => void;
  
  /** Se ejecuta cuando cambia el estado del audio */
  onAudioMuteStatusChanged?: (muted: boolean) => void;
  
  /** Se ejecuta cuando cambia el estado del video */
  onVideoMuteStatusChanged?: (muted: boolean) => void;
  
  /** Se ejecuta cuando cambia la calidad de conexión */
  onConnectionQualityChanged?: (quality: JitsiConnectionQuality) => void;
  
  /** Se ejecuta cuando ocurre un error */
  onError?: (error: Error) => void;
}

// ==================== TIPOS GLOBALES ====================

declare global {
  interface Window {
    JitsiMeetExternalAPI?: any;
  }
}

// ==================== COMPONENTE ====================

export function JitsiMeeting({
  roomName,
  jwt,
  userInfo,
  configOverwrite = {},
  interfaceConfigOverwrite = {},
  domain = 'meet.jit.si',
  width = '100%',
  height = '100%',
  className = '',
  onReady,
  onJoin,
  onLeave,
  onParticipantJoined,
  onParticipantLeft,
  onAudioMuteStatusChanged,
  onVideoMuteStatusChanged,
  onConnectionQualityChanged,
  onError,
}: JitsiMeetingProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [api, setApi] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // ==================== INICIALIZACIÓN ====================

  useEffect(() => {
    // Verificar que Jitsi External API esté disponible
    if (!window.JitsiMeetExternalAPI) {
      const err = new Error(
        'Jitsi Meet External API no está disponible. ' +
        'Asegúrate de incluir el script: ' +
        'https://meet.jit.si/external_api.js'
      );
      setError(err);
      onError?.(err);
      return;
    }

    // Verificar que el contenedor esté disponible
    if (!containerRef.current) {
      return;
    }

    // Configuración por defecto
    const defaultConfig: JitsiMeetConfig['configOverwrite'] = {
      startWithAudioMuted: false,
      startWithVideoMuted: false,
      enableWelcomePage: false,
      prejoinPageEnabled: false,
      disableDeepLinking: true,
      resolution: 720,
      constraints: {
        video: {
          height: { ideal: 720, max: 1080, min: 360 },
          width: { ideal: 1280, max: 1920, min: 640 },
        },
      },
      enableLayerSuspension: true,
      p2p: {
        enabled: false, // Desactivar P2P para salas grandes
      },
      ...configOverwrite,
    };

    const defaultInterfaceConfig: JitsiMeetConfig['interfaceConfigOverwrite'] = {
      TOOLBAR_BUTTONS: [
        'microphone',
        'camera',
        'closedcaptions',
        'desktop',
        'fullscreen',
        'fodeviceselection',
        'hangup',
        'chat',
        'recording',
        'livestreaming',
        'etherpad',
        'sharedvideo',
        'settings',
        'raisehand',
        'videoquality',
        'filmstrip',
        'stats',
        'shortcuts',
        'tileview',
        'select-background',
        'download',
        'help',
        'mute-everyone',
      ],
      SHOW_JITSI_WATERMARK: false,
      SHOW_WATERMARK_FOR_GUESTS: false,
      SHOW_BRAND_WATERMARK: false,
      MOBILE_APP_PROMO: false,
      ...interfaceConfigOverwrite,
    };

    // Crear instancia de Jitsi
    try {
      const jitsiAPI = new window.JitsiMeetExternalAPI(domain, {
        roomName,
        width,
        height,
        parentNode: containerRef.current,
        configOverwrite: defaultConfig,
        interfaceConfigOverwrite: defaultInterfaceConfig,
        jwt,
        userInfo: userInfo ? {
          displayName: userInfo.displayName,
          email: userInfo.email,
        } : undefined,
      });

      setApi(jitsiAPI);
      setIsLoading(false);

      // ==================== EVENT LISTENERS ====================

      // Ready
      jitsiAPI.addEventListener('videoConferenceJoined', (event: any) => {
        console.log('📹 Usuario se unió a la conferencia:', event);
        onJoin?.(event.id);
      });

      // Leave
      jitsiAPI.addEventListener('videoConferenceLeft', () => {
        console.log('📹 Usuario salió de la conferencia');
        onLeave?.();
      });

      // Ready to close
      jitsiAPI.addEventListener('readyToClose', () => {
        console.log('📹 Jitsi listo para cerrar');
        jitsiAPI.dispose();
        onLeave?.();
      });

      // Participant joined
      jitsiAPI.addEventListener('participantJoined', (event: any) => {
        console.log('👤 Participante se unió:', event);
        onParticipantJoined?.({
          id: event.id,
          displayName: event.displayName || 'Anónimo',
        });
      });

      // Participant left
      jitsiAPI.addEventListener('participantLeft', (event: any) => {
        console.log('👤 Participante salió:', event);
        onParticipantLeft?.(event.id);
      });

      // Audio mute status
      jitsiAPI.addEventListener('audioMuteStatusChanged', (event: any) => {
        console.log('🔇 Estado audio cambiado:', event.muted);
        onAudioMuteStatusChanged?.(event.muted);
      });

      // Video mute status
      jitsiAPI.addEventListener('videoMuteStatusChanged', (event: any) => {
        console.log('📹 Estado video cambiado:', event.muted);
        onVideoMuteStatusChanged?.(event.muted);
      });

      // Connection quality
      jitsiAPI.addEventListener('participantConnectionQualityChanged', (event: any) => {
        console.log('📊 Calidad de conexión:', event);
        onConnectionQualityChanged?.({
          participantId: event.id,
          connectionQuality: event.connectionQuality,
        });
      });

      // Errors
      jitsiAPI.addEventListener('errorOccurred', (event: any) => {
        console.error('❌ Error en Jitsi:', event);
        const err = new Error(event.error?.message || 'Error desconocido en Jitsi');
        setError(err);
        onError?.(err);
      });

      // Ready
      jitsiAPI.addEventListener('videoConferenceReady', () => {
        console.log('✅ Conferencia lista');
        onReady?.();
      });

    } catch (err) {
      console.error('Error inicializando Jitsi:', err);
      const error = err instanceof Error ? err : new Error('Error desconocido');
      setError(error);
      onError?.(error);
      setIsLoading(false);
    }

    // Cleanup
    return () => {
      if (api) {
        try {
          api.dispose();
        } catch (err) {
          console.error('Error disposing Jitsi API:', err);
        }
      }
    };
  }, [
    roomName,
    jwt,
    domain,
    width,
    height,
    // No incluir callbacks en deps para evitar re-renders
  ]);

  // ==================== RENDER ====================

  if (error) {
    return (
      <div
        className={`flex items-center justify-center bg-red-50 border-2 border-red-200 rounded-lg ${className}`}
        style={{ width, height }}
      >
        <div className="text-center p-8">
          <div className="text-6xl mb-4">❌</div>
          <h3 className="text-xl font-bold text-red-700 mb-2">
            Error al cargar videollamada
          </h3>
          <p className="text-red-600 mb-4">{error.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
          >
            Recargar página
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-100 rounded-lg ${className}`}
        style={{ width, height }}
      >
        <div className="text-center">
          <div className="animate-spin text-6xl mb-4">⏳</div>
          <p className="text-gray-600">Cargando videollamada...</p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`jitsi-meeting-container ${className}`}
      style={{ width, height }}
    />
  );
}

// ==================== EXPORTS ====================

export default JitsiMeeting;
