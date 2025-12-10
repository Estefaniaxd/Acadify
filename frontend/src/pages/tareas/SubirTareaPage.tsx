/**
 * SubirTareaPage
 *
 * Página dedicada para que estudiantes entreguen tareas.
 * Diseño tipo classroom con detalles completos y formulario funcional.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Clock,
  FileText,
  Upload,
  CheckCircle,
  AlertCircle,
  Calendar,
  Target,
  BookOpen,
  Award,
  Paperclip,
  Send,
  X,
  Download,
  Zap,
  Link,
  ExternalLink,
  Plus,
  Triangle,
  FileSpreadsheet,
  Presentation,
  Palette,
  Play,
  Loader2,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiClientTareas } from '../../modules/tareas/api';
import { Tarea, EntregaTarea, EstadoEntrega } from '../../modules/tareas/types';
import { ArchivoCard } from '../../components/features/tareas/ArchivoCard';
import GoogleResourceList from '../../components/tareas/GoogleResourceList';
import { useGoogleWorkspace } from '../../hooks/useGoogleWorkspace';

interface ArchivoSubido {
  file: File;
  preview?: string;
}

export default function SubirTareaPage() {
  const { tareaId } = useParams<{ tareaId: string }>();
  const navigate = useNavigate();

  // Estados principales
  const [tarea, setTarea] = useState<Tarea | null>(null);
  const [entregaExistente, setEntregaExistente] = useState<EntregaTarea | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [errorCarga, setErrorCarga] = useState<string | null>(null);

  // Estados del formulario
  const [comentarios, setComentarios] = useState('');
  const [archivos, setArchivos] = useState<ArchivoSubido[]>([]);  // Archivos NUEVOS
  const [enlaces, setEnlaces] = useState<{ url: string, titulo: string }[]>([]);  // Enlaces NUEVOS
  const [dragActive, setDragActive] = useState(false);

  // ✅ Estados para archivos/enlaces EXISTENTES a conservar
  const [archivosExistentes, setArchivosExistentes] = useState<any[]>([]);  // URLs de archivos anteriores
  const [enlacesExistentes, setEnlacesExistentes] = useState<{ url: string, titulo: string }[]>([]);  // Enlaces anteriores

  // Modal para agregar enlace
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');
  const [linkTitulo, setLinkTitulo] = useState('');

  // Modal para "Agregar o crear"
  const [showAgregarModal, setShowAgregarModal] = useState(false);

  // Google Workspace integration
  const {
    resources: googleResources,
    isLoading: isLoadingResources,
    deleteResource,
    createResource,
    oauthStatus,
    isCheckingAuth: isCheckingGoogleAuth,
    connectGoogleAccount,
    refreshOAuthStatus,
  } = useGoogleWorkspace(tareaId || '');
  const isGoogleLinked = Boolean(oauthStatus?.is_linked);
  const hasGoogleCredentials = Boolean(oauthStatus?.has_credentials ?? oauthStatus?.is_linked);
  const needsGoogleRelink = Boolean(oauthStatus?.needs_relink);
  const canUseGoogleWorkspace = isGoogleLinked && hasGoogleCredentials && !needsGoogleRelink;
  const googleProviderEmail = oauthStatus?.provider_email;
  const googleTokenExpiry = oauthStatus?.expires_at ? new Date(oauthStatus.expires_at) : null;

  // Debug
  useEffect(() => {
    console.log('SubirTareaPage - tareaId:', tareaId);
    console.log('SubirTareaPage - createResource available:', !!createResource);
  }, [tareaId, createResource]);

  // Ref para el input de archivos
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Estado para el menú desplegable de "Agregar o crear"
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const [attemptedGoogleWorkspace, setAttemptedGoogleWorkspace] = useState(false);

  const googleStatusBanner = (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/40 p-3 text-sm mb-4">
      {isCheckingGoogleAuth ? (
        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
          <Loader2 className="w-4 h-4 animate-spin" /> Verificando conexión...
        </div>
      ) : !isGoogleLinked ? (
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-red-600 dark:text-red-400 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Cuenta de Google no vinculada. Conéctala para crear documentos automáticamente.
          </p>
          <button
            type="button"
            onClick={connectGoogleAccount}
            className="px-3 py-1.5 rounded-lg bg-red-600 text-white text-xs font-semibold hover:bg-red-700 transition-colors"
          >
            Conectar ahora
          </button>
        </div>
      ) : needsGoogleRelink ? (
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-amber-600 dark:text-amber-400 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Tu vínculo con Google necesita actualizar los permisos. Vuelve a conectar tu cuenta para seguir creando documentos automáticamente.
          </p>
          <button
            type="button"
            onClick={connectGoogleAccount}
            className="px-3 py-1.5 rounded-lg bg-amber-500 text-white text-xs font-semibold hover:bg-amber-600 transition-colors"
          >
            Actualizar permisos
          </button>
        </div>
      ) : null}
    </div>
  );

  const googleWorkspaceSection = (
    <div className="space-y-3">
      {/* Mostrar banner solo si el usuario intentó usar Google Workspace y hay problemas */}
      {attemptedGoogleWorkspace && (needsGoogleRelink || !isGoogleLinked) && googleStatusBanner}

      <GoogleResourceList
        resources={googleResources}
        isLoading={isLoadingResources}
        onDelete={deleteResource}
        onOpen={(url) => window.open(url, '_blank')}
      />
    </div>
  );

  useEffect(() => {
    if (tareaId) {
      cargarDatosTarea();
    }
  }, [tareaId]);

  /**
   * Maneja la descarga de archivos correctamente
   */
  const handleDescargarArchivo = async (url: string, nombre: string) => {
    try {
      // Crear elemento de link temporal
      const link = document.createElement('a');
      link.href = url;
      link.download = nombre || 'archivo';
      link.target = '_blank';
      link.rel = 'noopener noreferrer';

      // Agregar al DOM, hacer click, remover
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success(`Descargando: ${nombre}`);
    } catch (error) {
      console.error('Error descargando archivo:', error);
      toast.error('Error al descargar el archivo');
    }
  };

  const cargarDatosTarea = async () => {
    if (!tareaId) return;

    try {
      setLoading(true);
      setErrorCarga(null);

      // 1. Cargar detalles de la tarea
      const tareaData = await apiClientTareas.obtenerTarea(tareaId);
      setTarea(tareaData);

      // 2. Intentar obtener la entrega existente
      if (tareaData.mi_entrega_id) {
        try {
          const entregaDetalle = await apiClientTareas.obtenerEntrega(tareaData.mi_entrega_id);
          setEntregaExistente(entregaDetalle);
        } catch (err) {
          console.warn("No se pudo cargar la entrega existente:", err);
          // No establecer error, solo advertencia en consola
        }
      } else {
        // Limpiar entrega existente si no hay ninguna
        setEntregaExistente(null);
      }


    } catch (error: any) {
      console.error('Error cargando tarea:', error);
      let mensaje = 'Error al cargar la información de la tarea';
      if (error?.response) {
        if (error.response.status === 404) {
          mensaje = 'La tarea no existe o fue eliminada.';
        } else if (error.response.status === 403) {
          mensaje = 'No tienes permisos para ver esta tarea.';
        } else if (error.response.data?.detail) {
          mensaje = error.response.data.detail;
        }
      }
      setErrorCarga(mensaje);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Poblar archivos/enlaces existentes SOLO en carga inicial, NO después de enviar
  const [yaCargoExistentes, setYaCargoExistentes] = useState(false);

  useEffect(() => {
    // Solo cargar existentes la PRIMERA vez, no cada vez que cambia entregaExistente
    if (entregaExistente && !yaCargoExistentes) {
      // Poblar archivos existentes
      if (entregaExistente.archivos_adicionales) {
        let archivos = entregaExistente.archivos_adicionales;
        // Si es un objeto con propiedad 'archivos' (formato nuevo)
        if (!Array.isArray(archivos) && (archivos as any).archivos) {
          archivos = (archivos as any).archivos;
        }

        if (Array.isArray(archivos)) {
          setArchivosExistentes(archivos);
        } else {
          setArchivosExistentes([]);
        }
      } else {
        setArchivosExistentes([]);
      }

      // Poblar enlaces existentes  
      if (entregaExistente.enlaces_externos && Array.isArray(entregaExistente.enlaces_externos)) {
        setEnlacesExistentes(entregaExistente.enlaces_externos);
      } else {
        setEnlacesExistentes([]);
      }

      setYaCargoExistentes(true);  // Marcar como cargado
    } else if (!entregaExistente) {
      // Si no hay entrega, limpiar y resetear flag
      setArchivosExistentes([]);
      setEnlacesExistentes([]);
      setYaCargoExistentes(false);
    }
  }, [entregaExistente, yaCargoExistentes]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files);
      agregarArchivos(files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const files = Array.from(e.target.files);
      agregarArchivos(files);
    }
  };

  const agregarArchivos = (files: File[]) => {
    const archivosValidos = files.filter(file => {
      // Validar tamaño (asumiendo límite de la tarea o 10MB por defecto)
      const maxSize = tarea?.tamano_maximo_mb ? tarea.tamano_maximo_mb * 1024 * 1024 : 10 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error(`Archivo ${file.name} es demasiado grande (máx. ${tarea?.tamano_maximo_mb || 10}MB)`);
        return false;
      }
      return true;
    });

    const nuevosArchivos: ArchivoSubido[] = archivosValidos.map(file => ({
      file,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));

    setArchivos(prev => [...prev, ...nuevosArchivos]);
  };

  const removerArchivo = (index: number) => {
    const nuevos = [...archivos];
    if (nuevos[index].preview) {
      URL.revokeObjectURL(nuevos[index].preview!);
    }
    setArchivos(archivos.filter((_, i) => i !== index));
  };

  const agregarEnlace = () => {
    // Validar URL
    if (!linkUrl.trim()) {
      toast.error('Por favor ingresa una URL');
      return;
    }

    // Validar formato de URL
    try {
      new URL(linkUrl);
    } catch {
      toast.error('Por favor ingresa una URL válida');
      return;
    }

    // Agregar enlace
    setEnlaces(prev => [...prev, {
      url: linkUrl.trim(),
      titulo: linkTitulo.trim() || linkUrl.trim()
    }]);

    // Limpiar modal
    setLinkUrl('');
    setLinkTitulo('');
    setShowLinkModal(false);
    toast.success('Enlace agregado');
  };

  const removerEnlace = (index: number) => {
    setEnlaces(enlaces.filter((_, i) => i !== index));
    toast.success('Enlace eliminado');
  };

  // ✅ Nuevos handlers para eliminar archivos/enlaces EXISTENTES
  const removerArchivoExistente = (index: number) => {
    setArchivosExistentes(prev => prev.filter((_, i) => i !== index));
    toast.success('Archivo eliminado');
  };

  const removerEnlaceExistente = (index: number) => {
    setEnlacesExistentes(prev => prev.filter((_, i) => i !== index));
    toast.success('Enlace eliminado');
  };

  const handleCancelarEntrega = async () => {
    if (!entregaExistente?.entrega_id) {
      toast.error('No hay entrega para cancelar');
      return;
    }

    // Confirmar con el usuario
    if (!window.confirm('¿Estás seguro de que quieres cancelar tu entrega? Podrás volver a entregar cuando quieras.')) {
      return;
    }

    try {
      setCancelling(true);
      await apiClientTareas.cancelarEntrega(entregaExistente.entrega_id);

      toast.success('Entrega cancelada. Puedes volver a entregar cuando quieras.');

      // ✅ FIX: Recargar la entrega CANCELADA para mostrar los archivos
      // pero el formulario quedará habilitado porque yaEntrego = false (estado !== 'entregada')
      try {
        const entregaActualizada = await apiClientTareas.obtenerEntrega(entregaExistente.entrega_id);
        setEntregaExistente(entregaActualizada);
      } catch (err) {
        console.warn("No se pudo recargar entrega después de cancelar:", err);
        setEntregaExistente(null);
      }

    } catch (error: any) {
      console.error('Error cancelando entrega:', error);
      const msg = error?.response?.data?.detail || 'Error al cancelar la entrega. Inténtalo de nuevo.';
      toast.error(msg);
    } finally {
      setCancelling(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!tareaId || !tarea) return;

    // Permitir enviar solo comentarios, solo archivos, o ambos
    // No requerir que haya al menos uno

    try {
      setSubmitting(true);

      // 1. Crear la entrega (inicializar)
      // Crear FormData para enviar
      const entregaData = new FormData();
      entregaData.append('contenido', comentarios || 'Entrega de tarea');

      // ✅ CRÍTICO: Enviar archivos EXISTENTES a conservar (URLs)
      if (archivosExistentes.length > 0) {
        entregaData.append('archivos_existentes', JSON.stringify(archivosExistentes));
      }

      // ✅ Agregar archivos NUEVOS al FormData
      archivos.forEach((archivo) => {
        entregaData.append('archivos', archivo.file);
      });

      // ✅ CRÍTICO: Enviar enlaces EXISTENTES a conservar
      if (enlacesExistentes.length > 0) {
        entregaData.append('enlaces_existentes', JSON.stringify(enlacesExistentes));
      }

      // ✅ Agregar enlaces NUEVOS como JSON string
      if (enlaces.length > 0) {
        entregaData.append('enlaces', JSON.stringify(enlaces));
      }

      // Enviar la entrega (los archivos se suben aquí, NO después)
      const response = await apiClientTareas.entregarTarea(tareaId, entregaData as any);

      // Recargar datos PRIMERO para obtener la entrega actualizada
      await cargarDatosTarea();

      // Mostrar mensaje de éxito DESPUÉS de recargar
      if (archivos.length === 0 && enlaces.length === 0) {
        toast.success('✅ Tarea entregada exitosamente!');
      } else if (archivos.length > 0 && enlaces.length === 0) {
        toast.success(`✅ Tarea entregada con ${archivos.length} archivo${archivos.length > 1 ? 's' : ''}!`);
      } else if (archivos.length === 0 && enlaces.length > 0) {
        toast.success(`✅ Tarea entregada con ${enlaces.length} enlace${enlaces.length > 1 ? 's' : ''}!`);
      } else {
        toast.success(`✅ Tarea entregada con ${archivos.length} archivo${archivos.length > 1 ? 's' : ''} y ${enlaces.length} enlace${enlaces.length > 1 ? 's' : ''}!`);
      }

      // Limpiar formulario
      setComentarios('');
      setArchivos([]);
      setEnlaces([]);
      setYaCargoExistentes(false);  // ✅ Reset flag para próxima carga
      // NO redirigir - quedarse en la página para que el usuario vea su entrega

    } catch (error: any) {
      console.error('Error entregando tarea:', error);
      const msg = error?.response?.data?.detail || error?.message || 'Error al entregar la tarea. Inténtalo de nuevo.';
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const getMensajeEstadoEntrega = () => {
    if (!entregaExistente || !tarea || !entregaExistente.fecha_entrega) return null;

    const fechaEntrega = new Date(entregaExistente.fecha_entrega);
    const fechaLimite = new Date(tarea.fecha_limite);
    const esTardia = fechaEntrega > fechaLimite;

    // Calcular diferencia en horas
    const diffMs = fechaEntrega.getTime() - fechaLimite.getTime();
    const diffHoras = Math.abs(Math.floor(diffMs / (1000 * 60 * 60)));
    const diffDias = Math.floor(diffHoras / 24);

    if (!esTardia) {
      // Entregada a tiempo
      const horasAntes = Math.floor((fechaLimite.getTime() - fechaEntrega.getTime()) / (1000 * 60 * 60));
      if (horasAntes > 48) {
        return {
          texto: "¡Excelente! Entregaste con mucha anticipación 🌟",
          color: "text-green-700 dark:text-green-400",
          bg: "bg-green-50 dark:bg-green-900/20",
          border: "border-green-200 dark:border-green-800"
        };
      } else if (horasAntes > 24) {
        return {
          texto: "¡Muy bien! Entregaste a tiempo ✅",
          color: "text-green-700 dark:text-green-400",
          bg: "bg-green-50 dark:bg-green-900/20",
          border: "border-green-200 dark:border-green-800"
        };
      } else {
        return {
          texto: "Entregaste justo a tiempo ⏰",
          color: "text-blue-700 dark:text-blue-400",
          bg: "bg-blue-50 dark:bg-blue-900/20",
          border: "border-blue-200 dark:border-blue-800"
        };
      }
    } else {
      // Entregada tarde
      if (diffDias >= 7) {
        return {
          texto: `Entregaste ${diffDias} días después de la fecha límite ⚠️`,
          color: "text-red-700 dark:text-red-400",
          bg: "bg-red-50 dark:bg-red-900/20",
          border: "border-red-200 dark:border-red-800"
        };
      } else if (diffDias >= 1) {
        return {
          texto: `Entregaste ${diffDias} día${diffDias > 1 ? 's' : ''} tarde 📅`,
          color: "text-orange-700 dark:text-orange-400",
          bg: "bg-orange-50 dark:bg-orange-900/20",
          border: "border-orange-200 dark:border-orange-800"
        };
      } else if (diffHoras > 0) {
        return {
          texto: `Entregaste ${diffHoras} hora${diffHoras > 1 ? 's' : ''} tarde ⏱️`,
          color: "text-yellow-700 dark:text-yellow-400",
          bg: "bg-yellow-50 dark:bg-yellow-900/20",
          border: "border-yellow-200 dark:border-yellow-800"
        };
      }
    }

    return null;
  };

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  /**
   * Obtiene el color según la calificación (1-5)
   * 1-2: Rojo (malo)
   * 2.1-3.5: Amarillo (regular)
   * 3.6-5: Verde (bueno/excelente)
   */
  const getGradeColor = (calificacion: number) => {
    if (calificacion <= 2) {
      return 'text-red-600 dark:text-red-400';
    } else if (calificacion <= 3.5) {
      return 'text-yellow-600 dark:text-yellow-400';
    } else {
      return 'text-green-600 dark:text-green-400';
    }
  };

  const getTiempoRestante = () => {
    if (!tarea?.fecha_limite) return null;

    const ahora = new Date();
    const limite = new Date(tarea.fecha_limite);
    const diferencia = limite.getTime() - ahora.getTime();

    if (diferencia <= 0) return { texto: 'Vencida', urgente: true };

    const dias = Math.floor(diferencia / (1000 * 60 * 60 * 24));
    const horas = Math.floor((diferencia % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    let texto = '';
    if (dias > 0) {
      texto = `${dias} día${dias > 1 ? 's' : ''}`;
      if (horas > 0) texto += ` ${horas}h`;
    } else {
      texto = `${horas} hora${horas > 1 ? 's' : ''}`;
    }

    return {
      texto,
      urgente: dias === 0 && horas < 24
    };
  };

  const tiempoRestante = getTiempoRestante();

  if (!tareaId) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Error de navegación
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No se especificó una tarea válida.
          </p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (errorCarga || !tarea) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Error al cargar la tarea
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-2">
            {errorCarga || 'No se pudo encontrar la información de la tarea.'}
          </p>

        </div>
      </div>
    );
  }

  // Permitir re-entrega incluso después de calificada
  // Solo bloquear si el estado es "entregada" Y no ha sido calificada aún
  const yaEntrego = false; // Siempre permitir re-entrega

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b]">
      {/* Header */}
      <div className="bg-white dark:bg-[#1f1f23] border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400 transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div className="flex flex-col">
                <h1 className="text-lg font-bold text-gray-900 dark:text-white leading-tight">
                  {tarea.titulo}
                </h1>
                <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>{tarea.tipo || 'Tarea'}</span>
                  <span>•</span>
                  <span>{formatearFecha(tarea.fecha_limite)}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {tiempoRestante && (
                <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${tiempoRestante.urgente
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                  : 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                  }`}>
                  <Clock className="h-3.5 w-3.5" />
                  {tiempoRestante.texto}
                </div>
              )}
              <div className="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-2"></div>

              {/* Dynamic Grade Color */}
              <div className="text-right">
                <p className="text-xs text-gray-500 dark:text-gray-400">Calificación</p>
                <p className={`text-lg font-bold ${entregaExistente?.calificacion !== null && entregaExistente?.calificacion !== undefined
                  ? getGradeColor(entregaExistente.calificacion)
                  : 'text-gray-400 dark:text-gray-500'
                  }`}>
                  {entregaExistente?.calificacion !== null && entregaExistente?.calificacion !== undefined
                    ? `${entregaExistente.calificacion} / ${tarea.puntuacion_maxima}`
                    : `- / ${tarea.puntuacion_maxima}`
                  }
                </p>
              </div>

              {/* Refresh Button */}
              <button
                onClick={cargarDatosTarea}
                disabled={loading}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50"
                title="Refrescar datos"
              >
                <Loader2 className={`h-4 w-4 text-gray-600 dark:text-gray-400 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Columna Izquierda: Detalles y Comentarios de Clase (8 cols) */}
          <div className="lg:col-span-8 space-y-8">

            {/* Descripción e Instrucciones */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-[#1f1f23] rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div className="p-6 space-y-6">
                {/* Descripción */}
                {tarea.descripcion && (
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-2">
                      Descripción
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {tarea.descripcion}
                    </p>
                  </div>
                )}

                <hr className="border-gray-100 dark:border-gray-800" />

                {/* Instrucciones */}
                {tarea.instrucciones && (
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-2 flex items-center gap-2">
                      <BookOpen className="h-4 w-4" /> Instrucciones
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg border border-gray-100 dark:border-gray-800">
                      {tarea.instrucciones}
                    </p>
                  </div>
                )}

                {/* Archivos Adjuntos */}
                {tarea.archivo_adjunto && (
                  <div className="mt-4">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                      <Paperclip className="h-4 w-4" /> Recursos
                    </h3>
                    <a
                      href="#"
                      className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/20 transition-colors group"
                    >
                      <div className="p-2 bg-white dark:bg-blue-900/30 rounded-md group-hover:scale-105 transition-transform">
                        <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <p className="font-medium text-blue-900 dark:text-blue-100">Material Adjunto</p>
                        <p className="text-xs text-blue-700 dark:text-blue-300">Click para descargar</p>
                      </div>
                      <Download className="h-4 w-4 text-blue-500 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  </div>
                )}
              </div>
            </motion.div>

            {/* Comentarios de la Clase */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white dark:bg-[#1f1f23] rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
                <div className="p-1.5 bg-indigo-100 dark:bg-indigo-900/30 rounded text-indigo-600 dark:text-indigo-400">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Comentarios de la clase</h3>
              </div>
              <div className="p-8 text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 mb-3">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </div>
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  No hay comentarios de la clase aún.
                </p>
                <button className="mt-3 text-sm text-blue-600 dark:text-blue-400 hover:underline font-medium">
                  Agregar un comentario a la clase
                </button>
              </div>
            </motion.div>

          </div>

          {/* Columna Derecha: Entrega y Comentarios Privados (4 cols) */}
          <div className="lg:col-span-4 space-y-6">

            {/* Tarjeta de Entrega */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white dark:bg-[#1f1f23] rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between bg-gray-50/50 dark:bg-gray-800/30">
                <h3 className="font-semibold text-gray-900 dark:text-white">Tu trabajo</h3>
                {(() => {
                  // Si tiene calificación, mostrar "Calificada"
                  if (entregaExistente?.calificacion !== null && entregaExistente?.calificacion !== undefined) {
                    return (
                      <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${entregaExistente.calificacion <= 2
                        ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        : entregaExistente.calificacion <= 3.5
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                          : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                        }`}>
                        Calificada
                      </span>
                    );
                  }

                  // Si ya entregó pero no calificada
                  if (entregaExistente) {
                    const mensajeEstado = getMensajeEstadoEntrega();
                    return mensajeEstado ? (
                      <div className={`text-xs font-medium px-2.5 py-1 rounded-full ${mensajeEstado.bg} ${mensajeEstado.border} ${mensajeEstado.color} max-w-xs text-center break-words`}>
                        {mensajeEstado.texto}
                      </div>
                    ) : (
                      <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        Entregado
                      </span>
                    );
                  }

                  // Si no ha entregado aún
                  return (
                    <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                      Asignada
                    </span>
                  );
                })()}
              </div>

              <div className="p-5 space-y-5">
                {yaEntrego ? (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Mensaje de tarea entregada con ícono - MANTENER */}
                    <div className="text-center py-4">
                      <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-2" />
                      <h4 className="font-medium text-gray-900 dark:text-white">¡Tarea entregada!</h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {entregaExistente.fecha_entrega ? formatearFecha(entregaExistente.fecha_entrega) : 'Fecha no disponible'}
                      </p>
                    </div>

                    {/* Botón Agregar o crear */}
                    {!yaEntrego && (
                      <div className="relative" ref={dropdownRef}>
                        <button
                          type="button"
                          onClick={() => setShowDropdown(!showDropdown)}
                          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-white dark:bg-[#27272a] border border-gray-300 dark:border-gray-600 rounded-lg text-blue-600 dark:text-blue-400 font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
                        >
                          <Plus className="h-5 w-5" />
                          Agregar o crear
                        </button>

                        {/* Dropdown Menu */}
                        <AnimatePresence>
                          {showDropdown && (
                            <motion.div
                              initial={{ opacity: 0, y: 10, scale: 0.95 }}
                              animate={{ opacity: 1, y: 0, scale: 1 }}
                              exit={{ opacity: 0, y: 10, scale: 0.95 }}
                              className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-[#1f1f23] rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 z-50 overflow-hidden"
                            >
                              <div className="p-2 space-y-1">
                                <p className="px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                  Adjuntar
                                </p>
                                <button
                                  type="button"
                                  onClick={() => {
                                    fileInputRef.current?.click();
                                    setShowDropdown(false);
                                  }}
                                  className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                >
                                  <Upload className="h-4 w-4 text-gray-500" />
                                  Archivo
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setShowLinkModal(true);
                                    setShowDropdown(false);
                                  }}
                                  className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                >
                                  <Link className="h-4 w-4 text-gray-500" />
                                  Enlace
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    // Lógica para Google Drive (pendiente)
                                    toast.success('Próximamente: Selector de Google Drive');
                                    setShowDropdown(false);
                                  }}
                                  className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                >
                                  <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg" alt="Drive" className="w-4 h-4" />
                                  Google Drive
                                </button>

                                <div className="h-px bg-gray-100 dark:bg-gray-800 my-1" />

                                <p className="px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                  Crear nuevo
                                </p>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setAttemptedGoogleWorkspace(true);
                                    if (!isGoogleLinked || needsGoogleRelink) {
                                      toast.error('Por favor conecta tu cuenta de Google primero');
                                      setShowDropdown(false);
                                      return;
                                    }
                                    createResource('document');
                                    setShowDropdown(false);
                                  }}
                                  className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                >
                                  <FileText className="h-4 w-4 text-blue-500" />
                                  Documento
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setAttemptedGoogleWorkspace(true);
                                    if (!isGoogleLinked || needsGoogleRelink) {
                                      toast.error('Por favor conecta tu cuenta de Google primero');
                                      setShowDropdown(false);
                                      return;
                                    }
                                    createResource('presentation');
                                    setShowDropdown(false);
                                  }}
                                  className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                >
                                  <Presentation className="h-4 w-4 text-yellow-500" />
                                  Presentación
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setAttemptedGoogleWorkspace(true);
                                    if (!isGoogleLinked || needsGoogleRelink) {
                                      toast.error('Por favor conecta tu cuenta de Google primero');
                                      setShowDropdown(false);
                                      return;
                                    }
                                    createResource('spreadsheet');
                                    setShowDropdown(false);
                                  }}
                                  className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                                >
                                  <FileSpreadsheet className="h-4 w-4 text-green-500" />
                                  Hoja de cálculo
                                </button>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    )}

                    {/* Lista de archivos y recursos */}
                    <div className="space-y-3">
                      {/* Archivos Locales */}
                      {archivos.map((archivo, index) => (
                        <ArchivoCard
                          key={index}
                          nombre={archivo.file.name}
                          tipo={archivo.file.type}
                          tamano={archivo.file.size}
                          preview={archivo.preview}
                          onRemove={!yaEntrego ? () => removerArchivo(index) : undefined}
                          onDownload={() => {
                            const url = URL.createObjectURL(archivo.file);
                            const link = document.createElement('a');
                            link.href = url;
                            link.download = archivo.file.name;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                          }}
                        />
                      ))}

                      {/* Enlaces */}
                      {enlaces.map((enlace, index) => (
                        <div key={index} className="flex items-center gap-3 p-3 bg-white dark:bg-[#27272a] border border-gray-200 dark:border-gray-700 rounded-lg group">
                          <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                            <Link className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {enlace.titulo}
                            </p>
                            <a href={enlace.url} target="_blank" rel="noopener noreferrer" className="text-xs text-gray-500 hover:text-blue-500 truncate block">
                              {enlace.url}
                            </a>
                          </div>
                          {!yaEntrego && (
                            <button
                              type="button"
                              onClick={() => removerEnlace(index)}
                              className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      ))}

                      {/* Google Workspace Resources */}
                      {googleWorkspaceSection}
                    </div>

                    {/* Input oculto para archivos */}
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      className="hidden"
                      multiple
                    />
                    <div className="mb-4">
                      {googleWorkspaceSection}
                    </div>

                    {entregaExistente?.archivos && entregaExistente.archivos.length > 0 && (
                      <div className="space-y-2">

                        {entregaExistente.archivos.map((archivo, index) => {
                          // Manejar tanto URLs simples como objetos con metadata
                          let archivoUrl = '';
                          let nombreArchivo = '';

                          if (typeof archivo === 'string') {
                            archivoUrl = archivo;
                            nombreArchivo = archivo.split('/').pop() || `Archivo ${index + 1}`;
                          } else if (typeof archivo === 'object' && archivo.url) {
                            archivoUrl = archivo.url;
                            // Priorizar nombre_original sobre nombre y UUID
                            const archivoObj = archivo as any;
                            nombreArchivo = archivoObj.nombre_original || archivo.nombre || archivo.url.split('/').pop() || `Archivo ${index + 1}`;
                          } else {
                            return null;
                          }

                          return (
                            <div
                              key={index}
                              className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700 group hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            >
                              <div className="p-2 bg-white dark:bg-gray-700 rounded shadow-sm flex-shrink-0">
                                <FileText className="h-5 w-5 text-blue-500" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{nombreArchivo}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Archivo entregado</p>
                              </div>
                              <button
                                onClick={() => handleDescargarArchivo(archivoUrl, nombreArchivo)}
                                type="button"
                                title="Descargar archivo"
                                className="p-1 text-gray-400 hover:text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                              >
                                <Download className="h-4 w-4" />
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}


                    {/* ✅ Enlaces entregados */}
                    {entregaExistente?.enlaces_externos && Array.isArray(entregaExistente.enlaces_externos) && entregaExistente.enlaces_externos.length > 0 && (
                      <div className="space-y-2">

                        {entregaExistente.enlaces_externos.map((enlace: any, index: number) => (
                          <div key={index} className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/10 rounded-lg border border-green-200 dark:border-green-800/40 group">
                            <div className="p-2 bg-white dark:bg-gray-700 rounded shadow-sm">
                              <Link className="h-5 w-5 text-green-600" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{enlace.titulo || enlace.url}</p>
                              <p className="text-xs text-gray-500 truncate">{enlace.url}</p>
                            </div>
                            <a href={enlace.url} target="_blank" rel="noopener noreferrer" className="p-1 text-gray-400 hover:text-green-600 opacity-0 group-hover:opacity-100 transition-opacity" title="Abrir enlace">
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Botón Cancelar Entrega */}
                    {/* Graded Info Message - Allows Re-submission */}
                    {entregaExistente?.calificacion !== null && entregaExistente?.calificacion !== undefined && (
                      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                        <div className="flex items-start gap-2">
                          <CheckCircle className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                              Calificada: <span className={getGradeColor(entregaExistente.calificacion)}>{entregaExistente.calificacion}/{tarea.puntuacion_maxima}</span>
                            </p>
                            <p className="text-xs text-blue-700 dark:text-blue-300 mt-0.5">
                              Puedes volver a entregar para mejorar tu trabajo (la calificación se mantiene hasta que el profesor califique de nuevo).
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Cancel Button - Only if NOT graded */}
                    {entregaExistente && !entregaExistente.calificacion && (
                      <button
                        type="button"
                        onClick={handleCancelarEntrega}
                        disabled={cancelling}
                        className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 rounded-lg font-medium hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                      >
                        {cancelling ? 'Cancelando...' : 'Cancelar Entrega'}
                      </button>
                    )}

                    {/* Calificación si existe */}
                    {entregaExistente.calificacion !== null && (
                      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-center border border-gray-100 dark:border-gray-700">
                        <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Calificación</p>
                        <div className="text-3xl font-bold text-gray-900 dark:text-white">
                          {entregaExistente.calificacion}
                          <span className="text-sm text-gray-400 font-normal">/{tarea.puntuacion_maxima}</span>
                        </div>
                      </div>
                    )}

                    {/* Botones de acción */}
                    <div className="grid grid-cols-1 gap-2">
                      {entregaExistente.retroalimentacion_ia && (
                        <div className="bg-purple-50 dark:bg-purple-900/10 rounded-lg p-4 border border-purple-100 dark:border-purple-800/30">
                          <div className="flex items-center gap-2 mb-2 text-purple-700 dark:text-purple-300 font-medium text-sm">
                            <Zap className="h-4 w-4" /> Feedback IA
                          </div>
                          <p className="text-sm text-gray-700 dark:text-gray-300 italic">
                            {typeof entregaExistente.retroalimentacion_ia === 'object'
                              ? `"${(entregaExistente.retroalimentacion_ia as any)?.comentarios_generales || 'Sin comentarios'}"`
                              : '"Sin comentarios"'}
                          </p>
                        </div>
                      )}


                    </div>
                  </form>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Archivos EXISTENTES (desde BD, eliminables) */}
                    {archivosExistentes && archivosExistentes.length > 0 && (
                      <div className="space-y-2 mb-4">
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Archivos actuales (clic en X para eliminar):</p>
                        {archivosExistentes.map((archivo: any, index: number) => {
                          const archivoUrl = archivo.url || '';
                          const nombreArchivo = archivo.nombre_original || archivo.nombre || archivo.url?.split('/').pop() || `Archivo ${index + 1}`;

                          return (
                            <div
                              key={`existente-${index}`}
                              className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/10 rounded-lg border border-green-200 dark:border-green-800/40 group hover:bg-green-100/50 dark:hover:bg-green-900/20 transition-colors"
                            >
                              <div className="p-2 bg-white dark:bg-gray-700 rounded shadow-sm flex-shrink-0">
                                <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{nombreArchivo}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Ya guardado</p>
                              </div>
                              <div className="flex items-center gap-1 flex-shrink-0">
                                <button
                                  onClick={() => handleDescargarArchivo(archivoUrl, nombreArchivo)}
                                  type="button"
                                  title="Descargar archivo"
                                  className="p-1 text-gray-400 hover:text-green-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                  <Download className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() => removerArchivoExistente(index)}
                                  type="button"
                                  title="Eliminar archivo (no se guardará en re-entrega)"
                                  className="p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                  <X className="h-4 w-4" />
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* ✅ Mostrar enlaces de entrega anterior */}
                    {/* Enlaces EXISTENTES (desde BD, eliminables) */}
                    {enlacesExistentes && enlacesExistentes.length > 0 && (
                      <div className="space-y-2 mb-4">
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Enlaces actuales (clic en X para eliminar):</p>
                        {enlacesExistentes.map((enlace: any, index: number) => (
                          <div key={`existente-enlace-${index}`} className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/10 rounded-lg border border-green-200 dark:border-green-800/40 group">
                            <div className="p-2 bg-white dark:bg-gray-700 rounded shadow-sm">
                              <Link className="h-5 w-5 text-green-600" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{enlace.titulo || enlace.url}</p>
                              <p className="text-xs text-gray-500 truncate">{enlace.url}</p>
                            </div>
                            <div className="flex items-center gap-1 flex-shrink-0">
                              <a href={enlace.url} target="_blank" rel="noopener noreferrer" className="p-1 text-gray-400 hover:text-green-600 opacity-0 group-hover:opacity-100 transition-opacity" title="Abrir enlace">
                                <ExternalLink className="h-4 w-4" />
                              </a>
                              <button
                                onClick={() => removerEnlaceExistente(index)}
                                type="button"
                                title="Eliminar enlace (no se guardará en re-entrega)"
                                className="p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Lista de archivos subidos actualmente */}
                    {archivos.length > 0 && (
                      <div className="space-y-2">
                        {archivos.map((archivo, index) => (
                          <div key={index} className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700 group">
                            <div className="p-2 bg-white dark:bg-gray-700 rounded shadow-sm">
                              {archivo.preview ? (
                                <img src={archivo.preview} alt="" className="h-8 w-8 object-cover rounded" />
                              ) : (
                                <FileText className="h-5 w-5 text-blue-500" />
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{archivo.file.name}</p>
                              <p className="text-xs text-gray-500">{(archivo.file.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                            <button
                              type="button"
                              onClick={() => removerArchivo(index)}
                              className="p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Botones de acción */}
                    <div className="grid grid-cols-1 gap-2">
                      {/* Hidden file input */}
                      <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        onChange={handleFileSelect}
                        className="hidden"
                      />

                      {/* Google Workspace section when no entrega */}
                      {googleWorkspaceSection}

                      {/* Lista de enlaces agregados - ANTES del botón */}
                      {enlaces.length > 0 && (
                        <div className="space-y-2">
                          {enlaces.map((enlace, index) => (
                            <div
                              key={index}
                              className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/10 rounded-lg border border-green-200 dark:border-green-800/40 group hover:bg-green-100/50 dark:hover:bg-green-900/20 transition-colors"
                            >
                              <div className="p-2 bg-white dark:bg-gray-700 rounded shadow-sm flex-shrink-0">
                                <ExternalLink className="h-5 w-5 text-green-600 dark:text-green-400" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{enlace.titulo}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{enlace.url}</p>
                              </div>
                              <button
                                onClick={() => removerEnlace(index)}
                                type="button"
                                title="Eliminar enlace"
                                className="p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Botón único "Agregar o crear" - mismo estilo que Cancelar Entrega */}
                      <button
                        type="button"
                        onClick={() => setShowAgregarModal(true)}
                        className="w-full px-4 py-2.5 bg-white dark:bg-gray-800 border-2 border-blue-300 dark:border-blue-700 text-blue-600 dark:text-blue-400 rounded-lg font-medium hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200 flex items-center justify-center gap-2"
                      >
                        <Plus className="h-5 w-5" />
                        Agregar o crear
                      </button>

                      {/* Botón Entregar Tarea con estilo glassmorphism */}
                      <button
                        type="submit"
                        disabled={submitting || (() => {
                          const tieneArchivosNuevos = archivos.length > 0;
                          const tieneComentarios = comentarios.trim().length > 0;
                          const tieneEnlaces = enlaces.length > 0;
                          const tieneArchivosAnteriores =
                            (entregaExistente?.estado as string) === 'cancelada' &&
                            (entregaExistente?.archivos?.length || 0) > 0;

                          // Puede entregar si tiene AL MENOS UNO de estos:
                          // - Archivos nuevos
                          // - Comentarios
                          // - Enlaces
                          // - Archivos anteriores de entrega cancelada
                          return !(tieneArchivosNuevos || tieneComentarios || tieneEnlaces || tieneArchivosAnteriores);
                        })()}
                        className="w-full px-4 py-2.5 bg-white dark:bg-gray-800 border-2 border-green-300 dark:border-green-700 text-green-600 dark:text-green-400 rounded-lg font-medium hover:bg-green-50 dark:hover:bg-green-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
                      >
                        {
                          submitting ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                              Entregando...
                            </>
                          ) : (
                            <>
                              <Send className="h-4 w-4" />
                              Entregar Tarea
                            </>
                          )}
                      </button>

                      {yaEntrego && entregaExistente && !entregaExistente.calificacion && (
                        <button
                          type="button"
                          onClick={handleCancelarEntrega}
                          disabled={cancelling}
                          className="px-6 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
                        >
                          {cancelling ? 'Cancelando...' : 'Cancelar Entrega'}
                        </button>
                      )}
                    </div>
                  </form>
                )}
              </div>
            </motion.div>

            {/* Comentarios Privados */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-[#1f1f23] rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
                <div className="p-1.5 bg-gray-100 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Comentarios privados</h3>
              </div>

              <div className="p-4 space-y-4">
                {/* Lista de comentarios (simulada o real) */}
                {entregaExistente?.comentarios_estudiante && (
                  <div className="flex gap-3 justify-end">
                    <div className="bg-blue-50 dark:bg-blue-900/20 text-gray-800 dark:text-gray-200 p-3 rounded-2xl rounded-tr-none text-sm max-w-[85%]">
                      <p>{entregaExistente.comentarios_estudiante}</p>
                      <span className="text-[10px] text-gray-400 mt-1 block text-right">Tú</span>
                    </div>
                  </div>
                )}

                {/* Input para nuevo comentario */}
                <div className="relative">
                  <textarea
                    value={comentarios}
                    onChange={(e) => setComentarios(e.target.value)}
                    placeholder="Añadir un comentario privado..."
                    rows={1}
                    className="w-full pl-4 pr-10 py-3 border border-gray-200 dark:border-gray-700 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white resize-none text-sm"
                  />
                  <button
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-full transition-colors"
                    disabled={!comentarios.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.div>

          </div>
        </div>
      </div >

      {/* Modal "Agregar o crear" */}
      {/* Modal "Agregar o crear" */}
      {showAgregarModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4" onClick={() => setShowAgregarModal(false)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white dark:bg-[#1f1f23] rounded-lg shadow-2xl max-w-xs w-full overflow-hidden"
          >
            {/* Header */}
            <div className="px-3 py-2.5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-1.5">
                <Plus className="h-4 w-4 text-blue-600" />
                Agregar o crear
              </h3>
              <button
                onClick={() => setShowAgregarModal(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
              >
                <X className="h-4 w-4 text-gray-500" />
              </button>
            </div>

            {/* Options */}
            <div className="p-1.5">
              {/* Upload options */}
              <div className="space-y-1">
                {/* Google Drive */}
                <button
                  onClick={() => {
                    setShowAgregarModal(false);
                    toast('Integración con Google Drive próximamente', { icon: '🚀' });
                  }}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left"
                >
                  <div className="p-1.5 bg-white dark:bg-gray-700 rounded shadow-sm">
                    <Triangle className="h-4 w-4 text-blue-500" />
                  </div>
                  <span className="text-xs font-medium text-gray-900 dark:text-white">Google Drive</span>
                </button>

                {/* Vínculo */}
                <button
                  onClick={() => {
                    setShowAgregarModal(false);
                    setShowLinkModal(true);
                  }}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left"
                >
                  <div className="p-1.5 bg-white dark:bg-gray-700 rounded shadow-sm">
                    <Link className="h-4 w-4 text-gray-700 dark:text-gray-300" />
                  </div>
                  <span className="text-xs font-medium text-gray-900 dark:text-white">Vínculo</span>
                </button>

                {/* Archivo */}
                <button
                  onClick={() => {
                    setShowAgregarModal(false);
                    fileInputRef.current?.click();
                  }}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left"
                >
                  <div className="p-1.5 bg-white dark:bg-gray-700 rounded shadow-sm">
                    <Upload className="h-4 w-4 text-gray-700 dark:text-gray-300" />
                  </div>
                  <span className="text-xs font-medium text-gray-900 dark:text-white">Archivo</span>
                </button>
              </div>

              {/* Separator */}
              <div className="my-2 px-2">
                <div className="border-t border-gray-200 dark:border-gray-700"></div>
                <p className="text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mt-2 mb-0.5">
                  Crear nuevo
                </p>
              </div>

              {/* Creation options */}
              <div className="space-y-1">
                {/* Documentos */}
                <button
                  onClick={async () => {
                    console.log('📄 Click en Documento');
                    setShowAgregarModal(false);
                    try {
                      await createResource({ type: 'document', title: `Documento de ${tarea?.titulo || 'Tarea'}` });
                      console.log('✅ Documento creado exitosamente');
                    } catch (err) {
                      console.error('❌ Error creando documento:', err);
                      toast.error('Error al crear documento');
                    }
                  }}
                  disabled={isLoadingResources}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left disabled:opacity-50"
                >
                  <div className="p-1.5 bg-blue-100 dark:bg-blue-900/30 rounded shadow-sm">
                    <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  </div>
                  <span className="text-xs font-medium text-gray-900 dark:text-white">Documentos</span>
                </button>

                {/* Presentaciones */}
                <button
                  onClick={async () => {
                    console.log('📊 Click en Presentación');
                    setShowAgregarModal(false);
                    try {
                      await createResource({ type: 'presentation', title: `Presentación de ${tarea?.titulo || 'Tarea'}` });
                      console.log('✅ Presentación creada exitosamente');
                    } catch (err) {
                      console.error('❌ Error creando presentación:', err);
                      toast.error('Error al crear presentación');
                    }
                  }}
                  disabled={isLoadingResources}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left disabled:opacity-50"
                >
                  <div className="p-1.5 bg-yellow-100 dark:bg-yellow-900/30 rounded shadow-sm">
                    <Presentation className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                  </div>
                  <span className="text-xs font-medium text-gray-900 dark:text-white">Presentaciones</span>
                </button>

                {/* Hojas de cálculo */}
                <button
                  onClick={async () => {
                    console.log('📈 Click en Hoja de cálculo');
                    setShowAgregarModal(false);
                    try {
                      await createResource({ type: 'spreadsheet', title: `Hoja de cálculo de ${tarea?.titulo || 'Tarea'}` });
                      console.log('✅ Hoja de cálculo creada exitosamente');
                    } catch (err) {
                      console.error('❌ Error creando hoja de cálculo:', err);
                      toast.error('Error al crear hoja de cálculo');
                    }
                  }}
                  disabled={isLoadingResources}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left disabled:opacity-50"
                >
                  <div className="p-1.5 bg-green-100 dark:bg-green-900/30 rounded shadow-sm">
                    <FileSpreadsheet className="h-4 w-4 text-green-600 dark:text-green-400" />
                  </div>
                  <span className="text-xs font-medium text-gray-900 dark:text-white">Hojas de cálculo</span>
                </button>

                {/* Dibujos */}
                <button
                  onClick={async () => {
                    console.log('🎨 Click en Dibujo');
                    setShowAgregarModal(false);
                    try {
                      await createResource({ type: 'drawing', title: `Dibujo de ${tarea?.titulo || 'Tarea'}` });
                      console.log('✅ Dibujo creado exitosamente');
                    } catch (err) {
                      console.error('❌ Error creando dibujo:', err);
                      toast.error('Error al crear dibujo');
                    }
                  }}
                  disabled={isLoadingResources}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left disabled:opacity-50"
                >
                  <div className="p-1.5 bg-red-100 dark:bg-red-900/30 rounded shadow-sm">
                    <Palette className="h-4 w-4 text-red-600 dark:text-red-400" />
                  </div>
                  <span className="text-xs font-medium text-gray-900 dark:text-white">Dibujos</span>
                </button>

                {/* Vida */}
                <button
                  onClick={() => {
                    setShowAgregarModal(false);
                    toast('Crear videos próximamente', { icon: '🎬' });
                  }}
                  className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors text-left"
                >
                  <div className="p-1.5 bg-purple-100 dark:bg-purple-900/30 rounded shadow-sm">
                    <Play className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="flex-1 flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-900 dark:text-white">Vida</span>
                    <span className="text-[10px] font-semibold px-1.5 py-0.5 bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400 rounded-full">
                      Novedad
                    </span>
                  </div>
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Modal para agregar enlace */}
      {
        showLinkModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white dark:bg-[#1f1f23] rounded-xl shadow-2xl max-w-md w-full p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Link className="h-5 w-5 text-green-600" />
                  Agregar enlace
                </h3>
                <button
                  onClick={() => {
                    setShowLinkModal(false);
                    setLinkUrl('');
                    setLinkTitulo('');
                  }}
                  className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                >
                  <X className="h-5 w-5 text-gray-500" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    URL del enlace *
                  </label>
                  <input
                    type="url"
                    value={linkUrl}
                    onChange={(e) => setLinkUrl(e.target.value)}
                    placeholder="https://ejemplo.com"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Título (opcional)
                  </label>
                  <input
                    type="text"
                    value={linkTitulo}
                    onChange={(e) => setLinkTitulo(e.target.value)}
                    placeholder="Nombre descriptivo del enlace"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>

                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() => {
                      setShowLinkModal(false);
                      setLinkUrl('');
                      setLinkTitulo('');
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={agregarEnlace}
                    disabled={!linkUrl.trim()}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Agregar
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )
      }
    </div >
  );
}