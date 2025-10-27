import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  TagIcon,
  DocumentDuplicateIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  BookOpenIcon,
  FolderIcon
} from '@heroicons/react/24/outline';
import { Card, CardHeader, CardContent, Grid, EmptyState } from '../common/LayoutComponents';
import { LoadingSpinner, CardSkeleton } from '../common/LoadingComponents';
import { ConfirmDialog, useToast } from '../common/AlertComponents';
import { useBancoPreguntas } from '../../hooks';
import { 
  BancoPregunta, 
  TipoPregunta, 
  DificultadPregunta, 
  FiltrosBancoPreguntas 
} from '../../types';
import { 
  TIPO_PREGUNTA_LABELS, 
  DIFICULTAD_LABELS,
  obtenerColorDificultad,
  obtenerColorTipo,
  formatearFecha
} from '../../utils';
import { CreadorPregunta } from './CreadorPregunta';

interface BancoPreguntasProps {
  className?: string;
}

type Vista = 'lista' | 'crear' | 'editar' | 'detalle';

export function BancoPreguntas({ className = '' }: BancoPreguntasProps) {
  const [vista, setVista] = useState<Vista>('lista');
  const [preguntaSeleccionada, setPreguntaSeleccionada] = useState<BancoPregunta | null>(null);
  const [filtros, setFiltros] = useState<FiltrosBancoPreguntas>({
    busqueda: '',
    materia: undefined,
    tema: undefined,
    tipo_pregunta: undefined,
    dificultad: undefined,
    categoria: undefined,
    nivel_educativo: undefined,
    es_publica: undefined,
    creado_por: undefined,
    tags: []
  });
  const [mostrarFiltrosAvanzados, setMostrarFiltrosAvanzados] = useState(false);
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

  const {
    preguntas,
    loading,
    error,
    crearPregunta,
    actualizarPregunta,
    eliminarPregunta,
    buscarPreguntas
  } = useBancoPreguntas();

  const manejarCrearPregunta = useCallback(() => {
    setPreguntaSeleccionada(null);
    setVista('crear');
  }, []);

  const manejarEditarPregunta = useCallback((pregunta: BancoPregunta) => {
    setPreguntaSeleccionada(pregunta);
    setVista('editar');
  }, []);

  const manejarVerDetalle = useCallback((pregunta: BancoPregunta) => {
    setPreguntaSeleccionada(pregunta);
    setVista('detalle');
  }, []);

  const manejarGuardarPregunta = useCallback(async (datos: any, esEdicion: boolean) => {
    try {
      if (esEdicion && preguntaSeleccionada) {
        await actualizarPregunta(preguntaSeleccionada.pregunta_id, datos);
        showToast({
          type: 'success',
          title: 'Pregunta actualizada',
          message: 'La pregunta se ha actualizado correctamente'
        });
      } else {
        await crearPregunta(datos);
        showToast({
          type: 'success',
          title: 'Pregunta creada',
          message: 'La pregunta se ha añadido al banco'
        });
      }
      setVista('lista');
      setPreguntaSeleccionada(null);
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: error instanceof Error ? error.message : 'Error al guardar la pregunta'
      });
    }
  }, [preguntaSeleccionada, actualizarPregunta, crearPregunta, showToast]);

  const manejarEliminarPregunta = useCallback(async (preguntaId: string) => {
    setConfirmDialog({
      isOpen: true,
      title: 'Confirmar eliminación',
      message: '¿Estás seguro de que quieres eliminar esta pregunta del banco? Esta acción no se puede deshacer.',
      onConfirm: async () => {
        try {
          await eliminarPregunta(preguntaId);
          showToast({
            type: 'success',
            title: 'Pregunta eliminada',
            message: 'La pregunta se ha eliminado del banco'
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

  const manejarDuplicarPregunta = useCallback(async (pregunta: BancoPregunta) => {
    try {
      // Crear una copia de la pregunta
      const preguntaCopiada = {
        ...pregunta,
        titulo: `Copia de ${pregunta.titulo}`,
        pregunta_id: undefined // Será generado por el backend
      };
      await crearPregunta(preguntaCopiada as any);
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
  }, [crearPregunta, showToast]);

  const manejarVolverALista = useCallback(() => {
    setVista('lista');
    setPreguntaSeleccionada(null);
  }, []);

  const manejarBusqueda = useCallback((termino: string) => {
    setFiltros((prev: FiltrosBancoPreguntas) => ({ ...prev, busqueda: termino }));
  }, []);

  const manejarFiltrosAvanzados = useCallback((nuevosFiltros: Partial<FiltrosBancoPreguntas>) => {
    setFiltros((prev: FiltrosBancoPreguntas) => ({ ...prev, ...nuevosFiltros }));
  }, []);

  const limpiarFiltros = useCallback(() => {
    setFiltros({
      busqueda: '',
      dificultad: undefined,
      tipo_pregunta: undefined,
      categoria: undefined,
      tags: []
    });
  }, []);

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 dark:text-red-400">Error: {error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Recargar página
        </button>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {vista === 'lista' && 'Banco de Preguntas'}
            {vista === 'crear' && 'Nueva Pregunta'}
            {vista === 'editar' && 'Editar Pregunta'}
            {vista === 'detalle' && 'Detalle de Pregunta'}
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            {vista === 'lista' && 'Gestiona tu biblioteca de preguntas reutilizables'}
            {vista === 'crear' && 'Añade una nueva pregunta a tu banco'}
            {vista === 'editar' && 'Modifica los detalles de la pregunta'}
            {vista === 'detalle' && 'Vista detallada de la pregunta'}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {vista === 'lista' && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={manejarCrearPregunta}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-lg"
            >
              <PlusIcon className="h-5 w-5" />
              <span>Nueva Pregunta</span>
            </motion.button>
          )}

          {vista !== 'lista' && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={manejarVolverALista}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
            >
              <span>Volver</span>
            </motion.button>
          )}
        </div>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* Vista Lista */}
        {vista === 'lista' && (
          <motion.div
            key="lista"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.3 }}
          >
            <ListaPreguntas
              preguntas={preguntas}
              loading={loading}
              filtros={filtros}
              mostrarFiltrosAvanzados={mostrarFiltrosAvanzados}
              onBusqueda={manejarBusqueda}
              onFiltrosAvanzados={manejarFiltrosAvanzados}
              onMostrarFiltros={setMostrarFiltrosAvanzados}
              onLimpiarFiltros={limpiarFiltros}
              onEditarPregunta={manejarEditarPregunta}
              onVerDetalle={manejarVerDetalle}
              onEliminarPregunta={manejarEliminarPregunta}
              onDuplicarPregunta={manejarDuplicarPregunta}
            />
          </motion.div>
        )}

        {/* Vista Crear/Editar */}
        {(vista === 'crear' || vista === 'editar') && (
          <motion.div
            key="formulario"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <CreadorPregunta
              pregunta={preguntaSeleccionada}
              onGuardar={(datos: any) => manejarGuardarPregunta(datos, vista === 'editar')}
              onCancelar={manejarVolverALista}
            />
          </motion.div>
        )}

        {/* Vista Detalle */}
        {vista === 'detalle' && preguntaSeleccionada && (
          <motion.div
            key="detalle"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader
                title="Detalle de Pregunta"
                subtitle="Información completa de la pregunta"
              />
              <CardContent>
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">{preguntaSeleccionada.titulo}</h3>
                  <p className="text-gray-600">{preguntaSeleccionada.descripcion}</p>
                  <button
                    onClick={manejarVolverALista}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Volver a la lista
                  </button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={confirmDialog.onConfirm}
        onClose={() => setConfirmDialog(prev => ({ ...prev, isOpen: false }))}
        type="error"
      />
    </div>
  );
}

interface ListaPreguntasProps {
  preguntas: BancoPregunta[];
  loading: boolean;
  filtros: FiltrosBancoPreguntas;
  mostrarFiltrosAvanzados: boolean;
  onBusqueda: (termino: string) => void;
  onFiltrosAvanzados: (filtros: Partial<FiltrosBancoPreguntas>) => void;
  onMostrarFiltros: (mostrar: boolean) => void;
  onLimpiarFiltros: () => void;
  onEditarPregunta: (pregunta: BancoPregunta) => void;
  onVerDetalle: (pregunta: BancoPregunta) => void;
  onEliminarPregunta: (preguntaId: string) => void;
  onDuplicarPregunta?: (pregunta: BancoPregunta) => void;
}

function ListaPreguntas({
  preguntas,
  loading,
  filtros,
  mostrarFiltrosAvanzados,
  onBusqueda,
  onFiltrosAvanzados,
  onMostrarFiltros,
  onLimpiarFiltros,
  onEditarPregunta,
  onVerDetalle,
  onEliminarPregunta,
  onDuplicarPregunta
}: ListaPreguntasProps) {
  // Calcular categorías y etiquetas únicas de las preguntas
  const categorias = [...new Set(preguntas.map(p => p.categoria).filter(Boolean))];
  const etiquetas = [...new Set(preguntas.flatMap(p => p.tags || []))];

  return (
    <div className="space-y-6">
      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpenIcon className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Total Preguntas
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {preguntas.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FolderIcon className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Categorías
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {categorias.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TagIcon className="h-8 w-8 text-purple-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Etiquetas
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {etiquetas.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentDuplicateIcon className="h-8 w-8 text-orange-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Más Usadas
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {preguntas.filter(p => p.tipo_pregunta === 'OPCION_MULTIPLE').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Buscar preguntas..."
                    value={filtros.busqueda}
                    onChange={(e) => onBusqueda(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>
              <button
                onClick={() => onMostrarFiltros(!mostrarFiltrosAvanzados)}
                className="flex items-center space-x-2 px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <FunnelIcon className="h-5 w-5" />
                <span>Filtros</span>
              </button>
              {(filtros.busqueda || filtros.dificultad || filtros.tipo_pregunta || filtros.categoria) && (
                <button
                  onClick={onLimpiarFiltros}
                  className="px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                >
                  Limpiar
                </button>
              )}
            </div>

            <AnimatePresence>
              {mostrarFiltrosAvanzados && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nivel de dificultad
                    </label>
                    <select
                      value={filtros.dificultad || ''}
                      onChange={(e) => onFiltrosAvanzados({
                        dificultad: e.target.value as DificultadPregunta || undefined
                      })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Todos los niveles</option>
                      {Object.entries(DIFICULTAD_LABELS).map(([valor, etiqueta]) => (
                        <option key={valor} value={valor}>{String(etiqueta)}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tipo de pregunta
                    </label>
                    <select
                      value={filtros.tipo_pregunta || ''}
                      onChange={(e) => onFiltrosAvanzados({
                        tipo_pregunta: e.target.value as TipoPregunta || undefined
                      })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Todos los tipos</option>
                      {Object.entries(TIPO_PREGUNTA_LABELS).map(([valor, etiqueta]) => (
                        <option key={valor} value={valor}>{etiqueta}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Categoría
                    </label>
                    <select
                      value={filtros.categoria || ''}
                      onChange={(e) => onFiltrosAvanzados({
                        categoria: e.target.value || undefined
                      })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Todas las categorías</option>
                      {categorias.map((categoria) => (
                        <option key={categoria} value={categoria}>{categoria}</option>
                      ))}
                    </select>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Preguntas */}
      {loading ? (
        <Grid cols={2}>
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} lines={5} />
          ))}
        </Grid>
      ) : preguntas.length === 0 ? (
        <EmptyState
          icon={<BookOpenIcon className="w-12 h-12" />}
          title="No hay preguntas"
          description="Tu banco de preguntas está vacío. Crea tu primera pregunta para comenzar."
          action={
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onLimpiarFiltros()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              Crear primera pregunta
            </motion.button>
          }
        />
      ) : (
        <Grid cols={2}>
          {preguntas.map((pregunta) => (
            <TarjetaPregunta
              key={pregunta.pregunta_id}
              pregunta={pregunta}
              onEditar={onEditarPregunta}
              onVerDetalle={onVerDetalle}
              onEliminar={onEliminarPregunta}
              onDuplicar={onDuplicarPregunta || (() => {})}
            />
          ))}
        </Grid>
      )}
    </div>
  );
}

interface TarjetaPreguntaProps {
  pregunta: BancoPregunta;
  onEditar: (pregunta: BancoPregunta) => void;
  onVerDetalle: (pregunta: BancoPregunta) => void;
  onEliminar: (preguntaId: string) => void;
  onDuplicar: (pregunta: BancoPregunta) => void;
}

function TarjetaPregunta({
  pregunta,
  onEditar,
  onVerDetalle,
  onEliminar,
  onDuplicar
}: TarjetaPreguntaProps) {
  const [mostrarMenu, setMostrarMenu] = useState(false);

  return (
    <Card hover className="relative">
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorDificultad(pregunta.dificultad)}`}>
                  {DIFICULTAD_LABELS[pregunta.dificultad]}
                </span>
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-xs">
                  {TIPO_PREGUNTA_LABELS[pregunta.tipo_pregunta]}
                </span>
              </div>
              
              <h3 className="font-medium text-gray-900 dark:text-white mb-2 line-clamp-2">
                {pregunta.titulo}
              </h3>
              
              <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                <span>{pregunta.puntuacion_sugerida} pts</span>
                <span>{pregunta.veces_utilizada} usos</span>
                {pregunta.categoria && (
                  <span className="text-blue-600 dark:text-blue-400">
                    {pregunta.categoria}
                  </span>
                )}
              </div>
            </div>

            <div className="relative ml-4">
              <button
                onClick={() => setMostrarMenu(!mostrarMenu)}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
              >
                <EyeIcon className="h-5 w-5" />
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
                        onVerDetalle(pregunta);
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
                    >
                      <EyeIcon className="h-4 w-4" />
                      <span>Ver detalle</span>
                    </button>
                    <button
                      onClick={() => {
                        onEditar(pregunta);
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
                    >
                      <PencilIcon className="h-4 w-4" />
                      <span>Editar</span>
                    </button>
                    <button
                      onClick={() => {
                        onDuplicar(pregunta);
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
                    >
                      <DocumentDuplicateIcon className="h-4 w-4" />
                      <span>Duplicar</span>
                    </button>
                    <button
                      onClick={() => {
                        onEliminar(pregunta.pregunta_id);
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
                    >
                      <TrashIcon className="h-4 w-4" />
                      <span>Eliminar</span>
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {pregunta.tags && pregunta.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {pregunta.tags.map((etiqueta: string, index: number) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded text-xs"
                >
                  {etiqueta}
                </span>
              ))}
            </div>
          )}

          <div className="text-xs text-gray-500 dark:text-gray-500 border-t pt-3">
            <p>Creada: {formatearFecha(pregunta.fecha_creacion)}</p>
            {pregunta.fecha_actualizacion && (
              <p>Actualizada: {formatearFecha(pregunta.fecha_actualizacion)}</p>
            )}
          </div>
        </div>
      </CardContent>

      {/* Click overlay para cerrar menú */}
      {mostrarMenu && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setMostrarMenu(false)}
        />
      )}
    </Card>
  );
}