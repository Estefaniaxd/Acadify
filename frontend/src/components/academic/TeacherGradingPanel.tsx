import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Save,
  AlertCircle,
  CheckCircle2,
  Star,
  FileText,
  MessageSquare,
  Loader2,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/utils/cn";
import {
  useCalificarEntrega,
  useCalificarEntregaConPuntos,
} from "@/hooks/academic/useCalificarEntrega";
import type { EntregaTarea } from "@/types";

interface TeacherGradingPanelProps {
  tareaId: number;
  entregas: EntregaTarea[];
  isLoading: boolean;
  selectedEntrega: EntregaTarea | null;
  onSelectEntrega: (entrega: EntregaTarea) => void;
  onRefresh: () => void;
}

interface GradingForm {
  calificacion: number;
  comentarios: string;
  rubrica: Record<string, number>;
  usePoints: boolean;
  aplicarPenalizaciones: boolean;
}

/**
 * Panel for teachers to grade student submissions.
 * Features:
 * - Quick grading interface
 * - Rubric assessment
 * - Points calculation with penalties
 * - Batch grading
 * - Audit trail
 * - IA feedback display
 */
export function TeacherGradingPanel({
  tareaId,
  entregas,
  isLoading,
  selectedEntrega,
  onSelectEntrega,
  onRefresh,
}: TeacherGradingPanelProps) {
  // ========================================================================
  // STATE
  // ========================================================================

  const [gradingForm, setGradingForm] = useState<GradingForm>({
    calificacion: 0,
    comentarios: "",
    rubrica: {},
    usePoints: true,
    aplicarPenalizaciones: true,
  });

  const [showRubric, setShowRubric] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // ========================================================================
  // MUTATIONS
  // ========================================================================

  const { mutate: calificar, isPending: isCalificando } = useCalificarEntrega({
    onSuccess: () => {
      resetForm();
      onRefresh();
    },
    onError: (error) => {
      setSubmitError(
        error instanceof Error ? error.message : "Error al calificar"
      );
    },
  });

  const { mutate: calificarConPuntos, isPending: isCalificandoConPuntos } =
    useCalificarEntregaConPuntos({
      onSuccess: () => {
        resetForm();
        onRefresh();
      },
      onError: (error) => {
        setSubmitError(
          error instanceof Error ? error.message : "Error al calificar"
        );
      },
    });

  // ========================================================================
  // HANDLERS
  // ========================================================================

  const resetForm = () => {
    setGradingForm({
      calificacion: 0,
      comentarios: "",
      rubrica: {},
      usePoints: true,
      aplicarPenalizaciones: true,
    });
    setSubmitError(null);
  };

  const handleSelectEntrega = (entrega: EntregaTarea) => {
    onSelectEntrega(entrega);
    resetForm();
  };

  const handleGradeSubmit = () => {
    if (!selectedEntrega) return;

    if (gradingForm.calificacion < 0 || gradingForm.calificacion > 5) {
      setSubmitError("La calificación debe estar entre 0 y 5");
      return;
    }

    if (gradingForm.usePoints) {
      calificarConPuntos({
        entregaId: selectedEntrega.entrega_id,
        payload: {
          calificacion: gradingForm.calificacion,
          comentarios_docente: gradingForm.comentarios,
          rubrica_calificacion: gradingForm.rubrica,
          aplicar_penalizacion_tardia: gradingForm.aplicarPenalizaciones,
          aplicar_penalizacion_intentos: gradingForm.aplicarPenalizaciones,
        },
      });
    } else {
      calificar({
        entregaId: selectedEntrega.entrega_id,
        payload: {
          calificacion: gradingForm.calificacion,
          comentarios_docente: gradingForm.comentarios,
          rubrica_calificacion: gradingForm.rubrica,
        },
      });
    }
  };

  // ========================================================================
  // COMPUTED
  // ========================================================================

  const stats = useMemo(() => {
    return {
      total: entregas.length,
      pendiente: entregas.filter((e) => e.estado === "ENTREGADA").length,
      calificada: entregas.filter((e) => e.estado === "CALIFICADA").length,
      tardia: entregas.filter((e) => e.es_tardia).length,
      promedio:
        entregas.length > 0
          ? (
              entregas.reduce((sum, e) => sum + (e.calificacion || 0), 0) /
              entregas.filter((e) => e.calificacion).length
            ).toFixed(2)
          : "N/A",
    };
  }, [entregas]);

  const isPending = isCalificando || isCalificandoConPuntos;

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-md p-6"
    >
      <h2 className="text-lg font-semibold text-slate-900 mb-4">
        Panel de Calificación
      </h2>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        <div className="p-3 bg-blue-50 rounded-lg">
          <p className="text-xs text-slate-600">Total</p>
          <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
        </div>
        <div className="p-3 bg-yellow-50 rounded-lg">
          <p className="text-xs text-slate-600">Por calificar</p>
          <p className="text-2xl font-bold text-yellow-600">{stats.pendiente}</p>
        </div>
        <div className="p-3 bg-green-50 rounded-lg">
          <p className="text-xs text-slate-600">Calificadas</p>
          <p className="text-2xl font-bold text-green-600">{stats.calificada}</p>
        </div>
        <div className="p-3 bg-red-50 rounded-lg">
          <p className="text-xs text-slate-600">Tardías</p>
          <p className="text-2xl font-bold text-red-600">{stats.tardia}</p>
        </div>
      </div>

      {/* Entregas List */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">
          Entregas por Calificar
        </h3>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
          </div>
        ) : entregas.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-green-600" />
            <p>Todas las entregas han sido calificadas</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {entregas.map((entrega) => (
              <motion.button
                key={entrega.entrega_id}
                onClick={() => handleSelectEntrega(entrega)}
                whileHover={{ x: 4 }}
                className={cn(
                  "w-full text-left p-3 rounded-lg border-2 transition-all",
                  selectedEntrega?.entrega_id === entrega.entrega_id
                    ? "border-blue-500 bg-blue-50"
                    : "border-slate-200 hover:border-slate-300"
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-slate-900">
                      {entrega.titulo_entrega ||
                        `Entrega de ${entrega.estudiante?.nombre || "Estudiante"}`}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(entrega.fecha_entrega).toLocaleDateString(
                        "es-ES"
                      )}{" "}
                      • Intento {entrega.numero_intento}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    {entrega.es_tardia && (
                      <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded">
                        Tardía
                      </span>
                    )}
                    <span
                      className={cn(
                        "px-2 py-1 text-xs font-semibold rounded",
                        entrega.estado === "ENTREGADA"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                      )}
                    >
                      {entrega.estado}
                    </span>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        )}
      </div>

      {/* Grading Form */}
      {selectedEntrega && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-t pt-6"
        >
          {/* Entrega Details */}
          <div className="mb-6 p-4 bg-slate-50 rounded-lg">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-slate-600 font-semibold">Estudiante</p>
                <p className="text-sm text-slate-900 mt-1">
                  {selectedEntrega.estudiante?.nombre || "N/A"}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-semibold">
                  Fecha Entrega
                </p>
                <p className="text-sm text-slate-900 mt-1">
                  {new Date(selectedEntrega.fecha_entrega).toLocaleDateString(
                    "es-ES"
                  )}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-semibold">Intento</p>
                <p className="text-sm text-slate-900 mt-1">
                  {selectedEntrega.numero_intento}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-semibold">Estado</p>
                <p className="text-sm text-slate-900 mt-1">
                  {selectedEntrega.es_tardia ? "❌ Tardía" : "✅ A tiempo"}
                </p>
              </div>
            </div>

            {/* Student Comments */}
            {selectedEntrega.comentarios_estudiante && (
              <div className="mt-4 p-3 bg-white rounded border border-slate-200">
                <p className="text-xs text-slate-600 font-semibold mb-1">
                  💬 Comentarios del Estudiante
                </p>
                <p className="text-sm text-slate-700">
                  {selectedEntrega.comentarios_estudiante}
                </p>
              </div>
            )}

            {/* File Preview */}
            {selectedEntrega.archivo_url && (
              <div className="mt-4">
                <a
                  href={selectedEntrega.archivo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  Ver archivo adjunto
                </a>
              </div>
            )}
          </div>

          {/* Error Message */}
          {submitError && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-red-900">Error</p>
                <p className="text-sm text-red-800">{submitError}</p>
              </div>
            </motion.div>
          )}

          {/* Grading Form Fields */}
          <div className="space-y-4">
            {/* Calificación */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                ⭐ Calificación (0-5)
              </label>
              <input
                type="number"
                min="0"
                max="5"
                step="0.1"
                value={gradingForm.calificacion}
                onChange={(e) =>
                  setGradingForm((prev) => ({
                    ...prev,
                    calificacion: parseFloat(e.target.value),
                  }))
                }
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isPending}
              />
            </div>

            {/* Grade Letter */}
            <div>
              <p className="text-xs text-slate-600 font-semibold">
                Equivalente en Letra
              </p>
              <div className="mt-2 p-3 bg-slate-50 rounded-lg">
                <div className="inline-block px-4 py-2 bg-blue-600 text-white rounded font-bold text-lg">
                  {gradingForm.calificacion < 3
                    ? "F"
                    : gradingForm.calificacion < 3.5
                      ? "D"
                      : gradingForm.calificacion < 4
                        ? "C"
                        : gradingForm.calificacion < 4.5
                          ? "B"
                          : "A"}
                </div>
              </div>
            </div>

            {/* Comments */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                💬 Comentarios
              </label>
              <textarea
                value={gradingForm.comentarios}
                onChange={(e) =>
                  setGradingForm((prev) => ({
                    ...prev,
                    comentarios: e.target.value,
                  }))
                }
                placeholder="Proporciona retroalimentación constructiva..."
                rows={3}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                disabled={isPending}
              />
            </div>

            {/* IA Feedback */}
            {selectedEntrega.retroalimentacion_ia && (
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <MessageSquare className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-purple-900">
                      💡 Sugerencias de IA
                    </p>
                    <p className="text-sm text-purple-800 mt-1">
                      {selectedEntrega.retroalimentacion_ia}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Rubric Toggle */}
            <button
              type="button"
              onClick={() => setShowRubric(!showRubric)}
              className="w-full flex items-center justify-between p-3 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors"
              disabled={isPending}
            >
              <span className="text-sm font-semibold text-slate-700">
                📋 Rúbrica de Evaluación
              </span>
              <motion.div
                animate={{ rotate: showRubric ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <ChevronDown className="w-4 h-4 text-slate-600" />
              </motion.div>
            </button>

            <AnimatePresence>
              {showRubric && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-3 p-4 bg-slate-50 rounded-lg"
                >
                  <div>
                    <label className="text-xs font-semibold text-slate-700">
                      Presentación (0-5)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.5"
                      value={gradingForm.rubrica.presentacion || 0}
                      onChange={(e) =>
                        setGradingForm((prev) => ({
                          ...prev,
                          rubrica: {
                            ...prev.rubrica,
                            presentacion: parseFloat(e.target.value),
                          },
                        }))
                      }
                      className="w-full px-3 py-1 text-sm border border-slate-300 rounded mt-1"
                      disabled={isPending}
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-700">
                      Contenido (0-5)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.5"
                      value={gradingForm.rubrica.contenido || 0}
                      onChange={(e) =>
                        setGradingForm((prev) => ({
                          ...prev,
                          rubrica: {
                            ...prev.rubrica,
                            contenido: parseFloat(e.target.value),
                          },
                        }))
                      }
                      className="w-full px-3 py-1 text-sm border border-slate-300 rounded mt-1"
                      disabled={isPending}
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-700">
                      Originalidad (0-5)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.5"
                      value={gradingForm.rubrica.originalidad || 0}
                      onChange={(e) =>
                        setGradingForm((prev) => ({
                          ...prev,
                          rubrica: {
                            ...prev.rubrica,
                            originalidad: parseFloat(e.target.value),
                          },
                        }))
                      }
                      className="w-full px-3 py-1 text-sm border border-slate-300 rounded mt-1"
                      disabled={isPending}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Options */}
            <div className="space-y-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={gradingForm.usePoints}
                  onChange={(e) =>
                    setGradingForm((prev) => ({
                      ...prev,
                      usePoints: e.target.checked,
                    }))
                  }
                  disabled={isPending}
                  className="w-4 h-4 rounded"
                />
                <span className="text-sm text-slate-700">
                  🎮 Calcular puntos de gamificación
                </span>
              </label>

              {gradingForm.usePoints && (
                <label className="flex items-center gap-3 cursor-pointer ml-7">
                  <input
                    type="checkbox"
                    checked={gradingForm.aplicarPenalizaciones}
                    onChange={(e) =>
                      setGradingForm((prev) => ({
                        ...prev,
                        aplicarPenalizaciones: e.target.checked,
                      }))
                    }
                    disabled={isPending}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-xs text-slate-600">
                    Aplicar penalizaciones (tardía, intentos)
                  </span>
                </label>
              )}
            </div>

            {/* Submit Button */}
            <button
              onClick={handleGradeSubmit}
              disabled={isPending}
              className={cn(
                "w-full py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2",
                isPending
                  ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                  : "bg-green-600 text-white hover:bg-green-700"
              )}
            >
              {isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Guardar Calificación
                </>
              )}
            </button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
