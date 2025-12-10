import { useState } from 'react';
import {
  X,
  Loader2,
  Sparkles,
  ChevronDown,
  Plus,
  Trash2,
  AlertCircle,
} from 'lucide-react';
import { TareaCreate, TipoTarea, PrioridadTarea } from '../types';
import { apiClientTareas } from '../api';

interface CrearTareaModalProps {
  cursoId: string;
  onClose: () => void;
  onTareaCreada: () => void;
}

interface FormData extends Omit<TareaCreate, 'fecha_limite'> {
  fecha_limite: string;
  fecha_inicio_disponible: string;
}

// Componente acordeón reutilizable
function Accordion({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 hover:bg-gray-100 dark:hover:bg-zinc-700 flex items-center justify-between transition-colors"
      >
        <span className="font-semibold text-gray-900 dark:text-gray-100">
          {title}
        </span>
        <ChevronDown
          className={`w-5 h-5 transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && (
        <div className="px-4 py-3 space-y-3 border-t border-gray-200 dark:border-gray-700">
          {children}
        </div>
      )}
    </div>
  );
}

export default function CrearTareaModalCompleto({
  cursoId,
  onClose,
  onTareaCreada,
}: CrearTareaModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<FormData>({
    titulo: '',
    descripcion: '',
    instrucciones: '',
    objetivos: '',
    tipo: TipoTarea.EJERCICIOS,
    prioridad: PrioridadTarea.MEDIA,
    tags: '',
    fecha_limite: '',
    fecha_inicio_disponible: '',
    tiempo_estimado: 0,
    permite_entrega_tardia: false,
    penalizacion_tardia: 0,
    intentos_maximos: 1,
    formato_entrega: '',
    tamano_maximo_mb: 10,
    puntuacion_maxima: 100,
    peso_evaluacion: 1,
    es_grupal: false,
    es_publica: true,
    requiere_aprobacion: false,
    recursos_necesarios: '',
    criterios_evaluacion: '',
    habilitar_retroalimentacion_ia: true,
    prompt_ia_personalizado: '',
  });

  const handleChange = (
    field: keyof FormData,
    value: string | number | boolean
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validación
    if (!formData.titulo.trim()) {
      setError('El título es requerido');
      return;
    }

    if (!formData.fecha_limite) {
      setError('La fecha límite es requerida');
      return;
    }

    if (formData.puntuacion_maxima <= 0) {
      setError('La puntuación máxima debe ser mayor a 0');
      return;
    }

    if (formData.intentos_maximos < 1) {
      setError('Los intentos máximos debe ser al menos 1');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Preparar datos para enviar
      // NOTA: El backend espera estos campos específicos según el schema
      const tareaData: TareaCreate = {
        titulo: formData.titulo.trim(),
        descripcion: formData.descripcion || undefined,
        instrucciones: formData.instrucciones || undefined,
        objetivos: formData.objetivos || undefined,
        tipo: formData.tipo,
        prioridad: formData.prioridad,
        tags: formData.tags || undefined,
        fecha_limite: new Date(formData.fecha_limite).toISOString(),
        fecha_inicio_disponible: formData.fecha_inicio_disponible
          ? new Date(formData.fecha_inicio_disponible).toISOString()
          : undefined,
        tiempo_estimado: formData.tiempo_estimado || undefined,
        permite_entrega_tardia: formData.permite_entrega_tardia,
        penalizacion_tardia: formData.penalizacion_tardia,
        intentos_maximos: formData.intentos_maximos,
        formato_entrega: formData.formato_entrega || undefined,
        tamano_maximo_mb: formData.tamano_maximo_mb,
        puntuacion_maxima: formData.puntuacion_maxima,
        peso_evaluacion: formData.peso_evaluacion,
        es_grupal: formData.es_grupal,
        es_publica: formData.es_publica,
        requiere_aprobacion: formData.requiere_aprobacion,
        recursos_necesarios: formData.recursos_necesarios || undefined,
        criterios_evaluacion: formData.criterios_evaluacion || undefined,
      };

      // Crear tarea
      await apiClientTareas.crearTarea(cursoId, tareaData);

      // Si IA está habilitada, guardar prompt personalizado
      if (formData.habilitar_retroalimentacion_ia && formData.prompt_ia_personalizado) {
        // TODO: Enviar prompt personalizado a endpoint adicional si es necesario
        console.log('Prompt IA:', formData.prompt_ia_personalizado);
      }

      onTareaCreada();
      setFormData({
        titulo: '',
        descripcion: '',
        instrucciones: '',
        objetivos: '',
        tipo: TipoTarea.EJERCICIOS,
        prioridad: PrioridadTarea.MEDIA,
        tags: '',
        fecha_limite: '',
        fecha_inicio_disponible: '',
        tiempo_estimado: 0,
        permite_entrega_tardia: false,
        penalizacion_tardia: 0,
        intentos_maximos: 1,
        formato_entrega: '',
        tamano_maximo_mb: 10,
        puntuacion_maxima: 100,
        peso_evaluacion: 1,
        es_grupal: false,
        es_publica: true,
        requiere_aprobacion: false,
        recursos_necesarios: '',
        criterios_evaluacion: '',
        habilitar_retroalimentacion_ia: true,
        prompt_ia_personalizado: '',
      });
    } catch (err) {
      console.error('Error creando tarea:', err);
      setError('Error al crear la tarea. Por favor intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-3xl w-full max-h-[95vh] overflow-hidden flex flex-col">
        {/* Header - Sticky */}
        <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Crear Nueva Tarea (Completa)
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-zinc-800 rounded-lg transition-colors disabled:opacity-50"
            disabled={loading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form - Scrollable */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-6 py-5">
          <div className="space-y-4 max-w-2xl mx-auto">
            {/* Error Alert */}
            {error && (
              <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 text-sm flex items-gap-2">
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* SECCIÓN 1: Información Básica */}
            <Accordion title="📝 Información Básica" defaultOpen={true}>
              {/* Título */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Título <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.titulo}
                  onChange={(e) => handleChange('titulo', e.target.value)}
                  placeholder="ej: Ecuaciones Diferenciales - Ejercicios"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  required
                />
              </div>

              {/* Descripción */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Descripción
                </label>
                <textarea
                  value={formData.descripcion}
                  onChange={(e) => handleChange('descripcion', e.target.value)}
                  placeholder="Descripción breve de la tarea..."
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>

              {/* Tipo y Prioridad */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Tipo
                  </label>
                  <select
                    value={formData.tipo}
                    onChange={(e) =>
                      handleChange('tipo', e.target.value as TipoTarea)
                    }
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  >
                    <option value={TipoTarea.EJERCICIOS}>Ejercicios</option>
                    <option value={TipoTarea.ENSAYO}>Ensayo</option>
                    <option value={TipoTarea.PROYECTO}>Proyecto</option>
                    <option value={TipoTarea.QUIZ}>Quiz</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Prioridad
                  </label>
                  <select
                    value={formData.prioridad}
                    onChange={(e) =>
                      handleChange('prioridad', e.target.value as PrioridadTarea)
                    }
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  >
                    <option value={PrioridadTarea.BAJA}>Baja</option>
                    <option value={PrioridadTarea.MEDIA}>Media</option>
                    <option value={PrioridadTarea.ALTA}>Alta</option>
                  </select>
                </div>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tags (separadas por comas)
                </label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => handleChange('tags', e.target.value)}
                  placeholder="ej: álgebra, cálculo, matemáticas"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>
            </Accordion>

            {/* SECCIÓN 2: Contenido */}
            <Accordion title="📖 Contenido y Recursos">
              {/* Instrucciones */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Instrucciones Detalladas
                </label>
                <textarea
                  value={formData.instrucciones}
                  onChange={(e) => handleChange('instrucciones', e.target.value)}
                  placeholder="Instrucciones paso a paso..."
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>

              {/* Objetivos */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Objetivos de Aprendizaje
                </label>
                <textarea
                  value={formData.objetivos}
                  onChange={(e) => handleChange('objetivos', e.target.value)}
                  placeholder="¿Qué deben aprender los estudiantes?"
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>

              {/* Recursos necesarios */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Recursos Necesarios
                </label>
                <input
                  type="text"
                  value={formData.recursos_necesarios}
                  onChange={(e) => handleChange('recursos_necesarios', e.target.value)}
                  placeholder="Libros, software, etc."
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>

              {/* Criterios de evaluación */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Criterios de Evaluación
                </label>
                <textarea
                  value={formData.criterios_evaluacion}
                  onChange={(e) =>
                    handleChange('criterios_evaluacion', e.target.value)
                  }
                  placeholder="Describe cómo se evaluará..."
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>
            </Accordion>

            {/* SECCIÓN 3: Fechas */}
            <Accordion title="📅 Fechas y Disponibilidad">
              {/* Fecha de inicio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Fecha de Inicio (disponible desde)
                </label>
                <input
                  type="datetime-local"
                  value={formData.fecha_inicio_disponible}
                  onChange={(e) =>
                    handleChange('fecha_inicio_disponible', e.target.value)
                  }
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>

              {/* Fecha límite */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Fecha Límite <span className="text-red-500">*</span>
                </label>
                <input
                  type="datetime-local"
                  value={formData.fecha_limite}
                  onChange={(e) => handleChange('fecha_limite', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  required
                />
              </div>

              {/* Tiempo estimado */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tiempo Estimado (minutos)
                </label>
                <input
                  type="number"
                  value={formData.tiempo_estimado}
                  onChange={(e) =>
                    handleChange('tiempo_estimado', parseInt(e.target.value) || 0)
                  }
                  min="0"
                  step="15"
                  placeholder="ej: 60"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>
            </Accordion>

            {/* SECCIÓN 4: Puntuación y Entrega */}
            <Accordion title="⭐ Puntuación y Entregas">
              {/* Puntuación máxima */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Puntuación Máxima <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formData.puntuacion_maxima}
                  onChange={(e) =>
                    handleChange('puntuacion_maxima', parseFloat(e.target.value))
                  }
                  min="0.1"
                  step="0.1"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  required
                />
              </div>

              {/* Peso en evaluación */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Peso en Evaluación
                </label>
                <input
                  type="number"
                  value={formData.peso_evaluacion}
                  onChange={(e) =>
                    handleChange('peso_evaluacion', parseFloat(e.target.value))
                  }
                  min="0.1"
                  step="0.1"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>

              {/* Intentos máximos */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Intentos Máximos <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formData.intentos_maximos}
                  onChange={(e) =>
                    handleChange('intentos_maximos', parseInt(e.target.value) || 1)
                  }
                  min="1"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  required
                />
              </div>

              {/* Permite entregas tardías */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.permite_entrega_tardia}
                  onChange={(e) =>
                    handleChange('permite_entrega_tardia', e.target.checked)
                  }
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Permitir entregas tardías
                </span>
              </label>

              {/* Penalización tardia */}
              {formData.permite_entrega_tardia && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Penalización Tardía (%)
                  </label>
                  <input
                    type="number"
                    value={formData.penalizacion_tardia}
                    onChange={(e) =>
                      handleChange('penalizacion_tardia', parseFloat(e.target.value))
                    }
                    min="0"
                    max="100"
                    step="5"
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  />
                </div>
              )}
            </Accordion>

            {/* SECCIÓN 5: Formato de Entrega */}
            <Accordion title="📁 Formato de Entrega">
              {/* Formato entrega */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Formatos Aceptados
                </label>
                <input
                  type="text"
                  value={formData.formato_entrega}
                  onChange={(e) => handleChange('formato_entrega', e.target.value)}
                  placeholder="ej: .pdf, .docx, .txt (separados por comas)"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>

              {/* Tamaño máximo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tamaño Máximo (MB)
                </label>
                <input
                  type="number"
                  value={formData.tamano_maximo_mb}
                  onChange={(e) =>
                    handleChange('tamano_maximo_mb', parseFloat(e.target.value))
                  }
                  min="0.1"
                  step="0.5"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                />
              </div>
            </Accordion>

            {/* SECCIÓN 6: Opciones Avanzadas */}
            <Accordion title="⚙️ Opciones Avanzadas">
              {/* Es grupal */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.es_grupal}
                  onChange={(e) => handleChange('es_grupal', e.target.checked)}
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Tarea Grupal
                </span>
              </label>

              {/* Es pública */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.es_publica}
                  onChange={(e) => handleChange('es_publica', e.target.checked)}
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Tarea Pública (visible para estudiantes)
                </span>
              </label>

              {/* Requiere aprobación */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.requiere_aprobacion}
                  onChange={(e) =>
                    handleChange('requiere_aprobacion', e.target.checked)
                  }
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Requiere Aprobación de Coordinador
                </span>
              </label>
            </Accordion>

            {/* SECCIÓN 7: IA y Retroalimentación */}
            <Accordion title="🤖 IA y Retroalimentación">
              {/* Habilitar IA */}
              <label className="flex items-center gap-3 cursor-pointer p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <input
                  type="checkbox"
                  checked={formData.habilitar_retroalimentacion_ia}
                  onChange={(e) =>
                    handleChange('habilitar_retroalimentacion_ia', e.target.checked)
                  }
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-500" />
                  Habilitar Retroalimentación con IA (Rutilio)
                </span>
              </label>

              {/* Prompt personalizado */}
              {formData.habilitar_retroalimentacion_ia && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Prompt Personalizado para IA (Opcional)
                  </label>
                  <textarea
                    value={formData.prompt_ia_personalizado}
                    onChange={(e) =>
                      handleChange('prompt_ia_personalizado', e.target.value)
                    }
                    placeholder="Ej: Evalúa siguiendo las mejores prácticas de Python. Revisa legibilidad, eficiencia y documentación..."
                    rows={3}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Si dejas esto vacío, se usará el prompt predeterminado.
                  </p>
                </div>
              )}
            </Accordion>
          </div>
        </form>

        {/* Footer - Sticky */}
        <div className="sticky bottom-0 bg-white dark:bg-zinc-900 border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors disabled:opacity-50 font-medium text-sm"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            className="px-6 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 font-medium text-sm"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Creando...</span>
              </>
            ) : (
              <span>Crear Tarea</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
