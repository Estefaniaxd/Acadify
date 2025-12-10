import React, { useMemo } from "react";
import { motion } from "framer-motion";
import {
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
} from "lucide-react";

import { Tarea, EstadoTarea } from "../../../modules/tareas/types";

// ====================================
// TIPOS
// ====================================

interface TareasStatisticsProps {
  tareas: Tarea[];
  tareasPorEstado: Record<EstadoTarea, Tarea[]>;
}

interface StatCard {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

// ====================================
// COMPONENTE
// ====================================

export const TareasStatistics: React.FC<TareasStatisticsProps> = ({
  tareas,
  tareasPorEstado,
}) => {
  // ====================================
  // CÁLCULOS DE ESTADÍSTICAS
  // ====================================

  const estadisticas = useMemo(() => {
    const total = tareas.length;
    const asignadas = tareasPorEstado[EstadoTarea.ASIGNADA]?.length || 0;
    const enProgreso = tareasPorEstado[EstadoTarea.EN_PROGRESO]?.length || 0;
    const entregadas = tareasPorEstado[EstadoTarea.ENTREGADA]?.length || 0;
    const calificadas = tareasPorEstado[EstadoTarea.CALIFICADA]?.length || 0;
    const vencidas = tareasPorEstado[EstadoTarea.VENCIDA]?.length || 0;
    const cerradas = tareasPorEstado[EstadoTarea.CERRADA]?.length || 0;

    // Porcentaje de completitud
    const completadas = calificadas + cerradas;
    const porcentajeCompletitud =
      total > 0 ? Math.round((completadas / total) * 100) : 0;

    // Promedio de puntos
    const promedioPuntos =
      total > 0
        ? Math.round(
            tareas.reduce((sum, t) => sum + (t.puntuacion_maxima || 0), 0) /
              total
          )
        : 0;

    // Tareas urgentes (próximas a vencer en menos de 48 horas)
    const hoy = new Date();
    const mañana48 = new Date(hoy);
    mañana48.setDate(mañana48.getDate() + 2);

    const urgentes = tareas.filter((t) => {
      const fechaLimite = new Date(t.fecha_limite);
      return fechaLimite <= mañana48 && fechaLimite > hoy;
    }).length;

    return {
      total,
      asignadas,
      enProgreso,
      entregadas,
      calificadas,
      vencidas,
      cerradas,
      completadas,
      porcentajeCompletitud,
      promedioPuntos,
      urgentes,
    };
  }, [tareas, tareasPorEstado]);

  // ====================================
  // TARJETAS DE ESTADÍSTICAS
  // ====================================

  const statCards: StatCard[] = [
    {
      label: "Total",
      value: estadisticas.total,
      icon: <BarChart3 size={24} />,
      color: "text-blue-600 dark:text-blue-400",
      bgColor: "bg-blue-100 dark:bg-blue-900/30",
    },
    {
      label: "Completadas",
      value: estadisticas.completadas,
      icon: <CheckCircle size={24} />,
      color: "text-green-600 dark:text-green-400",
      bgColor: "bg-green-100 dark:bg-green-900/30",
    },
    {
      label: "En Progreso",
      value: estadisticas.enProgreso,
      icon: <Clock size={24} />,
      color: "text-amber-600 dark:text-amber-400",
      bgColor: "bg-amber-100 dark:bg-amber-900/30",
    },
    {
      label: "Urgentes",
      value: estadisticas.urgentes,
      icon: <AlertCircle size={24} />,
      color: "text-red-600 dark:text-red-400",
      bgColor: "bg-red-100 dark:bg-red-900/30",
    },
  ];

  // ====================================
  // RENDER
  // ====================================

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-4"
    >
      {/* Título */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
          Estadísticas
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Resumen general de tareas
        </p>
      </div>

      {/* Grid de estadísticas */}
      <div className="grid grid-cols-2 gap-3">
        {statCards.map((card, index) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className={`p-4 rounded-lg border-2 border-slate-200 dark:border-slate-700 ${card.bgColor} hover:border-blue-300 dark:hover:border-blue-600 transition-colors`}
          >
            <div className={`flex items-center gap-2 mb-2 ${card.color}`}>
              {card.icon}
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">
              {card.value}
            </div>
            <div className="text-xs text-slate-600 dark:text-slate-400">
              {card.label}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Barra de progreso */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-white dark:bg-slate-800 rounded-lg p-4 border-2 border-slate-200 dark:border-slate-700"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Zap size={18} className="text-amber-600 dark:text-amber-400" />
            <span className="font-semibold text-slate-900 dark:text-white">
              Progreso General
            </span>
          </div>
          <span className="text-lg font-bold text-amber-600 dark:text-amber-400">
            {estadisticas.porcentajeCompletitud}%
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${estadisticas.porcentajeCompletitud}%` }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="h-full bg-gradient-to-r from-amber-500 to-amber-600"
          />
        </div>

        <div className="mt-2 text-xs text-slate-600 dark:text-slate-400">
          {estadisticas.completadas} de {estadisticas.total} completadas
        </div>
      </motion.div>

      {/* Puntos promedio */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg p-4 border-2 border-indigo-200 dark:border-indigo-700"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">
              Puntos Promedio
            </p>
            <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
              {estadisticas.promedioPuntos}
            </p>
          </div>
          <div className="text-4xl">⭐</div>
        </div>
      </motion.div>

      {/* Desglose por estado */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="bg-white dark:bg-slate-800 rounded-lg p-4 border-2 border-slate-200 dark:border-slate-700 space-y-2"
      >
        <p className="font-semibold text-slate-900 dark:text-white text-sm mb-3">
          Desglose por Estado
        </p>

        {[
          {
            label: "Asignadas",
            value: estadisticas.asignadas,
            color: "bg-blue-500",
          },
          {
            label: "En Progreso",
            value: estadisticas.enProgreso,
            color: "bg-amber-500",
          },
          {
            label: "Entregadas",
            value: estadisticas.entregadas,
            color: "bg-purple-500",
          },
          {
            label: "Calificadas",
            value: estadisticas.calificadas,
            color: "bg-green-500",
          },
          {
            label: "Vencidas",
            value: estadisticas.vencidas,
            color: "bg-red-500",
          },
          {
            label: "Cerradas",
            value: estadisticas.cerradas,
            color: "bg-slate-500",
          },
        ].map((item) => (
          <div key={item.label} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${item.color}`} />
              <span className="text-xs text-slate-600 dark:text-slate-400">
                {item.label}
              </span>
            </div>
            <span className="font-semibold text-slate-900 dark:text-white">
              {item.value}
            </span>
          </div>
        ))}
      </motion.div>
    </motion.div>
  );
};

export default TareasStatistics;
