import React from "react";
import { motion } from "framer-motion";
import { Eye, Calendar, AlertCircle, Star, Zap } from "lucide-react";
import { Tarea, PrioridadTarea } from "../../../modules/tareas/types";

// ====================================
// TIPOS
// ====================================

interface TareaCardItemProps {
  tarea: Tarea;
  onSelectTarea: (tarea: Tarea) => void;
}

// ====================================
// MAPEO DE PRIORIDADES
// ====================================

const prioridadConfig: Record<PrioridadTarea, {
  label: string;
  color: string;
  bgColor: string;
  icon: React.ReactNode;
}> = {
  [PrioridadTarea.BAJA]: {
    label: "Baja",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    icon: <AlertCircle size={14} />,
  },
  [PrioridadTarea.MEDIA]: {
    label: "Media",
    color: "text-amber-600 dark:text-amber-400",
    bgColor: "bg-amber-100 dark:bg-amber-900/30",
    icon: <Zap size={14} />,
  },
  [PrioridadTarea.ALTA]: {
    label: "Alta",
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    icon: <AlertCircle size={14} />,
  },
};

// Mapeo de tipos de tarea con emojis
const tipoTareaEmoji: Record<string, string> = {
  ensayo: "📝",
  proyecto: "🎯",
  ejercicios: "💪",
  investigacion: "🔍",
  presentacion: "🎤",
  laboratorio: "🧪",
  lectura: "📚",
  examen: "✏️",
  otro: "📋",
};

// ====================================
// FUNCIONES AUXILIARES
// ====================================

/**
 * Calcula los días restantes hasta la fecha límite
 */
const calcularDiasRestantes = (fechaLimite: string): number => {
  const hoy = new Date();
  const fecha = new Date(fechaLimite);
  const diferencia = fecha.getTime() - hoy.getTime();
  return Math.ceil(diferencia / (1000 * 3600 * 24));
};

/**
 * Determina si la tarea está próxima a vencer
 */
const estaDesesperada = (fechaLimite: string): boolean => {
  return calcularDiasRestantes(fechaLimite) <= 2;
};

/**
 * Formatea la fecha para mostrar
 */
const formatearFecha = (fecha: string): string => {
  const date = new Date(fecha);
  const hoy = new Date();
  const mañana = new Date(hoy);
  mañana.setDate(mañana.getDate() + 1);

  if (date.toDateString() === hoy.toDateString()) {
    return "Hoy";
  } else if (date.toDateString() === mañana.toDateString()) {
    return "Mañana";
  } else {
    return date.toLocaleDateString("es-ES", {
      day: "numeric",
      month: "short",
    });
  }
};

// ====================================
// COMPONENTE
// ====================================

export const TareaCardItem: React.FC<TareaCardItemProps> = ({
  tarea,
  onSelectTarea,
}) => {
  const diasRestantes = calcularDiasRestantes(tarea.fecha_limite);
  const isDesesperada = estaDesesperada(tarea.fecha_limite);
  const prioridad = tarea.prioridad as PrioridadTarea;
  const prioridadInfo = prioridadConfig[prioridad];
  const tipoEmoji = tipoTareaEmoji[tarea.tipo.toLowerCase()] || "📋";

  return (
    <motion.div
      onClick={() => onSelectTarea(tarea)}
      className={`p-3 rounded-lg border-2 cursor-pointer transition-all group ${
        isDesesperada
          ? "border-red-300 dark:border-red-700 bg-red-50/50 dark:bg-red-900/10 hover:bg-red-100/50 dark:hover:bg-red-900/20"
          : "border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/30 hover:border-blue-300 dark:hover:border-blue-600 hover:bg-blue-50/30 dark:hover:bg-blue-900/10"
      }`}
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="flex items-start justify-between mb-2">
        {/* Título + Tipo */}
        <div className="flex-1 min-w-0 pr-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{tipoEmoji}</span>
            <h4 className="font-semibold text-slate-900 dark:text-white truncate">
              {tarea.titulo}
            </h4>
          </div>

          {/* Descripción breve */}
          {tarea.descripcion && (
            <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2">
              {tarea.descripcion}
            </p>
          )}
        </div>

        {/* Badge de prioridad */}
        <motion.div
          className={`px-2 py-1 rounded-full text-xs font-semibold flex items-center gap-1 whitespace-nowrap ${prioridadInfo.bgColor} ${prioridadInfo.color}`}
          whileHover={{ scale: 1.1 }}
        >
          {prioridadInfo.icon}
          {prioridadInfo.label}
        </motion.div>
      </div>

      {/* Información de fecha y puntos */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          {/* Fecha límite */}
          <div className={`flex items-center gap-1 ${isDesesperada ? "text-red-600 dark:text-red-400" : "text-slate-600 dark:text-slate-400"}`}>
            <Calendar size={14} />
            <span>{formatearFecha(tarea.fecha_limite)}</span>
            {diasRestantes >= 0 && (
              <span className="font-semibold">
                ({diasRestantes} {diasRestantes === 1 ? "día" : "días"})
              </span>
            )}
            {diasRestantes < 0 && (
              <span className="font-semibold text-red-600 dark:text-red-400">
                Vencida
              </span>
            )}
          </div>

          {/* Separador */}
          <span className="text-slate-300 dark:text-slate-600">•</span>

          {/* Puntos */}
          {tarea.puntuacion_maxima && (
            <div className="flex items-center gap-1 text-slate-600 dark:text-slate-400">
              <Star size={14} />
              <span>{tarea.puntuacion_maxima} pts</span>
            </div>
          )}
        </div>

        {/* Botón de vista previa */}
        <motion.button
          onClick={(e) => {
            e.stopPropagation();
            onSelectTarea(tarea);
          }}
          className="p-1 rounded-md opacity-0 group-hover:opacity-100 transition-opacity bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          title="Ver detalles"
        >
          <Eye size={14} />
        </motion.button>
      </div>

      {/* Indicador visual de urgencia */}
      {isDesesperada && (
        <motion.div
          animate={{ opacity: [1, 0.6, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute -right-1 -top-1 w-2 h-2 bg-red-600 rounded-full"
        />
      )}
    </motion.div>
  );
};

export default TareaCardItem;
