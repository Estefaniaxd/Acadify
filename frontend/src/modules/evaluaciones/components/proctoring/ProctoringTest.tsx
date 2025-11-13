/**
 * Página de prueba para componentes de Proctoring
 * 
 * Este componente permite probar individualmente:
 * - ProctoringCamera
 * - ProctoringAudio
 * - AlertasProctoring
 * 
 * Uso: Importar en App.tsx o crear ruta temporal para testing
 */

import React, { useState, useCallback } from 'react';
import { ProctoringCamera } from './ProctoringCamera';
import { ProctoringAudio } from './ProctoringAudio';
import { AlertasProctoring } from './AlertasProctoring';
import type { 
  ConfiguracionProctoring, 
  AlertaProctoring, 
  SnapshotProctoring,
  EventoAudio 
} from '../../types';

export function ProctoringTest() {
  const [activo, setActivo] = useState(false);
  const [alertas, setAlertas] = useState<AlertaProctoring[]>([]);
  const [snapshots, setSnapshots] = useState<SnapshotProctoring[]>([]);
  const [eventosAudio, setEventosAudio] = useState<EventoAudio[]>([]);

  const [configuracion] = useState<ConfiguracionProctoring>({
    habilitarCamera: true,
    habilitarMicrofono: true,
    deteccionRostros: true,
    deteccionMultiplesRostros: true,
    deteccionAudio: true,
    grabarVideo: true,
    grabarAudio: true,
    frecuenciaSnapshotsSegundos: 10,
    umbralConfianzaRostro: 0.7,
    alertarSinRostro: true,
    alertarMultiplesRostros: true,
    alertarRostroDesconocido: true,
    alertarMultiplesVoces: true
  });

  const handleAlerta = useCallback((alerta: AlertaProctoring) => {
    // eslint-disable-next-line no-console
    console.log('🚨 Nueva alerta:', alerta);
    setAlertas(prev => [...prev, alerta]);
  }, []);

  const handleSnapshot = useCallback((snapshot: SnapshotProctoring) => {
    // eslint-disable-next-line no-console
    console.log('📸 Snapshot capturado:', snapshot.timestamp);
    setSnapshots(prev => [...prev, snapshot].slice(-5)); // Mantener últimos 5
  }, []);

  const handleEventoAudio = useCallback((evento: EventoAudio) => {
    // eslint-disable-next-line no-console
    console.log('🎤 Evento de audio:', evento);
    setEventosAudio(prev => [...prev, evento].slice(-10)); // Mantener últimos 10
  }, []);

  const handleResolverAlerta = useCallback((alertaId: string) => {
    setAlertas(prev =>
      prev.map(a => (a.id === alertaId ? { ...a, resuelta: true } : a))
    );
  }, []);

    const handleAlertaCritica = useCallback((contadorCriticas: number) => {
    // eslint-disable-next-line no-console
    console.log('⚠️ ALERTA CRÍTICA: Se han detectado', contadorCriticas, 'alertas críticas');
    // Aquí podrías: finalizar examen automáticamente, notificar al profesor, etc.
  }, []);

  const limpiarDatos = () => {
    setAlertas([]);
    setSnapshots([]);
    setEventosAudio([]);
  };

  const agregarAlertaPrueba = () => {
    const severidades: Array<'baja' | 'media' | 'alta' | 'critica'> = ['baja', 'media', 'alta', 'critica'];
    const mensajes = [
      'Cambio de pestaña detectado',
      'Audio sospechoso detectado',
      'Múltiples rostros en cámara',
      'Intento de copiar texto'
    ];
    
    const aleatoria = Math.floor(Math.random() * 4);
    handleAlerta({
      id: `test-${Date.now()}`,
      tipo: 'cambio_pestana',
      severidad: severidades[aleatoria],
      mensaje: mensajes[aleatoria],
      timestamp: new Date(),
      resuelta: false
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            🧪 Prueba de Componentes de Proctoring
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Prueba individual de los componentes de monitoreo de evaluaciones
          </p>
        </div>

        {/* Controles */}
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Controles de Prueba
          </h2>
          
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setActivo(!activo)}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activo
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
            >
              {activo ? '⏸️ Detener Monitoreo' : '▶️ Iniciar Monitoreo'}
            </button>

            <button
              onClick={agregarAlertaPrueba}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            >
              🚨 Agregar Alerta de Prueba
            </button>

            <button
              onClick={limpiarDatos}
              className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
            >
              🗑️ Limpiar Datos
            </button>
          </div>

          <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Estado:</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Monitoreo:</span>
                <span className={`ml-2 font-semibold ${activo ? 'text-green-600' : 'text-red-600'}`}>
                  {activo ? 'Activo' : 'Inactivo'}
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Alertas:</span>
                <span className="ml-2 font-semibold text-gray-900 dark:text-white">
                  {alertas.filter(a => !a.resuelta).length} activas
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Snapshots:</span>
                <span className="ml-2 font-semibold text-gray-900 dark:text-white">
                  {snapshots.length}
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Eventos Audio:</span>
                <span className="ml-2 font-semibold text-gray-900 dark:text-white">
                  {eventosAudio.length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Grid de componentes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Panel de Cámara */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              📹 Proctoring Camera
            </h2>
            <ProctoringCamera
              configuracion={configuracion}
              onAlerta={handleAlerta}
              onSnapshot={handleSnapshot}
              activo={activo}
            />
          </div>

          {/* Panel de Audio */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              🎤 Proctoring Audio
            </h2>
            <ProctoringAudio
              configuracion={configuracion}
              onAlerta={handleAlerta}
              onEventoAudio={handleEventoAudio}
              activo={activo}
            />
          </div>
        </div>

        {/* Logs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Log de Snapshots */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              📸 Últimos Snapshots ({snapshots.length})
            </h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {snapshots.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  No hay snapshots capturados aún
                </p>
              ) : (
                snapshots.map((snapshot, index) => (
                  <div
                    key={index}
                    className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-gray-900 dark:text-white">
                        {snapshot.timestamp.toLocaleTimeString()}
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        {snapshot.rostrosDetectados} rostro(s)
                      </span>
                    </div>
                    {snapshot.imagenBase64 && (
                      <img
                        src={snapshot.imagenBase64}
                        alt="Snapshot"
                        className="w-full h-24 object-cover rounded"
                      />
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Log de Eventos de Audio */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              🎵 Eventos de Audio ({eventosAudio.length})
            </h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {eventosAudio.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  No hay eventos de audio registrados
                </p>
              ) : (
                eventosAudio.map((evento, index) => (
                  <div
                    key={index}
                    className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-900 dark:text-white">
                        {evento.timestamp.toLocaleTimeString()}
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        Nivel: {evento.nivelAudio}%
                      </span>
                    </div>
                    <div className="mt-1">
                      <div className="h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${
                            evento.nivelAudio > 70
                              ? 'bg-red-500'
                              : evento.nivelAudio > 40
                              ? 'bg-orange-500'
                              : 'bg-green-500'
                          }`}
                          style={{ width: `${evento.nivelAudio}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Panel de Alertas (flotante) */}
      <AlertasProctoring
        alertas={alertas}
        onResolverAlerta={handleResolverAlerta}
        onAlertaCritica={handleAlertaCritica}
        mostrarPanel={true}
        reproducirSonidos={true}
      />
    </div>
  );
}

export default ProctoringTest;
