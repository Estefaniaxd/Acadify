import React, { useState, useEffect } from 'react';
import { Tarea, EntregaTarea, EstadoTarea, EstadoEntrega } from '../types';
import TareasApi from '../api';

interface DetalleTareaProps {
  tarea: Tarea;
  onClose: () => void;
  onEdit?: (tarea: Tarea) => void;
  onDelete?: (tareaId: string) => void;
  esDocente?: boolean;
  estudianteId?: string;
}

const DetalleTarea: React.FC<DetalleTareaProps> = ({
  tarea,
  onClose,
  onEdit,
  onDelete,
  esDocente = false,
  estudianteId
}) => {
  const [entregas, setEntregas] = useState<EntregaTarea[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const tareasApi = new TareasApi();

  useEffect(() => {
    if (esDocente && tarea.id) {
      cargarEntregas();
    }
  }, [tarea.id, esDocente]);

  const cargarEntregas = async () => {
    if (!tarea.id) return;
    
    setLoading(true);
    try {
      const entregasData = await tareasApi.obtenerEntregasTarea(tarea.id);
      setEntregas(entregasData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar entregas');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!tarea.id || !onDelete) return;
    
    try {
      await tareasApi.eliminarTarea(tarea.id);
      onDelete(tarea.id);
      setShowDeleteConfirm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al eliminar tarea');
    }
  };

  const getEstadoColor = (estado: EstadoTarea): string => {
    const colores = {
      [EstadoTarea.BORRADOR]: 'bg-gray-100 text-gray-800',
      [EstadoTarea.PUBLICADA]: 'bg-blue-100 text-blue-800',
      [EstadoTarea.EN_PROGRESO]: 'bg-yellow-100 text-yellow-800',
      [EstadoTarea.VENCIDA]: 'bg-red-100 text-red-800',
      [EstadoTarea.CERRADA]: 'bg-gray-100 text-gray-800',
      [EstadoTarea.ARCHIVADA]: 'bg-gray-100 text-gray-600'
    };
    return colores[estado] || 'bg-gray-100 text-gray-800';
  };

  const getEntregaEstadoColor = (estado: EstadoEntrega): string => {
    const colores = {
      [EstadoEntrega.BORRADOR]: 'bg-gray-100 text-gray-800',
      [EstadoEntrega.ENVIADA]: 'bg-blue-100 text-blue-800',
      [EstadoEntrega.EN_REVISION]: 'bg-yellow-100 text-yellow-800',
      [EstadoEntrega.CALIFICADA]: 'bg-green-100 text-green-800',
      [EstadoEntrega.DEVUELTA]: 'bg-orange-100 text-orange-800',
      [EstadoEntrega.RECHAZADA]: 'bg-red-100 text-red-800'
    };
    return colores[estado] || 'bg-gray-100 text-gray-800';
  };

  const getTiempoRestante = (): string => {
    if (!tarea.fecha_limite) return '';
    
    const ahora = new Date();
    const limite = new Date(tarea.fecha_limite);
    const diferencia = limite.getTime() - ahora.getTime();
    
    if (diferencia <= 0) return 'Vencida';
    
    const dias = Math.floor(diferencia / (1000 * 60 * 60 * 24));
    const horas = Math.floor((diferencia % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (dias > 0) return `${dias} día${dias > 1 ? 's' : ''} y ${horas} hora${horas > 1 ? 's' : ''}`;
    return `${horas} hora${horas > 1 ? 's' : ''}`;
  };

  const getProgreso = (): { completadas: number; total: number; porcentaje: number } => {
    if (!esDocente || entregas.length === 0) {
      return { completadas: 0, total: 0, porcentaje: 0 };
    }
    
    const completadas = entregas.filter(e => 
      e.estado === EstadoEntrega.ENVIADA || 
      e.estado === EstadoEntrega.CALIFICADA
    ).length;
    
    return {
      completadas,
      total: entregas.length,
      porcentaje: Math.round((completadas / entregas.length) * 100)
    };
  };

  const formatearFecha = (fecha: string): string => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const progreso = getProgreso();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-gray-900">{tarea.titulo}</h2>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getEstadoColor(tarea.estado)}`}>
                  {tarea.estado}
                </span>
              </div>
              
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>📝 {tarea.tipo_tarea}</span>
                <span>⭐ {tarea.prioridad}</span>
                <span>📊 {tarea.puntuacion_maxima} puntos</span>
                {tarea.es_grupal && <span>👥 Grupal</span>}
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {esDocente && onEdit && (
                <button
                  onClick={() => onEdit(tarea)}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Editar tarea"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              )}
              
              {esDocente && onDelete && (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Eliminar tarea"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
              
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Contenido */}
        <div className="p-6">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Columna principal */}
            <div className="lg:col-span-2 space-y-6">
              {/* Información de fechas */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-3">📅 Fechas Importantes</h3>
                <div className="space-y-2 text-sm">
                  {tarea.fecha_inicio_disponible && (
                    <div className="flex justify-between">
                      <span className="text-blue-700">Disponible desde:</span>
                      <span className="font-medium">{formatearFecha(tarea.fecha_inicio_disponible)}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-blue-700">Fecha límite:</span>
                    <span className="font-medium">{formatearFecha(tarea.fecha_limite)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Tiempo restante:</span>
                    <span className={`font-medium ${tarea.estado === EstadoTarea.VENCIDA ? 'text-red-600' : 'text-green-600'}`}>
                      {getTiempoRestante()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Descripción */}
              {tarea.descripcion && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">📝 Descripción</h3>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap">{tarea.descripcion}</p>
                  </div>
                </div>
              )}

              {/* Instrucciones */}
              {tarea.instrucciones && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">📋 Instrucciones</h3>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap">{tarea.instrucciones}</p>
                  </div>
                </div>
              )}

              {/* Objetivos */}
              {tarea.objetivos && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">🎯 Objetivos de Aprendizaje</h3>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap">{tarea.objetivos}</p>
                  </div>
                </div>
              )}

              {/* Criterios de evaluación */}
              {tarea.criterios_evaluacion && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">✅ Criterios de Evaluación</h3>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap">{tarea.criterios_evaluacion}</p>
                  </div>
                </div>
              )}

              {/* Recursos */}
              {tarea.recursos_necesarios && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">📚 Recursos Necesarios</h3>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap">{tarea.recursos_necesarios}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Columna lateral */}
            <div className="space-y-6">
              {/* Información rápida */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">📊 Información</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tiempo estimado:</span>
                    <span className="font-medium">{tarea.tiempo_estimado} min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Intentos máximos:</span>
                    <span className="font-medium">{tarea.intentos_maximos}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Peso en evaluación:</span>
                    <span className="font-medium">{tarea.peso_evaluacion}%</span>
                  </div>
                  {tarea.tamano_maximo_mb && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tamaño máximo:</span>
                      <span className="font-medium">{tarea.tamano_maximo_mb} MB</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Configuración de entrega */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">⚙️ Configuración</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className={tarea.permite_entrega_tardia ? 'text-green-600' : 'text-red-600'}>
                      {tarea.permite_entrega_tardia ? '✅' : '❌'}
                    </span>
                    <span>Entregas tardías</span>
                  </div>
                  {tarea.permite_entrega_tardia && tarea.penalizacion_tardia > 0 && (
                    <div className="ml-6 text-orange-600">
                      Penalización: {tarea.penalizacion_tardia}%
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <span className={tarea.es_publica ? 'text-green-600' : 'text-red-600'}>
                      {tarea.es_publica ? '✅' : '❌'}
                    </span>
                    <span>Visible para estudiantes</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={tarea.requiere_aprobacion ? 'text-yellow-600' : 'text-green-600'}>
                      {tarea.requiere_aprobacion ? '⏳' : '✅'}
                    </span>
                    <span>Requiere aprobación</span>
                  </div>
                </div>
              </div>

              {/* Progreso (solo para docentes) */}
              {esDocente && (
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900 mb-3">📈 Progreso</h3>
                  {loading ? (
                    <div className="text-center py-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-green-700">Entregas</span>
                        <span className="text-sm font-medium">{progreso.completadas}/{progreso.total}</span>
                      </div>
                      <div className="w-full bg-green-200 rounded-full h-2 mb-3">
                        <div 
                          className="bg-green-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${progreso.porcentaje}%` }}
                        />
                      </div>
                      <div className="text-center text-2xl font-bold text-green-600">
                        {progreso.porcentaje}%
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Lista de entregas (solo para docentes) */}
              {esDocente && entregas.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3">📤 Entregas Recientes</h3>
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {entregas.slice(0, 5).map((entrega) => (
                      <div key={entrega.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="flex-1">
                          <div className="font-medium text-sm text-gray-900">
                            {entrega.estudiante_nombre || 'Estudiante'}
                          </div>
                          <div className="text-xs text-gray-500">
                            {entrega.fecha_entrega ? formatearFecha(entrega.fecha_entrega) : 'No entregado'}
                          </div>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEntregaEstadoColor(entrega.estado)}`}>
                          {entrega.estado}
                        </span>
                      </div>
                    ))}
                    {entregas.length > 5 && (
                      <div className="text-center text-sm text-gray-500">
                        y {entregas.length - 5} más...
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal de confirmación de eliminación */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Confirmar Eliminación</h3>
            <p className="text-gray-600 mb-6">
              ¿Estás seguro de que deseas eliminar la tarea "{tarea.titulo}"? Esta acción no se puede deshacer.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DetalleTarea;