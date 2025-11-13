import { useState, useEffect } from 'react';
import { Plus, Search, Filter, Loader2 } from 'lucide-react';
import TareaCard from './TareaCard';
import { TareaEnriquecida, FiltrosTarea, EstadoVisualizacion } from '../types';
import { apiClientTareas } from '../api';

interface TareasListProps {
  cursoId: string;
  onTareaClick?: (tarea: TareaEnriquecida) => void;
  onCrearTarea?: () => void;
}

export default function TareasList({ cursoId, onTareaClick, onCrearTarea }: TareasListProps) {
  const [tareas, setTareas] = useState<TareaEnriquecida[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState<EstadoVisualizacion | 'todos'>('todos');
  const [mostrarFiltros, setMostrarFiltros] = useState(false);

  // Cargar tareas del curso
  const cargarTareas = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filtros: FiltrosTarea = {
        curso_id: cursoId,
        solo_activas: true,
      };

      if (filtroEstado !== 'todos') {
        filtros.estado_visual = filtroEstado;
      }

      // TODO: Implementar endpoint de tareas enriquecidas
      // Por ahora usamos el endpoint básico
      const response = await apiClientTareas.obtenerTareasCurso(cursoId, 50, 0);
      
      // Si la respuesta es un array, úsalo directamente; si es un objeto con 'tareas', extráelo
      const tareasData = Array.isArray(response) ? response : response.tareas || [];
      
      setTareas(tareasData as TareaEnriquecida[]);
    } catch (err) {
      console.error('Error cargando tareas:', err);
      setError('Error al cargar las tareas. Por favor intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarTareas();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cursoId, filtroEstado]);

  // Filtrar tareas por búsqueda
  const tareasFiltradas = tareas.filter(tarea => {
    if (!busqueda) return true;
    const searchLower = busqueda.toLowerCase();
    return (
      tarea.titulo.toLowerCase().includes(searchLower) ||
      tarea.descripcion?.toLowerCase().includes(searchLower)
    );
  });

  // Agrupar tareas por estado visual
  const tareasAgrupadas = {
    urgentes: tareasFiltradas.filter(t => 
      t.estado_visual === EstadoVisualizacion.PROXIMA_A_VENCER
    ),
    vencidas: tareasFiltradas.filter(t => 
      t.estado_visual === EstadoVisualizacion.VENCIDA
    ),
    pendientes: tareasFiltradas.filter(t => 
      t.estado_visual === EstadoVisualizacion.PENDIENTE
    ),
    entregadas: tareasFiltradas.filter(t => 
      t.estado_visual === EstadoVisualizacion.ENTREGADA
    ),
    calificadas: tareasFiltradas.filter(t => 
      t.estado_visual === EstadoVisualizacion.CALIFICADA
    ),
  };

  return (
    <div className="space-y-4">
      {/* Header con búsqueda y filtros */}
      <div className="flex items-center gap-3">
        {/* Barra de búsqueda */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar tareas..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        {/* Botón de filtros */}
        <button
          onClick={() => setMostrarFiltros(!mostrarFiltros)}
          className={`px-4 py-2 rounded-lg border flex items-center gap-2 transition-colors ${
            mostrarFiltros
              ? 'bg-primary text-white border-primary'
              : 'bg-white dark:bg-zinc-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-zinc-700'
          }`}
        >
          <Filter className="w-4 h-4" />
          <span>Filtros</span>
        </button>

        {/* Botón crear tarea */}
        {onCrearTarea && (
          <button
            onClick={onCrearTarea}
            className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors flex items-center gap-2 font-semibold"
          >
            <Plus className="w-4 h-4" />
            <span>Nueva Tarea</span>
          </button>
        )}
      </div>

      {/* Panel de filtros */}
      {mostrarFiltros && (
        <div className="p-4 rounded-lg bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Estado:</span>
            {(['todos', 'pendiente', 'proxima_a_vencer', 'vencida', 'entregada', 'calificada'] as const).map(estado => (
              <button
                key={estado}
                onClick={() => setFiltroEstado(estado === 'todos' ? 'todos' : estado as EstadoVisualizacion)}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition-colors ${
                  filtroEstado === estado
                    ? 'bg-primary text-white'
                    : 'bg-white dark:bg-zinc-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-zinc-600'
                }`}
              >
                {estado === 'todos' ? 'Todas' : estado.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Estado de carga */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin mb-2" />
          <p className="text-gray-600 dark:text-gray-400">Cargando tareas...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <p className="text-red-800 dark:text-red-300">{error}</p>
          <button
            onClick={cargarTareas}
            className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Lista de tareas */}
      {!loading && !error && (
        <div className="space-y-6">
          {/* Tareas urgentes */}
          {tareasAgrupadas.urgentes.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-yellow-700 dark:text-yellow-400 mb-3 flex items-center gap-2">
                ⏰ Próximas a vencer ({tareasAgrupadas.urgentes.length})
              </h3>
              <div className="grid gap-3">
                {tareasAgrupadas.urgentes.map(tarea => (
                  <TareaCard
                    key={tarea.tarea_id}
                    tarea={tarea}
                    onClick={() => onTareaClick?.(tarea)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Tareas vencidas */}
          {tareasAgrupadas.vencidas.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-red-700 dark:text-red-400 mb-3 flex items-center gap-2">
                ❌ Vencidas ({tareasAgrupadas.vencidas.length})
              </h3>
              <div className="grid gap-3">
                {tareasAgrupadas.vencidas.map(tarea => (
                  <TareaCard
                    key={tarea.tarea_id}
                    tarea={tarea}
                    onClick={() => onTareaClick?.(tarea)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Tareas pendientes */}
          {tareasAgrupadas.pendientes.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                📝 Pendientes ({tareasAgrupadas.pendientes.length})
              </h3>
              <div className="grid gap-3">
                {tareasAgrupadas.pendientes.map(tarea => (
                  <TareaCard
                    key={tarea.tarea_id}
                    tarea={tarea}
                    onClick={() => onTareaClick?.(tarea)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Tareas entregadas */}
          {tareasAgrupadas.entregadas.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-blue-700 dark:text-blue-400 mb-3 flex items-center gap-2">
                📤 Entregadas ({tareasAgrupadas.entregadas.length})
              </h3>
              <div className="grid gap-3">
                {tareasAgrupadas.entregadas.map(tarea => (
                  <TareaCard
                    key={tarea.tarea_id}
                    tarea={tarea}
                    onClick={() => onTareaClick?.(tarea)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Tareas calificadas */}
          {tareasAgrupadas.calificadas.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-green-700 dark:text-green-400 mb-3 flex items-center gap-2">
                ✅ Calificadas ({tareasAgrupadas.calificadas.length})
              </h3>
              <div className="grid gap-3">
                {tareasAgrupadas.calificadas.map(tarea => (
                  <TareaCard
                    key={tarea.tarea_id}
                    tarea={tarea}
                    onClick={() => onTareaClick?.(tarea)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Sin tareas */}
          {tareasFiltradas.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 dark:text-gray-500 mb-2">
                <Search className="w-12 h-12 mx-auto mb-3" />
              </div>
              <p className="text-gray-600 dark:text-gray-400">
                {busqueda ? 'No se encontraron tareas que coincidan con tu búsqueda' : 'No hay tareas disponibles'}
              </p>
              {onCrearTarea && !busqueda && (
                <button
                  onClick={onCrearTarea}
                  className="mt-4 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
                >
                  Crear la primera tarea
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
