import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertCircle,
  Calendar,
  Clock,
  DollarSign,
  FileText,
  Gauge,
  Info,
  Loader2,
  Paperclip,
  Save,
  Settings,
  Sparkles,
  Tag,
  Trash2,
  Upload,
  X,
} from 'lucide-react';
import { courseService } from '../../../modules/academico/services/courseService';

interface CrearTareaFormProps {
  cursoId: string;
  grupoId: string;
  docenteId: string;
  onSuccess?: (tarea: any) => void;
  onCancel?: () => void;
}

interface FormData {
  // Información básica
  titulo: string;
  descripcion: string;
  instrucciones: string;
  objetivos: string;

  // Clasificación
  tipo: string; // ensayo, proyecto, ejercicios, investigacion, presentacion, laboratorio, lectura, examen, otro
  prioridad: string; // baja, media, alta, urgente
  tags: string;

  // Fechas
  fechaAsignacion: string;
  fechaLimite: string;
  fechaInicioDisponible: string;
  tiempoEstimado: number; // en minutos

  // Configuración de entrega
  permiteEntregaTardia: boolean;
  penalizacionTardia: number; // porcentaje
  intentosMaximos: number;
  formatoEntrega: string;
  tamanoMaximoMb: number;

  // Calificación
  puntuacionMaxima: number;
  pesoEvaluacion: number;
  criteriosEvaluacion: string;

  // Gamificación
  puntosBase: number;
  puntosBonificacion: number;

  // IA
  habilitarRetroalimentacionIA: boolean;
  promptIAPersonalizado: string;

  // Configuración general
  esGrupal: boolean;
  esPublica: boolean;
  requiereAprobacion: boolean;
  activa: boolean;

  // Archivos
  archivoAdjunto?: File | null;
}

const TIPOS_TAREA = [
  { value: 'ensayo', label: 'Ensayo' },
  { value: 'proyecto', label: 'Proyecto' },
  { value: 'ejercicios', label: 'Ejercicios' },
  { value: 'investigacion', label: 'Investigación' },
  { value: 'presentacion', label: 'Presentación' },
  { value: 'laboratorio', label: 'Laboratorio' },
  { value: 'lectura', label: 'Lectura' },
  { value: 'examen', label: 'Examen' },
  { value: 'otro', label: 'Otro' },
];

const PRIORIDADES = [
  { value: 'baja', label: 'Baja', color: 'bg-blue-100 text-blue-800' },
  { value: 'media', label: 'Media', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'alta', label: 'Alta', color: 'bg-orange-100 text-orange-800' },
  { value: 'urgente', label: 'Urgente', color: 'bg-red-100 text-red-800' },
];

export function CrearTareaForm({
  cursoId,
  grupoId,
  docenteId,
  onSuccess,
  onCancel,
}: CrearTareaFormProps) {
  const [formData, setFormData] = useState<FormData>({
    titulo: '',
    descripcion: '',
    instrucciones: '',
    objetivos: '',
    tipo: 'ensayo',
    prioridad: 'media',
    tags: '',
    fechaAsignacion: new Date().toISOString().split('T')[0],
    fechaLimite: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0],
    fechaInicioDisponible: new Date().toISOString().split('T')[0],
    tiempoEstimado: 60,
    permiteEntregaTardia: false,
    penalizacionTardia: 0,
    intentosMaximos: 1,
    formatoEntrega: 'archivo',
    tamanoMaximoMb: 10,
    puntuacionMaxima: 100,
    pesoEvaluacion: 1,
    criteriosEvaluacion: '',
    puntosBase: 50,
    puntosBonificacion: 10,
    habilitarRetroalimentacionIA: true,
    promptIAPersonalizado: '',
    esGrupal: false,
    esPublica: true,
    requiereAprobacion: false,
    activa: true,
    archivoAdjunto: null,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState('basico');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target as any;
    const finalValue =
      type === 'checkbox'
        ? (e.target as HTMLInputElement).checked
        : type === 'number'
          ? parseFloat(value) || 0
          : value;

    setFormData((prev) => ({
      ...prev,
      [name]: finalValue,
    }));
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validar tamaño
      if (file.size > 50 * 1024 * 1024) {
        setError('El archivo no puede exceder 50 MB');
        return;
      }
      setFormData((prev) => ({
        ...prev,
        archivoAdjunto: file,
      }));
      setError(null);
    }
  };

  const removeFile = () => {
    setFormData((prev) => ({
      ...prev,
      archivoAdjunto: null,
    }));
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones básicas
    if (!formData.titulo.trim()) {
      setError('El título es requerido');
      return;
    }

    if (!formData.descripcion.trim()) {
      setError('La descripción es requerida');
      return;
    }

    if (!formData.fechaLimite) {
      setError('La fecha límite es requerida');
      return;
    }

    if (formData.puntuacionMaxima <= 0) {
      setError('La puntuación máxima debe ser mayor a 0');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Construir payload con TODOS los campos según el backend
      const payload: any = {
        grupo_id: grupoId,
        docente_id: docenteId,
        titulo: formData.titulo,
        descripcion: formData.descripcion,
        instrucciones: formData.instrucciones || null,
        objetivos: formData.objetivos || null,
        tipo: formData.tipo,
        prioridad: formData.prioridad,
        tags: formData.tags || null,
        fecha_asignacion: new Date(formData.fechaAsignacion).toISOString(),
        fecha_limite: new Date(formData.fechaLimite).toISOString(),
        fecha_inicio_disponible: formData.fechaInicioDisponible
          ? new Date(formData.fechaInicioDisponible).toISOString()
          : null,
        tiempo_estimado: formData.tiempoEstimado || null,
        permite_entrega_tardia: formData.permiteEntregaTardia,
        penalizacion_tardia: formData.penalizacionTardia,
        intentos_maximos: formData.intentosMaximos,
        formato_entrega: formData.formatoEntrega,
        tamano_maximo_mb: formData.tamanoMaximoMb,
        puntuacion_maxima: formData.puntuacionMaxima,
        peso_evaluacion: formData.pesoEvaluacion,
        criterios_evaluacion: formData.criteriosEvaluacion || null,
        puntos_base: formData.puntosBase || null,
        puntos_bonificacion: formData.puntosBonificacion || null,
        habilitar_retroalimentacion_ia: formData.habilitarRetroalimentacionIA,
        prompt_ia_personalizado: formData.promptIAPersonalizado || null,
        es_grupal: formData.esGrupal,
        es_publica: formData.esPublica,
        requiere_aprobacion: formData.requiereAprobacion,
        activa: formData.activa,
        archivo_adjunto: null,
      };

      console.log('📤 Creando tarea con payload:', payload);

      // Si hay archivo adjunto, primero subirlo
      let archivoUrl = null;
      if (formData.archivoAdjunto) {
        console.log('📁 Subiendo archivo adjunto...');
        const uploadResponse = await courseService.uploadFile(
          cursoId,
          formData.archivoAdjunto,
          'tarea'
        );

        if (uploadResponse.success) {
          archivoUrl = uploadResponse.data.url;
          payload.archivo_adjunto = archivoUrl;
          console.log('✅ Archivo subido:', archivoUrl);
        } else {
          throw new Error(`Error subiendo archivo: ${uploadResponse.message}`);
        }
      }

      // Crear la tarea
      const response = await courseService.createTask(cursoId, payload);

      if (response.success) {
        console.log('✅ Tarea creada exitosamente:', response.data);

        // Mostrar éxito
        alert(`✅ Tarea "${formData.titulo}" creada exitosamente`);

        // Callback de éxito
        if (onSuccess) {
          onSuccess(response.data);
        }

        // Resetear formulario
        setFormData({
          titulo: '',
          descripcion: '',
          instrucciones: '',
          objetivos: '',
          tipo: 'ensayo',
          prioridad: 'media',
          tags: '',
          fechaAsignacion: new Date().toISOString().split('T')[0],
          fechaLimite: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
            .toISOString()
            .split('T')[0],
          fechaInicioDisponible: new Date().toISOString().split('T')[0],
          tiempoEstimado: 60,
          permiteEntregaTardia: false,
          penalizacionTardia: 0,
          intentosMaximos: 1,
          formatoEntrega: 'archivo',
          tamanoMaximoMb: 10,
          puntuacionMaxima: 100,
          pesoEvaluacion: 1,
          criteriosEvaluacion: '',
          puntosBase: 50,
          puntosBonificacion: 10,
          habilitarRetroalimentacionIA: true,
          promptIAPersonalizado: '',
          esGrupal: false,
          esPublica: true,
          requiereAprobacion: false,
          activa: true,
          archivoAdjunto: null,
        });
      } else {
        throw new Error(response.message || 'Error creando tarea');
      }
    } catch (err) {
      console.error('❌ Error:', err);
      setError(
        err instanceof Error ? err.message : 'Error desconocido al crear tarea'
      );
    } finally {
      setLoading(false);
    }
  };

  const sections = [
    {
      id: 'basico',
      label: 'Información Básica',
      icon: <FileText className="w-4 h-4" />,
    },
    {
      id: 'configuracion',
      label: 'Configuración',
      icon: <Settings className="w-4 h-4" />,
    },
    {
      id: 'calificacion',
      label: 'Calificación',
      icon: <Gauge className="w-4 h-4" />,
    },
    {
      id: 'gamificacion',
      label: 'Gamificación',
      icon: <DollarSign className="w-4 h-4" />,
    },
    {
      id: 'ia',
      label: 'Inteligencia Artificial',
      icon: <Sparkles className="w-4 h-4" />,
    },
  ];

  return (
    <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden max-h-[90vh] flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 p-6 text-white flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Crear Nueva Tarea</h2>
            <p className="text-emerald-100 text-sm mt-1">
              Completa todos los campos para crear una tarea completa y bien configurada
            </p>
          </div>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-emerald-700 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex overflow-x-auto bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 flex-shrink-0">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`px-4 py-3 font-medium transition-all flex items-center space-x-2 border-b-2 whitespace-nowrap ${
              activeSection === section.id
                ? 'text-emerald-600 border-emerald-600'
                : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-gray-300'
            }`}
          >
            {section.icon}
            <span>{section.label}</span>
          </button>
        ))}
      </div>

      {/* Form Content - Scrollable */}
      <div className="overflow-y-auto flex-1">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Error Alert */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start space-x-3"
          >
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
          </motion.div>
        )}

        {/* Sección: Información Básica */}
        <AnimatePresence mode="wait">
          {activeSection === 'basico' && (
            <motion.div
              key="basico"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* Título */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Título de la Tarea <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="titulo"
                  value={formData.titulo}
                  onChange={handleInputChange}
                  placeholder="Ej: Ensayo sobre la Revolución Francesa"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  maxLength={200}
                />
              </div>

              {/* Descripción */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Descripción <span className="text-red-500">*</span>
                </label>
                <textarea
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleInputChange}
                  placeholder="Describe qué debe hacer el estudiante..."
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Instrucciones */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Instrucciones Detalladas
                </label>
                <textarea
                  name="instrucciones"
                  value={formData.instrucciones}
                  onChange={handleInputChange}
                  placeholder="Instrucciones paso a paso..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Objetivos */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Objetivos de Aprendizaje
                </label>
                <textarea
                  name="objetivos"
                  value={formData.objetivos}
                  onChange={handleInputChange}
                  placeholder="¿Qué debe aprender el estudiante?"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Tipo y Prioridad */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    Tipo de Tarea
                  </label>
                  <select
                    name="tipo"
                    value={formData.tipo}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {TIPOS_TAREA.map((tipo) => (
                      <option key={tipo.value} value={tipo.value}>
                        {tipo.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    Prioridad
                  </label>
                  <select
                    name="prioridad"
                    value={formData.prioridad}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {PRIORIDADES.map((p) => (
                      <option key={p.value} value={p.value}>
                        {p.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  <div className="flex items-center space-x-2">
                    <Tag className="w-4 h-4" />
                    <span>Etiquetas (separadas por comas)</span>
                  </div>
                </label>
                <input
                  type="text"
                  name="tags"
                  value={formData.tags}
                  onChange={handleInputChange}
                  placeholder="escritura, análisis, investigación"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Archivo Adjunto */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  <div className="flex items-center space-x-2">
                    <Paperclip className="w-4 h-4" />
                    <span>Archivo Adjunto (enunciado, rúbrica, etc.)</span>
                  </div>
                </label>

                {formData.archivoAdjunto ? (
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-green-100 dark:bg-green-800 rounded flex items-center justify-center">
                        <Upload className="w-5 h-5 text-green-600 dark:text-green-400" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {formData.archivoAdjunto.name}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {(formData.archivoAdjunto.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={removeFile}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full px-4 py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-900/10 transition-colors flex items-center justify-center space-x-2 text-gray-600 dark:text-gray-400"
                  >
                    <Upload className="w-5 h-5" />
                    <span>Haz clic para seleccionar archivo (máx 50 MB)</span>
                  </button>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  accept="*/*"
                />
              </div>
            </motion.div>
          )}

          {/* Sección: Configuración */}
          {activeSection === 'configuracion' && (
            <motion.div
              key="configuracion"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* Fechas */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4" />
                      <span>Fecha de Asignación</span>
                    </div>
                  </label>
                  <input
                    type="date"
                    name="fechaAsignacion"
                    value={formData.fechaAsignacion}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4" />
                      <span>Fecha Límite <span className="text-red-500">*</span></span>
                    </div>
                  </label>
                  <input
                    type="date"
                    name="fechaLimite"
                    value={formData.fechaLimite}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4" />
                      <span>Fecha Disponible Desde</span>
                    </div>
                  </label>
                  <input
                    type="date"
                    name="fechaInicioDisponible"
                    value={formData.fechaInicioDisponible}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              {/* Tiempo estimado */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4" />
                    <span>Tiempo Estimado (minutos)</span>
                  </div>
                </label>
                <input
                  type="number"
                  name="tiempoEstimado"
                  value={formData.tiempoEstimado}
                  onChange={handleInputChange}
                  min="1"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Entregas tardías */}
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg space-y-3">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    name="permiteEntregaTardia"
                    checked={formData.permiteEntregaTardia}
                    onChange={handleInputChange}
                    className="w-4 h-4 rounded border-gray-300"
                  />
                  <span className="font-medium text-gray-900 dark:text-white">
                    Permitir entregas tardías
                  </span>
                </label>

                {formData.permiteEntregaTardia && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="ml-6"
                  >
                    <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                      Penalización por Tardía (%)
                    </label>
                    <input
                      type="number"
                      name="penalizacionTardia"
                      value={formData.penalizacionTardia}
                      onChange={handleInputChange}
                      min="0"
                      max="100"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </motion.div>
                )}
              </div>

              {/* Intentos */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Intentos Máximos Permitidos
                </label>
                <input
                  type="number"
                  name="intentosMaximos"
                  value={formData.intentosMaximos}
                  onChange={handleInputChange}
                  min="1"
                  max="10"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Formato y tamaño */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    Formato de Entrega
                  </label>
                  <select
                    name="formatoEntrega"
                    value={formData.formatoEntrega}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="archivo">Archivo</option>
                    <option value="texto">Texto</option>
                    <option value="url">URL/Enlace</option>
                    <option value="mixto">Mixto</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    Tamaño Máximo (MB)
                  </label>
                  <input
                    type="number"
                    name="tamanoMaximoMb"
                    value={formData.tamanoMaximoMb}
                    onChange={handleInputChange}
                    min="1"
                    max="500"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              {/* Configuración general */}
              <div className="space-y-3 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    name="esGrupal"
                    checked={formData.esGrupal}
                    onChange={handleInputChange}
                    className="w-4 h-4 rounded border-gray-300"
                  />
                  <span className="text-gray-900 dark:text-white">Trabajo grupal</span>
                </label>

                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    name="esPublica"
                    checked={formData.esPublica}
                    onChange={handleInputChange}
                    className="w-4 h-4 rounded border-gray-300"
                  />
                  <span className="text-gray-900 dark:text-white">Visible para estudiantes</span>
                </label>

                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    name="requiereAprobacion"
                    checked={formData.requiereAprobacion}
                    onChange={handleInputChange}
                    className="w-4 h-4 rounded border-gray-300"
                  />
                  <span className="text-gray-900 dark:text-white">Requiere aprobación del docente</span>
                </label>

                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    name="activa"
                    checked={formData.activa}
                    onChange={handleInputChange}
                    className="w-4 h-4 rounded border-gray-300"
                  />
                  <span className="text-gray-900 dark:text-white">Tarea activa</span>
                </label>
              </div>
            </motion.div>
          )}

          {/* Sección: Calificación */}
          {activeSection === 'calificacion' && (
            <motion.div
              key="calificacion"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  <div className="flex items-center space-x-2">
                    <Gauge className="w-4 h-4" />
                    <span>Puntuación Máxima <span className="text-red-500">*</span></span>
                  </div>
                </label>
                <input
                  type="number"
                  name="puntuacionMaxima"
                  value={formData.puntuacionMaxima}
                  onChange={handleInputChange}
                  min="1"
                  required
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Peso en Evaluación
                </label>
                <input
                  type="number"
                  name="pesoEvaluacion"
                  value={formData.pesoEvaluacion}
                  onChange={handleInputChange}
                  min="0.1"
                  step="0.1"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Criterios de Evaluación
                </label>
                <textarea
                  name="criteriosEvaluacion"
                  value={formData.criteriosEvaluacion}
                  onChange={handleInputChange}
                  placeholder="Describe los criterios de evaluación..."
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </motion.div>
          )}

          {/* Sección: Gamificación */}
          {activeSection === 'gamificacion' && (
            <motion.div
              key="gamificacion"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start space-x-3">
                <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <p className="text-blue-800 dark:text-blue-300 text-sm">
                  Los puntos se otorgan cuando el estudiante completa la tarea. La bonificación se aplica si obtiene una calificación excelente.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    <div className="flex items-center space-x-2">
                      <DollarSign className="w-4 h-4" />
                      <span>Puntos Base</span>
                    </div>
                  </label>
                  <input
                    type="number"
                    name="puntosBase"
                    value={formData.puntosBase}
                    onChange={handleInputChange}
                    min="0"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4" />
                      <span>Puntos Bonificación</span>
                    </div>
                  </label>
                  <input
                    type="number"
                    name="puntosBonificacion"
                    value={formData.puntosBonificacion}
                    onChange={handleInputChange}
                    min="0"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {/* Sección: IA */}
          {activeSection === 'ia' && (
            <motion.div
              key="ia"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4 flex items-start space-x-3">
                <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
                <p className="text-purple-800 dark:text-purple-300 text-sm">
                  Habilita la retroalimentación automática con IA para cada entrega. Personaliza el prompt para obtener retroalimentación más relevante.
                </p>
              </div>

              <label className="flex items-center space-x-3 cursor-pointer bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <input
                  type="checkbox"
                  name="habilitarRetroalimentacionIA"
                  checked={formData.habilitarRetroalimentacionIA}
                  onChange={handleInputChange}
                  className="w-4 h-4 rounded border-gray-300"
                />
                <span className="font-medium text-gray-900 dark:text-white">
                  Habilitar retroalimentación automática con IA
                </span>
              </label>

              {formData.habilitarRetroalimentacionIA && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                >
                  <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    Prompt Personalizado para IA
                  </label>
                  <textarea
                    name="promptIAPersonalizado"
                    value={formData.promptIAPersonalizado}
                    onChange={handleInputChange}
                    placeholder="Ej: Evalúa especialmente la creatividad y la estructura del argumento. Sugiere mejoras para la gramática y el estilo de escritura."
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <Info className="w-4 h-4 inline mr-1" />
                    Personaliza este prompt para obtener retroalimentación más específica y relevante para tu tarea.
                  </p>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Botones de acción */}
        <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">Los botones aparecerán abajo al hacer scroll</p>
        </div>
        </form>
      </div>

      {/* Footer con botones - Siempre visible */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 flex-shrink-0">
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 font-medium transition-colors"
          >
            Cancelar
          </button>

          <button
            onClick={handleSubmit}
            disabled={loading || !formData.titulo || !formData.descripcion}
            className="flex items-center space-x-2 px-8 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Creando tarea...</span>
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                <span>Crear Tarea</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
