import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PlusIcon,
  DocumentDuplicateIcon,
  EyeIcon,
  PlayIcon,
  Cog6ToothIcon,
  BookOpenIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { Card, CardHeader, CardContent, Grid, EmptyState } from '../common/LayoutComponents';
import { LoadingSpinner, CardSkeleton } from '../common/LoadingComponents';
import { useToast } from '../common/AlertComponents';
import { useExamenes } from '../../hooks';
import { TIPO_EXAMEN_LABELS, ESTADO_EXAMEN_LABELS, obtenerColorEstado, obtenerColorTipo, formatearFecha } from '../../utils';
import { Examen, TipoExamen, EstadoExamen } from '../../types';
import { FormularioExamen } from './FormularioExamen';
import { EditorPreguntas } from './EditorPreguntas';

interface CreadorExamenesProps {
  className?: string;
}

type Vista = 'lista' | 'crear' | 'editar' | 'preguntas';

export function CreadorExamenes({ className = '' }: CreadorExamenesProps) {
  const [vista, setVista] = useState<Vista>('lista');
  const [examenSeleccionado, setExamenSeleccionado] = useState<Examen | null>(null);
  const [filtros, setFiltros] = useState({
    estado: '' as EstadoExamen | '',
    tipo: '' as TipoExamen | '',
    busqueda: ''
  });

  const { showToast } = useToast();
  const {
    examenes,
    loading,
    error,
    crearExamen,
    actualizarExamen,
    eliminarExamen,
    cambiarEstado,
    clonarExamen
  } = useExamenes({
    filtros: {
      estado: filtros.estado || undefined,
      tipo: filtros.tipo || undefined
    }
  });

  // Filtrar exámenes por búsqueda
  const examenesFiltrados = React.useMemo(() => {
    if (!filtros.busqueda) return examenes;
    
    return examenes.filter(examen =>
      examen.titulo.toLowerCase().includes(filtros.busqueda.toLowerCase()) ||
      examen.descripcion.toLowerCase().includes(filtros.busqueda.toLowerCase())
    );
  }, [examenes, filtros.busqueda]);

  const manejarCrearExamen = useCallback(() => {
    setExamenSeleccionado(null);
    setVista('crear');
  }, []);

  const manejarEditarExamen = useCallback((examen: Examen) => {
    setExamenSeleccionado(examen);
    setVista('editar');
  }, []);

  const manejarEditarPreguntas = useCallback((examen: Examen) => {
    setExamenSeleccionado(examen);
    setVista('preguntas');
  }, []);

  const manejarGuardarExamen = useCallback(async (datos: any, esEdicion: boolean) => {
    try {
      if (esEdicion && examenSeleccionado) {
        await actualizarExamen(examenSeleccionado.examen_id, datos);
        showToast({
          type: 'success',
          title: 'Examen actualizado',
          message: 'El examen se ha actualizado correctamente'
        });
      } else {
        await crearExamen(datos);
        showToast({
          type: 'success',
          title: 'Examen creado',
          message: 'El examen se ha creado correctamente'
        });
      }
      setVista('lista');
      setExamenSeleccionado(null);
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: error instanceof Error ? error.message : 'Error al guardar el examen'
      });
    }
  }, [examenSeleccionado, actualizarExamen, crearExamen, showToast]);

  const manejarEliminarExamen = useCallback(async (examenId: string) => {
    try {
      await eliminarExamen(examenId);
      showToast({
        type: 'success',
        title: 'Examen eliminado',
        message: 'El examen se ha eliminado correctamente'
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo eliminar el examen'
      });
    }
  }, [eliminarExamen, showToast]);

  const manejarCambiarEstado = useCallback(async (examenId: string, nuevoEstado: EstadoExamen) => {
    try {
      await cambiarEstado(examenId, nuevoEstado);
      showToast({
        type: 'success',
        title: 'Estado actualizado',
        message: `El examen ahora está ${ESTADO_EXAMEN_LABELS[nuevoEstado].toLowerCase()}`
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo cambiar el estado del examen'
      });
    }
  }, [cambiarEstado, showToast]);

  const manejarClonarExamen = useCallback(async (examen: Examen) => {
    try {
      await clonarExamen(examen.examen_id, `Copia de ${examen.titulo}`);
      showToast({
        type: 'success',
        title: 'Examen clonado',
        message: 'Se ha creado una copia del examen'
      });
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'No se pudo clonar el examen'
      });
    }
  }, [clonarExamen, showToast]);

  const manejarVolverALista = useCallback(() => {
    setVista('lista');
    setExamenSeleccionado(null);
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
            {vista === 'lista' && 'Mis Exámenes'}
            {vista === 'crear' && 'Crear Nuevo Examen'}
            {vista === 'editar' && 'Editar Examen'}
            {vista === 'preguntas' && 'Editor de Preguntas'}
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            {vista === 'lista' && 'Gestiona y organiza tus evaluaciones'}
            {vista === 'crear' && 'Configura los detalles de tu nuevo examen'}
            {vista === 'editar' && 'Modifica la configuración del examen'}
            {vista === 'preguntas' && 'Agrega y organiza las preguntas del examen'}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {vista === 'lista' && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={manejarCrearExamen}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-lg"
            >
              <PlusIcon className="h-5 w-5" />
              <span>Nuevo Examen</span>
            </motion.button>
          )}

          {(vista === 'crear' || vista === 'editar' || vista === 'preguntas') && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={manejarVolverALista}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
            >
              <span>Volver a Lista</span>
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
            <ListaExamenes
              examenes={examenesFiltrados}
              loading={loading}
              filtros={filtros}
              onFiltrosChange={setFiltros}
              onEditarExamen={manejarEditarExamen}
              onEditarPreguntas={manejarEditarPreguntas}
              onEliminarExamen={manejarEliminarExamen}
              onCambiarEstado={manejarCambiarEstado}
              onClonarExamen={manejarClonarExamen}
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
            <FormularioExamen
              examen={examenSeleccionado}
              onGuardar={(datos) => manejarGuardarExamen(datos, vista === 'editar')}
              onCancelar={manejarVolverALista}
            />
          </motion.div>
        )}

        {/* Vista Editor Preguntas */}
        {vista === 'preguntas' && examenSeleccionado && (
          <motion.div
            key="preguntas"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <EditorPreguntas
              examen={examenSeleccionado}
              onVolver={manejarVolverALista}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface ListaExamenesProps {
  examenes: Examen[];
  loading: boolean;
  filtros: {
    estado: EstadoExamen | '';
    tipo: TipoExamen | '';
    busqueda: string;
  };
  onFiltrosChange: (filtros: any) => void;
  onEditarExamen: (examen: Examen) => void;
  onEditarPreguntas: (examen: Examen) => void;
  onEliminarExamen: (examenId: string) => void;
  onCambiarEstado: (examenId: string, estado: EstadoExamen) => void;
  onClonarExamen: (examen: Examen) => void;
}

function ListaExamenes({
  examenes,
  loading,
  filtros,
  onFiltrosChange,
  onEditarExamen,
  onEditarPreguntas,
  onEliminarExamen,
  onCambiarEstado,
  onClonarExamen
}: ListaExamenesProps) {
  return (
    <div className="space-y-6">
      {/* Filtros */}
      <Card>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Buscar
              </label>
              <input
                type="text"
                placeholder="Buscar por título o descripción..."
                value={filtros.busqueda}
                onChange={(e) => onFiltrosChange({ ...filtros, busqueda: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Estado
              </label>
              <select
                value={filtros.estado}
                onChange={(e) => onFiltrosChange({ ...filtros, estado: e.target.value as EstadoExamen | '' })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos los estados</option>
                {Object.entries(ESTADO_EXAMEN_LABELS).map(([valor, etiqueta]) => (
                  <option key={valor} value={valor}>{etiqueta}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tipo
              </label>
              <select
                value={filtros.tipo}
                onChange={(e) => onFiltrosChange({ ...filtros, tipo: e.target.value as TipoExamen | '' })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos los tipos</option>
                {Object.entries(TIPO_EXAMEN_LABELS).map(([valor, etiqueta]) => (
                  <option key={valor} value={valor}>{etiqueta}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Exámenes */}
      {loading ? (
        <Grid cols={3}>
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} lines={4} />
          ))}
        </Grid>
      ) : examenes.length === 0 ? (
        <EmptyState
          icon={<BookOpenIcon className="w-12 h-12" />}
          title="No hay exámenes"
          description="Crea tu primer examen para comenzar a evaluar a tus estudiantes"
          action={
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onFiltrosChange({ estado: '', tipo: '', busqueda: '' })}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              Crear mi primer examen
            </motion.button>
          }
        />
      ) : (
        <Grid cols={3}>
          {examenes.map((examen) => (
            <TarjetaExamen
              key={examen.examen_id}
              examen={examen}
              onEditar={onEditarExamen}
              onEditarPreguntas={onEditarPreguntas}
              onEliminar={onEliminarExamen}
              onCambiarEstado={onCambiarEstado}
              onClonar={onClonarExamen}
            />
          ))}
        </Grid>
      )}
    </div>
  );
}

interface TarjetaExamenProps {
  examen: Examen;
  onEditar: (examen: Examen) => void;
  onEditarPreguntas: (examen: Examen) => void;
  onEliminar: (examenId: string) => void;
  onCambiarEstado: (examenId: string, estado: EstadoExamen) => void;
  onClonar: (examen: Examen) => void;
}

function TarjetaExamen({
  examen,
  onEditar,
  onEditarPreguntas,
  onEliminar,
  onCambiarEstado,
  onClonar
}: TarjetaExamenProps) {
  const [mostrarMenu, setMostrarMenu] = useState(false);

  return (
    <Card hover className="relative">
      <CardHeader
        title={examen.titulo}
        subtitle={examen.descripcion}
        actions={
          <div className="relative">
            <button
              onClick={() => setMostrarMenu(!mostrarMenu)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
            >
              <Cog6ToothIcon className="h-5 w-5" />
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
                      onEditar(examen);
                      setMostrarMenu(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    Editar configuración
                  </button>
                  <button
                    onClick={() => {
                      onEditarPreguntas(examen);
                      setMostrarMenu(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    Editar preguntas
                  </button>
                  <button
                    onClick={() => {
                      onClonar(examen);
                      setMostrarMenu(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    Clonar examen
                  </button>
                  {examen.estado_examen !== 'ACTIVO' && (
                    <button
                      onClick={() => {
                        onCambiarEstado(examen.examen_id, 'ACTIVO');
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-green-600 dark:text-green-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      Activar
                    </button>
                  )}
                  {examen.estado_examen === 'ACTIVO' && (
                    <button
                      onClick={() => {
                        onCambiarEstado(examen.examen_id, 'PAUSADO');
                        setMostrarMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-yellow-600 dark:text-yellow-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      Pausar
                    </button>
                  )}
                  <button
                    onClick={() => {
                      if (confirm('¿Estás seguro de que quieres eliminar este examen?')) {
                        onEliminar(examen.examen_id);
                      }
                      setMostrarMenu(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    Eliminar
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        }
      />

      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorTipo(examen.tipo_examen)}`}>
              {TIPO_EXAMEN_LABELS[examen.tipo_examen]}
            </span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${obtenerColorEstado(examen.estado_examen)}`}>
              {ESTADO_EXAMEN_LABELS[examen.estado_examen]}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-400">
            <div>
              <p className="font-medium">Preguntas</p>
              <p>{examen.total_preguntas}</p>
            </div>
            <div>
              <p className="font-medium">Duración</p>
              <p>{examen.tiempo_limite} min</p>
            </div>
            <div>
              <p className="font-medium">Intentos</p>
              <p>{examen.total_intentos}</p>
            </div>
            <div>
              <p className="font-medium">Aprobación</p>
              <p>{examen.puntuacion_minima_aprobacion}%</p>
            </div>
          </div>

          <div className="text-xs text-gray-500 dark:text-gray-500 border-t pt-3">
            <p>Creado: {formatearFecha(examen.fecha_creacion)}</p>
            <p>Límite: {formatearFecha(examen.fecha_limite)}</p>
          </div>
        </div>
      </CardContent>

      {/* Click overlay para abrir menú */}
      {mostrarMenu && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setMostrarMenu(false)}
        />
      )}
    </Card>
  );
}