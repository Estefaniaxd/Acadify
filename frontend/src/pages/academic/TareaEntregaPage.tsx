import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Calendar, Clock, AlertCircle, CheckCircle2, FileText, User } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { apiClientTareas } from "../../modules/tareas/api";
import type { Tarea, EntregaTarea, Usuario } from "@/types";
import { EstadoEntrega } from "../../modules/tareas/types";
import { Loading } from "@/components/ui/Loading";
import { ErrorAlert } from "@/components/ui/ErrorAlert";
import { StudentSubmissionForm } from "@/components/academic/StudentSubmissionForm";
import { TeacherGradingPanel } from "@/components/academic/TeacherGradingPanel";
import { EntregasList } from "@/components/academic/EntregasList";
import { cn } from "@/utils/cn";

interface TareaWithDetails extends Tarea {
  docente: Usuario;
  total_entregas: number;
  entregas_pendientes: number;
  promedio_calificaciones: number | null;
}

interface TareaEntregaPageState {
  isEditingTarea: boolean;
  selectedEntrega: EntregaTarea | null;
  showSubmissionForm: boolean;
  filterStatus: "todas" | "pendientes" | "entregadas" | "calificadas";
}

export function TareaEntregaPage() {
  const { tarea_id } = useParams<{ tarea_id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  // State Management
  const [state, setState] = useState<TareaEntregaPageState>({
    isEditingTarea: false,
    selectedEntrega: null,
    showSubmissionForm: false,
    filterStatus: "todas",
  });

  // ============================================================================
  // QUERIES - Fetch tarea details with relationships
  // ============================================================================
  const {
    data: tarea,
    isLoading: isTareaLoading,
    error: tareaError,
    refetch: refetchTarea,
  } = useQuery<TareaWithDetails>({
    queryKey: ["tareas", tarea_id],
    queryFn: async () => {
      if (!tarea_id) {
        throw new Error("Tarea no válida");
      }
      return apiClientTareas.obtenerTarea(tarea_id);
    },
    enabled: !!tarea_id,
  });

  // Fetch entregas (student submissions) for this task
  const {
    data: entregas,
    isLoading: isEntregasLoading,
    error: entregasError,
    refetch: refetchEntregas,
  } = useQuery<EntregaTarea[]>({
    queryKey: ["tareas", tarea_id, "entregas", state.filterStatus],
    queryFn: async () => {
      if (!tarea_id) {
        return [];
      }

      const filtros = (() => {
        switch (state.filterStatus) {
          case "pendientes":
            return { solo_pendientes: true };
          case "entregadas":
            return { estado: EstadoEntrega.ENTREGADA };
          case "calificadas":
            return { solo_calificadas: true };
          default:
            return undefined;
        }
      })();

      return apiClientTareas.obtenerEntregasTarea(tarea_id, filtros);
    },
    enabled: !!tarea_id,
  });

  // Fetch current user's submission (if student)
  const {
    data: miEntrega,
    isLoading: isMiEntregaLoading,
    refetch: refetchMiEntrega,
  } = useQuery<EntregaTarea | null>({
    queryKey: ["tareas", tarea_id, "mi-entrega"],
    queryFn: async () => {
      if (!tarea?.mi_entrega_id) {
        return null;
      }

      try {
        return await apiClientTareas.obtenerEntrega(tarea.mi_entrega_id);
      } catch (error) {
        console.warn("No se pudo obtener la entrega del estudiante", error);
        return null;
      }
    },
    enabled: !!tarea_id && user?.rol === "ESTUDIANTE" && !!tarea?.mi_entrega_id,
  });

  // ============================================================================
  // VALIDATION & AUTHORIZATION
  // ============================================================================

  const isDocente = user?.rol === "DOCENTE" || user?.rol === "COORDINADOR";
  const isEstudiante = user?.rol === "ESTUDIANTE";
  const isOwner = tarea?.docente_id === user?.id;

  const canGrade = isDocente && isOwner;
  const canSubmit = isEstudiante && tarea && !isPastDeadline();

  function isPastDeadline(): boolean {
    if (!tarea?.fecha_limite) return true;
    return new Date() > new Date(tarea.fecha_limite);
  }

  function isLateSubmission(): boolean {
    if (!tarea?.fecha_limite) return false;
    return new Date() > new Date(tarea.fecha_limite);
  }

  function getLateStatus(): {
    isLate: boolean;
    daysDifference: number;
    penaltyPercentage: number;
  } {
    if (!tarea?.fecha_limite || !miEntrega?.fecha_entrega) {
      return { isLate: false, daysDifference: 0, penaltyPercentage: 0 };
    }

    const deadline = new Date(tarea.fecha_limite);
    const submitted = new Date(miEntrega.fecha_entrega);
    const isLate = submitted > deadline;

    if (!isLate) {
      return { isLate: false, daysDifference: 0, penaltyPercentage: 0 };
    }

    const diffTime = submitted.getTime() - deadline.getTime();
    const daysDifference = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const penaltyPercentage = tarea.penalizacion_tardia || 30;

    return { isLate: true, daysDifference, penaltyPercentage };
  }

  const lateStatus = getLateStatus();

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleSelectEntrega = (entrega: EntregaTarea) => {
    setState((s) => ({ ...s, selectedEntrega: entrega }));
  };

  const handleRefreshData = () => {
    refetchTarea();
    refetchEntregas();
    if (isEstudiante) refetchMiEntrega();
  };

  const handleFilterChange = (
    filter: "todas" | "pendientes" | "entregadas" | "calificadas"
  ) => {
    setState((s) => ({ ...s, filterStatus: filter }));
  };

  // ============================================================================
  // RENDER - Loading & Errors
  // ============================================================================

  if (isTareaLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loading message="Cargando tarea..." />
      </div>
    );
  }

  if (tareaError) {
    return (
      <div className="container mx-auto py-8 px-4">
        <ErrorAlert
          title="Error al cargar la tarea"
          message={
            tareaError instanceof Error
              ? tareaError.message
              : "Error desconocido"
          }
          onRetry={refetchTarea}
        />
      </div>
    );
  }

  if (!tarea) {
    return (
      <div className="container mx-auto py-8 px-4">
        <ErrorAlert
          title="Tarea no encontrada"
          message="La tarea que buscas no existe"
          onRetry={() => navigate("/academic/tasks")}
        />
      </div>
    );
  }

  // ============================================================================
  // RENDER - Main Content
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-slate-900 mb-2">
                {tarea.titulo}
              </h1>
              <div className="flex items-center gap-4 text-sm text-slate-600">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  <span>{tarea.docente.nombre}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  <span>Tipo: {tarea.tipo}</span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>Prioridad: {tarea.prioridad}</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => navigate(-1)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              ← Volver
            </button>
          </div>
        </motion.div>

        {/* Alerts */}
        {isPastDeadline() && isEstudiante && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900">Fecha límite vencida</p>
              <p className="text-sm text-red-800">
                Ya no puedes enviar nuevas entregas. Contacta al docente si
                necesitas entregar posteriormente.
              </p>
            </div>
          </motion.div>
        )}

        {lateStatus.isLate && miEntrega && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-yellow-900">Entrega tardía</p>
              <p className="text-sm text-yellow-800">
                Entregaste {lateStatus.daysDifference} día(s) después de la
                fecha límite. Se aplicará una penalización del{" "}
                {lateStatus.penaltyPercentage}% a tu calificación.
              </p>
            </div>
          </motion.div>
        )}

        {miEntrega?.calificacion && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3"
          >
            <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-green-900">Calificado</p>
              <p className="text-sm text-green-800">
                Tu entrega ha sido calificada con{" "}
                <span className="font-bold">
                  {miEntrega.calificacion} ({miEntrega.calificacion_letras})
                </span>
              </p>
            </div>
          </motion.div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Task Details & Student Form */}
          <div className="lg:col-span-2">
            {/* Task Details Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-md p-6 mb-6"
            >
              <h2 className="text-xl font-semibold text-slate-900 mb-4">
                Detalles de la Tarea
              </h2>

              {/* Description */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-slate-700 mb-2">
                  Descripción
                </h3>
                <p className="text-slate-600 leading-relaxed">
                  {tarea.descripcion}
                </p>
              </div>

              {/* Instructions */}
              {tarea.instrucciones && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">
                    Instrucciones
                  </h3>
                  <p className="text-slate-600 leading-relaxed">
                    {tarea.instrucciones}
                  </p>
                </div>
              )}

              {/* Objectives */}
              {tarea.objetivos && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">
                    Objetivos
                  </h3>
                  <p className="text-slate-600 leading-relaxed">
                    {tarea.objetivos}
                  </p>
                </div>
              )}

              {/* Key Info Grid */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-lg">
                {/* Due Date */}
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Calendar className="w-4 h-4 text-slate-600" />
                    <span className="text-sm font-semibold text-slate-700">
                      Fecha Límite
                    </span>
                  </div>
                  <p
                    className={cn(
                      "text-sm",
                      isPastDeadline()
                        ? "text-red-600 font-semibold"
                        : "text-slate-600"
                    )}
                  >
                    {new Date(tarea.fecha_limite).toLocaleDateString("es-ES", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>

                {/* Max Score */}
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle2 className="w-4 h-4 text-slate-600" />
                    <span className="text-sm font-semibold text-slate-700">
                      Puntuación Máxima
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">
                    {tarea.puntuacion_maxima} puntos
                  </p>
                </div>

                {/* Estimated Time */}
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="w-4 h-4 text-slate-600" />
                    <span className="text-sm font-semibold text-slate-700">
                      Tiempo Estimado
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">
                    {tarea.tiempo_estimado || "No especificado"}
                  </p>
                </div>

                {/* Attempts */}
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle className="w-4 h-4 text-slate-600" />
                    <span className="text-sm font-semibold text-slate-700">
                      Intentos Máximos
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">
                    {tarea.intentos_maximos || "Ilimitados"}
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Student Submission Form */}
            {isEstudiante && canSubmit && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <StudentSubmissionForm
                  tareaId={tarea_id ?? ""}
                  miEntregaId={miEntrega?.entrega_id}
                  maxAttempts={tarea.intentos_maximos}
                  currentAttempts={miEntrega?.numero_intento || 0}
                  onSubmitSuccess={handleRefreshData}
                  maxFileSize={tarea.tamano_maximo_mb}
                  fileFormats={tarea.restricciones_archivo}
                />
              </motion.div>
            )}

            {/* Student Submission View */}
            {isEstudiante && miEntrega && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-lg shadow-md p-6"
              >
                <h2 className="text-xl font-semibold text-slate-900 mb-4">
                  Mi Entrega
                </h2>
                <div className="space-y-4">
                  {/* Status Badge */}
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-slate-700">
                      Estado:
                    </span>
                    <span
                      className={cn(
                        "px-3 py-1 rounded-full text-xs font-semibold",
                        miEntrega.estado === "ENTREGADA"
                          ? "bg-blue-100 text-blue-800"
                          : miEntrega.estado === "CALIFICADA"
                            ? "bg-green-100 text-green-800"
                            : "bg-yellow-100 text-yellow-800"
                      )}
                    >
                      {miEntrega.estado}
                    </span>
                  </div>

                  {/* Submission Date */}
                  <div>
                    <span className="text-sm font-semibold text-slate-700">
                      Fecha de Entrega:
                    </span>
                    <p className="text-sm text-slate-600">
                      {new Date(miEntrega.fecha_entrega).toLocaleDateString(
                        "es-ES",
                        {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        }
                      )}
                    </p>
                  </div>

                  {/* Attempt Number */}
                  <div>
                    <span className="text-sm font-semibold text-slate-700">
                      Número de Intento:
                    </span>
                    <p className="text-sm text-slate-600">
                      {miEntrega.numero_intento} /{" "}
                      {tarea.intentos_maximos || "Ilimitados"}
                    </p>
                  </div>

                  {/* Grade */}
                  {miEntrega.calificacion && (
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-slate-700">
                          Calificación:
                        </span>
                        <span className="text-2xl font-bold text-green-600">
                          {miEntrega.calificacion}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">
                        ({miEntrega.calificacion_letras}) -{" "}
                        {miEntrega.puntos_otorgados} puntos
                      </p>
                    </div>
                  )}

                  {/* File Preview */}
                  {miEntrega.archivo_url && (
                    <div className="p-4 border border-slate-200 rounded-lg">
                      <p className="text-sm font-semibold text-slate-700 mb-2">
                        Archivo Adjunto:
                      </p>
                      <a
                        href={miEntrega.archivo_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-2"
                      >
                        <FileText className="w-4 h-4" />
                        Ver archivo
                      </a>
                    </div>
                  )}

                  {/* Comments */}
                  {miEntrega.comentarios_estudiante && (
                    <div>
                      <span className="text-sm font-semibold text-slate-700">
                        Tus Comentarios:
                      </span>
                      <p className="text-sm text-slate-600 mt-1">
                        {miEntrega.comentarios_estudiante}
                      </p>
                    </div>
                  )}

                  {/* Teacher Comments */}
                  {miEntrega.comentarios_docente && (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <span className="text-sm font-semibold text-slate-700">
                        Comentarios del Docente:
                      </span>
                      <p className="text-sm text-slate-600 mt-1">
                        {miEntrega.comentarios_docente}
                      </p>
                    </div>
                  )}

                  {/* IA Feedback */}
                  {miEntrega.retroalimentacion_ia && (
                    <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                      <span className="text-sm font-semibold text-slate-700">
                        💡 Sugerencias de IA:
                      </span>
                      <p className="text-sm text-slate-600 mt-1">
                        {miEntrega.retroalimentacion_ia}
                      </p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </div>

          {/* Right Column - Statistics & Teacher Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Statistics Card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-lg shadow-md p-6"
            >
              <h3 className="text-lg font-semibold text-slate-900 mb-4">
                Estadísticas
              </h3>
              <div className="space-y-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-xs text-slate-600 font-medium">
                    Total de Entregas
                  </p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {tarea.total_entregas}
                  </p>
                </div>
                <div className="p-3 bg-yellow-50 rounded-lg">
                  <p className="text-xs text-slate-600 font-medium">
                    Pendientes
                  </p>
                  <p className="text-2xl font-bold text-yellow-600 mt-1">
                    {tarea.entregas_pendientes}
                  </p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-xs text-slate-600 font-medium">
                    Promedio
                  </p>
                  <p className="text-2xl font-bold text-green-600 mt-1">
                    {tarea.promedio_calificaciones?.toFixed(2) || "N/A"}
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Teacher Grading Panel */}
            {canGrade && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <TeacherGradingPanel
                  tareaId={Number(tarea_id)}
                  entregas={entregas || []}
                  isLoading={isEntregasLoading}
                  selectedEntrega={state.selectedEntrega}
                  onSelectEntrega={handleSelectEntrega}
                  onRefresh={handleRefreshData}
                />
              </motion.div>
            )}
          </div>
        </div>

        {/* Entregas List (for teachers) */}
        {canGrade && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-8"
          >
            <EntregasList
              entregas={entregas || []}
              isLoading={isEntregasLoading}
              filterStatus={state.filterStatus}
              onFilterChange={handleFilterChange}
              onSelectEntrega={handleSelectEntrega}
              selectedEntrega={state.selectedEntrega}
            />
          </motion.div>
        )}
      </div>
    </div>
  );
}
