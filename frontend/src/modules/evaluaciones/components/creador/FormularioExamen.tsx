import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
;
import { Card, CardHeader, CardContent } from '../common/LayoutComponents';
import { LoadingSpinner } from '../common/LoadingComponents';
import { useToast } from '../common/AlertComponents';
import { TipoExamen, EstadoExamen, DificultadPregunta, Examen } from '../../types';
import { TIPO_EXAMEN_LABELS, ESTADO_EXAMEN_LABELS, DIFICULTAD_LABELS } from '../../utils';
import { Calendar, Eye, GraduationCap, Info } from 'lucide-react';

interface FormularioExamenProps {
  examen?: Examen | null;
  onGuardar: (datos: any) => Promise<void>;
  onCancelar: () => void;
}

interface FormData {
  titulo: string;
  descripcion: string;
  instrucciones: string;
  tipo_examen: TipoExamen;
  estado_examen: EstadoExamen;
  tiempo_limite: number;
  intentos_permitidos: number;
  puntuacion_minima_aprobacion: number;
  fecha_inicio: string;
  fecha_limite: string;
  mostrar_resultados_inmediatos: boolean;
  randomizar_preguntas: boolean;
  modo_pantalla_completa: boolean;
  bloquear_navegacion: boolean;
  detectar_cambio_pestana: boolean;
  tiempo_maximo_inactividad: number;
  requiere_contraseña: boolean;
  contraseña_acceso?: string;
  permitir_revision: boolean;
  mostrar_respuestas_correctas: boolean;
  calificacion_automatica: boolean;
  // Propiedades adicionales para antitrampa
  requiere_camara: boolean;
  requiere_pantalla_completa: boolean;
  bloquear_copiar_pegar: boolean;
  mostrar_resultados_inmediatamente: boolean;
  permitir_navegacion_libre: boolean;
  aleatorizar_preguntas: boolean;
  aleatorizar_respuestas: boolean;
  // Configuraciones anidadas (se manejarán como campos planos)
  'configuracion_antitrampa.detectar_cambio_ventana': boolean;
  'configuracion_antitrampa.detectar_clic_derecho': boolean;
  'configuracion_antitrampa.limite_cambios_ventana': number;
  'configuracion_antitrampa.tiempo_maximo_inactivo': number;
  'configuracion_calificacion.penalizacion_respuesta_incorrecta': number;
  'configuracion_calificacion.puntos_pregunta_facil': number;
  'configuracion_calificacion.puntos_pregunta_media': number;
  'configuracion_calificacion.puntos_pregunta_dificil': number;
  'configuracion_accesibilidad.tiempo_extra_dislexia': number;
  'configuracion_accesibilidad.permitir_lector_pantalla': boolean;
  'configuracion_accesibilidad.alto_contraste': boolean;
  'configuracion_accesibilidad.texto_grande': boolean;
}

export function FormularioExamen({ examen, onGuardar, onCancelar }: FormularioExamenProps) {
  const [guardando, setGuardando] = useState(false);
  const [mostrarPrevia, setMostrarPrevia] = useState(false);
  const [seccionActiva, setSeccionActiva] = useState<'basica' | 'configuracion' | 'antitrampa' | 'avanzada'>('basica');
  const { showToast } = useToast();
  
  const esEdicion = Boolean(examen);

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isValid, isDirty },
    reset,
    setValue,
    getValues
  } = useForm<FormData>({
    defaultValues: {
      titulo: examen?.titulo || '',
      descripcion: examen?.descripcion || '',
      instrucciones: examen?.instrucciones || '',
      tipo_examen: examen?.tipo_examen || 'QUIZ',
      estado_examen: examen?.estado_examen || 'BORRADOR',
      tiempo_limite: examen?.tiempo_limite || 60,
      intentos_permitidos: examen?.intentos_permitidos || 1,
      puntuacion_minima_aprobacion: examen?.puntuacion_minima_aprobacion || 70,
      fecha_inicio: examen?.fecha_inicio ? new Date(examen.fecha_inicio).toISOString().slice(0, 16) : '',
      fecha_limite: examen?.fecha_limite ? new Date(examen.fecha_limite).toISOString().slice(0, 16) : '',
      mostrar_resultados_inmediatos: examen?.mostrar_resultados_inmediatos ?? true,
      randomizar_preguntas: examen?.randomizar_preguntas ?? false,
      modo_pantalla_completa: examen?.modo_pantalla_completa ?? false,
      bloquear_navegacion: examen?.bloquear_navegacion ?? true,
      detectar_cambio_pestana: examen?.detectar_cambio_pestana ?? true,
      tiempo_maximo_inactividad: examen?.tiempo_maximo_inactividad ?? 300,
      requiere_contraseña: examen?.requiere_contraseña ?? false,
      contraseña_acceso: examen?.contraseña_acceso || '',
      permitir_revision: examen?.permitir_revision ?? true,
      mostrar_respuestas_correctas: examen?.mostrar_respuestas_correctas ?? false,
      calificacion_automatica: examen?.calificacion_automatica ?? true,
    },
    mode: 'onChange'
  });

  const watchedValues = watch();

  const manejarSubmit = useCallback(async (datos: FormData) => {
    setGuardando(true);
    try {
      const datosParaGuardar = {
        ...datos,
        fecha_inicio: datos.fecha_inicio ? new Date(datos.fecha_inicio) : null,
        fecha_limite: datos.fecha_limite ? new Date(datos.fecha_limite) : null,
      };
      
      await onGuardar(datosParaGuardar);
      
      if (!esEdicion) {
        reset();
      }
    } catch (error) {
      console.error('Error al guardar examen:', error);
    } finally {
      setGuardando(false);
    }
  }, [onGuardar, reset, esEdicion]);

  const validarFechas = useCallback(() => {
    const fechaInicio = new Date(watchedValues.fecha_inicio);
    const fechaLimite = new Date(watchedValues.fecha_limite);
    
    if (fechaInicio && fechaLimite && fechaInicio >= fechaLimite) {
      showToast({
        type: 'warning',
        title: 'Fechas inválidas',
        message: 'La fecha límite debe ser posterior a la fecha de inicio'
      });
      return false;
    }
    return true;
  }, [watchedValues.fecha_inicio, watchedValues.fecha_limite, showToast]);

  const secciones = [
    { id: 'basica', nombre: 'Información Básica', icono: Info },
    { id: 'configuracion', nombre: 'Configuración', icono: ClockIcon },
    { id: 'antitrampa', nombre: 'Anti-trampa', icono: ExclamationTriangleIcon },
    { id: 'avanzada', nombre: 'Opciones Avanzadas', icono: GraduationCap }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Navegación por pestañas */}
      <Card className="mb-6">
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {secciones.map((seccion) => (
              <button
                key={seccion.id}
                onClick={() => setSeccionActiva(seccion.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  seccionActiva === seccion.id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <seccion.icono className="h-5 w-5" />
                <span>{seccion.nombre}</span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit(manejarSubmit)} className="space-y-6">
        <AnimatePresence mode="wait">
          {/* Sección Básica */}
          {seccionActiva === 'basica' && (
            <motion.div
              key="basica"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader
                  title="Información Básica"
                  subtitle="Define los detalles principales de tu examen"
                />
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="lg:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Título del Examen *
                      </label>
                      <input
                        {...register('titulo', { 
                          required: 'El título es obligatorio',
                          minLength: { value: 3, message: 'El título debe tener al menos 3 caracteres' }
                        })}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                          errors.titulo ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                        }`}
                        placeholder="Ej: Examen Final de Matemáticas"
                      />
                      {errors.titulo && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.titulo.message}
                        </p>
                      )}
                    </div>

                    <div className="lg:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Descripción
                      </label>
                      <textarea
                        {...register('descripcion')}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder="Describe brevemente el contenido y objetivos del examen..."
                      />
                    </div>

                    <div className="lg:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Instrucciones para los estudiantes
                      </label>
                      <textarea
                        {...register('instrucciones')}
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder="Proporciona instrucciones claras sobre cómo realizar el examen..."
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Tipo de Examen *
                      </label>
                      <Controller
                        name="tipo_examen"
                        control={control}
                        rules={{ required: 'El tipo de examen es obligatorio' }}
                        render={({ field }: any) => (
                          <select
                            {...field}
                            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                              errors.tipo_examen ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                            }`}
                          >
                            {Object.entries(TIPO_EXAMEN_LABELS).map(([valor, etiqueta]) => (
                              <option key={valor} value={valor}>{etiqueta}</option>
                            ))}
                          </select>
                        )}
                      />
                      {errors.tipo_examen && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.tipo_examen.message}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Estado del Examen
                      </label>
                      <Controller
                        name="estado_examen"
                        control={control}
                        render={({ field }: any) => (
                          <select
                            {...field}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          >
                            {Object.entries(ESTADO_EXAMEN_LABELS).map(([valor, etiqueta]) => (
                              <option key={valor} value={valor}>{etiqueta}</option>
                            ))}
                          </select>
                        )}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Sección Configuración */}
          {seccionActiva === 'configuracion' && (
            <motion.div
              key="configuracion"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader
                  title="Configuración del Examen"
                  subtitle="Ajusta los parámetros de tiempo, intentos y fechas"
                />
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Tiempo límite (minutos) *
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="600"
                        {...register('tiempo_limite', { 
                          required: 'El tiempo límite es obligatorio',
                          min: { value: 1, message: 'El tiempo mínimo es 1 minuto' },
                          max: { value: 600, message: 'El tiempo máximo es 600 minutos' }
                        })}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                          errors.tiempo_limite ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                        }`}
                        placeholder="60"
                      />
                      {errors.tiempo_limite && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.tiempo_limite.message}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Intentos máximos *
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        {...register('intentos_permitidos', { 
                          required: 'Los intentos máximos son obligatorios',
                          min: { value: 1, message: 'Mínimo 1 intento' },
                          max: { value: 10, message: 'Máximo 10 intentos' }
                        })}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                          errors.intentos_permitidos ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                        }`}
                        placeholder="1"
                      />
                      {errors.intentos_permitidos && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.intentos_permitidos.message}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Puntuación mínima para aprobar (%) *
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        {...register('puntuacion_minima_aprobacion', { 
                          required: 'La puntuación mínima es obligatoria',
                          min: { value: 0, message: 'Mínimo 0%' },
                          max: { value: 100, message: 'Máximo 100%' }
                        })}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                          errors.puntuacion_minima_aprobacion ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                        }`}
                        placeholder="70"
                      />
                      {errors.puntuacion_minima_aprobacion && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.puntuacion_minima_aprobacion.message}
                        </p>
                      )}
                    </div>

                    <div className="lg:col-span-2 grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Fecha de inicio
                        </label>
                        <input
                          type="datetime-local"
                          {...register('fecha_inicio')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Fecha límite
                        </label>
                        <input
                          type="datetime-local"
                          {...register('fecha_limite')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          onChange={validarFechas}
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Sección Anti-trampa */}
          {seccionActiva === 'antitrampa' && (
            <motion.div
              key="antitrampa"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader
                  title="Configuración Anti-trampa"
                  subtitle="Medidas de seguridad para mantener la integridad del examen"
                />
                <CardContent>
                  <div className="space-y-6">
                    {/* Controles básicos */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('requiere_camara')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Requiere cámara encendida
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('requiere_pantalla_completa')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Requiere pantalla completa
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('bloquear_copiar_pegar')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Bloquear copiar/pegar
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('configuracion_antitrampa.detectar_cambio_ventana')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Detectar cambio de ventana
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('configuracion_antitrampa.detectar_clic_derecho')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Detectar clic derecho
                        </label>
                      </div>
                    </div>

                    {/* Límites numéricos */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Límite de cambios de ventana
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="20"
                          {...register('configuracion_antitrampa.limite_cambios_ventana')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder="3"
                        />
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                          0 = sin límite
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Tiempo máximo inactivo (segundos)
                        </label>
                        <input
                          type="number"
                          min="60"
                          max="1800"
                          {...register('configuracion_antitrampa.tiempo_maximo_inactivo')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder="300"
                        />
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                          Tiempo después del cual se envía automáticamente
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Sección Avanzada */}
          {seccionActiva === 'avanzada' && (
            <motion.div
              key="avanzada"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <div className="space-y-6">
                {/* Configuración de navegación */}
                <Card>
                  <CardHeader
                    title="Configuración de Navegación"
                    subtitle="Controla cómo los estudiantes interactúan con el examen"
                  />
                  <CardContent>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('mostrar_resultados_inmediatamente')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Mostrar resultados inmediatamente
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('permitir_navegacion_libre')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Permitir navegación libre entre preguntas
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('aleatorizar_preguntas')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Aleatorizar orden de preguntas
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('aleatorizar_respuestas')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Aleatorizar orden de respuestas
                        </label>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Configuración de Calificación */}
                <Card>
                  <CardHeader
                    title="Sistema de Calificación"
                    subtitle="Personaliza cómo se calculan las puntuaciones"
                  />
                  <CardContent>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Penalización por respuesta incorrecta (puntos)
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="5"
                          step="0.1"
                          {...register('configuracion_calificacion.penalizacion_respuesta_incorrecta')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Puntos por pregunta fácil
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          {...register('configuracion_calificacion.puntos_pregunta_facil')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Puntos por pregunta media
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          {...register('configuracion_calificacion.puntos_pregunta_media')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Puntos por pregunta difícil
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          {...register('configuracion_calificacion.puntos_pregunta_dificil')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Configuración de Accesibilidad */}
                <Card>
                  <CardHeader
                    title="Accesibilidad"
                    subtitle="Opciones para estudiantes con necesidades especiales"
                  />
                  <CardContent>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Tiempo extra para dislexia (%)
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="100"
                          {...register('configuracion_accesibilidad.tiempo_extra_dislexia')}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('configuracion_accesibilidad.permitir_lector_pantalla')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Permitir lector de pantalla
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('configuracion_accesibilidad.alto_contraste')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Modo alto contraste
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('configuracion_accesibilidad.texto_grande')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Texto grande por defecto
                        </label>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Botones de acción */}
        <Card>
          <CardContent>
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
              <div className="flex items-center space-x-4">
                <button
                  type="button"
                  onClick={() => setMostrarPrevia(!mostrarPrevia)}
                  className="flex items-center space-x-2 px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <Eye className="h-5 w-5" />
                  <span>{mostrarPrevia ? 'Ocultar' : 'Ver'} previa</span>
                </button>

                {isDirty && (
                  <div className="flex items-center space-x-2 text-sm text-amber-600 dark:text-amber-400">
                    <ExclamationTriangleIcon className="h-4 w-4" />
                    <span>Hay cambios sin guardar</span>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-3">
                <button
                  type="button"
                  onClick={onCancelar}
                  className="px-6 py-2 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!isValid || guardando}
                  className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
                >
                  {guardando && <LoadingSpinner size="sm" />}
                  <span>{esEdicion ? 'Actualizar' : 'Crear'} Examen</span>
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Vista previa */}
        <AnimatePresence>
          {mostrarPrevia && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader
                  title="Vista Previa del Examen"
                  subtitle="Cómo verán los estudiantes este examen"
                />
                <CardContent>
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                      {watchedValues.titulo || 'Sin título'}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      {watchedValues.descripcion || 'Sin descripción'}
                    </p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Tipo:</span>
                        <p>{TIPO_EXAMEN_LABELS[watchedValues.tipo_examen as TipoExamen]}</p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Duración:</span>
                        <p>{watchedValues.tiempo_limite} min</p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Intentos:</span>
                        <p>{watchedValues.intentos_permitidos}</p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Aprobación:</span>
                        <p>{watchedValues.puntuacion_minima_aprobacion}%</p>
                      </div>
                    </div>
                    
                    {watchedValues.instrucciones && (
                      <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <h4 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
                          Instrucciones:
                        </h4>
                        <p className="text-blue-700 dark:text-blue-400 text-sm whitespace-pre-line">
                          {watchedValues.instrucciones}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </form>
    </div>
  );
}