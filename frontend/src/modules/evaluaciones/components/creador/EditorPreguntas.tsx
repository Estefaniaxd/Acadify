import React, { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence, Reorder } from 'framer-motion';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { AlertTriangle, ArrowUpDown, Eye, FileText, GraduationCap, Image as ImageIcon, Info, Plus, Tag, Trash, Volume2, X } from 'lucide-react';
import { Card, CardHeader, CardContent, Grid } from '../common/LayoutComponents';
import { LoadingSpinner, ProgressBar } from '../common/LoadingComponents';
import { ConfirmDialog, useToast } from '../common/AlertComponents';
import { useExamen, useBancoPreguntas } from '../../hooks';
import { 
  Examen, 
  PreguntaExamen, 
  TipoPregunta, 
  DificultadPregunta,
  OpcionRespuesta 
} from '../../types';
import { 
  TIPO_PREGUNTA_LABELS, 
  DIFICULTAD_LABELS,
  obtenerColorDificultad
} from '../../utils';

interface EditorPreguntasProps {
  examen: Examen;
  onVolver: () => void;
}

interface FormDataPregunta {
  pregunta_id?: string;
  titulo: string;
  tipo_pregunta: TipoPregunta;
  dificultad: DificultadPregunta;
  puntuacion_sugerida: number;
  tiempo_sugerido: number;
  explicacion: string;
  imagen_url?: string;
  audio_url?: string;
  opciones_respuesta: OpcionRespuesta[];
  orden: number;
  es_obligatoria: boolean;
  puntos_respuesta_parcial: boolean;
}

export function EditorPreguntas({ examen, onVolver }: EditorPreguntasProps) {
  const [modo, setModo] = useState<'lista' | 'crear' | 'editar' | 'previa'>('lista');
  const [preguntaSeleccionada, setPreguntaSeleccionada] = useState<PreguntaExamen | null>(null);
  const [mostrarBanco, setMostrarBanco] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
  }>({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {}
  });

  const { showToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);

  const {
    preguntas,
    loading,
    error,
    agregarPregunta,
    actualizarPregunta,
    eliminarPregunta,
    reordenarPreguntas,
    importarDesdeBanco
  } = useExamen(examen.examen_id);

  const {
    preguntas: preguntasBanco,
    loading: loadingBanco,
    buscarPreguntas
  } = useBancoPreguntas({
    filtros: {
      nivel_dificultad: undefined,
      tipo_pregunta: undefined
    }
  });

  const manejarCrearPregunta = useCallback(() => {
    setPreguntaSeleccionada(null);
    setModo('crear');
  }, []);

  const manejarEditarPregunta = useCallback((pregunta: PreguntaExamen) => {
    setPreguntaSeleccionada(pregunta);
    setModo('editar');
  }, []);

  const manejarVisualizarPregunta = useCallback((pregunta: PreguntaExamen) => {
    setPreguntaSeleccionada(pregunta);
    setModo('previa');
  }, []);

  const manejarEliminarPregunta = useCallback(async (preguntaId: string) => {
    setConfirmDialog({
      isOpen: true,
      title: 'Confirmar eliminación',
      message: '¿Estás seguro de que quieres eliminar esta pregunta? Esta acción no se puede deshacer.',
      onConfirm: async () => {
        try {
          await eliminarPregunta(preguntaId);
          showToast({
            type: 'success',
            title: 'Pregunta eliminada',
            message: 'La pregunta se ha eliminado correctamente'
          });
        } catch (error) {
          showToast({
            type: 'error',
            title: 'Error',
            message: 'No se pudo eliminar la pregunta'
          });
        }
        setConfirmDialog(prev => ({ ...prev, isOpen: false }));
      }
    });
  }, [eliminarPregunta, showToast]);

  const manejarDuplicarPregunta = useCallback(async (pregunta: PreguntaExamen) => {
    try {
      const preguntaDuplicada = {
        ...pregunta,
        texto_pregunta: `${pregunta.texto_pregunta} (Copia)`,
        pregunta_id: undefined,
        orden: preguntas.length + 1
      };
      
      await agregarPregunta(preguntaDuplicada);
      showToast({
        type: 'success',
        title: 'Pregunta duplicada',
        message: 'Se ha creado una copia de la pregunta'
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo duplicar la pregunta'
      });
    }
  }, [preguntas.length, agregarPregunta, showToast]);

  const manejarReordenarPreguntas = useCallback(async (nuevasPreguntas: PreguntaExamen[]) => {
    try {
      const preguntasConOrden = nuevasPreguntas.map((pregunta, index) => ({
        ...pregunta,
        orden: index + 1
      }));
      
      await reordenarPreguntas(preguntasConOrden);
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo reordenar las preguntas'
      });
    }
  }, [reordenarPreguntas, showToast]);

  const manejarImportarDesdeBanco = useCallback(async (preguntasIds: string[]) => {
    try {
      setGuardando(true);
      await importarDesdeBanco(preguntasIds);
      setMostrarBanco(false);
      showToast({
        type: 'success',
        title: 'Preguntas importadas',
        message: `Se han importado ${preguntasIds.length} preguntas del banco`
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudieron importar las preguntas'
      });
    } finally {
      setGuardando(false);
    }
  }, [importarDesdeBanco, showToast]);

  const manejarVolverALista = useCallback(() => {
    setModo('lista');
    setPreguntaSeleccionada(null);
  }, []);

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 dark:text-red-400">Error: {error}</p>
        <button
          onClick={onVolver}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Volver al examen
        </button>
      </div>
    );
  }

  const preguntasOrdenadas = [...preguntas].sort((a, b) => a.orden - b.orden);
  const totalPuntos = preguntas.reduce((suma, p) => suma + p.puntos, 0);
  const progresoCompletitud = preguntas.length > 0 ? (preguntas.length / Math.max(preguntas.length, 10)) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header con estadísticas */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card>
          <CardContent>
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Editor de Preguntas: {examen.titulo}
                </h2>
                <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4" />
                    <span>{preguntas.length} preguntas</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{totalPuntos} puntos totales</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>Tiempo estimado: {preguntas.reduce((suma, p) => suma + p.tiempo_sugerido, 0)} min</span>
                  </div>
                </div>
                <div className="mt-3">
                  <ProgressBar
                    value={progresoCompletitud}
                    className="h-2"
                    label={`${Math.round(progresoCompletitud)}% completado`}
                  />
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {modo === 'lista' && (
                  <>
                    <button
                      onClick={() => setMostrarBanco(true)}
                      className="flex items-center space-x-2 px-4 py-2 text-blue-600 dark:text-blue-400 border border-blue-300 dark:border-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                    >
                      <FileText className="h-5 w-5" />
                      <span>Banco de Preguntas</span>
                    </button>
                    <button
                      onClick={manejarCrearPregunta}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-lg"
                    >
                      <Plus className="h-5 w-5" />
                      <span>Nueva Pregunta</span>
                    </button>
                  </>
                )}
                
                <button
                  onClick={modo === 'lista' ? onVolver : manejarVolverALista}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  {modo === 'lista' ? 'Volver al Examen' : 'Volver a Lista'}
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* Vista Lista */}
        {modo === 'lista' && (
          <motion.div
            key="lista"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.3 }}
          >
            <ListaPreguntas
              preguntas={preguntasOrdenadas}
              loading={loading}
              onEditarPregunta={manejarEditarPregunta}
              onVisualizarPregunta={manejarVisualizarPregunta}
              onEliminarPregunta={manejarEliminarPregunta}
              onDuplicarPregunta={manejarDuplicarPregunta}
              onReordenarPreguntas={manejarReordenarPreguntas}
            />
          </motion.div>
        )}

        {/* Vista Crear/Editar */}
        {(modo === 'crear' || modo === 'editar') && (
          <motion.div
            key="formulario"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <FormularioPregunta
              pregunta={preguntaSeleccionada}
              examenId={examen.examen_id}
              siguienteOrden={preguntas.length + 1}
              onGuardar={async (datos) => {
                try {
                  setGuardando(true);
                  if (modo === 'editar' && preguntaSeleccionada) {
                    await actualizarPregunta(preguntaSeleccionada.pregunta_id, datos);
                    showToast({
                      type: 'success',
                      title: 'Pregunta actualizada',
                      message: 'La pregunta se ha actualizado correctamente'
                    });
                  } else {
                    await agregarPregunta(datos);
                    showToast({
                      type: 'success',
                      title: 'Pregunta creada',
                      message: 'La pregunta se ha creado correctamente'
                    });
                  }
                  manejarVolverALista();
                } catch (error) {
                  showToast({
                    type: 'error',
                    title: 'Error',
                    message: error instanceof Error ? error.message : 'Error al guardar la pregunta'
                  });
                } finally {
                  setGuardando(false);
                }
              }}
              onCancelar={manejarVolverALista}
              guardando={guardando}
            />
          </motion.div>
        )}

        {/* Vista Previa */}
        {modo === 'previa' && preguntaSeleccionada && (
          <motion.div
            key="previa"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <PreviaEstudiante
              pregunta={preguntaSeleccionada}
              onCerrar={manejarVolverALista}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal Banco de Preguntas */}
      <AnimatePresence>
        {mostrarBanco && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
            >
              <BancoPreguntas
                preguntas={preguntasBanco}
                loading={loadingBanco}
                onImportar={manejarImportarDesdeBanco}
                onCerrar={() => setMostrarBanco(false)}
                guardando={guardando}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog(prev => ({ ...prev, isOpen: false }))}
        type="danger"
      />
    </div>
  );
}

interface ListaPreguntasProps {
  preguntas: PreguntaExamen[];
  loading: boolean;
  onEditarPregunta: (pregunta: PreguntaExamen) => void;
  onVisualizarPregunta: (pregunta: PreguntaExamen) => void;
  onEliminarPregunta: (preguntaId: string) => void;
  onDuplicarPregunta: (pregunta: PreguntaExamen) => void;
  onReordenarPreguntas: (preguntas: PreguntaExamen[]) => void;
}

function ListaPreguntas({
  preguntas,
  loading,
  onEditarPregunta,
  onVisualizarPregunta,
  onEliminarPregunta,
  onDuplicarPregunta,
  onReordenarPreguntas
}: ListaPreguntasProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (preguntas.length === 0) {
    return (
      <Card>
        <CardContent>
          <div className="text-center py-12">
            <FileText className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No hay preguntas
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Comienza agregando la primera pregunta a tu examen
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Reorder.Group
        axis="y"
        values={preguntas}
        onReorder={onReordenarPreguntas}
        className="space-y-3"
      >
        {preguntas.map((pregunta, index) => (
          <Reorder.Item
            key={pregunta.pregunta_id}
            value={pregunta}
            className="cursor-move"
          >
            <TarjetaPregunta
              pregunta={pregunta}
              numero={index + 1}
              onEditar={onEditarPregunta}
              onVisualizar={onVisualizarPregunta}
              onEliminar={onEliminarPregunta}
              onDuplicar={onDuplicarPregunta}
            />
          </Reorder.Item>
        ))}
      </Reorder.Group>
    </div>
  );
}

interface TarjetaPreguntaProps {
  pregunta: PreguntaExamen;
  numero: number;
  onEditar: (pregunta: PreguntaExamen) => void;
  onVisualizar: (pregunta: PreguntaExamen) => void;
  onEliminar: (preguntaId: string) => void;
  onDuplicar: (pregunta: PreguntaExamen) => void;
}

function TarjetaPregunta({
  pregunta,
  numero,
  onEditar,
  onVisualizar,
  onEliminar,
  onDuplicar
}: TarjetaPreguntaProps) {
  const [mostrarMenu, setMostrarMenu] = useState(false);

  return (
    <Card hover className="relative">
      <CardContent>
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4 flex-1">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full font-medium text-sm flex-shrink-0">
              {numero}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3 mb-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorDificultad(pregunta.dificultad)}`}>
                  {DIFICULTAD_LABELS[pregunta.dificultad]}
                </span>
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-xs">
                  {TIPO_PREGUNTA_LABELS[pregunta.tipo_pregunta]}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {pregunta.puntuacion_sugerida} pts • {pregunta.tiempo_estimado_segundos ? Math.round(pregunta.tiempo_estimado_segundos / 60) : 0} min
                </span>
              </div>
              
              <p className="text-gray-900 dark:text-white font-medium mb-2 line-clamp-2">
                {pregunta.titulo}
              </p>
              
              {pregunta.imagen_url && (
                <div className="flex items-center space-x-1 text-xs text-blue-600 dark:text-blue-400 mb-2">
                  <ImageIcon className="h-3 w-3" />
                  <span>Con imagen</span>
                </div>
              )}
              
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {pregunta.opciones_respuesta.length} opciones de respuesta
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 flex-shrink-0 ml-4">
            <button
              onClick={() => onVisualizar(pregunta)}
              className="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg transition-colors"
              title="Vista previa"
            >
              <Eye className="h-4 w-4" />
            </button>
            
            <div className="relative">
              <button
                onClick={() => setMostrarMenu(!mostrarMenu)}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
              >
                <ArrowUpDown className="h-4 w-4" />
              </button>
              
              <AnimatePresence>
                {mostrarMenu && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10"
                  >
                    <button
                      onClick={() => {
                        onEditar(pregunta);
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      Editar pregunta
                    </button>
                    <button
                      onClick={() => {
                        onDuplicar(pregunta);
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      Duplicar pregunta
                    </button>
                    <button
                      onClick={() => {
                        onEliminar(pregunta.pregunta_id);
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      Eliminar pregunta
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </CardContent>
      
      {/* Overlay para cerrar menú */}
      {mostrarMenu && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setMostrarMenu(false)}
        />
      )}
    </Card>
  );
}

// Componentes adicionales simplificados para mantener el archivo legible
function FormularioPregunta({ 
  pregunta, 
  examenId, 
  siguienteOrden, 
  onGuardar, 
  onCancelar, 
  guardando 
}: {
  pregunta: PreguntaExamen | null;
  examenId: string;
  siguienteOrden: number;
  onGuardar: (datos: FormDataPregunta) => Promise<void>;
  onCancelar: () => void;
  guardando: boolean;
}) {
  const [seccionActiva, setSeccionActiva] = useState<'contenido' | 'opciones' | 'multimedia' | 'configuracion'>('contenido');
  const [mostrarPrevia, setMostrarPrevia] = useState(false);
  const [subiendoArchivo, setSubiendoArchivo] = useState(false);
  
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
      pregunta_id: pregunta?.pregunta_id || undefined,
      titulo: pregunta?.titulo || '',
      tipo_pregunta: pregunta?.tipo_pregunta || 'OPCION_MULTIPLE',
      dificultad: pregunta?.dificultad || 'MEDIO',
      puntuacion_sugerida: pregunta?.puntuacion_sugerida || 1,
      tiempo_sugerido: pregunta?.tiempo_estimado_segundos ? Math.round(pregunta.tiempo_estimado_segundos / 60) : 2,
      explicacion: pregunta?.explicacion || '',
      imagen_url: pregunta?.imagen_url || '',
      audio_url: pregunta?.audio_url || '',
      opciones_respuesta: pregunta?.opciones_respuesta || [
        { id: '1', texto: '', es_correcta: true },
        { id: '2', texto: '', es_correcta: false }
      ],
      orden: pregunta?.orden || siguienteOrden,
      es_obligatoria: pregunta?.es_obligatoria ?? true,
      puntos_respuesta_parcial: pregunta?.puntos_respuesta_parcial ?? false
    },
    mode: 'onChange'
  });

  const { fields: opciones, append, remove, move } = useFieldArray({
    control,
    name: 'opciones_respuesta'
  });

  const watchedValues = watch();
  const tipoPregunta = watch('tipo_pregunta');

  const manejarSubmit = useCallback(async (datos: FormDataPregunta) => {
    try {
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
          orden: index + 1
        }))
      };

      await onGuardar(datosFinales);
    } catch (error) {
      console.error('Error al guardar pregunta:', error);
    }
  }, [onGuardar, tipoPregunta, showToast]);

  const agregarOpcion = useCallback(() => {
    append({
      id: `option_${Date.now()}`,
      texto: '',
      es_correcta: false
    });
  }, [append]);

  const eliminarOpcion = useCallback((index: number) => {
    if (opciones.length > 2) {
      remove(index);
    }
  }, [remove, opciones.length]);

  const manejarCambioTipo = useCallback((nuevoTipo: TipoPregunta) => {
    setValue('tipo_pregunta', nuevoTipo);
    
    // Ajustar opciones según el tipo
    if (nuevoTipo === 'VERDADERO_FALSO') {
      setValue('opciones_respuesta', [
        { id: '1', texto: 'Verdadero', es_correcta: true },
        { id: '2', texto: 'Falso', es_correcta: false }
      ]);
    } else if (nuevoTipo === 'ENSAYO' || nuevoTipo === 'COMPLETAR') {
      setValue('opciones_respuesta', []);
    } else if (opciones.length === 0) {
      setValue('opciones_respuesta', [
        { id: '1', texto: '', es_correcta: true },
        { id: '2', texto: '', es_correcta: false }
      ]);
    }
  }, [setValue, opciones.length]);

  const subirArchivo = useCallback(async (archivo: File, tipo: 'imagen' | 'audio') => {
    try {
      setSubiendoArchivo(true);
      
      // Aquí iría la lógica real de subida de archivos
      // Por ahora simulamos la subida
      const url = URL.createObjectURL(archivo);
      
      if (tipo === 'imagen') {
        setValue('imagen_url', url);
      } else {
        setValue('audio_url', url);
      }
      
      showToast({
        type: 'success',
        title: 'Archivo subido',
        message: `${tipo} subida correctamente`
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: `No se pudo subir la ${tipo}`
      });
    } finally {
      setSubiendoArchivo(false);
    }
  }, [setValue, showToast]);

  const secciones = [
    { id: 'contenido', nombre: 'Contenido', icono: FileText },
    { id: 'opciones', nombre: 'Opciones', icono: Info },
    { id: 'multimedia', nombre: 'Multimedia', icono: ImageIcon },
    { id: 'configuracion', nombre: 'Configuración', icono: GraduationCap }
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
          {/* Sección Contenido */}
          {seccionActiva === 'contenido' && (
            <motion.div
              key="contenido"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader
                  title="Contenido de la Pregunta"
                  subtitle="Define el texto principal y detalles de la pregunta"
                />
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Texto de la pregunta *
                      </label>
                      <textarea
                        {...register('titulo', { 
                          required: 'El texto de la pregunta es obligatorio',
                          minLength: { value: 10, message: 'La pregunta debe tener al menos 10 caracteres' }
                        })}
                        rows={4}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                          errors.titulo ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                        }`}
                        placeholder="Escribe aquí el texto de tu pregunta..."
                      />
                      {errors.titulo && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.titulo.message}
                        </p>
                      )}
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                          render={({ field }) => (
                            <select
                              {...field}
                              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            >
                              {Object.entries(DIFICULTAD_LABELS).map(([valor, etiqueta]) => (
                                <option key={valor} value={valor}>{etiqueta}</option>
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
                          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                            errors.puntos ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                          }`}
                        />
                        {errors.puntos && (
                          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.puntos.message}
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Tiempo sugerido (minutos)
                        </label>
                        <input
                          type="number"
                          min="0.5"
                          max="30"
                          step="0.5"
                          {...register('tiempo_sugerido')}
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
            </motion.div>
          )}

          {/* Sección Opciones */}
          {seccionActiva === 'opciones' && (
            <motion.div
              key="opciones"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader
                  title="Opciones de Respuesta"
                  subtitle={`Configura las opciones para ${TIPO_PREGUNTA_LABELS[tipoPregunta]}`}
                  actions={
                    (tipoPregunta === 'MULTIPLE_CHOICE' || tipoPregunta === 'MULTIPLE_RESPONSE') && (
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
                  {(tipoPregunta === 'ESSAY' || tipoPregunta === 'SHORT_ANSWER') ? (
                    <div className="text-center py-8">
                      <FileText className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
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
                              type={tipoPregunta === 'MULTIPLE_RESPONSE' ? 'checkbox' : 'radio'}
                              {...register(`opciones_respuesta.${index}.es_correcta`)}
                              name={tipoPregunta === 'MULTIPLE_RESPONSE' ? `opciones_respuesta.${index}.es_correcta` : 'respuesta_correcta'}
                              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                              disabled={tipoPregunta === 'TRUE_FALSE'}
                            />
                          </div>
                          
                          <div className="flex-1">
                            <input
                              {...register(`opciones_respuesta.${index}.texto_opcion`, {
                                required: 'El texto de la opción es obligatorio'
                              })}
                              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                              placeholder={`Opción ${index + 1}`}
                              disabled={tipoPregunta === 'TRUE_FALSE'}
                            />
                          </div>

                          {(tipoPregunta !== 'TRUE_FALSE' && opciones.length > 2) && (
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
            </motion.div>
          )}

          {/* Sección Multimedia */}
          {seccionActiva === 'multimedia' && (
            <motion.div
              key="multimedia"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader
                  title="Contenido Multimedia"
                  subtitle="Agrega imágenes o audio para enriquecer tu pregunta"
                />
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Imagen */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        Imagen
                      </label>
                      
                      {watchedValues.imagen_url ? (
                        <div className="relative">
                          <img
                            src={watchedValues.imagen_url}
                            alt="Imagen de la pregunta"
                            className="w-full h-48 object-cover rounded-lg"
                          />
                          <button
                            type="button"
                            onClick={() => setValue('imagen_url', '')}
                            className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ) : (
                        <div
                          onClick={() => fileInputRef.current?.click()}
                          className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
                        >
                          <ImageIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                          <p className="text-gray-500 dark:text-gray-400">
                            Haz clic para subir una imagen
                          </p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                            PNG, JPG, GIF hasta 5MB
                          </p>
                        </div>
                      )}
                      
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) subirArchivo(file, 'imagen');
                        }}
                      />
                    </div>

                    {/* Audio */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        Audio
                      </label>
                      
                      {watchedValues.audio_url ? (
                        <div className="space-y-3">
                          <audio
                            controls
                            className="w-full"
                            src={watchedValues.audio_url}
                          />
                          <button
                            type="button"
                            onClick={() => setValue('audio_url', '')}
                            className="flex items-center space-x-2 px-3 py-2 text-red-600 dark:text-red-400 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                          >
                            <Trash className="h-4 w-4" />
                            <span>Eliminar audio</span>
                          </button>
                        </div>
                      ) : (
                        <div
                          onClick={() => audioInputRef.current?.click()}
                          className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
                        >
                          <Volume2 className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                          <p className="text-gray-500 dark:text-gray-400">
                            Haz clic para subir un audio
                          </p>
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                            MP3, WAV hasta 10MB
                          </p>
                        </div>
                      )}
                      
                      <input
                        ref={audioInputRef}
                        type="file"
                        accept="audio/*"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) subirArchivo(file, 'audio');
                        }}
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
                  title="Configuración Avanzada"
                  subtitle="Opciones adicionales para personalizar el comportamiento de la pregunta"
                />
                <CardContent>
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('es_obligatoria')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Pregunta obligatoria
                        </label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          {...register('permite_respuesta_parcial')}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900 dark:text-white">
                          Permitir respuesta parcial
                        </label>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Orden en el examen
                      </label>
                      <input
                        type="number"
                        min="1"
                        {...register('orden')}
                        className="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Vista previa y botones de acción */}
        <div className="space-y-6">
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
                    title="Vista Previa - Perspectiva del Estudiante"
                    subtitle="Cómo verán los estudiantes esta pregunta"
                  />
                  <CardContent>
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          Pregunta {watchedValues.orden} de X
                        </span>
                        <div className="flex items-center space-x-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorDificultad(watchedValues.nivel_dificultad)}`}>
                            {NIVEL_DIFICULTAD_LABELS[watchedValues.nivel_dificultad]}
                          </span>
                          <span className="text-gray-600 dark:text-gray-400">
                            {watchedValues.puntos} pts
                          </span>
                        </div>
                      </div>
                      
                      <div className="mb-6">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                          {watchedValues.texto_pregunta || 'Escribe tu pregunta aquí...'}
                        </h3>
                        
                        {watchedValues.imagen_url && (
                          <img
                            src={watchedValues.imagen_url}
                            alt="Imagen de la pregunta"
                            className="max-w-md mx-auto rounded-lg mb-4"
                          />
                        )}
                        
                        {watchedValues.audio_url && (
                          <audio
                            controls
                            className="mb-4"
                            src={watchedValues.audio_url}
                          />
                        )}
                      </div>

                      {(tipoPregunta !== 'ESSAY' && tipoPregunta !== 'SHORT_ANSWER') && (
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
                              {watchedValues.opciones_respuesta[index]?.texto_opcion || `Opción ${index + 1}`}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {(tipoPregunta === 'ESSAY' || tipoPregunta === 'SHORT_ANSWER') && (
                        <textarea
                          placeholder="El estudiante escribirá su respuesta aquí..."
                          rows={tipoPregunta === 'ESSAY' ? 6 : 3}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          disabled
                        />
                      )}

                      {watchedValues.explicacion && (
                        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                          <h4 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
                            Explicación (se mostrará después de responder):
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
                      <AlertTriangle className="h-4 w-4" />
                      <span>Cambios sin guardar</span>
                    </div>
                  )}

                  {subiendoArchivo && (
                    <div className="flex items-center space-x-2 text-sm text-blue-600 dark:text-blue-400">
                      <LoadingSpinner size="sm" />
                      <span>Subiendo archivo...</span>
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
                    disabled={!isValid || guardando || subiendoArchivo}
                    className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
                  >
                    {guardando && <LoadingSpinner size="sm" />}
                    <span>{esEdicion ? 'Actualizar' : 'Crear'} Pregunta</span>
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>
    </div>
  );
}

function PreviaEstudiante({ 
  pregunta, 
  onCerrar 
}: {
  pregunta: PreguntaExamen;
  onCerrar: () => void;
}) {
  // Implementación de la vista previa para estudiantes
  return (
    <Card>
      <CardHeader
        title="Vista previa - Perspectiva del estudiante"
        actions={
          <button
            onClick={onCerrar}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        }
      />
      <CardContent>
        <div className="space-y-4">
          <p className="text-lg font-medium text-gray-900 dark:text-white">
            {pregunta.texto_pregunta}
          </p>
          
          <div className="space-y-2">
            {pregunta.opciones_respuesta.map((opcion, index) => (
              <div
                key={index}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  opcion.es_correcta
                    ? 'border-green-300 bg-green-50 dark:bg-green-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                {opcion.texto_opcion}
              </div>
            ))}
          </div>
          
          {pregunta.explicacion && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h4 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
                Explicación:
              </h4>
              <p className="text-blue-700 dark:text-blue-400 text-sm">
                {pregunta.explicacion}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function BancoPreguntas({ 
  preguntas, 
  loading, 
  onImportar, 
  onCerrar, 
  guardando 
}: {
  preguntas: any[];
  loading: boolean;
  onImportar: (ids: string[]) => Promise<void>;
  onCerrar: () => void;
  guardando: boolean;
}) {
  const [filtros, setFiltros] = useState({
    busqueda: '',
    nivel_dificultad: '' as NivelDificultad | '',
    tipo_pregunta: '' as TipoPregunta | ''
  });
  const [preguntasSeleccionadas, setPreguntasSeleccionadas] = useState<Set<string>>(new Set());
  const [mostrarDetalles, setMostrarDetalles] = useState<string | null>(null);

  const preguntasFiltradas = preguntas.filter(pregunta => {
    const cumpleBusqueda = !filtros.busqueda || 
      pregunta.texto_pregunta.toLowerCase().includes(filtros.busqueda.toLowerCase());
    const cumpleNivel = !filtros.nivel_dificultad || 
      pregunta.nivel_dificultad === filtros.nivel_dificultad;
    const cumpleTipo = !filtros.tipo_pregunta || 
      pregunta.tipo_pregunta === filtros.tipo_pregunta;
    
    return cumpleBusqueda && cumpleNivel && cumpleTipo;
  });

  const manejarSeleccion = useCallback((preguntaId: string, seleccionada: boolean) => {
    const nuevasSeleccionadas = new Set(preguntasSeleccionadas);
    if (seleccionada) {
      nuevasSeleccionadas.add(preguntaId);
    } else {
      nuevasSeleccionadas.delete(preguntaId);
    }
    setPreguntasSeleccionadas(nuevasSeleccionadas);
  }, [preguntasSeleccionadas]);

  const manejarSeleccionarTodas = useCallback(() => {
    if (preguntasSeleccionadas.size === preguntasFiltradas.length) {
      setPreguntasSeleccionadas(new Set());
    } else {
      setPreguntasSeleccionadas(new Set(preguntasFiltradas.map(p => p.pregunta_id)));
    }
  }, [preguntasSeleccionadas.size, preguntasFiltradas]);

  const manejarImportar = useCallback(async () => {
    if (preguntasSeleccionadas.size === 0) return;
    
    await onImportar(Array.from(preguntasSeleccionadas));
    setPreguntasSeleccionadas(new Set());
  }, [preguntasSeleccionadas, onImportar]);

  return (
    <div className="flex flex-col h-full max-h-[80vh]">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Banco de Preguntas
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Selecciona preguntas para importar al examen
          </p>
        </div>
        <button
          onClick={onCerrar}
          className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Filtros */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Buscar
            </label>
            <input
              type="text"
              placeholder="Buscar preguntas..."
              value={filtros.busqueda}
              onChange={(e) => setFiltros(prev => ({ ...prev, busqueda: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nivel
            </label>
            <select
              value={filtros.nivel_dificultad}
              onChange={(e) => setFiltros(prev => ({ ...prev, nivel_dificultad: e.target.value as NivelDificultad | '' }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">Todos los niveles</option>
              {Object.entries(NIVEL_DIFICULTAD_LABELS).map(([valor, etiqueta]) => (
                <option key={valor} value={valor}>{etiqueta}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tipo
            </label>
            <select
              value={filtros.tipo_pregunta}
              onChange={(e) => setFiltros(prev => ({ ...prev, tipo_pregunta: e.target.value as TipoPregunta | '' }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">Todos los tipos</option>
              {Object.entries(TIPO_PREGUNTA_LABELS).map(([valor, etiqueta]) => (
                <option key={valor} value={valor}>{etiqueta}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Controles de selección */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-4">
            <button
              onClick={manejarSeleccionarTodas}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              {preguntasSeleccionadas.size === preguntasFiltradas.length ? 'Deseleccionar todas' : 'Seleccionar todas'}
            </button>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {preguntasSeleccionadas.size} de {preguntasFiltradas.length} seleccionadas
            </span>
          </div>

          <button
            onClick={manejarImportar}
            disabled={preguntasSeleccionadas.size === 0 || guardando}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg text-sm font-medium transition-colors disabled:cursor-not-allowed"
          >
            {guardando && <LoadingSpinner size="sm" />}
            <span>Importar ({preguntasSeleccionadas.size})</span>
          </button>
        </div>
      </div>

      {/* Lista de preguntas */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : preguntasFiltradas.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No hay preguntas
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              {preguntas.length === 0 
                ? 'El banco de preguntas está vacío'
                : 'No se encontraron preguntas con los filtros aplicados'
              }
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {preguntasFiltradas.map((pregunta) => (
              <motion.div
                key={pregunta.pregunta_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={preguntasSeleccionadas.has(pregunta.pregunta_id)}
                      onChange={(e) => manejarSeleccion(pregunta.pregunta_id, e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorDificultad(pregunta.nivel_dificultad)}`}>
                        {NIVEL_DIFICULTAD_LABELS[pregunta.nivel_dificultad]}
                      </span>
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-xs">
                        {TIPO_PREGUNTA_LABELS[pregunta.tipo_pregunta]}
                      </span>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => setMostrarDetalles(
                      mostrarDetalles === pregunta.pregunta_id ? null : pregunta.pregunta_id
                    )}
                    className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                </div>

                <p className="text-gray-900 dark:text-white font-medium mb-2 line-clamp-2">
                  {pregunta.texto_pregunta}
                </p>

                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>{pregunta.puntos} pts</span>
                  <span>{pregunta.opciones_respuesta?.length || 0} opciones</span>
                  <span>{pregunta.tiempo_sugerido} min</span>
                </div>

                {/* Detalles expandibles */}
                <AnimatePresence>
                  {mostrarDetalles === pregunta.pregunta_id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600"
                    >
                      {pregunta.imagen_url && (
                        <img
                          src={pregunta.imagen_url}
                          alt="Imagen de la pregunta"
                          className="max-w-full h-32 object-cover rounded mb-3"
                        />
                      )}
                      
                      {pregunta.opciones_respuesta?.length > 0 && (
                        <div className="space-y-2">
                          {pregunta.opciones_respuesta.map((opcion: any, index: number) => (
                            <div
                              key={index}
                              className={`text-xs p-2 rounded ${
                                opcion.es_correcta
                                  ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-700'
                                  : 'bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                              }`}
                            >
                              {opcion.texto_opcion}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {pregunta.explicacion && (
                        <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs">
                          <span className="font-medium text-blue-700 dark:text-blue-300">Explicación: </span>
                          <span className="text-blue-600 dark:text-blue-400">{pregunta.explicacion}</span>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}