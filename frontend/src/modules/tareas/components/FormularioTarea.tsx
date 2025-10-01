import React, { useState } from 'react';
import { TareaCreate, TipoTarea, PrioridadTarea, Tarea } from '../types';
import TareasApi from '../api';

interface FormularioTareaProps {
  onSubmit: (tarea: TareaCreate) => Promise<void>;
  onCancel: () => void;
  grupoId: string;
  docenteId: string;
  tareaInicial?: Tarea | null;
}

const FormularioTarea: React.FC<FormularioTareaProps> = ({
  onSubmit,
  onCancel,
  grupoId,
  docenteId,
  tareaInicial = null
}) => {
  const [formData, setFormData] = useState<TareaCreate>({
    grupo_id: grupoId,
    docente_id: docenteId,
    titulo: tareaInicial?.titulo || '',
    descripcion: tareaInicial?.descripcion || '',
    instrucciones: tareaInicial?.instrucciones || '',
    objetivos: tareaInicial?.objetivos || '',
    tipo_tarea: tareaInicial?.tipo_tarea || TipoTarea.ENSAYO,
    prioridad: tareaInicial?.prioridad || PrioridadTarea.MEDIA,
    categoria: tareaInicial?.categoria || '',
    tags: tareaInicial?.tags || '',
    fecha_limite: tareaInicial?.fecha_limite ? 
      new Date(tareaInicial.fecha_limite).toISOString().slice(0, 16) : '',
    fecha_inicio_disponible: tareaInicial?.fecha_inicio_disponible ? 
      new Date(tareaInicial.fecha_inicio_disponible).toISOString().slice(0, 16) : '',
    tiempo_estimado: tareaInicial?.tiempo_estimado || 60,
    permite_entrega_tardia: tareaInicial?.permite_entrega_tardia ?? false,
    penalizacion_tardia: tareaInicial?.penalizacion_tardia || 0,
    intentos_maximos: tareaInicial?.intentos_maximos || 1,
    formato_entrega: tareaInicial?.formato_entrega || '',
    tamano_maximo_mb: tareaInicial?.tamano_maximo_mb || 10,
    puntuacion_maxima: tareaInicial?.puntuacion_maxima || 100,
    peso_evaluacion: tareaInicial?.peso_evaluacion || 1,
    es_grupal: tareaInicial?.es_grupal ?? false,
    es_publica: tareaInicial?.es_publica ?? true,
    requiere_aprobacion: tareaInicial?.requiere_aprobacion ?? false,
    recursos_necesarios: tareaInicial?.recursos_necesarios || '',
    criterios_evaluacion: tareaInicial?.criterios_evaluacion || '',
    rubrica_id: tareaInicial?.rubrica_id || undefined,
    configuracion_json: tareaInicial?.configuracion_json || undefined
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);

  const totalSteps = 4;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : 
               type === 'number' ? (value === '' ? 0 : Number(value)) : 
               value
    }));
  };

  const validateStep = (stepNumber: number): string | null => {
    switch (stepNumber) {
      case 1:
        if (!formData.titulo.trim()) return 'El título es obligatorio';
        if (!formData.fecha_limite) return 'La fecha límite es obligatoria';
        if (formData.puntuacion_maxima <= 0) return 'La puntuación máxima debe ser mayor a 0';
        break;
      
      case 2:
        // Validaciones opcionales para el paso 2
        break;
      
      case 3:
        if (formData.fecha_inicio_disponible && formData.fecha_limite) {
          if (new Date(formData.fecha_inicio_disponible) >= new Date(formData.fecha_limite)) {
            return 'La fecha de inicio debe ser anterior a la fecha límite';
          }
        }
        break;
      
      default:
        break;
    }
    return null;
  };

  const handleNext = () => {
    const error = validateStep(step);
    if (error) {
      setError(error);
      return;
    }
    setError(null);
    if (step < totalSteps) {
      setStep(step + 1);
    }
  };

  const handlePrev = () => {
    setError(null);
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar todos los pasos
    for (let i = 1; i <= totalSteps; i++) {
      const stepError = validateStep(i);
      if (stepError) {
        setError(stepError);
        setStep(i);
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al procesar la tarea');
    } finally {
      setLoading(false);
    }
  };

  const getTipoIcon = (tipo: TipoTarea): string => {
    const iconos = {
      [TipoTarea.ENSAYO]: '📝',
      [TipoTarea.PROYECTO]: '🏗️',
      [TipoTarea.EJERCICIOS]: '💪',
      [TipoTarea.INVESTIGACION]: '🔍',
      [TipoTarea.PRESENTACION]: '📊',
      [TipoTarea.LABORATORIO]: '🧪',
      [TipoTarea.LECTURA]: '📚',
      [TipoTarea.EXAMEN]: '📋',
      [TipoTarea.OTRO]: '📌',
    };
    return iconos[tipo] || '📌';
  };

  const renderProgressBar = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {Array.from({ length: totalSteps }, (_, i) => i + 1).map((stepNum) => (
          <React.Fragment key={stepNum}>
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                stepNum === step
                  ? 'bg-blue-600 text-white'
                  : stepNum < step
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-300 text-gray-700'
              }`}
            >
              {stepNum < step ? '✓' : stepNum}
            </div>
            {stepNum < totalSteps && (
              <div
                className={`flex-1 h-1 mx-2 ${
                  stepNum < step ? 'bg-green-500' : 'bg-gray-300'
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
      <h3 className="text-lg font-semibold text-center text-gray-900">
        {step === 1 && 'Información Básica'}
        {step === 2 && 'Contenido y Objetivos'}
        {step === 3 && 'Configuración'}
        {step === 4 && 'Revisión'}
      </h3>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {tareaInicial ? 'Editar Tarea' : 'Nueva Tarea'}
            </h2>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Contenido */}
        <form onSubmit={handleSubmit} className="p-6">
          {renderProgressBar()}

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Paso 1: Información Básica */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Título de la Tarea *
                </label>
                <input
                  type="text"
                  name="titulo"
                  value={formData.titulo}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ej: Ensayo sobre la Guerra Civil"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Tarea
                  </label>
                  <select
                    name="tipo_tarea"
                    value={formData.tipo_tarea}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {Object.values(TipoTarea).map((tipo) => (
                      <option key={tipo} value={tipo}>
                        {getTipoIcon(tipo)} {tipo.charAt(0).toUpperCase() + tipo.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prioridad
                  </label>
                  <select
                    name="prioridad"
                    value={formData.prioridad}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {Object.values(PrioridadTarea).map((prioridad) => (
                      <option key={prioridad} value={prioridad}>
                        {prioridad.charAt(0).toUpperCase() + prioridad.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha Límite *
                  </label>
                  <input
                    type="datetime-local"
                    name="fecha_limite"
                    value={formData.fecha_limite}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Puntuación Máxima *
                  </label>
                  <input
                    type="number"
                    name="puntuacion_maxima"
                    value={formData.puntuacion_maxima}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción Breve
                </label>
                <textarea
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Descripción general de la tarea..."
                />
              </div>
            </div>
          )}

          {/* Paso 2: Contenido y Objetivos */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Instrucciones Detalladas
                </label>
                <textarea
                  name="instrucciones"
                  value={formData.instrucciones}
                  onChange={handleInputChange}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Instrucciones paso a paso para completar la tarea..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Objetivos de Aprendizaje
                </label>
                <textarea
                  name="objetivos"
                  value={formData.objetivos}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="¿Qué se espera que los estudiantes aprendan?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Criterios de Evaluación
                </label>
                <textarea
                  name="criterios_evaluacion"
                  value={formData.criterios_evaluacion}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="¿Cómo será evaluada la tarea?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Recursos Necesarios
                </label>
                <textarea
                  name="recursos_necesarios"
                  value={formData.recursos_necesarios}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Materiales, libros, herramientas necesarias..."
                />
              </div>
            </div>
          )}

          {/* Paso 3: Configuración */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tiempo Estimado (minutos)
                  </label>
                  <input
                    type="number"
                    name="tiempo_estimado"
                    value={formData.tiempo_estimado}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Intentos Máximos
                  </label>
                  <input
                    type="number"
                    name="intentos_maximos"
                    value={formData.intentos_maximos}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tamaño Máximo (MB)
                  </label>
                  <input
                    type="number"
                    name="tamano_maximo_mb"
                    value={formData.tamano_maximo_mb}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Formatos Aceptados
                  </label>
                  <input
                    type="text"
                    name="formato_entrega"
                    value={formData.formato_entrega}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="PDF, DOCX, TXT..."
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Inicio Disponible
                </label>
                <input
                  type="datetime-local"
                  name="fecha_inicio_disponible"
                  value={formData.fecha_inicio_disponible}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="permite_entrega_tardia"
                    checked={formData.permite_entrega_tardia}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Permitir entregas tardías
                  </label>
                </div>

                {formData.permite_entrega_tardia && (
                  <div className="ml-6">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Penalización por entrega tardía (%)
                    </label>
                    <input
                      type="number"
                      name="penalizacion_tardia"
                      value={formData.penalizacion_tardia}
                      onChange={handleInputChange}
                      min="0"
                      max="100"
                      className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                )}

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="es_grupal"
                    checked={formData.es_grupal}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Tarea grupal
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="es_publica"
                    checked={formData.es_publica}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Visible para todos los estudiantes del grupo
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Paso 4: Revisión */}
          {step === 4 && (
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Resumen de la Tarea</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Título:</span>
                    <span className="ml-2 text-gray-900">{formData.titulo}</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Tipo:</span>
                    <span className="ml-2 text-gray-900">
                      {getTipoIcon(formData.tipo_tarea)} {formData.tipo_tarea}
                    </span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Prioridad:</span>
                    <span className="ml-2 text-gray-900">{formData.prioridad}</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Puntuación:</span>
                    <span className="ml-2 text-gray-900">{formData.puntuacion_maxima} puntos</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Fecha límite:</span>
                    <span className="ml-2 text-gray-900">
                      {new Date(formData.fecha_limite).toLocaleString('es-ES')}
                    </span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Tipo:</span>
                    <span className="ml-2 text-gray-900">
                      {formData.es_grupal ? 'Grupal' : 'Individual'}
                    </span>
                  </div>
                </div>

                {formData.descripcion && (
                  <div className="mt-4">
                    <span className="font-medium text-gray-700 block mb-1">Descripción:</span>
                    <p className="text-gray-900 text-sm">{formData.descripcion}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navegación */}
          <div className="flex justify-between pt-6 border-t border-gray-200 mt-8">
            <div>
              {step > 1 && (
                <button
                  type="button"
                  onClick={handlePrev}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  ← Anterior
                </button>
              )}
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              
              {step < totalSteps ? (
                <button
                  type="button"
                  onClick={handleNext}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Siguiente →
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Procesando...' : (tareaInicial ? 'Actualizar Tarea' : 'Crear Tarea')}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormularioTarea;