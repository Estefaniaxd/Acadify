import React, { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, Plus, Search, Filter, TrendingUp, FileDown, Loader2 } from "lucide-react";
import { apiClientTareas } from "../../../modules/tareas/api";

import { TareasApi } from "../../../modules/tareas";
import {
  Tarea,
  TareaEnriquecida,
  TipoTarea,
  PrioridadTarea,
  EstadoTarea,
} from "../../../modules/tareas/types";

// Componentes locales
import { TareasAccordion } from "./components/TareasAccordion";
import { TareasStatistics } from "./components/TareasStatistics";
import { TareaFormModal } from "./components/TareaFormModal";
import { TareaPreviewModal } from "./components/TareaPreviewModal";

// ====================================
// TIPOS LOCALES
// ====================================

interface TareasPageState {
  showCreateModal: boolean;
  showPreviewModal: boolean;
  selectedTarea: Tarea | null;
  searchTerm: string;
  filterType: TipoTarea | "all";
  filterPriority: PrioridadTarea | "all";
  filterStatus: EstadoTarea | "all";
  showExpired: boolean;
  isExporting: boolean;
}

// ====================================
// PÁGINA PRINCIPAL DE TAREAS
// ====================================

export const TareasPage: React.FC = () => {
  const { cursoId, grupoId } = useParams<{
    cursoId?: string;
    grupoId?: string;
  }>();
  const navigate = useNavigate();

  // Estados locales
  const [state, setState] = useState<TareasPageState>({
    showCreateModal: false,
    showPreviewModal: false,
    selectedTarea: null,
    searchTerm: "",
    filterType: "all",
    filterPriority: "all",
    filterStatus: "all",
    showExpired: false,
    isExporting: false,
  });

  // ====================================
  // QUERIES
  // ====================================

  const { data: tareas = [], isLoading, error, refetch } = useQuery({
    queryKey: ["tareas", grupoId, state.showExpired],
    queryFn: async () => {
      if (!grupoId) return [];
      // Pasamos incluir_vencidas según el estado
      const response = await TareasApi.obtenerTareasPorGrupo(grupoId, {
        incluir_vencidas: state.showExpired
      });
      return response.data || [];
    },
    enabled: !!grupoId,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // ====================================
  // FILTRADO Y BÚSQUEDA
  // ====================================

  const filteredTareas = useMemo(() => {
    return tareas.filter((tarea: Tarea) => {
      // Búsqueda por título
      if (
        state.searchTerm &&
        !tarea.titulo.toLowerCase().includes(state.searchTerm.toLowerCase())
      ) {
        return false;
      }

      // Filtro por tipo
      if (state.filterType !== "all" && tarea.tipo !== state.filterType) {
        return false;
      }

      // Filtro por prioridad
      if (
        state.filterPriority !== "all" &&
        tarea.prioridad !== state.filterPriority
      ) {
        return false;
      }

      // Filtro por estado
      if (state.filterStatus !== "all" && tarea.estado !== state.filterStatus) {
        return false;
      }

      return true;
    });
  }, [tareas, state.searchTerm, state.filterType, state.filterPriority, state.filterStatus]);

  // ====================================
  // AGRUPAR TAREAS POR ESTADO
  // ====================================

  const tareasPorEstado = useMemo(() => {
    const grouped: Record<EstadoTarea, Tarea[]> = {
      [EstadoTarea.ASIGNADA]: [],
      [EstadoTarea.EN_PROGRESO]: [],
      [EstadoTarea.ENTREGADA]: [],
      [EstadoTarea.CALIFICADA]: [],
      [EstadoTarea.VENCIDA]: [],
      [EstadoTarea.CERRADA]: [],
    };

    filteredTareas.forEach((tarea: Tarea) => {
      grouped[tarea.estado as EstadoTarea]?.push(tarea);
    });

    return grouped;
  }, [filteredTareas]);

  // ====================================
  // HANDLERS
  // ====================================

  const handleCreateTarea = async (
    formData: Omit<Tarea, "tarea_id" | "fecha_creacion">
  ) => {
    try {
      if (!grupoId) throw new Error("Grupo no especificado");

      await TareasApi.crearTarea(grupoId, formData as any);

      // Cerrar modal
      setState((prev) => ({
        ...prev,
        showCreateModal: false,
      }));

      // Refrescar tareas
      refetch();

      // Mostrar notificación de éxito (si tienes toast notifications)
    } catch (error) {
      console.error("Error al crear tarea:", error);
      // Mostrar error (si tienes toast notifications)
    }
  };

  const handlePreviewTarea = (tarea: Tarea) => {
    setState((prev) => ({
      ...prev,
      selectedTarea: tarea,
      showPreviewModal: true,
    }));
  };

  const handleClosePreviewModal = () => {
    setState((prev) => ({
      ...prev,
      showPreviewModal: false,
      selectedTarea: null,
    }));
  };

  const handleCloseCreateModal = () => {
    setState((prev) => ({
      ...prev,
      showCreateModal: false,
    }));
  };

  // Handler para exportar reporte CSV
  const handleExportCSV = async () => {
    if (!cursoId && !grupoId) {
      alert("No se puede exportar: ID de curso no disponible");
      return;
    }

    setState((prev) => ({ ...prev, isExporting: true }));

    try {
      const exportId = cursoId || grupoId || "";
      const blob = await apiClientTareas.exportarReporteCurso(exportId);

      // Crear URL y descargar
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const timestamp = new Date().toISOString().slice(0, 10);
      link.download = `reporte_curso_${exportId}_${timestamp}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      alert("✅ Reporte descargado exitosamente");
    } catch (error) {
      console.error("Error exportando reporte:", error);
      alert("❌ Error al exportar el reporte. Por favor intente nuevamente.");
    } finally {
      setState((prev) => ({ ...prev, isExporting: false }));
    }
  };

  // ====================================
  // RENDER
  // ====================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">
                Tareas
              </h1>
              <p className="text-slate-600 dark:text-slate-400">
                Gestiona y realiza un seguimiento de todas las tareas del curso
              </p>
            </div>

            {/* Botones de acción */}
            <div className="flex items-center gap-3">
              {/* Botón exportar CSV */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleExportCSV}
                disabled={state.isExporting}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white rounded-lg font-semibold transition-colors shadow-lg"
              >
                {state.isExporting ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <FileDown size={20} />
                )}
                {state.isExporting ? "Exportando..." : "Exportar CSV"}
              </motion.button>

              {/* Botón crear tarea */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() =>
                  setState((prev) => ({
                    ...prev,
                    showCreateModal: true,
                  }))
                }
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors shadow-lg"
              >
                <Plus size={20} />
                Nueva Tarea
              </motion.button>
            </div>
          </div>

          {/* Barra de búsqueda y filtros */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Búsqueda */}
            <div className="relative col-span-1 md:col-span-2">
              <Search
                size={20}
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400"
              />
              <input
                type="text"
                placeholder="Buscar tareas..."
                value={state.searchTerm}
                onChange={(e) =>
                  setState((prev) => ({
                    ...prev,
                    searchTerm: e.target.value,
                  }))
                }
                className="w-full pl-10 pr-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Filtro tipo */}
            <select
              value={state.filterType}
              onChange={(e) =>
                setState((prev) => ({
                  ...prev,
                  filterType: e.target.value as TipoTarea | "all",
                }))
              }
              className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Todos los tipos</option>
              <option value="ensayo">Ensayo</option>
              <option value="proyecto">Proyecto</option>
              <option value="ejercicios">Ejercicios</option>
              <option value="investigacion">Investigación</option>
              <option value="presentacion">Presentación</option>
              <option value="laboratorio">Laboratorio</option>
              <option value="lectura">Lectura</option>
              <option value="examen">Examen</option>
              <option value="otro">Otro</option>
            </select>

            {/* Filtro prioridad */}
            <select
              value={state.filterPriority}
              onChange={(e) =>
                setState((prev) => ({
                  ...prev,
                  filterPriority: e.target.value as PrioridadTarea | "all",
                }))
              }
              className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Todas las prioridades</option>
              <option value="baja">Baja</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
            </select>

            {/* Toggle Mostrar Vencidas */}
            <div className="flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800">
              <input
                type="checkbox"
                id="showExpired"
                checked={state.showExpired}
                onChange={(e) =>
                  setState((prev) => ({
                    ...prev,
                    showExpired: e.target.checked,
                  }))
                }
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <label htmlFor="showExpired" className="text-sm font-medium text-gray-900 dark:text-gray-300 cursor-pointer select-none">
                Mostrar vencidas
              </label>
            </div>
          </div>
        </motion.div>

        {/* Contenido principal */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600" />
          </div>
        ) : error ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3"
          >
            <AlertCircle className="text-red-600 dark:text-red-400" size={24} />
            <div>
              <p className="font-semibold text-red-900 dark:text-red-200">
                Error al cargar tareas
              </p>
              <p className="text-sm text-red-700 dark:text-red-300">
                {error instanceof Error ? error.message : "Error desconocido"}
              </p>
            </div>
          </motion.div>
        ) : filteredTareas.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 rounded-lg p-12 text-center"
          >
            <div className="text-6xl mb-4">📋</div>
            <p className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              No hay tareas disponibles
            </p>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              Las tareas aparecerán aquí cuando se asignen nuevas
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() =>
                setState((prev) => ({
                  ...prev,
                  showCreateModal: true,
                }))
              }
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
            >
              Crear primera tarea
            </motion.button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Panel de estadísticas (sidebar) */}
            <div className="lg:col-span-1">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <TareasStatistics
                  tareas={filteredTareas}
                  tareasPorEstado={tareasPorEstado}
                />
              </motion.div>
            </div>

            {/* Panel de tareas con accordion (main content) */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <TareasAccordion
                  tareasPorEstado={tareasPorEstado}
                  onSelectTarea={handlePreviewTarea}
                />
              </motion.div>
            </div>
          </div>
        )}
      </div>

      {/* Modales */}
      <AnimatePresence>
        {state.showCreateModal && (
          <TareaFormModal
            isOpen={state.showCreateModal}
            onClose={handleCloseCreateModal}
            onSubmit={handleCreateTarea}
            grupoId={grupoId}
          />
        )}

        {state.showPreviewModal && state.selectedTarea && (
          <TareaPreviewModal
            isOpen={state.showPreviewModal}
            onClose={handleClosePreviewModal}
            tarea={state.selectedTarea}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default TareasPage;
