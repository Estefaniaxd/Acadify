import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, AlertCircle, CheckCircle, Clock, Eye } from "lucide-react";

import { Tarea, EstadoTarea } from "../../../modules/tareas/types";
import { TareaCardItem } from "./TareaCardItem";

// ====================================
// TIPOS
// ====================================

interface TareasAccordionProps {
  tareasPorEstado: Record<EstadoTarea, Tarea[]>;
  onSelectTarea: (tarea: Tarea) => void;
}

interface EstadoSección {
  [key: string]: boolean;
}

// ====================================
// MAPEO DE ESTADOS
// ====================================

const estadoConfig: Record<EstadoTarea, {
  label: string;
  color: string;
  bgColor: string;
  icon: React.ReactNode;
  descripcion: string;
}> = {
  [EstadoTarea.ASIGNADA]: {
    label: "Asignadas",
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
    icon: <AlertCircle size={20} />,
    descripcion: "Tareas pendientes de iniciar",
  },
  [EstadoTarea.EN_PROGRESO]: {
    label: "En Progreso",
    color: "text-amber-600 dark:text-amber-400",
    bgColor: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800",
    icon: <Clock size={20} />,
    descripcion: "Tareas que están siendo trabajadas",
  },
  [EstadoTarea.ENTREGADA]: {
    label: "Entregadas",
    color: "text-purple-600 dark:text-purple-400",
    bgColor: "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800",
    icon: <CheckCircle size={20} />,
    descripcion: "Tareas entregadas, pendientes de calificación",
  },
  [EstadoTarea.CALIFICADA]: {
    label: "Calificadas",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800",
    icon: <CheckCircle size={20} />,
    descripcion: "Tareas calificadas y evaluadas",
  },
  [EstadoTarea.VENCIDA]: {
    label: "Vencidas",
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800",
    icon: <AlertCircle size={20} />,
    descripcion: "Tareas que pasaron la fecha límite",
  },
  [EstadoTarea.CERRADA]: {
    label: "Cerradas",
    color: "text-slate-600 dark:text-slate-400",
    bgColor: "bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700",
    icon: <CheckCircle size={20} />,
    descripcion: "Tareas completadas y archivadas",
  },
};

// ====================================
// COMPONENTE PRINCIPAL
// ====================================

export const TareasAccordion: React.FC<TareasAccordionProps> = ({
  tareasPorEstado,
  onSelectTarea,
}) => {
  const [openSecciones, setOpenSecciones] = useState<EstadoSección>({
    asignada: true,
    en_progreso: true,
    entregada: false,
    calificada: false,
    vencida: true,
    cerrada: false,
  });

  const toggleSección = (estado: string) => {
    setOpenSecciones((prev) => ({
      ...prev,
      [estado]: !prev[estado],
    }));
  };

  const renderSección = (estado: EstadoTarea, tareas: Tarea[]) => {
    const config = estadoConfig[estado];
    const isOpen = openSecciones[estado];
    const count = tareas.length;

    return (
      <motion.div
        key={estado}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="mb-4"
      >
        {/* Header de sección */}
        <motion.button
          onClick={() => toggleSección(estado)}
          className={`w-full p-4 rounded-lg border-2 transition-all ${config.bgColor} group`}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={config.color}>{config.icon}</div>
              <div className="text-left">
                <h3 className="font-bold text-slate-900 dark:text-white">
                  {config.label}
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  {config.descripcion}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Badge de conteo */}
              <motion.div
                className={`px-3 py-1 rounded-full font-semibold text-sm ${config.color}`}
              >
                {count}
              </motion.div>

              {/* Chevron icon */}
              <motion.div
                animate={{ rotate: isOpen ? 180 : 0 }}
                transition={{ duration: 0.3 }}
                className={config.color}
              >
                <ChevronDown size={20} />
              </motion.div>
            </div>
          </div>
        </motion.button>

        {/* Contenido - Lista de tareas */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="p-4 space-y-3 bg-white dark:bg-slate-800 rounded-b-lg border-x-2 border-b-2 border-slate-200 dark:border-slate-700">
                {count === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-8"
                  >
                    <p className="text-slate-500 dark:text-slate-400">
                      No hay tareas en esta categoría
                    </p>
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-3"
                  >
                    {tareas.map((tarea, index) => (
                      <motion.div
                        key={tarea.tarea_id || index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <TareaCardItem
                          tarea={tarea}
                          onSelectTarea={onSelectTarea}
                        />
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    );
  };

  return (
    <div className="space-y-2">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          Tareas por Estado
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Organiza y visualiza tus tareas según su estado actual
        </p>
      </motion.div>

      <AnimatePresence>
        {Object.entries(estadoConfig).map(([estado, _]) => {
          const tareas = tareasPorEstado[estado as EstadoTarea] || [];
          return renderSección(estado as EstadoTarea, tareas);
        })}
      </AnimatePresence>
    </div>
  );
};

export default TareasAccordion;
