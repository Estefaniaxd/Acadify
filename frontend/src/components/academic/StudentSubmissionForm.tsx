import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  FileText,
  AlertCircle,
  CheckCircle2,
  X,
  Loader2,
  Link as LinkIcon,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useEntregarTarea, useCrearEntrega } from "@/hooks/academic/useCalificarEntrega";
import type { EntregaTarea } from "@/types";

interface StudentSubmissionFormProps {
  tareaId: string | number;
  miEntregaId?: number | null;
  maxAttempts?: number | null;
  currentAttempts: number;
  maxFileSize?: number; // in MB
  fileFormats?: string; // comma-separated or JSON
  onSubmitSuccess: (entrega: EntregaTarea) => void;
}

interface FormState {
  comentarios: string;
  archivo: File | null;
  enlaces: string[];
  contenido: string;
  nuevoEnlace: string;
}

interface ValidationError {
  field: string;
  message: string;
}

/**
 * Component for students to submit assignments.
 * Features:
 * - File upload with drag-and-drop
 * - Multiple file formats support
 * - Comments/notes field
 * - External links support
 * - Attempt limiting
 * - File size validation
 * - Format validation
 */
export function StudentSubmissionForm({
  tareaId,
  miEntregaId,
  maxAttempts,
  currentAttempts,
  maxFileSize = 10, // 10 MB default
  fileFormats,
  onSubmitSuccess,
}: StudentSubmissionFormProps) {
  const tareaIdNumber = typeof tareaId === "number" ? tareaId : Number(tareaId);
  const tareaIdIsValid = Number.isFinite(tareaIdNumber);

  // ========================================================================
  // STATE
  // ========================================================================

  const [form, setForm] = useState<FormState>({
    comentarios: "",
    archivo: null,
    enlaces: [],
    contenido: "",
    nuevoEnlace: "",
  });

  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  // ========================================================================
  // MUTATIONS
  // ========================================================================

  const {
    mutate: entregarTarea,
    mutateAsync: entregarTareaAsync,
    isPending,
    isError,
    error,
  } = useEntregarTarea({
    onSuccess: (data) => {
      // Reset form
      setForm({
        comentarios: "",
        archivo: null,
        enlaces: [],
        contenido: "",
        nuevoEnlace: "",
      });
      setErrors([]);
      onSubmitSuccess(data);
    },
  });

  const { mutateAsync: crearEntregaAsync } = useCrearEntrega();

  // ========================================================================
  // VALIDATION
  // ========================================================================

  function validateFile(file: File): ValidationError[] {
    const errors: ValidationError[] = [];

    // Check file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxFileSize) {
      errors.push({
        field: "archivo",
        message: `El archivo es muy grande (${fileSizeMB.toFixed(2)} MB). Máximo permitido: ${maxFileSize} MB`,
      });
    }

    // Check file format
    if (fileFormats) {
      const allowedFormats = fileFormats
        .split(",")
        .map((f) => f.toLowerCase().trim());
      const fileExtension = file.name.split(".").pop()?.toLowerCase();

      if (fileExtension && !allowedFormats.includes(fileExtension)) {
        errors.push({
          field: "archivo",
          message: `Formato de archivo no permitido. Formatos permitidos: ${fileFormats}`,
        });
      }
    }

    // Check for suspicious files
    if (
      file.name.includes("..") ||
      file.name.includes("/") ||
      file.name.includes("\\")
    ) {
      errors.push({
        field: "archivo",
        message: "El nombre del archivo contiene caracteres no permitidos",
      });
    }

    return errors;
  }

  function validateForm(): ValidationError[] {
    const formErrors: ValidationError[] = [];

    // At least one submission method required
    if (!form.archivo && !form.comentarios && form.enlaces.length === 0) {
      formErrors.push({
        field: "submission",
        message: "Debes enviar algo (archivo, comentarios o enlaces)",
      });
    }

    // Validate URLs if provided
    form.enlaces.forEach((enlace, index) => {
      try {
        new URL(enlace);
      } catch {
        formErrors.push({
          field: `enlaces.${index}`,
          message: `URL inválida: ${enlace}`,
        });
      }
    });

    return formErrors;
  }

  // ========================================================================
  // HANDLERS
  // ========================================================================

  const handleFileSelect = useCallback((file: File) => {
    const fileErrors = validateFile(file);
    if (fileErrors.length > 0) {
      setErrors(fileErrors);
      return;
    }

    setForm((prev) => ({ ...prev, archivo: file }));
    setErrors((prev) => prev.filter((e) => e.field !== "archivo"));
  }, [maxFileSize, fileFormats]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files?.[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleRemoveFile = () => {
    setForm((prev) => ({ ...prev, archivo: null }));
  };

  const handleAddLink = () => {
    if (!form.nuevoEnlace.trim()) return;

    try {
      new URL(form.nuevoEnlace);
      setForm((prev) => ({
        ...prev,
        enlaces: [...prev.enlaces, form.nuevoEnlace],
        nuevoEnlace: "",
      }));
      setErrors((prev) => prev.filter((e) => !e.field.startsWith("enlaces")));
    } catch {
      setErrors((prev) => [
        ...prev.filter((e) => !e.field.startsWith("enlaces")),
        {
          field: `enlaces.nuevo`,
          message: "URL inválida",
        },
      ]);
    }
  };

  const handleRemoveLink = (index: number) => {
    setForm((prev) => ({
      ...prev,
      enlaces: prev.enlaces.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const formErrors = validateForm();
    if (formErrors.length > 0) {
      setErrors(formErrors);
      return;
    }

    if (!tareaIdIsValid) {
      setErrors([
        {
          field: "submission",
          message: "No se pudo identificar la tarea. Refresca la página e inténtalo de nuevo.",
        },
      ]);
      return;
    }

    // Submission flow:
    // - If there's already an entrega id (miEntregaId prop), use it
    // - Otherwise create an entrega first, then deliver
    (async () => {
      try {
        let entregaIdToUse: number | undefined = (typeof miEntregaId !== "undefined" && miEntregaId !== null)
          ? miEntregaId
          : undefined;

        if (!entregaIdToUse) {
          // Create a new entrega for this tarea
          const created = await crearEntregaAsync({
            tareaId: tareaIdNumber,
            payload: { comentarios_estudiante: form.comentarios },
          });
          entregaIdToUse = created.entrega_id;
        }

        if (!entregaIdToUse) {
          setErrors([{ field: "submission", message: "No se pudo crear la entrega." }]);
          return;
        }

        // Si no hay comentario ni contenido, pero hay archivo, autocompletar contenido
        let contenidoFinal = form.contenido;
        if (!contenidoFinal || !contenidoFinal.trim()) {
          if (form.comentarios && form.comentarios.trim()) {
            contenidoFinal = form.comentarios;
          } else if (form.archivo) {
            contenidoFinal = "Archivo adjunto";
          }
        }

        await (entregarTareaAsync as any)({
          entregaId: entregaIdToUse,
          payload: {
            comentarios_estudiante: form.comentarios,
            archivo: form.archivo || undefined,
            enlaces_externos: form.enlaces,
            contenido_texto: contenidoFinal,
          },
        });
      } catch (err) {
        // Let the hook onError handle it (and set UI-level errors where appropriate)
        console.error("Error enviando entrega:", err);
      }
    })();
  };

  // ========================================================================
  // UTILS
  // ========================================================================

  const attemptWarning = maxAttempts && currentAttempts >= maxAttempts;
  const canSubmit =
    !isPending && (!maxAttempts || currentAttempts < maxAttempts);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes, k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
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
      <h2 className="text-xl font-semibold text-slate-900 mb-4">
        Enviar Tarea
      </h2>

      {/* Attempt Warning */}
      {attemptWarning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
        >
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-900">
              Has agotado tus intentos
            </p>
            <p className="text-sm text-red-800">
              Has realizado {currentAttempts} de {maxAttempts} intentos permitidos.
            </p>
          </div>
        </motion.div>
      )}

      {/* Error Alert */}
      {errors.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-red-900 mb-2">
                Hay errores en el formulario:
              </p>
              <ul className="space-y-1">
                {errors.map((error, index) => (
                  <li key={index} className="text-sm text-red-800">
                    • {error.message}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      )}

      {/* Success Alert */}
      {!isPending && isError && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900">
                Error al enviar la tarea
              </p>
              <p className="text-sm text-red-800">
                {error instanceof Error
                  ? error.message
                  : "Error desconocido"}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload Section */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-3">
            📎 Archivo
            <span className="text-xs font-normal text-slate-500 ml-2">
              (Máx: {maxFileSize}MB)
            </span>
          </label>

          {form.archivo ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-4 bg-green-50 border-2 border-green-200 rounded-lg flex items-start justify-between"
            >
              <div className="flex items-start gap-3 flex-1">
                <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-green-900">{form.archivo.name}</p>
                  <p className="text-xs text-green-700 mt-1">
                    {formatFileSize(form.archivo.size)}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleRemoveFile}
                className="text-green-600 hover:text-green-700 flex-shrink-0"
              >
                <X className="w-5 h-5" />
              </button>
            </motion.div>
          ) : (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={cn(
                "relative border-2 border-dashed rounded-lg p-8 text-center transition-all",
                isDragOver
                  ? "border-blue-500 bg-blue-50"
                  : "border-slate-300 hover:border-slate-400 bg-slate-50"
              )}
            >
              <input
                type="file"
                onChange={handleFileInputChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
                disabled={isPending}
              />

              <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="font-medium text-slate-700">
                Arrastra tu archivo aquí o haz click
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {fileFormats ? `Formatos permitidos: ${fileFormats}` : ""}
              </p>
            </div>
          )}
        </div>

        {/* Comments Section */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            💬 Comentarios
          </label>
          <textarea
            value={form.comentarios}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, comentarios: e.target.value }))
            }
            placeholder="Cuéntale al docente sobre tu entrega..."
            rows={4}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={isPending}
          />
          <p className="text-xs text-slate-500 mt-1">
            {form.comentarios.length}/500 caracteres
          </p>
        </div>

        {/* Content Section */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            📝 Contenido Directo
          </label>
          <textarea
            value={form.contenido}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, contenido: e.target.value }))
            }
            placeholder="O pega tu contenido directamente aquí..."
            rows={4}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={isPending}
          />
        </div>

        {/* External Links Section */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            🔗 Enlaces Externos
          </label>

          {form.enlaces.length > 0 && (
            <div className="mb-3 space-y-2">
              {form.enlaces.map((enlace, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg"
                >
                  <LinkIcon className="w-4 h-4 text-blue-600 flex-shrink-0" />
                  <a
                    href={enlace}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-700 break-all flex-1"
                  >
                    {enlace}
                  </a>
                  <button
                    type="button"
                    onClick={() => handleRemoveLink(index)}
                    className="text-blue-600 hover:text-blue-700 flex-shrink-0"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </motion.div>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <input
              type="url"
              value={form.nuevoEnlace}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, nuevoEnlace: e.target.value }))
              }
              placeholder="https://ejemplo.com"
              className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isPending}
            />
            <button
              type="button"
              onClick={handleAddLink}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              disabled={isPending || !form.nuevoEnlace.trim()}
            >
              Agregar
            </button>
          </div>
        </div>

        {/* Attempt Counter */}
        {maxAttempts && (
          <div className="p-3 bg-slate-100 rounded-lg text-sm text-slate-700">
            Intento {currentAttempts + 1} de {maxAttempts}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={!canSubmit}
            className={cn(
              "flex-1 py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2",
              canSubmit
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-slate-300 text-slate-500 cursor-not-allowed"
            )}
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Enviando...
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                Enviar Tarea
              </>
            )}
          </button>

          {!canSubmit && (
            <div className="flex-1 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm font-medium flex items-center justify-center">
              ❌ No puedes enviar más entregas
            </div>
          )}
        </div>
      </form>
    </motion.div>
  );
}
