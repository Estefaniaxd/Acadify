
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Calendar, Award, FileText, AlertCircle, CheckCircle, Zap, Upload, BookOpen, Target, Beaker, Presentation, Search, Edit, ClipboardList, ListChecks, Lightbulb, BarChart3, Library, Gamepad2, Pencil, User, Bot } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { Tarea } from '../../../modules/tareas/types';
import { EntregasList } from '../../../components/EntregasList';
import { RetroalimentacionVisor } from "../../../components/RetroalimentacionVisor";
import { useRetroalimentacionIA } from "../../../modules/tareas/hooks/useRetroalimentacionIA";

// ====================================
// TIPOS
// ====================================

interface TareaPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  tarea: Tarea;
  entregaId?: string;
  isStudentUser?: boolean;
  cursoId?: string;
  onEdit?: (tarea: Tarea) => void;
}

// ====================================
// FUNCIONES AUXILIARES
// ====================================

const formatearFecha = (fecha: string): string => {
  return new Date(fecha).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const tipoTareaIcon: Record<string, React.ComponentType<any>> = {
  ensayo: Edit,
  proyecto: Target,
  ejercicios: Award,
  investigacion: Search,
  presentacion: Presentation,
  laboratorio: Beaker,
  lectura: BookOpen,
  examen: FileText,
  otro: ClipboardList,
};

const prioridadColor: Record<string, string> = {
  baja: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300",
  media: "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300",
  alta: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300",
};

const estadoColor: Record<string, string> = {
  asignada: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300",
  en_progreso:
    "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300",
  entregada:
    "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300",
  calificada:
    "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300",
  vencida: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300",
  cerrada: "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300",
};

// ====================================
// COMPONENTE
// ====================================

export const TareaPreviewModal: React.FC<TareaPreviewModalProps> = ({
  isOpen,
  onClose,
  tarea,
  entregaId,
  isStudentUser = false,
  cursoId,
  onEdit,
}) => {
  const navigate = useNavigate();
  const [pestaña, setPestaña] = useState<"info" | "retroalimentacion">("info");
  const [showSubmissionForm, setShowSubmissionForm] = useState(false);
  const { cargando, retroalimentacion, generarRetroalimentacion, obtenerRetroalimentacion } =
    useRetroalimentacionIA();

  const tipoKey = typeof tarea.tipo === "string" ? tarea.tipo.toLowerCase() : "otro";
  const TipoIcon = tipoTareaIcon[tipoKey] || ClipboardList;

  // Cargar retroalimentación si existe
  useEffect(() => {
    if (isOpen && entregaId && pestaña === "retroalimentacion") {
      obtenerRetroalimentacion(entregaId);
    }
  }, [isOpen, pestaña, entregaId, obtenerRetroalimentacion]);

  const handleGenerarRetroalimentacion = async () => {
    if (entregaId) {
      try {
        await generarRetroalimentacion(entregaId, "gemini-2.5-flash", "completo");
      } catch (error) {
        console.error("Error generando retroalimentación:", error);
      }
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          {/* Backdrop for closing */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="relative bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <motion.div
              className="sticky top-0 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 border-b border-slate-200 dark:border-slate-700 flex items-start justify-between z-10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                    <TipoIcon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                      {tarea.titulo}
                    </h2>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${prioridadColor[tarea.prioridad]}`}>
                    Prioridad: {tarea.prioridad}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${estadoColor[tarea.estado]}`}>
                    Estado: {tarea.estado}
                  </span>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-2 hover:bg-white/50 dark:hover:bg-slate-700/50 rounded-lg transition-colors"
              >
                <X size={24} className="text-slate-600 dark:text-slate-400" />
              </button>
            </motion.div>

            {/* Pestañas */}
            {tarea.habilitar_retroalimentacion_ia && entregaId && (
              <div className="border-b border-slate-200 dark:border-slate-700 px-6 py-3 flex gap-2">
                <button
                  onClick={() => setPestaña("info")}
                  className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${pestaña === "info"
                    ? "bg-blue-600 text-white shadow-md"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                    }`}
                >
                  <FileText className="w-4 h-4" />
                  Información
                </button>
                <button
                  onClick={() => setPestaña("retroalimentacion")}
                  className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${pestaña === "retroalimentacion"
                    ? "bg-purple-600 text-white shadow-md"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                    }`}
                >
                  <Zap className="w-4 h-4" />
                  IA Feedback
                  {retroalimentacion && (
                    <CheckCircle size={16} className="text-green-400" />
                  )}
                </button>
              </div>
            )}

            {/* Contenido */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="p-6 space-y-6"
            >
              <AnimatePresence mode="wait">
                {pestaña === "info" ? (
                  <motion.div
                    key="info"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="space-y-6"
                  >
                    {/* Grid de información - Fecha y Puntos */}
                    <div className="grid grid-cols-2 gap-4">
                      <motion.div
                        className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                      >
                        <div className="flex items-center gap-2 text-blue-700 dark:text-blue-400 mb-2">
                          <Calendar size={18} />
                          <span className="text-sm font-semibold">Fecha Límite</span>
                        </div>
                        <p className="font-bold text-slate-900 dark:text-white">
                          {formatearFecha(tarea.fecha_limite)}
                        </p>
                      </motion.div>

                      <motion.div
                        className="p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800"
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                      >
                        <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 mb-2">
                          <Award size={18} />
                          <span className="text-sm font-semibold">Puntuación</span>
                        </div>
                        <p className="font-bold text-slate-900 dark:text-white">
                          {tarea.puntuacion_maxima} puntos
                        </p>
                      </motion.div>
                    </div>

                    {/* Información completa de la tarea */}
                    <div className="space-y-4">
                      {/* Información básica expandida */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Tipo de Tarea</p>
                          <p className="font-semibold text-slate-900 dark:text-white capitalize flex items-center gap-2">
                            <TipoIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                            {tarea.tipo}
                          </p>
                        </div>

                        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Prioridad</p>
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold inline-block ${prioridadColor[tarea.prioridad]}`}>
                            {tarea.prioridad.toUpperCase()}
                          </span>
                        </div>

                        {tarea.tiempo_estimado && (
                          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                            <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Tiempo Estimado</p>
                            <p className="font-semibold text-slate-900 dark:text-white">
                              {tarea.tiempo_estimado} minutos
                            </p>
                          </div>
                        )}

                        {(tarea as any).intentos_permitidos && (
                          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                            <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Intentos Permitidos</p>
                            <p className="font-semibold text-slate-900 dark:text-white">
                              {(tarea as any).intentos_permitidos}
                            </p>
                          </div>
                        )}

                        {tarea.tamano_maximo_mb && (
                          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                            <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Tamaño Máximo</p>
                            <p className="font-semibold text-slate-900 dark:text-white">
                              {tarea.tamano_maximo_mb} MB
                            </p>
                          </div>
                        )}

                        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Formato de Entrega</p>
                          <p className="font-semibold text-slate-900 dark:text-white capitalize">{tarea.formato_entrega || 'Archivo'}</p>
                        </div>

                        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Entregas Tardías</p>
                          <div className="space-y-1">
                            {tarea.permite_entrega_tardia || tarea.permite_entregas_tardias ? (
                              <span className="text-green-600 dark:text-green-400 flex items-center gap-1">
                                <CheckCircle className="w-4 h-4" /> Permitidas
                              </span>
                            ) : (
                              <span className="text-red-600 dark:text-red-400 flex items-center gap-1">
                                <X className="w-4 h-4" /> No permitidas
                              </span>
                            )}
                            {tarea.penalizacion_tardia > 0 && (
                              <span className="text-orange-600 dark:text-orange-400 block text-sm">
                                Penalización: -{tarea.penalizacion_tardia}%
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Descripción completa */}
                      {tarea.descripcion && (
                        <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                          <h4 className="text-sm font-bold text-blue-900 dark:text-blue-100 mb-2 flex items-center gap-2">
                            <FileText size={16} />
                            Descripción
                          </h4>
                          <p className="text-blue-800 dark:text-blue-200 whitespace-pre-wrap">
                            {tarea.descripcion}
                          </p>
                        </div>
                      )}

                      {/* Instrucciones detalladas */}
                      {tarea.instrucciones && (
                        <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                          <h4 className="font-semibold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                            Instrucciones Detalladas
                          </h4>
                          <div className="text-green-800 dark:text-green-200 whitespace-pre-wrap">
                            {tarea.instrucciones}
                          </div>
                        </div>
                      )}

                      {/* Objetivos de aprendizaje */}
                      {tarea.objetivos && (
                        <div className="p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                          <h4 className="font-semibold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                            <Target className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                            Objetivos de Aprendizaje
                          </h4>
                          <div className="text-purple-800 dark:text-purple-200 whitespace-pre-wrap">
                            {tarea.objetivos}
                          </div>
                        </div>
                      )}

                      {/* Criterios de evaluación */}
                      {tarea.criterios_evaluacion && (
                        <div className="p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
                          <h4 className="font-semibold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                            <ListChecks className="w-5 h-5 text-green-600 dark:text-green-400" />
                            Criterios de Evaluación
                          </h4>
                          <div className="text-yellow-800 dark:text-yellow-200 whitespace-pre-wrap">
                            {tarea.criterios_evaluacion}
                          </div>
                        </div>
                      )}

                      {/* Rúbrica de Evaluación */}
                      {tarea.rubrica && (
                        <div className="p-4 rounded-lg bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800">
                          <h4 className="font-semibold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                            Rúbrica de Evaluación
                          </h4>
                          <div className="space-y-3">
                            {/* Si es un objeto simple de criterios */}
                            {tarea.rubrica.criterios && typeof tarea.rubrica.criterios === 'object' ? (
                              Object.entries(tarea.rubrica.criterios as Record<string, any>).map(([criterio, detalle], index) => (
                                <div key={index} className="bg-white dark:bg-slate-800 p-3 rounded border border-orange-100 dark:border-orange-900/50">
                                  <p className="font-semibold text-slate-800 dark:text-slate-200 mb-1">{criterio}</p>
                                  <p className="text-sm text-slate-600 dark:text-slate-400">{detalle.descripcion || detalle}</p>
                                  {detalle.puntos && (
                                    <span className="text-xs font-bold text-orange-600 dark:text-orange-400 mt-1 block">
                                      {detalle.puntos} pts
                                    </span>
                                  )}
                                </div>
                              ))
                            ) : (
                              <div className="text-orange-800 dark:text-orange-200 text-sm">
                                Ver detalles de la rúbrica en la entrega.
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Recursos necesarios */}
                      {tarea.recursos_necesarios && (
                        <div className="p-4 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800">
                          <h4 className="font-semibold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                            <Library className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                            Recursos Necesarios
                          </h4>
                          <div className="text-indigo-800 dark:text-indigo-200 whitespace-pre-wrap">
                            {tarea.recursos_necesarios}
                          </div>
                        </div>
                      )}

                      {/* Archivo adjunto */}
                      {tarea.archivo_adjunto && (
                        <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-600">
                          <h4 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
                            📎 Archivo Adjunto
                          </h4>
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                              <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div className="flex-1">
                              <p className="font-medium text-gray-900 dark:text-white">
                                Archivo de la tarea
                              </p>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                Click para descargar
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Información del profesor/creador */}
                      <div className="p-4 rounded-lg bg-slate-100 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                          <User className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                          Información del Profesor
                        </h4>
                        <div className="space-y-1 text-sm">
                          <p className="text-slate-700 dark:text-slate-300">
                            <span className="font-medium">Creada por:</span> {tarea.creado_por || 'Profesor'}
                          </p>
                          {tarea.fecha_creacion && (
                            <p className="text-slate-700 dark:text-slate-300">
                              <span className="font-medium">Fecha de creación:</span> {formatearFecha(tarea.fecha_creacion)}
                            </p>
                          )}
                          {tarea.fecha_actualizacion && tarea.fecha_actualizacion !== tarea.fecha_creacion && (
                            <p className="text-slate-700 dark:text-slate-300">
                              <span className="font-medium">Última actualización:</span> {formatearFecha(tarea.fecha_actualizacion)}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Estado y visibilidad */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Estado</p>
                          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                            <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Visible</p>
                            <p className="font-semibold text-slate-900 dark:text-white">
                              {tarea.visible_estudiantes ? (
                                <span className="text-green-600 dark:text-green-400 flex items-center gap-1"><CheckCircle className="w-4 h-4" /> Para estudiantes</span>
                              ) : (
                                <span className="text-red-600 dark:text-red-400 flex items-center gap-1"><X className="w-4 h-4" /> Oculta</span>
                              )}
                            </p>
                          </div>
                        </div>

                        {/* Retroalimentación IA */}
                        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-600">
                          <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 font-medium">Retroalimentación IA</p>
                          <div>
                            {tarea.habilitar_retroalimentacion_ia ? (
                              <span className="text-green-600 dark:text-green-400 flex items-center gap-1">
                                <Lightbulb className="w-4 h-4" /> Para estudiantes
                              </span>
                            ) : (
                              <span className="text-red-600 dark:text-red-400 flex items-center gap-1">
                                <X className="w-4 h-4" /> Oculta
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Gamificación */}
                        {(tarea.puntos_base || tarea.puntos_bonificacion) && (
                          <div className="p-4 rounded-lg bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border border-yellow-200 dark:border-yellow-800">
                            <h4 className="font-semibold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                              <Gamepad2 className="w-5 h-5 text-pink-600 dark:text-pink-400" />
                              Gamificación
                            </h4>
                            <div className="grid grid-cols-2 gap-4">
                              {tarea.puntos_base && (
                                <div>
                                  <p className="text-xs text-yellow-700 dark:text-yellow-300">Puntos Base</p>
                                  <p className="font-bold text-yellow-900 dark:text-yellow-100">{tarea.puntos_base}</p>
                                </div>
                              )}
                              {tarea.puntos_bonificacion && (
                                <div>
                                  <p className="text-xs text-yellow-700 dark:text-yellow-300">Puntos Bonificación</p>
                                  <p className="font-bold text-yellow-900 dark:text-yellow-100">{tarea.puntos_bonificacion}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* IA Features */}
                        {tarea.habilitar_retroalimentacion_ia && (
                          <div className="p-4 rounded-lg bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800">
                            <h4 className="text-sm font-bold text-purple-900 dark:text-purple-100 mb-2 flex items-center gap-2">
                              <Bot className="w-5 h-5" />
                              Características de IA
                            </h4>
                            <div className="space-y-2">
                              <p className="text-purple-800 dark:text-purple-200 flex items-center gap-2">
                                <CheckCircle className="h-4 w-4" />
                                Retroalimentación automática con IA
                              </p>
                              {tarea.prompt_ia_personalizado && (
                                <p className="text-purple-800 dark:text-purple-200 text-sm">
                                  <span className="font-medium">Prompt personalizado:</span> Configurado
                                </p>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Botones */}
                    <div className="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={onClose}
                        className="flex-1 px-4 py-3 rounded-lg border-2 border-slate-200 dark:border-slate-600 text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors font-semibold"
                      >
                        Cerrar
                      </motion.button>

                      {isStudentUser ? (
                        // Botón para estudiantes: Entregar Tarea - Redirige a página dedicada
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            onClose(); // Cerrar modal
                            // Usar tarea_id si existe, sino el id del objeto
                            const tareaId = tarea.tarea_id || (tarea as any).id;
                            if (tareaId) {
                              navigate(`/tareas/${tareaId}/entregar`);
                            } else {
                              console.error('No se pudo obtener el ID de la tarea');
                            }
                          }}
                          className="flex-1 px-4 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold transition-colors flex items-center justify-center gap-2"
                        >
                          <Upload size={18} />
                          Entregar Tarea
                        </motion.button >
                      ) : (
                        // Botones para profesores
                        <div className="flex gap-2 flex-1">
                          {/* Botón Ver Entregas/Calificar */}
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              onClose(); // Cerrar modal
                              const tareaId = tarea.tarea_id || (tarea as any).id;
                              if (tareaId) {
                                // Navegar a la página de calificación
                                navigate(`/academic/tareas/${tareaId}/calificar`);
                              } else {
                                console.error('No se pudo obtener el ID de la tarea', { tareaId });
                              }
                            }}
                            className="flex-1 px-4 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold transition-colors flex items-center justify-center gap-2"
                          >
                            <ClipboardList className="w-5 h-5" />
                            Ver Entregas
                          </motion.button>

                          {/* Botón Editar Tarea */}
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              onClose();
                              onEdit?.(tarea);
                            }}
                            className="flex-1 px-4 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors flex items-center justify-center gap-2"
                          >
                            <Pencil className="w-5 h-5" />
                            Editar Tarea
                          </motion.button>
                        </div>
                      )}
                    </div >

                    {/* Lista de Entregas (Solo Profesores) */}
                    {
                      !isStudentUser && tarea.entregas && tarea.entregas.length > 0 && (
                        <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700">
                          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
                            Entregas ({tarea.entregas.length})
                          </h3>
                          <EntregasList
                            entregas={tarea.entregas}
                            cargando={false}
                            onOpenEntrega={(id) => {
                              // TODO: Implementar navegación a detalle de entrega para calificación manual
                              console.log("Abrir entrega para calificación:", id);
                              // Podríamos navegar a una ruta de calificación si existe
                              // navigate(`/cursos/${courseId}/tareas/${tarea.id}/entregas/${id}`);
                            }}
                            onGenerarIndividual={async (id) => {
                              await generarRetroalimentacion(id, "gemini-2.5-flash", "completo");
                            }}
                          />
                        </div>
                      )
                    }
                  </motion.div >
                ) : (
                  <motion.div
                    key="retroalimentacion"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="space-y-6"
                  >
                    {retroalimentacion && retroalimentacion.retroalimentacion ? (
                      <RetroalimentacionVisor data={retroalimentacion.retroalimentacion} isLoading={cargando} />
                    ) : cargando ? (
                      <div className="p-8 text-center">
                        <Zap className="w-8 h-8 text-purple-600 mx-auto animate-spin mb-2" />
                        <p className="text-gray-600">Generando análisis con IA...</p>
                      </div>
                    ) : (
                      <div className="p-8 text-center space-y-4">
                        <p className="text-gray-600">No hay retroalimentación IA disponible</p>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={handleGenerarRetroalimentacion}
                          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold flex items-center justify-center gap-2 mx-auto"
                        >
                          <Zap size={18} />
                          Generar Retroalimentación con IA
                        </motion.button>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>
        </div >
      )}
    </AnimatePresence >
  );
};


