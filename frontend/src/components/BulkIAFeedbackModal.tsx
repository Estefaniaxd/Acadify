import React, { useState } from 'react';
import {
  Zap,
  CheckCircle,
  AlertCircle,
  Loader,
  X,
  BarChart3,
  Play,
  Pause,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { iaService } from '@/services/iaService';

// ====================================
// TIPOS
// ====================================

export interface TareaBulkOperation {
  id: string;
  titulo: string;
  status: 'pendiente' | 'procesando' | 'completada' | 'error';
  progreso: number;
  retroalimentacion?: string;
  error?: string;
}

interface BulkIAFeedbackModalProps {
  isOpen: boolean;
  tareas: any[];
  onClose: () => void;
  onComplete?: (resultados: TareaBulkOperation[]) => void;
}

// ====================================
// COMPONENTE PRINCIPAL
// ====================================

export function BulkIAFeedbackModal({
  isOpen,
  tareas,
  onClose,
  onComplete,
}: BulkIAFeedbackModalProps) {
  const pollerRef = React.useRef<number | null>(null);
  const eventSourceRef = React.useRef<EventSource | null>(null);

  // Limpiar polling si el modal se cierra o el componente se desmonta
  React.useEffect(() => {
    return () => {
      if (pollerRef.current) {
        clearInterval(pollerRef.current);
        pollerRef.current = null;
      }
      if (eventSourceRef.current) {
        try {
          eventSourceRef.current.close();
        } catch (e) {
          // ignore
        }
        eventSourceRef.current = null;
      }
    };
  }, []);
  const [tareasOperacion, setTareasOperacion] = useState<TareaBulkOperation[]>([]);
  const [procesando, setProcesando] = useState(false);
  const [pausado, setPausado] = useState(false);
  const [configuracion, setConfiguracion] = useState({
    modelo: 'gemini-2.5-flash',
    nivelProfundidad: 'completo',
    incluirRecomendaciones: true,
    incluirFortalezas: true,
  });
  const [estadisticas, setEstadisticas] = useState({
    totalTareas: 0,
    completadas: 0,
    conError: 0,
    tiempoEstimado: 0,
  });

  // Inicializar tareas
  React.useEffect(() => {
    if (isOpen && tareas.length > 0) {
      const nuevasTareas: TareaBulkOperation[] = tareas.map((tarea) => ({
        id: tarea.id,
        titulo: tarea.titulo,
        status: 'pendiente',
        progreso: 0,
      }));
      setTareasOperacion(nuevasTareas);
      setEstadisticas({
        totalTareas: tareas.length,
        completadas: 0,
        conError: 0,
        tiempoEstimado: tareas.length * 15, // ~15 segundos por tarea
      });
    }
  }, [isOpen, tareas]);

  // Procesar tareas
  const procesarTareas = async () => {
    setProcesando(true);

    // Extraer solo los IDs de entregas
    const entregaIds = tareas.map((t) => t.id);

    try {
      console.log(`🚀 Iniciando procesamiento masivo de ${entregaIds.length} entregas`);

      // Llamar al endpoint masivo
      const resultado = await iaService.generarRetroalimentacionMasiva(
        entregaIds,
        configuracion.modelo,
        configuracion.nivelProfundidad as 'basico' | 'medio' | 'completo',
        true,
        true
      );

      console.log(`✅ Job iniciado: ${resultado.job_id}`);
      console.log(`📊 Procesando ${resultado.total_entregas} entregas...`);

      // Actualizar tareas localmente al estado "procesando"
      setTareasOperacion((prev) =>
        prev.map((t) => ({
          ...t,
          status: 'procesando' as const,
          progreso: 5,
        }))
      );

      // Preferir SSE (EventSource) para actualizaciones en tiempo real
      try {
        const token = localStorage.getItem('access_token');
        if (token && typeof EventSource !== 'undefined') {
          const base = import.meta.env.VITE_API_URL || '';
          const url = `${base}/ia/retroalimentacion-masiva/stream/${resultado.job_id}?access_token=${encodeURIComponent(
            token
          )}`;
          const es = new EventSource(url);
          eventSourceRef.current = es;

          es.onmessage = (ev) => {
            try {
              const data = JSON.parse(ev.data);
              const job = data.job;
              if (!job) return;

              // Actualizar items individuales basados en el tracker del job
              setTareasOperacion((prev) =>
                prev.map((t) => {
                  const item = job.items?.find((it: any) => it.entrega_id === t.id);
                  if (!item) return t;

                  const statusMap: Record<string, TareaBulkOperation['status']> = {
                    pendiente: 'pendiente',
                    procesando: 'procesando',
                    completado: 'completada',
                    error: 'error',
                  };

                  return {
                    ...t,
                    status: statusMap[item.status] || t.status,
                    progreso: item.status === 'completado' ? 100 : item.status === 'procesando' ? 50 : t.progreso,
                    error: item.error || undefined,
                  };
                })
              );

              // Actualizar métricas
              setEstadisticas((prev) => ({
                ...prev,
                totalTareas: job.total ?? prev.totalTareas,
                completadas: job.completed ?? prev.completadas,
                conError: job.errors ?? prev.conError,
              }));

              // Si el job terminó, cerrar EventSource y finalizar
              if (job.estado === 'completado' || job.estado === 'error') {
                if (eventSourceRef.current) {
                  eventSourceRef.current.close();
                  eventSourceRef.current = null;
                }
                setProcesando(false);
                if (onComplete) onComplete(tareasOperacion);
              }
            } catch (err) {
              console.error('❌ Error procesando evento SSE:', err);
            }
          };

          es.onerror = (err) => {
            console.error('❌ SSE error:', err);
            // fallback: cerrar SSE y (opcional) iniciar polling si necesario
            if (eventSourceRef.current) {
              eventSourceRef.current.close();
              eventSourceRef.current = null;
            }
            // Opcional: podríamos iniciar polling aquí como fallback
          };
        } else {
          // Si no hay token o EventSource, caer en polling HTTP (compatibilidad)
          const pollInterval = 2000;
          pollerRef.current = window.setInterval(async () => {
            try {
              const estado = await iaService.obtenerEstadoJobMasivo(resultado.job_id);
              const job = estado?.job;
              if (!job) return;

              setTareasOperacion((prev) =>
                prev.map((t) => {
                  const item = job.items?.find((it: any) => it.entrega_id === t.id);
                  if (!item) return t;
                  const statusMap: Record<string, TareaBulkOperation['status']> = {
                    pendiente: 'pendiente',
                    procesando: 'procesando',
                    completado: 'completada',
                    error: 'error',
                  };
                  return {
                    ...t,
                    status: statusMap[item.status] || t.status,
                    progreso: item.status === 'completado' ? 100 : item.status === 'procesando' ? 50 : t.progreso,
                    error: item.error || undefined,
                  };
                })
              );

              setEstadisticas((prev) => ({
                ...prev,
                totalTareas: job.total ?? prev.totalTareas,
                completadas: job.completed ?? prev.completadas,
                conError: job.errors ?? prev.conError,
              }));

              if (job.estado === 'completado' || job.estado === 'error') {
                if (pollerRef.current) {
                  clearInterval(pollerRef.current);
                  pollerRef.current = null;
                }
                setProcesando(false);
                if (onComplete) onComplete(tareasOperacion);
              }
            } catch (e) {
              console.error('❌ Error haciendo polling del job (fallback):', e);
            }
          }, pollInterval);
        }
      } catch (e) {
        console.error('❌ Error iniciando SSE/polling:', e);
      }
    } catch (error) {
      console.error('❌ Error en procesamiento masivo:', error);

      // Marcar todas como error
      setTareasOperacion((prev) =>
        prev.map((t) => ({
          ...t,
          status: 'error' as const,
          progreso: 100,
          error: error instanceof Error ? error.message : 'Error desconocido',
        }))
      );

      setEstadisticas((prev) => ({
        ...prev,
        conError: prev.totalTareas,
      }));
    } finally {
      setProcesando(false);

      // Llamar callback si está definido
      if (onComplete) {
        onComplete(tareasOperacion);
      }
    }
  };

  const actualizarTarea = (index: number, actualizacion: Partial<TareaBulkOperation>) => {
    setTareasOperacion((prev) => [
      ...prev.slice(0, index),
      { ...prev[index], ...actualizacion },
      ...prev.slice(index + 1),
    ]);
  };

  const porcentajeTotal =
    tareasOperacion.length > 0
      ? Math.round((estadisticas.completadas + estadisticas.conError) / tareasOperacion.length) * 100
      : 0;

  const togglePausa = () => {
    setPausado(!pausado);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Modal */}
            <motion.div
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white p-6 border-b flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Zap className="w-6 h-6" />
                  <div>
                    <h2 className="text-xl font-bold">Retroalimentación IA en Masiva</h2>
                    <p className="text-xs text-yellow-100 mt-1">
                      Procesa múltiples tareas automáticamente
                    </p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="hover:bg-yellow-600 p-2 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Contenido */}
              <div className="overflow-y-auto" style={{ maxHeight: 'calc(90vh - 280px)' }}>
                {/* Configuración (solo si no está procesando) */}
                {!procesando && (
                  <div className="p-6 border-b bg-gray-50">
                    <h3 className="font-semibold text-gray-900 mb-4">Configuración</h3>
                    <div className="grid grid-cols-2 gap-4">
                      {/* Modelo */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Modelo IA
                        </label>
                        <select
                          value={configuracion.modelo}
                          onChange={(e) =>
                            setConfiguracion({ ...configuracion, modelo: e.target.value })
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-yellow-500 outline-none"
                        >
                          <option value="gemini-2.5-flash">⚡ Gemini 2.5 Flash (Rápido)</option>
                          <option value="gemini-2.5-pro">🧠 Gemini 2.5 Pro (Preciso)</option>
                          <option value="gemini-2.0-flash">💫 Gemini 2.0 Flash</option>
                        </select>
                      </div>

                      {/* Nivel de Profundidad */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Nivel de Detalle
                        </label>
                        <select
                          value={configuracion.nivelProfundidad}
                          onChange={(e) =>
                            setConfiguracion({
                              ...configuracion,
                              nivelProfundidad: e.target.value,
                            })
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-yellow-500 outline-none"
                        >
                          <option value="basico">📋 Básico</option>
                          <option value="medio">📊 Medio</option>
                          <option value="completo">📈 Completo</option>
                        </select>
                      </div>

                      {/* Checkboxes */}
                      <div className="col-span-2 flex gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={configuracion.incluirFortalezas}
                            onChange={(e) =>
                              setConfiguracion({
                                ...configuracion,
                                incluirFortalezas: e.target.checked,
                              })
                            }
                            className="w-4 h-4 accent-yellow-500"
                          />
                          <span className="text-sm text-gray-700">Incluir fortalezas</span>
                        </label>

                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={configuracion.incluirRecomendaciones}
                            onChange={(e) =>
                              setConfiguracion({
                                ...configuracion,
                                incluirRecomendaciones: e.target.checked,
                              })
                            }
                            className="w-4 h-4 accent-yellow-500"
                          />
                          <span className="text-sm text-gray-700">Incluir recomendaciones</span>
                        </label>
                      </div>
                    </div>
                  </div>
                )}

                {/* Barra de Progreso General */}
                {procesando && (
                  <div className="p-6 border-b bg-gradient-to-r from-yellow-50 to-orange-50">
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-gray-900">Progreso General</h3>
                        <span className="text-2xl font-bold text-yellow-600">{porcentajeTotal}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${porcentajeTotal}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>

                    {/* Estadísticas */}
                    <div className="grid grid-cols-4 gap-2 text-sm">
                      <div className="bg-white p-3 rounded-lg border">
                        <p className="text-gray-600 text-xs">Total</p>
                        <p className="font-bold text-lg text-gray-900">
                          {estadisticas.totalTareas}
                        </p>
                      </div>
                      <div className="bg-green-50 p-3 rounded-lg border border-green-200">
                        <p className="text-green-700 text-xs">Completadas</p>
                        <p className="font-bold text-lg text-green-600">
                          {estadisticas.completadas}
                        </p>
                      </div>
                      <div className="bg-red-50 p-3 rounded-lg border border-red-200">
                        <p className="text-red-700 text-xs">Errores</p>
                        <p className="font-bold text-lg text-red-600">{estadisticas.conError}</p>
                      </div>
                      <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                        <p className="text-blue-700 text-xs">Est. Tiempo</p>
                        <p className="font-bold text-lg text-blue-600">
                          {Math.ceil(estadisticas.tiempoEstimado / 60)}m
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Lista de Tareas */}
                <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
                  {tareasOperacion.map((tarea, idx) => (
                    <TareaOperacionItem key={tarea.id} tarea={tarea} />
                  ))}
                </div>
              </div>

              {/* Footer */}
              <div className="bg-gray-50 p-6 border-t flex justify-end gap-3">
                {procesando ? (
                  <>
                    <button
                      onClick={togglePausa}
                      className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
                        pausado
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-orange-500 text-white hover:bg-orange-600'
                      }`}
                    >
                      {pausado ? (
                        <>
                          <Play className="w-4 h-4" />
                          Reanudar
                        </>
                      ) : (
                        <>
                          <Pause className="w-4 h-4" />
                          Pausar
                        </>
                      )}
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={onClose}
                      className="px-4 py-2 rounded-lg font-medium text-gray-700 hover:bg-gray-200 transition-colors"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={procesarTareas}
                      disabled={tareasOperacion.length === 0}
                      className="px-6 py-2 rounded-lg font-medium bg-yellow-500 text-white hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                      <Zap className="w-4 h-4" />
                      Iniciar Procesamiento
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// ====================================
// COMPONENTE ITEM TAREA
// ====================================

interface TareaOperacionItemProps {
  tarea: TareaBulkOperation;
}

function TareaOperacionItem({ tarea }: TareaOperacionItemProps) {
  const getColorEstatus = () => {
    switch (tarea.status) {
      case 'pendiente':
        return 'bg-gray-100 text-gray-700';
      case 'procesando':
        return 'bg-blue-100 text-blue-700';
      case 'completada':
        return 'bg-green-100 text-green-700';
      case 'error':
        return 'bg-red-100 text-red-700';
    }
  };

  const getIconoEstatus = () => {
    switch (tarea.status) {
      case 'pendiente':
        return <AlertCircle className="w-4 h-4" />;
      case 'procesando':
        return <Loader className="w-4 h-4 animate-spin" />;
      case 'completada':
        return <CheckCircle className="w-4 h-4" />;
      case 'error':
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  return (
    <motion.div
      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-medium text-gray-900 flex-1 pr-4 line-clamp-2">{tarea.titulo}</h4>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${getColorEstatus()}`}>
          {getIconoEstatus()}
          <span className="capitalize">{tarea.status}</span>
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="mb-2">
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <motion.div
            className="h-full bg-yellow-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${tarea.progreso}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Retroalimentación o error */}
      {tarea.retroalimentacion && (
        <p className="text-xs text-gray-600 line-clamp-2 mt-2">{tarea.retroalimentacion}</p>
      )}

      {tarea.error && (
        <p className="text-xs text-red-600 line-clamp-2 mt-2">Error: {tarea.error}</p>
      )}
    </motion.div>
  );
}
