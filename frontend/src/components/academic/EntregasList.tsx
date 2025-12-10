import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  ChevronDown,
  Filter,
  Search,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Clock,
} from "lucide-react";
import { cn } from "@/utils/cn";
import type { EntregaTarea } from "@/types";

type FilterStatus = "todas" | "pendientes" | "entregadas" | "calificadas";

interface EntregasListProps {
  entregas: EntregaTarea[];
  isLoading: boolean;
  filterStatus: FilterStatus;
  onFilterChange: (status: FilterStatus) => void;
  onSelectEntrega: (entrega: EntregaTarea) => void;
  selectedEntrega: EntregaTarea | null;
}

interface SortConfig {
  key: keyof EntregaTarea;
  direction: "asc" | "desc";
}

/**
 * Component to display list of all submissions for a task.
 * Features:
 * - Filter by status (BORRADOR, ENTREGADA, CALIFICADA, etc)
 * - Search by student name
 * - Sort by multiple columns
 * - Late submission indicators
 * - Grade preview
 * - Bulk actions (future)
 */
export function EntregasList({
  entregas,
  isLoading,
  filterStatus,
  onFilterChange,
  onSelectEntrega,
  selectedEntrega,
}: EntregasListProps) {
  // ========================================================================
  // STATE
  // ========================================================================

  const [searchTerm, setSearchTerm] = useState("");
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    key: "fecha_entrega" as keyof EntregaTarea,
    direction: "desc",
  });
  const [expandedId, setExpandedId] = useState<number | null>(null);

  // ========================================================================
  // FILTERING & SORTING
  // ========================================================================

  const filteredAndSorted = useMemo(() => {
    let filtered = [...entregas];

    // Filter by status
    if (filterStatus !== "todas") {
      filtered = filtered.filter((e) => {
        if (filterStatus === "pendientes") return e.estado === "ENTREGADA";
        if (filterStatus === "entregadas")
          return e.estado === "ENTREGADA" && e.calificacion === null;
        if (filterStatus === "calificadas") return e.estado === "CALIFICADA";
        return true;
      });
    }

    // Filter by search term
    if (searchTerm.trim()) {
      filtered = filtered.filter((e) =>
        e.estudiante?.nombre
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        e.estudiante?.email?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Sort
    filtered.sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];

      if (typeof aVal === "string") {
        return sortConfig.direction === "asc"
          ? (aVal as string).localeCompare(bVal as string)
          : (bVal as string).localeCompare(aVal as string);
      }

      if (typeof aVal === "number") {
        const aNum = aVal || 0;
        const bNum = bVal || 0;
        return sortConfig.direction === "asc" ? aNum - bNum : bNum - aNum;
      }

      if (aVal instanceof Date || typeof aVal === "string") {
        const aDate = new Date(aVal);
        const bDate = new Date(bVal as any);
        return sortConfig.direction === "asc"
          ? aDate.getTime() - bDate.getTime()
          : bDate.getTime() - aDate.getTime();
      }

      return 0;
    });

    return filtered;
  }, [entregas, filterStatus, searchTerm, sortConfig]);

  // ========================================================================
  // STATS
  // ========================================================================

  const stats = useMemo(() => {
    return {
      total: entregas.length,
      entregadas: entregas.filter((e) => e.estado === "ENTREGADA").length,
      calificadas: entregas.filter((e) => e.estado === "CALIFICADA").length,
      tardias: entregas.filter((e) => e.es_tardia).length,
    };
  }, [entregas]);

  // ========================================================================
  // HANDLERS
  // ========================================================================

  const handleSort = (key: keyof EntregaTarea) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  };

  const toggleExpanded = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getStatusBadge = (estado: string, esTardia: boolean) => {
    if (esTardia) {
      return "bg-red-100 text-red-800";
    }
    if (estado === "CALIFICADA") {
      return "bg-green-100 text-green-800";
    }
    if (estado === "ENTREGADA") {
      return "bg-blue-100 text-blue-800";
    }
    return "bg-gray-100 text-gray-800";
  };

  const getStatusIcon = (estado: string, esTardia: boolean) => {
    if (esTardia) return "❌";
    if (estado === "CALIFICADA") return "✅";
    if (estado === "ENTREGADA") return "📝";
    return "📋";
  };

  const getGradeColor = (calificacion: number | null) => {
    if (calificacion === null) return "text-slate-500";
    if (calificacion < 3) return "text-red-600";
    if (calificacion < 3.5) return "text-yellow-600";
    if (calificacion < 4) return "text-blue-600";
    return "text-green-600";
  };

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-md p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-900">
          Todas las Entregas
        </h2>
        <div className="text-sm text-slate-600">
          {filteredAndSorted.length} de {entregas.length}
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        <button
          onClick={() => onFilterChange("todas")}
          className={cn(
            "p-3 rounded-lg text-sm font-medium transition-all cursor-pointer",
            filterStatus === "todas"
              ? "bg-blue-600 text-white"
              : "bg-blue-50 text-blue-700 hover:bg-blue-100"
          )}
        >
          <div className="text-lg font-bold">{stats.total}</div>
          <div className="text-xs">Total</div>
        </button>

        <button
          onClick={() => onFilterChange("pendientes")}
          className={cn(
            "p-3 rounded-lg text-sm font-medium transition-all cursor-pointer",
            filterStatus === "pendientes"
              ? "bg-yellow-600 text-white"
              : "bg-yellow-50 text-yellow-700 hover:bg-yellow-100"
          )}
        >
          <div className="text-lg font-bold">{stats.entregadas}</div>
          <div className="text-xs">Por calificar</div>
        </button>

        <button
          onClick={() => onFilterChange("calificadas")}
          className={cn(
            "p-3 rounded-lg text-sm font-medium transition-all cursor-pointer",
            filterStatus === "calificadas"
              ? "bg-green-600 text-white"
              : "bg-green-50 text-green-700 hover:bg-green-100"
          )}
        >
          <div className="text-lg font-bold">{stats.calificadas}</div>
          <div className="text-xs">Calificadas</div>
        </button>

        <div className="p-3 rounded-lg bg-red-50 text-red-700 text-sm font-medium">
          <div className="text-lg font-bold">{stats.tardias}</div>
          <div className="text-xs">Tardías</div>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="mb-6 flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-2.5 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar por nombre o email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <button className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 flex items-center gap-2 text-sm font-medium text-slate-700">
          <Filter className="w-4 h-4" />
          Filtros
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-slate-400 animate-spin" />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredAndSorted.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          <AlertCircle className="w-8 h-8 mx-auto mb-2 text-slate-400" />
          <p>No hay entregas que coincidan con los filtros</p>
        </div>
      )}

      {/* Entregas List */}
      {!isLoading && filteredAndSorted.length > 0 && (
        <div className="space-y-3 overflow-x-auto">
          {/* Table Header */}
          <div className="hidden lg:grid grid-cols-12 gap-4 px-4 py-3 bg-slate-50 rounded-lg font-semibold text-sm text-slate-700 sticky top-0">
            <button
              onClick={() => handleSort("estudiante" as any)}
              className="col-span-3 text-left hover:text-slate-900 flex items-center gap-1"
            >
              Estudiante
              <ChevronDown className="w-3 h-3" />
            </button>
            <button
              onClick={() => handleSort("fecha_entrega" as any)}
              className="col-span-2 text-left hover:text-slate-900 flex items-center gap-1"
            >
              Fecha
              <ChevronDown className="w-3 h-3" />
            </button>
            <button
              onClick={() => handleSort("numero_intento" as any)}
              className="col-span-1 text-center hover:text-slate-900 flex items-center justify-center gap-1"
            >
              Intento
              <ChevronDown className="w-3 h-3" />
            </button>
            <button
              onClick={() => handleSort("estado" as any)}
              className="col-span-2 text-left hover:text-slate-900 flex items-center gap-1"
            >
              Estado
              <ChevronDown className="w-3 h-3" />
            </button>
            <button
              onClick={() => handleSort("calificacion" as any)}
              className="col-span-2 text-center hover:text-slate-900 flex items-center justify-center gap-1"
            >
              Calificación
              <ChevronDown className="w-3 h-3" />
            </button>
            <button
              onClick={() => handleSort("puntos_otorgados" as any)}
              className="col-span-2 text-center hover:text-slate-900 flex items-center justify-center gap-1"
            >
              Puntos
              <ChevronDown className="w-3 h-3" />
            </button>
          </div>

          {/* Entrega Rows */}
          {filteredAndSorted.map((entrega) => (
            <motion.div
              key={entrega.entrega_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {/* Desktop Row */}
              <div
                className="hidden lg:grid grid-cols-12 gap-4 p-4 border border-slate-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors"
                onClick={() => {
                  onSelectEntrega(entrega);
                }}
              >
                <div className="col-span-3">
                  <p className="font-medium text-slate-900">
                    {entrega.estudiante?.nombre}
                  </p>
                  <p className="text-xs text-slate-500">
                    {entrega.estudiante?.email}
                  </p>
                </div>

                <div className="col-span-2 text-sm text-slate-700">
                  {new Date(entrega.fecha_entrega).toLocaleDateString("es-ES")}
                </div>

                <div className="col-span-1 text-center text-sm text-slate-700">
                  {entrega.numero_intento}
                </div>

                <div className="col-span-2">
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold",
                      getStatusBadge(entrega.estado, entrega.es_tardia)
                    )}
                  >
                    {getStatusIcon(entrega.estado, entrega.es_tardia)}{" "}
                    {entrega.es_tardia ? "Tardía" : entrega.estado}
                  </span>
                </div>

                <div className={cn("col-span-2 text-center font-bold text-lg", getGradeColor(entrega.calificacion))}>
                  {entrega.calificacion?.toFixed(1) || "—"}
                </div>

                <div className="col-span-2 text-center text-sm text-slate-700">
                  {entrega.puntos_otorgados || "—"}
                </div>
              </div>

              {/* Mobile Card */}
              <div
                className="lg:hidden border border-slate-200 rounded-lg overflow-hidden"
                onClick={() => toggleExpanded(entrega.entrega_id)}
              >
                <div className="p-4 hover:bg-slate-50 cursor-pointer flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-slate-900">
                      {entrega.estudiante?.nombre}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={cn(
                          "inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold",
                          getStatusBadge(entrega.estado, entrega.es_tardia)
                        )}
                      >
                        {getStatusIcon(entrega.estado, entrega.es_tardia)}
                        {entrega.es_tardia ? "Tardía" : entrega.estado}
                      </span>
                      <span
                        className={cn(
                          "text-sm font-bold",
                          getGradeColor(entrega.calificacion)
                        )}
                      >
                        {entrega.calificacion?.toFixed(1) || "—"}
                      </span>
                    </div>
                  </div>
                  <motion.div
                    animate={{
                      rotate: expandedId === entrega.entrega_id ? 180 : 0,
                    }}
                  >
                    <ChevronDown className="w-5 h-5 text-slate-600" />
                  </motion.div>
                </div>

                {/* Expanded Details */}
                {expandedId === entrega.entrega_id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="border-t border-slate-200 p-4 bg-slate-50 text-sm text-slate-700 space-y-2"
                  >
                    <div>
                      <span className="font-semibold">Email:</span> {entrega.estudiante?.email}
                    </div>
                    <div>
                      <span className="font-semibold">Fecha:</span>{" "}
                      {new Date(entrega.fecha_entrega).toLocaleDateString("es-ES")}
                    </div>
                    <div>
                      <span className="font-semibold">Intento:</span> {entrega.numero_intento}
                    </div>
                    <div>
                      <span className="font-semibold">Puntos:</span>{" "}
                      {entrega.puntos_otorgados || "—"}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectEntrega(entrega);
                      }}
                      className="w-full mt-3 px-3 py-2 bg-blue-600 text-white rounded font-medium text-sm hover:bg-blue-700"
                    >
                      Calificar
                    </button>
                  </motion.div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
