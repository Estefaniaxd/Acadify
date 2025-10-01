import React, { useState, useEffect } from 'react';
import { Tarea, TareaDetallada, FiltrosTarea, EstadoTarea, TipoTarea, PrioridadTarea } from '../types';
import TareasApi from '../api';

interface ListaTareasProps {
  grupoId: string;
  onTareaSeleccionada?: (tarea: Tarea) => void;
  onCrearTarea?: () => void;
  filtrosIniciales?: Partial<FiltrosTarea>;
}

const ListaTareas: React.FC<ListaTareasProps> = ({
  grupoId,
  onTareaSeleccionada,
  onCrearTarea,
  filtrosIniciales = {}
}) => {
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtros, setFiltros] = useState<Partial<FiltrosTarea>>({
    solo_activas: true,
    ordenar_por: 'fecha_limite',
    orden_desc: false,
    ...filtrosIniciales
  });

  const tareasApi = new TareasApi();

  useEffect(() => {
    cargarTareas();
  }, [grupoId, filtros]);

  const cargarTareas = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const tareasData = await tareasApi.obtenerTareasGrupo(grupoId, filtros);
      setTareas(tareasData);
    } catch (err) {
      setError('Error al cargar las tareas');
      console.error('Error cargando tareas:', err);
    } finally {
      setLoading(false);
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

  const getPrioridadColor = (prioridad: PrioridadTarea): string => {
    const colores = {
      [PrioridadTarea.BAJA]: 'text-green-600',
      [PrioridadTarea.MEDIA]: 'text-yellow-600',
      [PrioridadTarea.ALTA]: 'text-orange-600',
      [PrioridadTarea.URGENTE]: 'text-red-600',
    };
    return colores[prioridad] || 'text-gray-600';
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

  const formatearFecha = (fecha: string): string => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const esFechaProxima = (fecha: string): boolean => {
    const fechaLimite = new Date(fecha);
    const ahora = new Date();
    const diferenciaDias = (fechaLimite.getTime() - ahora.getTime()) / (1000 * 60 * 60 * 24);
    return diferenciaDias <= 3 && diferenciaDias > 0;
  };

  const handleFiltroChange = (campo: keyof FiltrosTarea, valor: any) => {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Cargando tareas...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 mb-4">⚠️</div>
        <p className="text-red-600 mb-4">{error}</p>
        <button 
          onClick={cargarTareas}
          className="bg-red-100 text-red-800 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con filtros */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Tareas</h2>
          <p className="text-sm text-gray-600">
            {tareas.length} {tareas.length === 1 ? 'tarea' : 'tareas'} encontradas
          </p>
        </div>
        
        {onCrearTarea && (
          <button
            onClick={onCrearTarea}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <span>➕</span>
            Nueva Tarea
          </button>
        )}
      </div>

      {/* Filtros rápidos */}
      <div className="flex flex-wrap gap-2">
        <select
          value={filtros.estado || ''}
          onChange={(e) => handleFiltroChange('estado', e.target.value || undefined)}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">Todos los estados</option>
          {Object.values(EstadoTarea).map(estado => (
            <option key={estado} value={estado}>
              {estado.charAt(0).toUpperCase() + estado.slice(1).replace('_', ' ')}
            </option>
          ))}
        </select>

        <select
          value={filtros.tipo_tarea || ''}
          onChange={(e) => handleFiltroChange('tipo_tarea', e.target.value || undefined)}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">Todos los tipos</option>
          {Object.values(TipoTarea).map(tipo => (
            <option key={tipo} value={tipo}>
              {getTipoIcon(tipo)} {tipo.charAt(0).toUpperCase() + tipo.slice(1)}
            </option>
          ))}
        </select>

        <select
          value={filtros.prioridad || ''}
          onChange={(e) => handleFiltroChange('prioridad', e.target.value || undefined)}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">Todas las prioridades</option>
          {Object.values(PrioridadTarea).map(prioridad => (
            <option key={prioridad} value={prioridad}>
              {prioridad.charAt(0).toUpperCase() + prioridad.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Lista de tareas */}
      {tareas.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="text-4xl mb-4">📝</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No hay tareas disponibles
          </h3>
          <p className="text-gray-600 mb-4">
            {filtros.estado || filtros.tipo_tarea || filtros.prioridad
              ? 'No se encontraron tareas con los filtros seleccionados'
              : 'Aún no se han creado tareas para este grupo'}
          </p>
          {onCrearTarea && (
            <button
              onClick={onCrearTarea}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Crear Primera Tarea
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {tareas.map((tarea, index) => (
            <div
              key={tarea.id || `tarea-${index}`}
              onClick={() => onTareaSeleccionada?.(tarea)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Header de la tarea */}
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xl">{getTipoIcon(tarea.tipo_tarea)}</span>
                    <h3 className="font-semibold text-gray-900 truncate">
                      {tarea.titulo}
                    </h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getEstadoColor(tarea.estado)}`}>
                      {tarea.estado.replace('_', ' ')}
                    </span>
                  </div>

                  {/* Descripción */}
                  {tarea.descripcion && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {tarea.descripcion}
                    </p>
                  )}

                  {/* Metadatos */}
                  <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <span>⏰</span>
                      <span className={esFechaProxima(tarea.fecha_limite) ? 'text-orange-600 font-medium' : ''}>
                        {formatearFecha(tarea.fecha_limite)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-1">
                      <span>🎯</span>
                      <span>{tarea.puntuacion_maxima} pts</span>
                    </div>
                    
                    <div className={`flex items-center gap-1 ${getPrioridadColor(tarea.prioridad)}`}>
                      <span>🏷️</span>
                      <span>{tarea.prioridad}</span>
                    </div>

                    {tarea.es_grupal && (
                      <div className="flex items-center gap-1 text-blue-600">
                        <span>👥</span>
                        <span>Grupal</span>
                      </div>
                    )}
                  </div>

                  {/* Estadísticas de entregas */}
                  {(tarea.total_entregas || 0) > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="flex items-center gap-4 text-xs text-gray-600">
                        <span>📬 {tarea.total_entregas} entregas</span>
                        {(tarea.entregas_pendientes || 0) > 0 && (
                          <span className="text-yellow-600">
                            ⏳ {tarea.entregas_pendientes} pendientes
                          </span>
                        )}
                        {tarea.promedio_calificaciones && (
                          <span className="text-green-600">
                            📊 Promedio: {tarea.promedio_calificaciones.toFixed(1)}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Indicador de vencimiento */}
                {tarea.esta_vencida && (
                  <div className="ml-4 flex-shrink-0">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ListaTareas;