import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useForm, Controller } from 'react-hook-form';
import { AlertTriangle, Tag } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../common/LayoutComponents';
import { LoadingSpinner } from '../common/LoadingComponents';
import { ConfirmDialog, useToast } from '../common/AlertComponents';
import { 
  BancoPregunta, 
  TipoPregunta, 
  DificultadPregunta,
  OpcionRespuesta 
} from '../../types';
import { 
  TIPO_PREGUNTA_LABELS, 
  DIFICULTAD_LABELS,
  obtenerColorDificultad
} from '../../utils';

interface CreadorPreguntaProps {
  pregunta?: BancoPregunta | null;
  categorias: string[];
  etiquetas: string[];
  onGuardar: (datos: any) => Promise<void>;
  onCancelar: () => void;
}

interface FormDataPregunta {
  texto_pregunta: string;
  tipo_pregunta: TipoPregunta;
  nivel_dificultad: DificultadPregunta;
  puntos: number;
  tiempo_sugerido: number;
  explicacion: string;
  categoria: string;
  etiquetas: string[];
  imagen_url?: string;
  audio_url?: string;
  opciones_respuesta: OpcionRespuesta[];
  palabras_clave: string[];
  objetivo_aprendizaje: string;
  referencia: string;
}

export function CreadorPregunta({ 
  pregunta, 
  categorias, 
  etiquetas: etiquetasDisponibles, 
  onGuardar, 
  onCancelar 
}: CreadorPreguntaProps) {
  const [seccionActiva, setSeccionActiva] = useState<'contenido' | 'opciones' | 'multimedia' | 'metadata'>('contenido');
  const [mostrarPrevia, setMostrarPrevia] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [subiendoArchivo, setSubiendoArchivo] = useState(false);
  const [nuevaCategoria, setNuevaCategoria] = useState('');
  const [nuevaEtiqueta, setNuevaEtiqueta] = useState('');
  
  const esEdicion = Boolean(pregunta);
  const { showToast } = useToast();

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid, isDirty },
    reset
  } = useForm<FormDataPregunta>({
    defaultValues: {
      texto_pregunta: pregunta?.titulo || '',
      tipo_pregunta: pregunta?.tipo_pregunta || 'OPCION_MULTIPLE',
      nivel_dificultad: pregunta?.dificultad || 'MEDIO',
      puntos: pregunta?.puntuacion_sugerida || 1,
      tiempo_sugerido: pregunta?.tiempo_estimado_segundos ? Math.round(pregunta.tiempo_estimado_segundos / 60) : 2,
      explicacion: pregunta?.explicacion || '',
      categoria: pregunta?.categoria || '',
      etiquetas: pregunta?.tags || [],
      imagen_url: pregunta?.imagen_url || '',
      audio_url: pregunta?.audio_url || '',
      opciones_respuesta: pregunta?.opciones_respuesta || [
        { id: '1', texto: '', es_correcta: true },
        { id: '2', texto: '', es_correcta: false }
      ],
      palabras_clave: [],
      objetivo_aprendizaje: '',
      referencia: ''
    },
    mode: 'onChange'
  });

  const { fields: opciones, append, remove } = useFieldArray({
    control,
    name: 'opciones_respuesta'
  });

  const watchedValues = watch();
  const tipoPregunta = watch('tipo_pregunta');

  const manejarSubmit = useCallback(async (datos: FormDataPregunta) => {
    try {
      setGuardando(true);
      
      // Validar que al menos una opción sea correcta para preguntas de múltiple opción
      if (tipoPregunta === 'OPCION_MULTIPLE' || tipoPregunta === 'VERDADERO_FALSO') {
        const tieneRespuestaCorrecta = datos.opciones_respuesta.some(opcion => opcion.es_correcta);
        if (!tieneRespuestaCorrecta) {
          showToast({
            type: 'error',
            title: 'Error de validación',
            message: 'Debe marcar al menos una opción como correcta'
          });
          return;
        }
      }

      // Filtrar opciones vacías
      const opcionesFiltradas = datos.opciones_respuesta.filter(opcion => 
        opcion.texto.trim() !== ''
      );

      if (opcionesFiltradas.length < 2 && (tipoPregunta === 'OPCION_MULTIPLE' || tipoPregunta === 'VERDADERO_FALSO')) {
        showToast({
          type: 'error',
          title: 'Error de validación',
          message: 'Debe proporcionar al menos 2 opciones de respuesta'
        });
        return;
      }

      const datosFinales = {
        ...datos,
        opciones_respuesta: opcionesFiltradas.map((opcion, index) => ({
          ...opcion,
          id: opcion.id || `opcion-${index + 1}`
        }))
      };

      await onGuardar(datosFinales);
    } catch (error) {
      console.error('Error al guardar pregunta:', error);
    } finally {
      setGuardando(false);
    }
  }, [onGuardar, tipoPregunta, showToast]);

  const agregarOpcion = useCallback(() => {
    append({
      id: `opcion-${opciones.length + 1}`,
      texto: '',
      es_correcta: false
    });
  }, [append, opciones.length]);

  const eliminarOpcion = useCallback((index: number) => {
    if (opciones.length > 2) {
      remove(index);
    }
  }, [remove, opciones.length]);

  const manejarCambioTipo = useCallback((nuevoTipo: TipoPregunta) => {
    setValue('tipo_pregunta', nuevoTipo);
    
    if (nuevoTipo === 'VERDADERO_FALSO') {
      setValue('opciones_respuesta', [
        { id: '1', texto: 'Verdadero', es_correcta: true },
        { id: '2', texto: 'Falso', es_correcta: false }
      ]);
    } else if (nuevoTipo === 'ENSAYO' || nuevoTipo === 'COMPLETAR') {
      setValue('opciones_respuesta', []);
    }
  }, [setValue]);

  const agregarCategoria = useCallback(() => {
    if (nuevaCategoria.trim() && !categorias.includes(nuevaCategoria)) {
      setValue('categoria', nuevaCategoria);
      setNuevaCategoria('');
    }
  }, [nuevaCategoria, categorias, setValue]);

  const agregarEtiqueta = useCallback(() => {
    if (nuevaEtiqueta.trim()) {
      const etiquetasActuales = watchedValues.etiquetas;
      if (!etiquetasActuales.includes(nuevaEtiqueta)) {
        setValue('etiquetas', [...etiquetasActuales, nuevaEtiqueta]);
        setNuevaEtiqueta('');
      }
    }
  }, [nuevaEtiqueta, watchedValues.etiquetas, setValue]);

  const eliminarEtiqueta = useCallback((etiqueta: string) => {
    const etiquetasActuales = watchedValues.etiquetas;
    setValue('etiquetas', etiquetasActuales.filter((e: string) => e !== etiqueta));
  }, [watchedValues.etiquetas, setValue]);

  const secciones = [
    { id: 'contenido', nombre: 'Contenido' },
    { id: 'opciones', nombre: 'Opciones' },
    { id: 'multimedia', nombre: 'Multimedia' },
    { id: 'metadata', nombre: 'Metadata' }
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
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  seccionActiva === seccion.id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {seccion.nombre}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit(manejarSubmit)} className="space-y-6">
        {/* Sección Contenido */}
        {seccionActiva === 'contenido' && (
          <Card>
            <CardHeader
              title="Contenido de la Pregunta"
              subtitle="Define los detalles principales de la pregunta"
            />
            <CardContent>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Texto de la pregunta *
                  </label>
                  <textarea
                    {...register('texto_pregunta', { 
                      required: 'El texto de la pregunta es obligatorio',
                      minLength: { value: 10, message: 'La pregunta debe tener al menos 10 caracteres' }
                    })}
                    rows={4}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      errors.texto_pregunta ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder="Escribe aquí el texto de tu pregunta..."
                  />
                  {errors.texto_pregunta && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                      {errors.texto_pregunta.message}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tipo de pregunta *
                    </label>
                    <Controller
                      name="tipo_pregunta"
                      control={control}
                      render={({ field }) => (
                        <select
                          {...field}
                          onChange={(e) => manejarCambioTipo(e.target.value as TipoPregunta)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          {Object.entries(TIPO_PREGUNTA_LABELS).map(([valor, etiqueta]) => (
                            <option key={valor} value={valor}>{etiqueta}</option>
                          ))}
                        </select>
                      )}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nivel de dificultad
                    </label>
                    <Controller
                      name="nivel_dificultad"
                      control={control}
                      render={({ field }: any) => (
                        <select
                          {...field}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          {Object.entries(DIFICULTAD_LABELS).map(([valor, etiqueta]) => (
                            <option key={valor} value={valor}>{etiqueta as string}</option>
                          ))}
                        </select>
                      )}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Puntos *
                    </label>
                    <input
                      type="number"
                      min="0.5"
                      max="20"
                      step="0.5"
                      {...register('puntos', { 
                        required: 'Los puntos son obligatorios',
                        min: { value: 0.5, message: 'Mínimo 0.5 puntos' },
                        max: { value: 20, message: 'Máximo 20 puntos' }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Explicación (opcional)
                  </label>
                  <textarea
                    {...register('explicacion')}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Proporciona una explicación detallada de la respuesta correcta..."
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Sección Opciones */}
        {seccionActiva === 'opciones' && (
          <Card>
            <CardHeader
              title="Opciones de Respuesta"
              subtitle={`Configura las opciones para ${TIPO_PREGUNTA_LABELS[tipoPregunta]}`}
              actions={
                (tipoPregunta === 'OPCION_MULTIPLE') && (
                  <button
                    type="button"
                    onClick={agregarOpcion}
                    className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Agregar Opción</span>
                  </button>
                )
              }
            />
            <CardContent>
              {(tipoPregunta === 'ENSAYO' || tipoPregunta === 'COMPLETAR') ? (
                <div className="text-center py-8">
                  <p className="text-gray-500 dark:text-gray-400">
                    Las preguntas de tipo {TIPO_PREGUNTA_LABELS[tipoPregunta]} no requieren opciones predefinidas
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {opciones.map((opcion, index) => (
                    <motion.div
                      key={opcion.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-start space-x-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                    >
                      <div className="flex items-center pt-2">
                        <input
                          type={tipoPregunta === 'OPCION_MULTIPLE' ? 'radio' : 'radio'}
                          {...register(`opciones_respuesta.${index}.es_correcta`)}
                          name={tipoPregunta === 'OPCION_MULTIPLE' ? `opciones_respuesta.${index}.es_correcta` : 'respuesta_correcta'}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                          disabled={tipoPregunta === 'VERDADERO_FALSO'}
                        />
                      </div>
                      
                      <div className="flex-1">
                        <input
                          {...register(`opciones_respuesta.${index}.texto`, {
                            required: 'El texto de la opción es obligatorio'
                          })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder={`Opción ${index + 1}`}
                          disabled={tipoPregunta === 'VERDADERO_FALSO'}
                        />
                      </div>

                      {(tipoPregunta !== 'VERDADERO_FALSO' && opciones.length > 2) && (
                        <button
                          type="button"
                          onClick={() => eliminarOpcion(index)}
                          className="p-2 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                        >
                          <Trash className="h-4 w-4" />
                        </button>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Sección Multimedia */}
        {seccionActiva === 'multimedia' && (
          <Card>
            <CardHeader
              title="Contenido Multimedia"
              subtitle="Agrega imágenes o audio para enriquecer tu pregunta"
            />
            <CardContent>
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-400">
                  Funcionalidad de multimedia disponible próximamente
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Sección Metadata */}
        {seccionActiva === 'metadata' && (
          <Card>
            <CardHeader
              title="Información Adicional"
              subtitle="Categorías, etiquetas y metadatos de la pregunta"
            />
            <CardContent>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Categoría
                  </label>
                  <div className="flex space-x-2">
                    <Controller
                      name="categoria"
                      control={control}
                      render={({ field }) => (
                        <select
                          {...field}
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="">Seleccionar categoría</option>
                          {categorias.map((categoria) => (
                            <option key={categoria} value={categoria}>{categoria}</option>
                          ))}
                        </select>
                      )}
                    />
                    <input
                      type="text"
                      value={nuevaCategoria}
                      onChange={(e) => setNuevaCategoria(e.target.value)}
                      placeholder="Nueva categoría"
                      className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <button
                      type="button"
                      onClick={agregarCategoria}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Etiquetas
                  </label>
                  <div className="space-y-3">
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={nuevaEtiqueta}
                        onChange={(e) => setNuevaEtiqueta(e.target.value)}
                        placeholder="Nueva etiqueta"
                        className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            agregarEtiqueta();
                          }
                        }}
                      />
                      <button
                        type="button"
                        onClick={agregarEtiqueta}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>

                    {watchedValues.etiquetas.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {watchedValues.etiquetas.map((etiqueta, index) => (
                          <span
                            key={index}
                            className="flex items-center space-x-1 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-sm"
                          >
                            <Tag className="h-3 w-3" />
                            <span>{etiqueta}</span>
                            <button
                              type="button"
                              onClick={() => eliminarEtiqueta(etiqueta)}
                              className="ml-1 hover:text-red-600 dark:hover:text-red-400"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Objetivo de aprendizaje
                  </label>
                  <textarea
                    {...register('objetivo_aprendizaje')}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="¿Qué debe aprender el estudiante con esta pregunta?"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Referencia (opcional)
                  </label>
                  <input
                    type="text"
                    {...register('referencia')}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Libro, página, URL, etc."
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

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
                    <AlertTriangle className="h-4 w-4" />
                    <span>Cambios sin guardar</span>
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
                  <span>{esEdicion ? 'Actualizar' : 'Crear'} Pregunta</span>
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Vista previa */}
        {mostrarPrevia && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader
                title="Vista Previa"
                subtitle="Cómo se verá esta pregunta"
              />
              <CardContent>
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorDificultad(watchedValues.nivel_dificultad)}`}>
                      {DIFICULTAD_LABELS[watchedValues.nivel_dificultad]}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {watchedValues.puntos} puntos
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    {watchedValues.texto_pregunta || 'Escribe tu pregunta aquí...'}
                  </h3>

                  {(tipoPregunta !== 'ENSAYO' && tipoPregunta !== 'COMPLETAR') && (
                    <div className="space-y-3">
                      {opciones.map((opcion, index) => (
                        <div
                          key={index}
                          className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                            watchedValues.opciones_respuesta[index]?.es_correcta
                              ? 'border-green-300 bg-green-50 dark:bg-green-900/20'
                              : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                          }`}
                        >
                          {watchedValues.opciones_respuesta[index]?.texto || `Opción ${index + 1}`}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {watchedValues.explicacion && (
                    <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <h4 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
                        Explicación:
                      </h4>
                      <p className="text-blue-700 dark:text-blue-400 text-sm">
                        {watchedValues.explicacion}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </form>
    </div>
  );
}