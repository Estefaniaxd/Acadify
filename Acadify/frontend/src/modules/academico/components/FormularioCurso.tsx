import React, { useState, useEffect } from 'react';
import { Curso, ModalidadCurso, EstadoCurso } from '../types.js';

interface FormularioCursoProps {
  onSubmit: (curso: Partial<Curso>) => Promise<void>;
  onCancel: () => void;
  cursoInicial?: Curso | null;
}

const FormularioCurso: React.FC<FormularioCursoProps> = ({
  onSubmit,
  onCancel,
  cursoInicial = null
}) => {
  const [formData, setFormData] = useState({
    nombre: cursoInicial?.nombre || '',
    descripcion: cursoInicial?.descripcion || '',
    objetivos: cursoInicial?.objetivos || '',
    codigo_curso: cursoInicial?.codigo_curso || '',
    categoria: cursoInicial?.categoria || '',
    nivel: cursoInicial?.nivel || 'Básico',
    idioma: cursoInicial?.idioma || 'Español',
    creditos: cursoInicial?.creditos || 1,
    horas_academicas: cursoInicial?.horas_academicas || 1,
    duracion_estimada: cursoInicial?.duracion_estimada || 1,
    modalidad: cursoInicial?.modalidad || ModalidadCurso.SEMESTRAL,
    fecha_inicio: cursoInicial?.fecha_inicio ? new Date(cursoInicial.fecha_inicio).toISOString().split('T')[0] : '',
    fecha_fin: cursoInicial?.fecha_fin ? new Date(cursoInicial.fecha_fin).toISOString().split('T')[0] : '',
    maximo_estudiantes: cursoInicial?.maximo_estudiantes || 30,
    minimo_estudiantes: cursoInicial?.minimo_estudiantes || 5,
    estado: cursoInicial?.estado || EstadoCurso.BORRADOR,
    permite_inscripcion: cursoInicial?.permite_inscripcion ?? true,
    permite_material_estudiantes: cursoInicial?.permite_material_estudiantes ?? false,
    requiere_aprobacion_material: cursoInicial?.requiere_aprobacion_material ?? true,
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
        if (!formData.nombre.trim()) return 'El nombre del curso es obligatorio';
        if (!formData.codigo_curso?.trim()) return 'El código del curso es obligatorio';
        if (formData.creditos < 1) return 'Los créditos deben ser mayor a 0';
        break;
      
      case 2:
        if (formData.horas_academicas < 1) return 'Las horas académicas deben ser mayor a 0';
        if (formData.duracion_estimada && formData.duracion_estimada < 1) return 'La duración debe ser mayor a 0';
        break;
      
      case 3:
        if (formData.fecha_inicio && formData.fecha_fin) {
          if (new Date(formData.fecha_inicio) >= new Date(formData.fecha_fin)) {
            return 'La fecha de inicio debe ser anterior a la fecha de fin';
          }
        }
        if (formData.maximo_estudiantes && formData.maximo_estudiantes < formData.minimo_estudiantes) {
          return 'El máximo de estudiantes debe ser mayor o igual al mínimo';
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
      const cursoData: Partial<Curso> = {
        ...formData,
        nombre: formData.nombre.trim(),
        descripcion: formData.descripcion?.trim() || undefined,
        objetivos: formData.objetivos?.trim() || undefined,
        codigo_curso: formData.codigo_curso?.trim(),
        categoria: formData.categoria?.trim() || undefined,
        fecha_inicio: formData.fecha_inicio || undefined,
        fecha_fin: formData.fecha_fin || undefined,
      };

      await onSubmit(cursoData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al procesar el curso');
    } finally {
      setLoading(false);
    }
  };

  const getStepTitle = (stepNumber: number): string => {
    const titles = {
      1: 'Información Básica',
      2: 'Detalles Académicos',
      3: 'Configuración',
      4: 'Revisión'
    };
    return titles[stepNumber as keyof typeof titles] || '';
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
        {getStepTitle(step)}
      </h3>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {cursoInicial ? 'Editar Curso' : 'Crear Nuevo Curso'}
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
                  Nombre del Curso *
                </label>
                <input
                  type="text"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ej: Matemáticas Avanzadas"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Código del Curso *
                </label>
                <input
                  type="text"
                  name="codigo_curso"
                  value={formData.codigo_curso}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ej: MATH-401"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Descripción del curso, objetivos principales..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Categoría
                  </label>
                  <input
                    type="text"
                    name="categoria"
                    value={formData.categoria}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Ej: Matemáticas"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Créditos *
                  </label>
                  <input
                    type="number"
                    name="creditos"
                    value={formData.creditos}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>
            </div>
          )}

          {/* Paso 2: Detalles Académicos */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Objetivos del Curso
                </label>
                <textarea
                  name="objetivos"
                  value={formData.objetivos}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Objetivos específicos que se esperan alcanzar..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Horas Académicas *
                  </label>
                  <input
                    type="number"
                    name="horas_academicas"
                    value={formData.horas_academicas}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duración (horas)
                  </label>
                  <input
                    type="number"
                    name="duracion_estimada"
                    value={formData.duracion_estimada}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Modalidad
                  </label>
                  <select
                    name="modalidad"
                    value={formData.modalidad}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {Object.values(ModalidadCurso).map((modalidad) => (
                      <option key={modalidad} value={modalidad}>
                        {modalidad.charAt(0).toUpperCase() + modalidad.slice(1).replace('_', ' ')}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nivel
                  </label>
                  <select
                    name="nivel"
                    value={formData.nivel}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Básico">Básico</option>
                    <option value="Intermedio">Intermedio</option>
                    <option value="Avanzado">Avanzado</option>
                    <option value="Especialización">Especialización</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Idioma
                  </label>
                  <select
                    name="idioma"
                    value={formData.idioma}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Español">Español</option>
                    <option value="Inglés">Inglés</option>
                    <option value="Francés">Francés</option>
                    <option value="Portugués">Portugués</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Paso 3: Configuración */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha de Inicio
                  </label>
                  <input
                    type="date"
                    name="fecha_inicio"
                    value={formData.fecha_inicio}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha de Fin
                  </label>
                  <input
                    type="date"
                    name="fecha_fin"
                    value={formData.fecha_fin}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Mínimo de Estudiantes
                  </label>
                  <input
                    type="number"
                    name="minimo_estudiantes"
                    value={formData.minimo_estudiantes}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Máximo de Estudiantes
                  </label>
                  <input
                    type="number"
                    name="maximo_estudiantes"
                    value={formData.maximo_estudiantes || ''}
                    onChange={handleInputChange}
                    min={formData.minimo_estudiantes}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estado del Curso
                </label>
                <select
                  name="estado"
                  value={formData.estado}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {Object.values(EstadoCurso).map((estado) => (
                    <option key={estado} value={estado}>
                      {estado.charAt(0).toUpperCase() + estado.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="permite_inscripcion"
                    checked={formData.permite_inscripcion}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Permitir inscripción de estudiantes
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="permite_material_estudiantes"
                    checked={formData.permite_material_estudiantes}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Permitir que estudiantes suban material
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="requiere_aprobacion_material"
                    checked={formData.requiere_aprobacion_material}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Requiere aprobación para material de estudiantes
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Paso 4: Revisión */}
          {step === 4 && (
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Resumen del Curso</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Nombre:</span>
                    <span className="ml-2 text-gray-900">{formData.nombre}</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Código:</span>
                    <span className="ml-2 text-gray-900">{formData.codigo_curso}</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Categoría:</span>
                    <span className="ml-2 text-gray-900">{formData.categoria || 'No especificada'}</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Nivel:</span>
                    <span className="ml-2 text-gray-900">{formData.nivel}</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Créditos:</span>
                    <span className="ml-2 text-gray-900">{formData.creditos}</span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Modalidad:</span>
                    <span className="ml-2 text-gray-900">
                      {formData.modalidad.charAt(0).toUpperCase() + formData.modalidad.slice(1).replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Estudiantes:</span>
                    <span className="ml-2 text-gray-900">
                      {formData.minimo_estudiantes} - {formData.maximo_estudiantes || '∞'}
                    </span>
                  </div>
                  
                  <div>
                    <span className="font-medium text-gray-700">Estado:</span>
                    <span className="ml-2 text-gray-900">
                      {formData.estado.charAt(0).toUpperCase() + formData.estado.slice(1)}
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
                  {loading ? 'Procesando...' : (cursoInicial ? 'Actualizar Curso' : 'Crear Curso')}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormularioCurso;