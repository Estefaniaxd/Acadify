/**
 * Página de Videollamadas
 * 
 * @module pages/VideollamadasPage
 * @description Página principal para gestionar videollamadas.
 * Integra lista de videollamadas y ventana de videollamada activa.
 */

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import VideollamadasList from '../modules/comunicacion/components/VideollamadasList';
import VideoCallWindow from '../modules/comunicacion/components/VideoCallWindow';
import type { Videollamada } from '../types/videollamada.types';

// ==================== TIPOS ====================

interface VideollamadasPageProps {
  /** ID de sala de chat (opcional) */
  salaChatId?: string;
}

// ==================== COMPONENTE ====================

export function VideollamadasPage({
  salaChatId,
}: VideollamadasPageProps) {
  const { user } = useAuth();
  const [videollamadaActiva, setVideollamadaActiva] = useState<Videollamada | null>(null);
  
  // Obtener nombre y email del usuario autenticado
  const currentUserName = user?.username || 'Usuario';
  const currentUserEmail = user?.email || undefined;

  // ==================== HANDLERS ====================

  const handleSelectVideollamada = (videollamada: Videollamada) => {
    setVideollamadaActiva(videollamada);
  };

  const handleCloseVideollamada = () => {
    setVideollamadaActiva(null);
  };

  // ==================== RENDER ====================

  // Si hay videollamada activa, mostrar ventana completa
  if (videollamadaActiva) {
    return (
      <VideoCallWindow
        videollamadaId={videollamadaActiva.id}
        displayName={currentUserName}
        email={currentUserEmail}
        onClose={handleCloseVideollamada}
      />
    );
  }

  // Sino, mostrar lista de videollamadas
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            📹 Videollamadas
          </h1>
          <p className="text-gray-600">
            Crea y únete a videollamadas con Jitsi Meet
          </p>
        </div>

        <VideollamadasList
          salaChatId={salaChatId}
          soloActivas={true}
          onSelectVideollamada={handleSelectVideollamada}
        />

        {/* Información adicional */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">
            ℹ️ Información
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Puedes crear videollamadas de video o solo audio</li>
            <li>• Hasta 50 participantes por videollamada</li>
            <li>• Las grabaciones están disponibles después de finalizar</li>
            <li>• Los moderadores pueden finalizar y gestionar la llamada</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// ==================== EXPORTS ====================

export default VideollamadasPage;
