import { useParams } from 'react-router-dom';
import { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { TareaFormModal } from '../tareas/components/TareaFormModal';
import { TareaPreviewModal } from '../tareas/components/TareaPreviewModal';
import { TareasAccordion } from '../tareas/components/TareasAccordion';
import { TareasStatistics } from '../tareas/components/TareasStatistics';
import { Tarea, EstadoTarea } from '../../modules/tareas/types';
import { Loader2, AlertCircle, Search } from 'lucide-react';
import axios from 'axios';

export default function ClaseTareasPage() {
  const { id: cursoId } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  // ====================================
  // ESTADO LOCAL
  // ====================================
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [tareaSeleccionada, setTareaSeleccionada] = useState<Tarea | null>(null);
  const [tareaAEditar, setTareaAEditar] = useState<Tarea | undefined>(undefined);
  const [searchTerm, setSearchTerm] = useState('');
  const [filtroTipo, setFiltroTipo] = useState<'todos' | 'tarea' | 'quiz' | 'proyecto'>('todos');
  const [filtroPrioridad, setFiltroPrioridad] = useState<'todos' | 'baja' | 'media' | 'alta'>('todos');
  const [filtroEstado, setFiltroEstado] = useState<'todos' | 'asignada' | 'en_progreso' | 'entregada' | 'calificada' | 'vencida' | 'cerrada'>('todos');

  // ====================================
  // FETCH TAREAS
  // ====================================
  const { data: tareas = [], isLoading, error } = useQuery({
    queryKey: ['cursoTareas', cursoId],
    queryFn: async () => {
      if (!cursoId) return [];
      try {
        const response = await axios.get<Tarea[]>(`/api/cursos/tareas/${cursoId}/tareas`);
        return response.data;
      } catch (err) {
        console.error('Error fetching tareas:', err);
        throw err;
      }
    },
    enabled: !!cursoId,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  // ====================================
  // FILTRADO DE TAREAS
  // ====================================
  const filteredTareas = useMemo(() => {
    return tareas.filter((tarea: Tarea) => {
      const matchSearch = tarea.titulo?.toLowerCase().includes(searchTerm.toLowerCase()) ?? true;
      const matchTipo = filtroTipo === 'todos' || tarea.tipo === filtroTipo;
      const matchPrioridad = filtroPrioridad === 'todos' || tarea.prioridad === filtroPrioridad;
      const matchEstado = filtroEstado === 'todos' || tarea.estado === filtroEstado;
      return matchSearch && matchTipo && matchPrioridad && matchEstado;
    });
  }, [tareas, searchTerm, filtroTipo, filtroPrioridad, filtroEstado]);

  // ====================================
  // AGRUPACIÓN POR ESTADO
  // ====================================
  const tareasPorEstado = useMemo(() => {
    const agrupadas: Record<EstadoTarea, Tarea[]> = {
      [EstadoTarea.ASIGNADA]: [],
      [EstadoTarea.EN_PROGRESO]: [],
      [EstadoTarea.ENTREGADA]: [],
      [EstadoTarea.CALIFICADA]: [],
      [EstadoTarea.VENCIDA]: [],
      [EstadoTarea.CERRADA]: [],
    };

    filteredTareas.forEach((tarea: Tarea) => {
      const estado = tarea.estado as EstadoTarea;
      if (estado in agrupadas) {
        agrupadas[estado].push(tarea);
      }
    });

    return agrupadas;
  }, [filteredTareas]);

  // ====================================
  // HANDLERS
  // ====================================
  const handleTareaCreada = () => {
    setIsFormOpen(false);
    setTareaAEditar(undefined);
    queryClient.invalidateQueries({ queryKey: ['cursoTareas', cursoId] });
  };

  const handleEditarTarea = (tarea: Tarea) => {
    setTareaAEditar(tarea);
    setTareaSeleccionada(null); // Cerrar preview
    setIsFormOpen(true);
  };

  const handleGuardarTarea = async (formData: Omit<Tarea, 'tarea_id' | 'fecha_creacion'>) => {
    try {
      if (tareaAEditar) {
        // Actualizar tarea existente
        // Usamos el endpoint principal de tareas: PUT /api/tareas/{id}
        await axios.put(`/api/tareas/${tareaAEditar.tarea_id}`, formData);
      } else {
        // Crear nueva tarea
        await axios.post(`/api/cursos/tareas/${cursoId}/tareas`, formData);
      }
      handleTareaCreada();
    } catch (error) {
      console.error('Error saving tarea:', error);
      throw error;
    }
  };

  if (!cursoId) {
    return (
      <div className="flex items-center gap-2 py-8 px-4 bg-red-50 dark:bg-red-900/20 rounded-lg text-red-600 dark:text-red-400">
        <AlertCircle size={20} />
        <span>Error: No se pudo obtener el ID del curso</span>
      </div>
    );
  }

  // ====================================
  // RENDER
  // ====================================
  return (
    <div className="space-y-6">
      {/* ===== BARRA DE FILTROS ===== */}
      <div className="space-y-4">
        {/* Búsqueda */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Buscar tareas por título..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Filtros - Grid responsivo */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Tipo */}
          <select
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value as any)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          >
            <option value="todos">📋 Todos los tipos</option>
            <option value="tarea">✓ Tarea</option>
            <option value="quiz">❓ Quiz</option>
            <option value="proyecto">🎯 Proyecto</option>
          </select>

          {/* Prioridad */}
          <select
            value={filtroPrioridad}
            onChange={(e) => setFiltroPrioridad(e.target.value as any)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          >
            <option value="todos">⭐ Todas prioridades</option>
            <option value="baja">🟢 Baja</option>
            <option value="media">🟡 Media</option>
            <option value="alta">🔴 Alta</option>
          </select>

          {/* Estado */}
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value as any)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          >
            <option value="todos">📊 Todos los estados</option>
            <option value="asignada">🔵 Asignada</option>
            <option value="en_progreso">🟡 En Progreso</option>
            <option value="entregada">🟣 Entregada</option>
            <option value="calificada">🟢 Calificada</option>
            <option value="vencida">🔴 Vencida</option>
            <option value="cerrada">⚫ Cerrada</option>
          </select>

          {/* Botón crear tarea */}
          <button
            onClick={() => {
              setTareaAEditar(undefined);
              setIsFormOpen(true);
            }}
            className="px-4 py-2 bg-primary hover:bg-primary/90 text-white font-semibold rounded-lg transition-colors text-sm whitespace-nowrap"
          >
            + Crear Tarea
          </button>
        </div>
      </div>

      {/* ===== CONTENIDO PRINCIPAL ===== */}
      <div className="flex gap-6">
        {/* Sidebar Estadísticas */}
        <div className="w-80 flex-shrink-0">
          {isLoading ? (
            <div className="animate-pulse space-y-4">
              <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
            </div>
          ) : (
            <TareasStatistics tareas={filteredTareas} tareasPorEstado={tareasPorEstado} />
          )}
        </div>

        {/* Contenido - Acordeón de tareas */}
        <div className="flex-1">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-primary" size={40} />
            </div>
          ) : error ? (
            <div className="flex items-center gap-2 py-8 px-4 bg-red-50 dark:bg-red-900/20 rounded-lg text-red-600 dark:text-red-400">
              <AlertCircle size={20} />
              <span>Error al cargar las tareas</span>
            </div>
          ) : filteredTareas.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <p className="text-lg font-semibold">No hay tareas que coincidan</p>
              <p className="text-sm mt-2">Intenta cambiar los filtros o crea una nueva tarea</p>
            </div>
          ) : (
            <TareasAccordion tareasPorEstado={tareasPorEstado} onSelectTarea={setTareaSeleccionada} />
          )}
        </div>
      </div>

      {/* ===== MODALES ===== */}
      {/* Modal crear tarea - Nuestro hermoso formulario */}
      {isFormOpen && (
        <TareaFormModal
          isOpen={isFormOpen}
          onClose={() => {
            setIsFormOpen(false);
            setTareaAEditar(undefined);
          }}
          onSubmit={handleGuardarTarea}
          grupoId={cursoId}
          tarea={tareaAEditar}
        />
      )}

      {/* Modal preview tarea */}
      {tareaSeleccionada && (
        <TareaPreviewModal
          isOpen={true}
          tarea={tareaSeleccionada}
          onClose={() => setTareaSeleccionada(null)}
          cursoId={cursoId}
          onEdit={handleEditarTarea}
        />
      )}
    </div>
  );
}
