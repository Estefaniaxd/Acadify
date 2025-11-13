/**
 * Componente de Alertas de Proctoring
 * 
 * Funcionalidades:
 * - Panel lateral de alertas en tiempo real
 * - Contador de infracciones por tipo y severidad
 * - Indicador visual de nivel de riesgo
 * - Notificaciones toast con sonido
 * - Modal de advertencia crítica
 * - Timeline de eventos
 * 
 * Principios SOLID aplicados:
 * - Single Responsibility: Solo maneja visualización de alertas
 * - Open/Closed: Extensible mediante props
 * - Component Composition: Dividido en sub-componentes
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  AlertTriangle, 
  AlertCircle, 
  Info, 
  X, 
  Eye, 
  EyeOff,
  Bell,
  BellOff,
  Shield,
  ShieldAlert,
  Activity
} from 'lucide-react';
import type { AlertaProctoring } from '../../types';

interface AlertasProctoringProps {
  alertas: AlertaProctoring[];
  onResolverAlerta: (alertaId: string) => void;
  onAlertaCritica?: (contadorCriticas: number) => void;
  mostrarPanel?: boolean;
  reproducirSonidos?: boolean;
  className?: string;
}

/**
 * Hook para reproducir sonidos de alerta
 */
function useSonidosAlerta(reproducirSonidos: boolean) {
  const reproducirSonido = useCallback((severidad: AlertaProctoring['severidad']) => {
    if (!reproducirSonidos) return;

    // Crear AudioContext para generar tonos
    const audioContext = new AudioContext();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    // Configurar tono según severidad
    const frecuencias = {
      baja: 440,    // La
      media: 523,   // Do
      alta: 659,    // Mi
      critica: 880  // La (octava superior)
    };

    oscillator.frequency.value = frecuencias[severidad];
    gainNode.gain.value = 0.3;

    // Reproducir
    oscillator.start();
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    oscillator.stop(audioContext.currentTime + 0.5);

    // Cleanup
    setTimeout(() => {
      audioContext.close();
    }, 600);
  }, [reproducirSonidos]);

  return { reproducirSonido };
}

/**
 * Componente de contador de infracciones
 */
function ContadorInfracciones({ alertas }: { alertas: AlertaProctoring[] }) {
  const contadores = useMemo(() => {
    const counts = {
      baja: 0,
      media: 0,
      alta: 0,
      critica: 0
    };

    alertas.forEach(alerta => {
      if (!alerta.resuelta) {
        counts[alerta.severidad]++;
      }
    });

    return counts;
  }, [alertas]);

  const total = Object.values(contadores).reduce((sum, count) => sum + count, 0);

  const obtenerColorNivelRiesgo = () => {
    if (contadores.critica > 0) return 'text-red-600 dark:text-red-400';
    if (contadores.alta > 2) return 'text-orange-600 dark:text-orange-400';
    if (contadores.media > 5) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-green-600 dark:text-green-400';
  };

  const obtenerTextoNivelRiesgo = () => {
    if (contadores.critica > 0) return 'Riesgo Crítico';
    if (contadores.alta > 2) return 'Riesgo Alto';
    if (contadores.media > 5) return 'Riesgo Medio';
    return 'Riesgo Bajo';
  };

  const obtenerIconoNivelRiesgo = () => {
    if (contadores.critica > 0) return <ShieldAlert className="h-5 w-5 text-red-600" />;
    return <Shield className="h-5 w-5 text-green-600" />;
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
      {/* Nivel de riesgo global */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          {obtenerIconoNivelRiesgo()}
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Nivel de Riesgo</p>
            <p className={`text-sm font-semibold ${obtenerColorNivelRiesgo()}`}>
              {obtenerTextoNivelRiesgo()}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{total}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Alertas activas</p>
        </div>
      </div>

      {/* Grid de contadores por severidad */}
      <div className="grid grid-cols-4 gap-2">
        <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
          <p className="text-lg font-bold text-blue-600 dark:text-blue-400">{contadores.baja}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Bajas</p>
        </div>
        <div className="text-center p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
          <p className="text-lg font-bold text-yellow-600 dark:text-yellow-400">{contadores.media}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Medias</p>
        </div>
        <div className="text-center p-2 bg-orange-50 dark:bg-orange-900/20 rounded">
          <p className="text-lg font-bold text-orange-600 dark:text-orange-400">{contadores.alta}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Altas</p>
        </div>
        <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded">
          <p className="text-lg font-bold text-red-600 dark:text-red-400">{contadores.critica}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Críticas</p>
        </div>
      </div>
    </div>
  );
}

/**
 * Componente de tarjeta de alerta individual
 */
function TarjetaAlerta({ 
  alerta, 
  onResolver 
}: { 
  alerta: AlertaProctoring; 
  onResolver: () => void;
}) {
  const obtenerColorSeveridad = () => {
    switch (alerta.severidad) {
      case 'baja': return 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20';
      case 'media': return 'border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/20';
      case 'alta': return 'border-orange-300 dark:border-orange-700 bg-orange-50 dark:bg-orange-900/20';
      case 'critica': return 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20';
      default: return 'border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/20';
    }
  };

  const obtenerIconoSeveridad = () => {
    switch (alerta.severidad) {
      case 'baja': return <Info className="h-4 w-4 text-blue-600" />;
      case 'media': return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      case 'alta': return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      case 'critica': return <ShieldAlert className="h-4 w-4 text-red-600" />;
      default: return <Info className="h-4 w-4" />;
    }
  };

  const formatearHora = (date: Date) => {
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  return (
    <div className={`p-3 rounded-lg border-2 ${obtenerColorSeveridad()} ${alerta.resuelta ? 'opacity-50' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-2 flex-1">
          <div className="mt-0.5">{obtenerIconoSeveridad()}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
              {alerta.mensaje}
            </p>
            <div className="flex items-center space-x-3 mt-1">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {formatearHora(alerta.timestamp)}
              </p>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                alerta.severidad === 'critica' ? 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200' :
                alerta.severidad === 'alta' ? 'bg-orange-200 dark:bg-orange-800 text-orange-800 dark:text-orange-200' :
                alerta.severidad === 'media' ? 'bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200' :
                'bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
              }`}>
                {alerta.severidad.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
        {!alerta.resuelta && (
          <button
            onClick={onResolver}
            className="ml-2 p-1 hover:bg-white/50 dark:hover:bg-gray-800/50 rounded transition-colors"
            title="Marcar como resuelta"
          >
            <X className="h-4 w-4 text-gray-600 dark:text-gray-400" />
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Componente principal de alertas de proctoring
 */
export function AlertasProctoring({
  alertas,
  onResolverAlerta,
  onAlertaCritica,
  mostrarPanel = true,
  reproducirSonidos = true,
  className = ''
}: AlertasProctoringProps) {
  const [panelVisible, setPanelVisible] = useState(mostrarPanel);
  const [sonidosActivos, setSonidosActivos] = useState(reproducirSonidos);
  const { reproducirSonido } = useSonidosAlerta(sonidosActivos);

  // Monitorear nuevas alertas para reproducir sonidos
  useEffect(() => {
    if (alertas.length === 0) return;

    const ultimaAlerta = alertas[alertas.length - 1];
    if (!ultimaAlerta.resuelta) {
      reproducirSonido(ultimaAlerta.severidad);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alertas.length]); // Solo cuando cambia el número de alertas

  // Monitorear alertas críticas
  useEffect(() => {
    const alertasCriticas = alertas.filter(a => a.severidad === 'critica' && !a.resuelta);
    if (alertasCriticas.length > 0 && onAlertaCritica) {
      onAlertaCritica(alertasCriticas.length);
    }
  }, [alertas, onAlertaCritica]);

  const alertasActivas = useMemo(() => 
    alertas.filter(a => !a.resuelta), 
    [alertas]
  );

  const alertasRecientes = useMemo(() => 
    [...alertasActivas].reverse().slice(0, 10), 
    [alertasActivas]
  );

  return (
    <div className={`${className}`}>
      {/* Botón flotante de toggle */}
      <div className="fixed top-20 right-4 z-40 flex flex-col space-y-2">
        <button
          onClick={() => setPanelVisible(!panelVisible)}
          className={`
            p-3 rounded-full shadow-lg transition-all
            ${alertasActivas.length > 0 
              ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
              : 'bg-gray-700 hover:bg-gray-800'
            }
            text-white
          `}
          title={panelVisible ? 'Ocultar alertas' : 'Mostrar alertas'}
        >
          {panelVisible ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          {alertasActivas.length > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
              {alertasActivas.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setSonidosActivos(!sonidosActivos)}
          className="p-2 bg-gray-700 hover:bg-gray-800 text-white rounded-full shadow-lg transition-all"
          title={sonidosActivos ? 'Desactivar sonidos' : 'Activar sonidos'}
        >
          {sonidosActivos ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
        </button>
      </div>

      {/* Panel lateral de alertas */}
      {panelVisible && (
        <div className="fixed top-20 right-4 w-96 max-h-[calc(100vh-6rem)] bg-white dark:bg-gray-900 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 z-30 overflow-hidden flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  Monitoreo de Integridad
                </h3>
              </div>
              <button
                onClick={() => setPanelVisible(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
              >
                <X className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
          </div>

          {/* Contador de infracciones */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <ContadorInfracciones alertas={alertas} />
          </div>

          {/* Lista de alertas */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {alertasRecientes.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <Shield className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No hay alertas activas</p>
                <p className="text-xs mt-1">El sistema está monitoreando</p>
              </div>
            ) : (
              alertasRecientes.map(alerta => (
                <TarjetaAlerta
                  key={alerta.id}
                  alerta={alerta}
                  onResolver={() => onResolverAlerta(alerta.id)}
                />
              ))
            )}
          </div>

          {/* Footer con estadísticas */}
          <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
              <span>Total de eventos: {alertas.length}</span>
              <span>Activas: {alertasActivas.length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AlertasProctoring;
