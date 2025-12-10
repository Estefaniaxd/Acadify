import React, { memo } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Calendar,
  Clock,
  Star,
  FileText,
  AlertCircle,
  BookOpen,
  Award,
  User,
  CheckCircle,
  Upload
} from 'lucide-react';
import { Button } from './Button';
import { Badge } from './Badge';

interface TaskDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: any;
  isStudent: boolean;
  courseId: string;
}

/**
 * Modal de detalle de tarea - Simple, limpio y funcional
 * Usa Portal para evitar problemas de z-index
 */
export const TaskDetailModal = memo(({
  isOpen,
  onClose,
  task,
  isStudent,
  courseId
}: TaskDetailModalProps) => {
  const navigate = useNavigate();

  if (!task) return null;

  // Extraer el ID de la tarea (intentar múltiples campos)
  const taskId = task?.tarea_id || task?.id || task?.task_id;

  const handleSubmitTask = () => {
    console.log('📤 Navegando a entregar tarea:', { taskId, courseId });
    if (!taskId) {
      alert('Error: No se pudo identificar la tarea');
      return;
    }
    onClose();
    setTimeout(() => {
      navigate(`/tareas/${taskId}/entregar`);
    }, 100);
  };

  const content = (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-neutral-900 rounded-2xl shadow-2xl border border-neutral-200 dark:border-neutral-800"
          >
            {/* Header */}
            <div className="sticky top-0 flex items-start justify-between gap-4 p-6 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/50 backdrop-blur-sm z-10">
              <div className="flex-1 min-w-0">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white truncate">
                  {task?.titulo || 'Tarea sin título'}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {task?.categoria && `${task.categoria} • `}
                  {task?.tipo && `Tipo: ${task.tipo}`}
                </p>
              </div>

              {/* Close button */}
              <button
                onClick={onClose}
                className="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-neutral-800 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Status badges */}
              <div className="flex flex-wrap gap-2">
                {task?.estado && (
                  <Badge variant={task.estado === 'asignada' ? 'default' : 'secondary'}>
                    {task.estado}
                  </Badge>
                )}
                {task?.prioridad && (
                  <Badge
                    variant={
                      task.prioridad === 'urgente' || task.prioridad === 'alta'
                        ? 'danger'
                        : task.prioridad === 'media'
                        ? 'warning'
                        : 'success'
                    }
                  >
                    {task.prioridad}
                  </Badge>
                )}
                {task?.puntuacion_maxima && (
                  <Badge variant="primary">
                    <Star className="w-3 h-3 mr-1" />
                    {task.puntuacion_maxima} pts
                  </Badge>
                )}
              </div>

              {/* Description */}
              {task?.descripcion && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Descripción
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                    {task.descripcion}
                  </p>
                </div>
              )}

              {/* Instructions */}
              {task?.instrucciones && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Instrucciones
                  </h3>
                  <p className="text-blue-800 dark:text-blue-200 whitespace-pre-wrap">
                    {task.instrucciones}
                  </p>
                </div>
              )}

              {/* Key details grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Dates */}
                <div className="bg-gray-50 dark:bg-neutral-800 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    Fechas
                  </h4>
                  <div className="space-y-2 text-sm">
                    {task?.fecha_asignacion && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Asignada:</span>
                        <span className="font-medium">
                          {new Date(task.fecha_asignacion).toLocaleDateString('es-ES')}
                        </span>
                      </div>
                    )}
                    {task?.fecha_limite && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Vencimiento:</span>
                        <span className="font-medium text-red-600 dark:text-red-400">
                          {new Date(task.fecha_limite).toLocaleDateString('es-ES')}
                        </span>
                      </div>
                    )}
                    {task?.tiempo_estimado && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Tiempo:</span>
                        <span className="font-medium flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {task.tiempo_estimado} min
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Configuration */}
                <div className="bg-gray-50 dark:bg-neutral-800 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    Configuración
                  </h4>
                  <div className="space-y-2 text-sm">
                    {task?.formato_entrega && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Formato:</span>
                        <span className="font-medium">{task.formato_entrega}</span>
                      </div>
                    )}
                    {task?.tamano_maximo_mb && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Tamaño máx:</span>
                        <span className="font-medium">{task.tamano_maximo_mb} MB</span>
                      </div>
                    )}
                    {task?.intentos_maximos && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Intentos:</span>
                        <span className="font-medium">{task.intentos_maximos}</span>
                      </div>
                    )}
                    {task?.permite_entrega_tardia || task?.permite_entregas_tardias ? (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Entrega tardía:</span>
                        <Badge variant="success" size="sm">Permitida</Badge>
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>

              {/* Evaluation criteria */}
              {task?.criterios_evaluacion && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                    <Award className="w-4 h-4" />
                    Criterios de Evaluación
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {task.criterios_evaluacion}
                  </p>
                </div>
              )}

              {/* Professor info */}
              {(task?.docente_nombre || task?.docente_email) && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Profesor
                  </h4>
                  <div className="text-sm">
                    <p className="font-medium text-blue-900 dark:text-blue-100">
                      {task.docente_nombre || 'Profesor'}
                    </p>
                    {task?.docente_email && (
                      <p className="text-blue-700 dark:text-blue-300">
                        {task.docente_email}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Objectives */}
              {task?.objetivos && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Objetivos de Aprendizaje
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                    {task.objetivos}
                  </p>
                </div>
              )}

              {/* Resources */}
              {task?.recursos_necesarios && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Recursos Necesarios
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                    {task.recursos_necesarios}
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 flex items-center justify-end gap-3 p-6 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/50">
              <Button variant="secondary" onClick={onClose}>
                Cerrar
              </Button>

              {isStudent && taskId && (
                <Button
                  variant="primary"
                  onClick={handleSubmitTask}
                  leftIcon={Upload}
                >
                  Entregar Tarea
                </Button>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );

  // Render using Portal to avoid z-index issues
  return createPortal(content, document.body);
});

TaskDetailModal.displayName = 'TaskDetailModal';

export default TaskDetailModal;
