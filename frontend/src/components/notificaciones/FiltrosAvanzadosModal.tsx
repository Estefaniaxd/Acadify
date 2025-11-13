/**
 * Modal de Filtros Avanzados de Notificaciones
 * 
 * @module components/notificaciones/FiltrosAvanzadosModal
 * @description Modal con opciones avanzadas de filtrado
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X, Filter, Calendar, Tag, Check, RotateCcw
} from 'lucide-react';
import { type TipoNotificacion } from '../../services/notificaciones.service';

interface FiltrosAvanzadosModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAplicar: (filtros: FiltrosAvanzados) => void;
  filtrosActuales: FiltrosAvanzados;
}

export interface FiltrosAvanzados {
  tipos: TipoNotificacion[];
  fechaDesde?: string;
  fechaHasta?: string;
  soloNoLeidas: boolean;
  soloImportantes: boolean;
  ordenarPor: 'fecha_creacion' | 'fecha_lectura';
  ordenDesc: boolean;
}

const TIPOS_DISPONIBLES: { value: TipoNotificacion; label: string; emoji: string }[] = [
  { value: 'mensaje_directo', label: 'Mensajes Directos', emoji: '💬' },
  { value: 'mencion', label: 'Menciones', emoji: '@' },
  { value: 'respuesta_hilo', label: 'Respuestas', emoji: '💭' },
  { value: 'mensaje_importante', label: 'Importantes', emoji: '⚠️' },
  { value: 'tarea_nueva', label: 'Nuevas Tareas', emoji: '📝' },
  { value: 'tarea_vencimiento', label: 'Vencimientos', emoji: '⏰' },
  { value: 'tarea_calificada', label: 'Calificaciones', emoji: '✅' },
  { value: 'tarea_comentario', label: 'Comentarios Tarea', emoji: '💬' },
  { value: 'curso_nuevo', label: 'Nuevos Cursos', emoji: '🎓' },
  { value: 'clase_cancelada', label: 'Clases Canceladas', emoji: '🚫' },
  { value: 'evaluacion_disponible', label: 'Evaluaciones', emoji: '📊' },
  { value: 'logro_desbloqueado', label: 'Logros', emoji: '🏆' },
  { value: 'sistema', label: 'Sistema', emoji: '⚙️' },
];

export default function FiltrosAvanzadosModal({
  isOpen,
  onClose,
  onAplicar,
  filtrosActuales,
}: FiltrosAvanzadosModalProps) {
  const [filtros, setFiltros] = useState<FiltrosAvanzados>(filtrosActuales);

  const handleToggleTipo = (tipo: TipoNotificacion) => {
    setFiltros((prev) => ({
      ...prev,
      tipos: prev.tipos.includes(tipo)
        ? prev.tipos.filter((t) => t !== tipo)
        : [...prev.tipos, tipo],
    }));
  };

  const handleSelectAll = () => {
    setFiltros((prev) => ({
      ...prev,
      tipos: TIPOS_DISPONIBLES.map((t) => t.value),
    }));
  };

  const handleDeselectAll = () => {
    setFiltros((prev) => ({
      ...prev,
      tipos: [],
    }));
  };

  const handleReset = () => {
    setFiltros({
      tipos: [],
      fechaDesde: undefined,
      fechaHasta: undefined,
      soloNoLeidas: false,
      soloImportantes: false,
      ordenarPor: 'fecha_creacion',
      ordenDesc: true,
    });
  };

  const handleAplicar = () => {
    onAplicar(filtros);
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
                      <Filter className="w-5 h-5 text-white" />
                    </div>
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      Filtros Avanzados
                    </h2>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Tipos de Notificación */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Tag className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        Tipos de Notificación
                      </h3>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleSelectAll}
                        className="text-xs text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300"
                      >
                        Seleccionar todo
                      </button>
                      <span className="text-xs text-gray-400">|</span>
                      <button
                        onClick={handleDeselectAll}
                        className="text-xs text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300"
                      >
                        Limpiar
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    {TIPOS_DISPONIBLES.map((tipo) => {
                      const isSelected = filtros.tipos.includes(tipo.value);
                      return (
                        <button
                          key={tipo.value}
                          onClick={() => handleToggleTipo(tipo.value)}
                          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                            isSelected
                              ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300 ring-2 ring-violet-500'
                              : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                          }`}
                        >
                          <span>{tipo.emoji}</span>
                          <span className="flex-1 text-left">{tipo.label}</span>
                          {isSelected && <Check className="w-4 h-4" />}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Rango de Fechas */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Calendar className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      Rango de Fechas
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Desde
                      </label>
                      <input
                        type="date"
                        value={filtros.fechaDesde || ''}
                        onChange={(e) =>
                          setFiltros((prev) => ({ ...prev, fechaDesde: e.target.value }))
                        }
                        className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Hasta
                      </label>
                      <input
                        type="date"
                        value={filtros.fechaHasta || ''}
                        onChange={(e) =>
                          setFiltros((prev) => ({ ...prev, fechaHasta: e.target.value }))
                        }
                        className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Opciones Adicionales */}
                <div className="space-y-3">
                  <ToggleOption
                    label="Solo no leídas"
                    description="Mostrar únicamente notificaciones sin leer"
                    checked={filtros.soloNoLeidas}
                    onChange={() =>
                      setFiltros((prev) => ({ ...prev, soloNoLeidas: !prev.soloNoLeidas }))
                    }
                  />
                  <ToggleOption
                    label="Solo importantes"
                    description="Mostrar únicamente notificaciones marcadas como importantes"
                    checked={filtros.soloImportantes}
                    onChange={() =>
                      setFiltros((prev) => ({ ...prev, soloImportantes: !prev.soloImportantes }))
                    }
                  />
                </div>

                {/* Ordenamiento */}
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                    Ordenar por
                  </h3>
                  <div className="space-y-2">
                    <label className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                      <input
                        type="radio"
                        name="ordenar"
                        checked={filtros.ordenarPor === 'fecha_creacion'}
                        onChange={() =>
                          setFiltros((prev) => ({ ...prev, ordenarPor: 'fecha_creacion' }))
                        }
                        className="w-4 h-4 text-violet-600"
                      />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        Fecha de creación
                      </span>
                    </label>
                    <label className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                      <input
                        type="radio"
                        name="ordenar"
                        checked={filtros.ordenarPor === 'fecha_lectura'}
                        onChange={() =>
                          setFiltros((prev) => ({ ...prev, ordenarPor: 'fecha_lectura' }))
                        }
                        className="w-4 h-4 text-violet-600"
                      />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        Fecha de lectura
                      </span>
                    </label>
                  </div>

                  <div className="mt-3">
                    <ToggleOption
                      label="Orden descendente"
                      description="Mostrar primero las más recientes"
                      checked={filtros.ordenDesc}
                      onChange={() =>
                        setFiltros((prev) => ({ ...prev, ordenDesc: !prev.ordenDesc }))
                      }
                    />
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <button
                  onClick={handleReset}
                  className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  Restaurar
                </button>
                <div className="flex gap-3">
                  <button
                    onClick={onClose}
                    className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleAplicar}
                    className="px-6 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                  >
                    Aplicar Filtros
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// Componente auxiliar
interface ToggleOptionProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: () => void;
}

function ToggleOption({ label, description, checked, onChange }: ToggleOptionProps) {
  return (
    <div className="flex items-start justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <div className="flex-1">
        <p className="font-medium text-gray-900 dark:text-white text-sm">{label}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">{description}</p>
      </div>
      <button
        onClick={onChange}
        className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 ${
          checked ? 'bg-violet-600' : 'bg-gray-300 dark:bg-gray-600'
        }`}
      >
        <span
          className={`inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  );
}
