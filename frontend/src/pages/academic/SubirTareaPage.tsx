import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Upload,
  File,
  Link as LinkIcon,
  MessageSquare,
  AlertCircle,
  CheckCircle,
  Clock,
  XCircle,
  Loader2,
  Trash2,
  Plus,
  Eye,
} from 'lucide-react';
import { apiClientTareas } from '../../modules/tareas/api';
import { Tarea, EntregaTarea, EstadoEntrega } from '../../modules/tareas/types';
import GoogleWorkspaceModal from '../../components/tareas/GoogleWorkspaceModal';
import GoogleResourceList from '../../components/tareas/GoogleResourceList';
import { useGoogleWorkspace } from '../../hooks/useGoogleWorkspace';

/**
 * SubirTareaPage - Página para que estudiantes entreguen sus tareas
 * Soporta: Archivos, comentarios, enlaces externos, contenido de texto
 */

interface FormState {
  archivo: File | null;
  comentarios: string;
  enlaces: { url: string; descripcion: string }[];
  contenidoTexto: string;
  nuevoEnlace: { url: string; descripcion: string };
}

export default function SubirTareaPage() {
  const { tareaId } = useParams<{ tareaId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Estado local del formulario
  const [formState, setFormState] = useState<FormState>({
    archivo: null,
    comentarios: '',
    enlaces: [],
    contenidoTexto: '',
    nuevoEnlace: { url: '', descripcion: '' },
  });

  const [error, setError] = useState<string | null>(null);
  const [archivoPreview, setArchivoPreview] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showGoogleModal, setShowGoogleModal] = useState(false);

  // Google Workspace integration
  const {
    resources: googleResources,
    isLoading: isLoadingResources,
    deleteResource,
    createResource,
    isCreating: isCreatingGoogleResource,
    oauthStatus,
    isCheckingAuth: isCheckingGoogleAuth,
    connectGoogleAccount,
  } = useGoogleWorkspace(tareaId || '');
  const isGoogleLinked = Boolean(oauthStatus?.is_linked);
  const hasGoogleCredentials = Boolean(oauthStatus?.has_credentials ?? oauthStatus?.is_linked);
  const needsGoogleRelink = Boolean(oauthStatus?.needs_relink);
  const canUseGoogleWorkspace = isGoogleLinked && hasGoogleCredentials && !needsGoogleRelink;
  const googleProviderEmail = oauthStatus?.provider_email;
  const googleTokenExpiry = oauthStatus?.expires_at ? new Date(oauthStatus.expires_at) : null;

  // Debug: Track modal state changes
  useEffect(() => {
    console.log('🔵 showGoogleModal changed to:', showGoogleModal);
  }, [showGoogleModal]);

  // ====================================
  // QUERIES
  // ====================================

  // Obtener detalle de la tarea
  const {
    data: tarea,
    isLoading: isLoadingTarea,
    error: errorTarea,
  } = useQuery<Tarea>({
    queryKey: ['tarea', tareaId],
    queryFn: () => apiClientTareas.obtenerTarea(tareaId!),
    enabled: !!tareaId,
  });

  // Obtener mi entrega (si existe)
  const { data: miEntrega } = useQuery<EntregaTarea | null>({
    queryKey: ['miEntrega', tareaId],
    queryFn: async () => {
      // TODO: Implementar endpoint obtenerMiEntrega en backend
      return null;
    },
    enabled: !!tareaId,
  });


  // ====================================
  // HANDLERS
  // ====================================

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validar tamaño
    const maxSizeKb = (tarea?.tamano_maximo_mb || 10) * 1024;
    if (file.size > maxSizeKb * 1024) {
      setError(`Archivo muy grande. Máximo: ${tarea?.tamano_maximo_mb || 10}MB`);
      return;
    }

    setFormState((prev) => ({ ...prev, archivo: file }));
    setArchivoPreview(file.name);
    setError(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      const input = document.createElement('input');
      input.type = 'file';
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      input.files = dataTransfer.files;
      handleFileSelect({ target: input } as any);
    }
  };

  const handleAgregarEnlace = () => {
    if (!formState.nuevoEnlace.url.trim()) {
      setError('Por favor ingresa una URL');
      return;
    }

    setFormState((prev) => ({
      ...prev,
      enlaces: [...prev.enlaces, formState.nuevoEnlace],
      nuevoEnlace: { url: '', descripcion: '' },
    }));
    setError(null);
  };

  const handleEliminarEnlace = (index: number) => {
    setFormState((prev) => ({
      ...prev,
      enlaces: prev.enlaces.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validación: al menos archivo O contenido
    if (!formState.archivo && !formState.contenidoTexto) {
      setError('Debes adjuntar un archivo o escribir contenido');
      return;
    }

    if (!tareaId) {
      setError('ID de tarea no disponible');
      return;
    }

    try {
      setError(null);
      setIsSubmitting(true);

      console.log('📦 INICIO handleSubmit');
      console.log('  - formState.contenidoTexto:', `"${formState.contenidoTexto}"`);
      console.log('  - formState.comentarios:', `"${formState.comentarios}"`);
      console.log('  - formState.archivo:', formState.archivo?.name || 'null');

      // Construir contenido directamente aquí
      let contenido = formState.contenidoTexto || '';
      console.log('📦 1️⃣ contenido inicial:', `"${contenido}"`);

      if (formState.comentarios) {
        contenido = contenido
          ? `${formState.comentarios}\n\n${contenido}`
          : formState.comentarios;
        console.log('📦 2️⃣ contenido con comentarios:', `"${contenido}"`);
      }

      // FALLBACK: Si no hay contenido, usar algo por defecto
      if (!contenido || !contenido.trim()) {
        contenido = 'Archivo adjunto - sin contenido de texto';
        console.log('📦 3️⃣ FALLBACK APLICADO:', `"${contenido}"`);
      }

      console.log('📦 4️⃣ contenido FINAL antes FormData:', {
        length: contenido.length,
        value: `"${contenido}"`,
        typeof: typeof contenido,
      });

      // **CLAVE**: Crear FormData aquí, sin función separada
      console.log('📦 5️⃣ Creando NEW FormData()...');
      const formData = new FormData();

      console.log('📦 6️⃣ FormData creado, instanceof:', formData instanceof FormData);

      console.log('📦 7️⃣ Haciendo append("contenido", ...)');
      formData.append('contenido', contenido);
      console.log('📦 8️⃣ ✅ append contenido completado');

      if (formState.archivo) {
        console.log('📦 9️⃣ Haciendo append("archivo", ...)', formState.archivo.name);
        formData.append('archivo', formState.archivo);
        console.log('📦 🔟 ✅ append archivo completado');
      }

      console.log('📦 1️⃣1️⃣ FormData completado, instanceof:', formData instanceof FormData);

      // **Verificar FormData antes de enviar**
      const entries = Array.from(
        (formData as unknown as {
          entries: () => IterableIterator<[string, FormDataEntryValue]>;
        }).entries()
      );
      console.log('📦 1️⃣2️⃣ FormData entries count:', entries.length);
      for (const [key, val] of entries) {
        if (val instanceof File) {
          console.log(`  - ${key}: File(${(val as File).name})`);
        } else {
          console.log(`  - ${key}: "${val}"`);
        }
      }

      console.log('📦 1️⃣3️⃣ ANTES de llamar entregarTarea()');

      // ENVIAR FormData
      const result = await apiClientTareas.entregarTarea(tareaId, formData);

      console.log('📦 1️⃣4️⃣ ✅ ÉXITO - Tarea entregada');

      // Si llegamos aquí, fue éxito
      queryClient.invalidateQueries({ queryKey: ['entregas', tareaId] });
      queryClient.invalidateQueries({ queryKey: ['miEntrega', tareaId] });
      setFormState({
        archivo: null,
        comentarios: '',
        enlaces: [],
        contenidoTexto: '',
        nuevoEnlace: { url: '', descripcion: '' },
      });
      navigate(-1);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Error al entregar la tarea';
      setError(
        typeof errorMsg === 'string'
          ? errorMsg
          : Array.isArray(errorMsg)
            ? errorMsg.map((e: any) => e.msg || e).join(', ')
            : 'Error desconocido'
      );
      console.error('❌ Error entregando tarea:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteGoogleResource = async (resourceId: string) => {
    if (confirm('¿Eliminar este recurso? El archivo permanecerá en tu Google Drive.')) {
      try {
        await deleteResource(resourceId, false);
      } catch (err) {
        setError('Error al eliminar recurso');
      }
    }
  };

  const handleOpenGoogleResource = (url: string) => {
    window.open(url, '_blank');
  };

  // ====================================
  // RENDER
  // ====================================

  if (isLoadingTarea) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (errorTarea || !tarea) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 p-6">
        <div className="max-w-2xl mx-auto">
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>No se pudo cargar la tarea</span>
          </div>
        </div>
      </div>
    );
  }

  // Verificar si está vencida
  const ahora = new Date();
  const fechaLimite = new Date(tarea.fecha_limite);
  const estaVencida = ahora > fechaLimite;
  const esTardia = miEntrega && estaVencida;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="text-primary hover:text-primary/80 font-medium mb-4 flex items-center gap-2"
          >
            ← Volver
          </button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {tarea.titulo}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">{tarea.descripcion}</p>
        </div>

        {/* Grid: Detalle + Formulario */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Columna Izquierda: Detalles de la Tarea */}
          <div className="lg:col-span-1 space-y-4">
            {/* Card: Información */}
            <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 space-y-3 border border-gray-200 dark:border-gray-700">
              <div>
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                  Puntuación Máxima
                </p>
                <p className="text-2xl font-bold text-primary">
                  {tarea.puntuacion_maxima} pts
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                  Tipo
                </p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {tarea.tipo || 'Ejercicio'}
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                  Intentos
                </p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {miEntrega?.numero_intento || 0}/{tarea.intentos_maximos}
                </p>
              </div>
            </div>

            {/* Card: Fechas */}
            <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 space-y-3 border border-gray-200 dark:border-gray-700">
              {miEntrega?.enlaces_externos && Array.isArray(miEntrega.enlaces_externos) && miEntrega.enlaces_externos.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Enlaces entregados:
                  </p>
                  {(miEntrega.enlaces_externos as Array<{ url: string; titulo?: string }>).map((enlace, index) => (
                    <a
                      key={index}
                      href={enlace.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      <LinkIcon className="w-4 h-4" />
                      {enlace.titulo || enlace.url}
                    </a>
                  ))}
                </div>
              )}
              {tarea.fecha_inicio_disponible && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                    Disponible desde
                  </p>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {new Date(tarea.fecha_inicio_disponible).toLocaleDateString('es-ES')}
                  </p>
                </div>
              )}

              <div>
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                  Vence
                </p>
                <p
                  className={`text-sm font-semibold ${estaVencida
                    ? 'text-red-600 dark:text-red-400'
                    : 'text-gray-700 dark:text-gray-300'
                    }`}
                >
                  {fechaLimite.toLocaleDateString('es-ES')}{' '}
                  {fechaLimite.toLocaleTimeString('es-ES')}
                </p>
              </div>

              {estaVencida && tarea.permite_entrega_tardia && (
                <div className="p-2 rounded bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
                  <p className="text-xs text-yellow-800 dark:text-yellow-300">
                    ⚠️ Entrega tardía (-{tarea.penalizacion_tardia}%)
                  </p>
                </div>
              )}
            </div>

            {/* Card: Mi Entrega */}
            {miEntrega && (
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Mi Entrega
                </p>

                <div
                  className={`p-3 rounded-lg flex items-center gap-2 text-sm font-medium ${miEntrega.estado === EstadoEntrega.CALIFICADA
                    ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300'
                    : miEntrega.estado === EstadoEntrega.ENTREGADA
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300'
                      : 'bg-gray-50 dark:bg-gray-900/20 text-gray-800 dark:text-gray-300'
                    }`}
                >
                  {miEntrega.estado === EstadoEntrega.CALIFICADA && (
                    <CheckCircle className="w-4 h-4" />
                  )}
                  {miEntrega.estado === EstadoEntrega.ENTREGADA && (
                    <Clock className="w-4 h-4" />
                  )}
                  {miEntrega.estado === EstadoEntrega.BORRADOR && (
                    <AlertCircle className="w-4 h-4" />
                  )}
                  <span>{miEntrega.estado}</span>
                </div>

                {miEntrega.calificacion && (
                  <div className="mt-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      Calificación
                    </p>
                    <p className="text-2xl font-bold text-primary">
                      {miEntrega.calificacion}/{tarea.puntuacion_maxima}
                    </p>
                    {miEntrega.calificacion_letras && (
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        ({miEntrega.calificacion_letras})
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Columna Derecha: Formulario */}
          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Error */}
              {error && (
                <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 text-sm flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {error}
                </div>
              )}

              {/* 1. Subir Archivo */}
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-primary transition-colors"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <label className="cursor-pointer">
                  <div className="flex flex-col items-center gap-3 text-center">
                    <Upload className="w-8 h-8 text-primary" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">
                        Sube tu archivo aquí
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        o haz clic para seleccionar
                      </p>
                    </div>
                    {archivoPreview && (
                      <p className="text-sm font-medium text-green-600 dark:text-green-400 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        {archivoPreview}
                      </p>
                    )}
                  </div>
                  <input
                    type="file"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
              </div>

              {/* Google Workspace Integration */}
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <p className="font-semibold text-gray-900 dark:text-gray-100">
                    Google Workspace
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      console.log('🟡 Abriendo Google Workspace Modal');
                      setShowGoogleModal(true);
                    }}
                    className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors font-medium flex items-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Agregar o crear
                  </button>
                </div>

                <div className="mb-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-zinc-900/40 p-3 text-sm">
                  {isCheckingGoogleAuth ? (
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
                      <Loader2 className="w-4 h-4 animate-spin" /> Verificando tu conexión con Google...
                    </div>
                  ) : canUseGoogleWorkspace ? (
                    <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                      <div className="text-green-700 dark:text-green-400 text-left">
                        <p className="font-medium">
                          Cuenta conectada {googleProviderEmail ? `(${googleProviderEmail})` : ''}
                        </p>
                        {googleTokenExpiry && (
                          <p className="text-xs text-green-600 dark:text-green-300">
                            Token válido hasta {googleTokenExpiry.toLocaleString('es-CO')}
                          </p>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={connectGoogleAccount}
                        className="text-xs text-green-700 dark:text-green-300 underline"
                      >
                        Cambiar cuenta
                      </button>
                    </div>
                  ) : isGoogleLinked ? (
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-amber-600 dark:text-amber-400 text-left">
                        Tu vínculo con Google caducó o no tiene permisos suficientes. Reautoriza para seguir creando recursos desde Drive.
                      </p>
                      <button
                        type="button"
                        onClick={connectGoogleAccount}
                        className="px-3 py-1.5 rounded-lg bg-amber-500 text-white text-xs font-semibold hover:bg-amber-600"
                      >
                        Re-vincular Google
                      </button>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-red-600 dark:text-red-400">
                        Conecta tu cuenta de Google para crear documentos en Drive.
                      </p>
                      <button
                        type="button"
                        onClick={connectGoogleAccount}
                        className="px-3 py-1.5 rounded-lg bg-red-600 text-white text-xs font-semibold hover:bg-red-700"
                      >
                        Conectar con Google
                      </button>
                    </div>
                  )}
                </div>

                <GoogleResourceList
                  resources={googleResources}
                  isLoading={isLoadingResources}
                  onDelete={handleDeleteGoogleResource}
                  onOpen={handleOpenGoogleResource}
                />
              </div>

              {/* 2. Comentarios */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <MessageSquare className="w-4 h-4 inline mr-2" />
                  Comentarios (opcional)
                </label>
                <textarea
                  value={formState.comentarios}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      comentarios: e.target.value,
                    }))
                  }
                  placeholder="Escribe algo si deseas..."
                  rows={3}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>

              {/* 3. Contenido de Texto */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Contenido (opcional)
                </label>
                <textarea
                  value={formState.contenidoTexto}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      contenidoTexto: e.target.value,
                    }))
                  }
                  placeholder="O pega tu respuesta aquí..."
                  rows={4}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>

              {/* 4. Enlaces */}
              <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 space-y-3">
                <p className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                  <LinkIcon className="w-4 h-4" />
                  Enlaces (opcional)
                </p>

                {/* Lista de enlaces */}
                {formState.enlaces.map((enlace, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 flex items-center justify-between gap-3"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                        {enlace.descripcion || enlace.url}
                      </p>
                      <a
                        href={enlace.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline truncate block"
                      >
                        {enlace.url}
                      </a>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleEliminarEnlace(idx)}
                      className="p-2 hover:bg-red-100 dark:hover:bg-red-900 text-red-600 dark:text-red-400 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}

                {/* Agregar nuevo enlace */}
                <div className="pt-2 space-y-2 border-t border-gray-200 dark:border-gray-700">
                  <input
                    type="url"
                    value={formState.nuevoEnlace.url}
                    onChange={(e) =>
                      setFormState((prev) => ({
                        ...prev,
                        nuevoEnlace: { ...prev.nuevoEnlace, url: e.target.value },
                      }))
                    }
                    placeholder="URL del enlace..."
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  />
                  <input
                    type="text"
                    value={formState.nuevoEnlace.descripcion}
                    onChange={(e) =>
                      setFormState((prev) => ({
                        ...prev,
                        nuevoEnlace: { ...prev.nuevoEnlace, descripcion: e.target.value },
                      }))
                    }
                    placeholder="Descripción (opcional)..."
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  />
                  <button
                    type="button"
                    onClick={handleAgregarEnlace}
                    className="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 transition-colors font-medium text-sm flex items-center justify-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Agregar Enlace
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => navigate(-1)}
                  className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors font-medium"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 px-4 py-3 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors font-medium disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Entregando...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Entregar Tarea
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Google Workspace Modal */}
      {showGoogleModal && (
        <GoogleWorkspaceModal
          onClose={() => setShowGoogleModal(false)}
          onResourceCreated={(resource) => {
            console.log('Recurso creado:', resource);
            setShowGoogleModal(false);
          }}
          createResource={createResource}
          isCreating={isCreatingGoogleResource}
          isCheckingAuth={isCheckingGoogleAuth}
          isGoogleLinked={canUseGoogleWorkspace}
          oauthStatus={oauthStatus}
          onConnectGoogle={connectGoogleAccount}
        />
      )}
    </div>
  );
}
