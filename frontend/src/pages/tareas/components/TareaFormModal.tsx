import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, AlertCircle } from "lucide-react";

import { Tarea, TipoTarea, PrioridadTarea, EstadoTarea } from "../../../modules/tareas/types";

// ====================================
// TIPOS
// ====================================

interface TareaFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: Omit<Tarea, "tarea_id" | "fecha_creacion">) => Promise<void>;
  grupoId?: string;
  tarea?: Tarea;
}

interface FormErrors {
  [key: string]: string;
}

// ====================================
// COMPONENTE
// ====================================

export const TareaFormModal: React.FC<TareaFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  grupoId,
  tarea,
}) => {
  // Helper para fecha segura
  const getSafeDate = (dateStr?: string) => {
    if (!dateStr) return "";
    try {
      return new Date(dateStr).toISOString().slice(0, 16);
    } catch (e) {
      return "";
    }
  };

  // Estados del formulario
  const [formData, setFormData] = useState({
    titulo: tarea?.titulo || "",
    descripcion: tarea?.descripcion || "",
    fecha_limite: getSafeDate(tarea?.fecha_limite),
    puntuacion_maxima: tarea?.puntuacion_maxima || 100,
    tipo: (tarea?.tipo || "ejercicios") as TipoTarea,
    prioridad: (tarea?.prioridad || "media") as PrioridadTarea,
    instrucciones: tarea?.instrucciones || "",
    permite_entrega_tardia: tarea?.permite_entrega_tardia || false,
    habilitar_retroalimentacion_ia: tarea?.habilitar_retroalimentacion_ia || false,
  });

  // Actualizar form cuando cambia la tarea
  React.useEffect(() => {
    if (tarea) {
      setFormData({
        titulo: tarea.titulo || "",
        descripcion: tarea.descripcion || "",
        fecha_limite: getSafeDate(tarea.fecha_limite),
        puntuacion_maxima: tarea.puntuacion_maxima || 100,
        tipo: (tarea.tipo || "ejercicios") as TipoTarea,
        prioridad: (tarea.prioridad || "media") as PrioridadTarea,
        instrucciones: tarea.instrucciones || "",
        permite_entrega_tardia: tarea.permite_entrega_tardia || false,
        habilitar_retroalimentacion_ia: tarea.habilitar_retroalimentacion_ia || false,
      });
    } else {
      // Reset si no hay tarea (modo crear)
      setFormData({
        titulo: "",
        descripcion: "",
        fecha_limite: "",
        puntuacion_maxima: 100,
        tipo: "ejercicios" as TipoTarea,
        prioridad: "media" as PrioridadTarea,
        instrucciones: "",
        permite_entrega_tardia: false,
        habilitar_retroalimentacion_ia: false,
      });
    }
  }, [tarea]);

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ====================================
  // VALIDACIÓN
  // ====================================

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.titulo.trim()) {
      newErrors.titulo = "El título es requerido";
    } else if (formData.titulo.length < 3) {
      newErrors.titulo = "El título debe tener al menos 3 caracteres";
    } else if (formData.titulo.length > 200) {
      newErrors.titulo = "El título no debe exceder 200 caracteres";
    }

    if (!formData.fecha_limite) {
      newErrors.fecha_limite = "La fecha límite es requerida";
    } else {
      const fechaLimite = new Date(formData.fecha_limite);
      const hoy = new Date();
      if (fechaLimite < hoy) {
        newErrors.fecha_limite = "La fecha límite debe ser en el futuro";
      }
    }

    if (formData.puntuacion_maxima < 1 || formData.puntuacion_maxima > 1000) {
      newErrors.puntuacion_maxima = "Los puntos deben estar entre 1 y 1000";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ====================================
  // HANDLERS
  // ====================================

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;

    if (type === "checkbox") {
      const target = e.target as HTMLInputElement;
      setFormData((prev) => ({
        ...prev,
        [name]: target.checked,
      }));
    } else if (type === "number") {
      setFormData((prev) => ({
        ...prev,
        [name]: parseInt(value) || 0,
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }

    // Limpiar error del campo
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const submitData: Omit<Tarea, "tarea_id" | "fecha_creacion"> = {
        grupo_id: grupoId || "",
        docente_id: "", // Se obtiene del contexto auth
        titulo: formData.titulo,
        descripcion: formData.descripcion,
        instrucciones: formData.instrucciones,
        fecha_limite: new Date(formData.fecha_limite).toISOString(),
        fecha_asignacion: new Date().toISOString(),
        puntuacion_maxima: formData.puntuacion_maxima,
        tipo: formData.tipo,
        prioridad: formData.prioridad,
        permite_entrega_tardia: formData.permite_entrega_tardia,
        permite_entregas_tardias: formData.permite_entrega_tardia,
        penalizacion_tardia: 10,
        intentos_maximos: 3,
        tamano_maximo_mb: 50,
        peso_evaluacion: 0,
        habilitar_retroalimentacion_ia: formData.habilitar_retroalimentacion_ia,
        estado: "asignada" as EstadoTarea,
        visible_estudiantes: true,
        requiere_confirmacion_lectura: true,
        puntos_base: formData.puntuacion_maxima,
      };

      await onSubmit(submitData);
      onClose();
    } catch (error) {
      console.error("Error al crear tarea:", error);
      setErrors({
        submit: error instanceof Error ? error.message : "Error al crear tarea",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // ====================================
  // RENDER
  // ====================================

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="sticky top-0 flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                    {tarea ? "Editar Tarea" : "Crear Nueva Tarea"}
                  </h2>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    {tarea ? "Modifica los campos de la tarea" : "Completa los campos para crear una nueva tarea"}
                  </p>
                </div>

                <button
                  onClick={onClose}
                  disabled={isSubmitting}
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
                >
                  <X size={24} className="text-slate-600 dark:text-slate-400" />
                </button>
              </div>

              {/* Contenido */}
              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                {/* Error general */}
                {errors.submit && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3"
                  >
                    <AlertCircle className="text-red-600 dark:text-red-400" />
                    <span className="text-sm text-red-800 dark:text-red-200">
                      {errors.submit}
                    </span>
                  </motion.div>
                )}

                {/* Título */}
                <div>
                  <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                    Título *
                  </label>
                  <input
                    type="text"
                    name="titulo"
                    value={formData.titulo}
                    onChange={handleChange}
                    placeholder="Ej: Tarea de Álgebra Lineal"
                    className={`w-full px-4 py-2 rounded-lg border-2 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.titulo
                      ? "border-red-500 dark:border-red-600"
                      : "border-slate-200 dark:border-slate-600"
                      }`}
                    disabled={isSubmitting}
                  />
                  {errors.titulo && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                      {errors.titulo}
                    </p>
                  )}
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                    Descripción
                  </label>
                  <textarea
                    name="descripcion"
                    value={formData.descripcion}
                    onChange={handleChange}
                    placeholder="Describe brevemente la tarea..."
                    rows={3}
                    className="w-full px-4 py-2 rounded-lg border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors resize-none"
                    disabled={isSubmitting}
                  />
                </div>

                {/* Instrucciones */}
                <div>
                  <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                    Instrucciones
                  </label>
                  <textarea
                    name="instrucciones"
                    value={formData.instrucciones}
                    onChange={handleChange}
                    placeholder="Instrucciones detalladas para los estudiantes..."
                    rows={3}
                    className="w-full px-4 py-2 rounded-lg border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors resize-none"
                    disabled={isSubmitting}
                  />
                </div>

                {/* Grid 2 columnas */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Fecha límite */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                      Fecha Límite *
                    </label>
                    <input
                      type="datetime-local"
                      name="fecha_limite"
                      value={formData.fecha_limite}
                      onChange={handleChange}
                      className={`w-full px-4 py-2 rounded-lg border-2 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.fecha_limite
                        ? "border-red-500 dark:border-red-600"
                        : "border-slate-200 dark:border-slate-600"
                        }`}
                      disabled={isSubmitting}
                    />
                    {errors.fecha_limite && (
                      <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                        {errors.fecha_limite}
                      </p>
                    )}
                  </div>

                  {/* Puntuación máxima */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                      Puntuación Máxima (1-1000) *
                    </label>
                    <input
                      type="number"
                      name="puntuacion_maxima"
                      value={formData.puntuacion_maxima}
                      onChange={handleChange}
                      min="1"
                      max="1000"
                      className={`w-full px-4 py-2 rounded-lg border-2 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.puntuacion_maxima
                        ? "border-red-500 dark:border-red-600"
                        : "border-slate-200 dark:border-slate-600"
                        }`}
                      disabled={isSubmitting}
                    />
                    {errors.puntuacion_maxima && (
                      <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                        {errors.puntuacion_maxima}
                      </p>
                    )}
                  </div>
                </div>

                {/* Grid 2 columnas - Tipo y Prioridad */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Tipo */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                      Tipo de Tarea *
                    </label>
                    <select
                      name="tipo"
                      value={formData.tipo}
                      onChange={handleChange}
                      className="w-full px-4 py-2 rounded-lg border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                      disabled={isSubmitting}
                    >
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
                  </div>

                  {/* Prioridad */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                      Prioridad *
                    </label>
                    <select
                      name="prioridad"
                      value={formData.prioridad}
                      onChange={handleChange}
                      className="w-full px-4 py-2 rounded-lg border-2 border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                      disabled={isSubmitting}
                    >
                      <option value="baja">Baja</option>
                      <option value="media">Media</option>
                      <option value="alta">Alta</option>
                    </select>
                  </div>
                </div>

                {/* Checkboxes */}
                <div className="space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      name="permite_entrega_tardia"
                      checked={formData.permite_entrega_tardia}
                      onChange={handleChange}
                      disabled={isSubmitting}
                      className="w-4 h-4 rounded border-2 border-slate-300 dark:border-slate-600 cursor-pointer"
                    />
                    <span className="text-sm text-slate-700 dark:text-slate-300">
                      Permitir entregas tardías
                    </span>
                  </label>

                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      name="habilitar_retroalimentacion_ia"
                      checked={formData.habilitar_retroalimentacion_ia}
                      onChange={handleChange}
                      disabled={isSubmitting}
                      className="w-4 h-4 rounded border-2 border-slate-300 dark:border-slate-600 cursor-pointer"
                    />
                    <span className="text-sm text-slate-700 dark:text-slate-300">
                      Habilitar retroalimentación IA (futuro)
                    </span>
                  </label>
                </div>

                {/* Botones */}
                <div className="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="button"
                    onClick={onClose}
                    disabled={isSubmitting}
                    className="flex-1 px-4 py-2 rounded-lg border-2 border-slate-200 dark:border-slate-600 text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
                  >
                    Cancelar
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? (tarea ? "Guardando..." : "Creando...") : (tarea ? "Guardar Cambios" : "Crear Tarea")}
                  </motion.button>
                </div>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default TareaFormModal;
