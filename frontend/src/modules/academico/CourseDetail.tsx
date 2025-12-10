import { EmojiReactions } from '../../components/EmojiReactions';
import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
;
import { useNavigate } from 'react-router-dom';
import { UserAvatar } from '../../utils/avatarHelpers';

import courseService from './services/courseService';
// Cliente API para tareas (detalle de entregas)
import { apiClientTareas } from '../tareas/api';
import { getUserInfo } from '../../utils/auth';
import { AlertCircle, ArrowLeft, Bell, Book, BookOpen, Calendar, Check, Clipboard, Download, Edit3, Eye, File, FileText, Flag, Home, Image, Loader2, Mail, MessageCircle, MoreVertical, Paperclip, Phone, Plus, Save, Search, Send, Settings, Shield, Star, Trash2, User, Users, Video, X } from 'lucide-react';

// Importar componentes de tareas
import { TareaFormModal } from '../../pages/tareas/components/TareaFormModal';
import { TareasAccordion } from '../../pages/tareas/components/TareasAccordion';
import { TareasStatistics } from '../../pages/tareas/components/TareasStatistics';
import { TareaPreviewModal } from '../../pages/tareas/components/TareaPreviewModal';
import { EntregasList } from '../../components/EntregasList';
import { EstadoTarea } from '../../modules/tareas/types';
import { CrearTareaForm } from '../../modules/tareas/components/CrearTareaForm';
import { Tarea } from '../../modules/tareas/types';

// Base URL para archivos estáticos
const API_BASE_URL = 'http://localhost:8000';

interface CourseDetailProps {
  courseId: string;
  onBack: () => void;
}

interface Course {
  id: string;
  nombre: string;
  codigo: string;
  profesor: string;
  descripcion: string;
  estudiantes: number;
  estado: string;
  fechaInicio: string;
  fechaFin: string;
  progreso?: number;
  programa?: {
    id: string;
    nombre: string;
    codigo: string;
    facultad?: string;
  };
  personas?: {
    estudiantes: Person[];
    profesores: Person[];
    total_estudiantes: number;
    total_profesores: number;
  };
}

interface Person {
  id: string;
  nombres: string;
  apellidos: string;
  nombre_completo: string;
  correo: string;
  avatar_url?: string;
  fecha_vinculacion?: string;
  fecha_asignacion?: string;
  ultimo_acceso?: string;
  rol: 'estudiante' | 'docente';
  // No existe correo_institucional, usar correo
}

interface ArchivoAdjunto {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  archivo_id?: string;
  nombre?: string;
  tamaño?: number;
  tipo?: string;
}

interface Reply {
  id: string;
  autor: string;
  autor_id?: string;
  contenido: string;
  fecha: string;
  tipo: string;
  archivos: ArchivoAdjunto[];
  editado: boolean;
}

interface StreamPost {
  id: string;
  tipo: 'anuncio' | 'pregunta' | 'comentario' | 'respuesta' | 'tarea' | 'material';
  titulo: string;
  contenido: string;
  autor: string;
  autor_id?: string;
  fecha: string;
  adjuntos?: string[];
  comentarios?: number;
  archivos?: ArchivoAdjunto[];
  respuestas?: Reply[];
  editado?: boolean;
}

interface Task {
  id: string;
  titulo: string;
  descripcion: string;
  fechaCreacion: string;
  fechaVencimiento: string;
  puntos: number;
  estado: 'pendiente' | 'entregado' | 'calificado';
  archivos?: {
    id: string;
    name: string;
    size: number;
    type: string;
    url: string;
  }[];
  entrega?: {
    id: string;
    fechaEntrega: string;
    archivos: any[];
    comentario?: string;
    calificacion?: number;
  };
  // Entregas completas (si se obtiene detalle desde el backend)
  entregas?: any[];
}

export default function CourseDetail({ courseId, onBack }: CourseDetailProps): JSX.Element {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('stream');
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [streamPosts, setStreamPosts] = useState<StreamPost[]>([]);
  const [newPostContent, setNewPostContent] = useState('');
  const [newPostType, setNewPostType] = useState<'anuncio' | 'pregunta' | 'comentario'>('comentario');
  const [creatingPost, setCreatingPost] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [uploadingFiles, setUploadingFiles] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showEmojiPicker, setShowEmojiPicker] = useState<{ [key: string]: boolean }>({});
  const [postReactions, setPostReactions] = useState<{ [key: string]: any[] }>({});
  const [showAllStudents, setShowAllStudents] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [showCourseSettings, setShowCourseSettings] = useState(false);
  const [expandedPost, setExpandedPost] = useState<string | null>(null);
  const [postComments, setPostComments] = useState<{ [key: string]: Reply[] }>({});
  const [newComment, setNewComment] = useState<{ [key: string]: string }>({});
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTarea, setSelectedTarea] = useState<Tarea | null>(null);
  const [showTaskDetail, setShowTaskDetail] = useState(false);
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [grupoId, setGrupoId] = useState<string>('');
  const [docenteId, setDocenteId] = useState<string>('');
  const [taskFormData, setTaskFormData] = useState({
    titulo: '',
    descripcion: '',
    fechaVencimiento: '',
    puntos: 100
  });
  const [creatingTask, setCreatingTask] = useState(false);
  const [calendarEvents, setCalendarEvents] = useState<any[]>([]); // TODO: tipar eventos si es necesario
  const [showCreateEvent, setShowCreateEvent] = useState(false);
  const [eventFormData, setEventFormData] = useState({
    titulo: '',
    descripcion: '',
    fecha: '',
    tipo: 'evaluacion' // evaluacion, entrega, clase, otro
  });

  const [openPostDropdown, setOpenPostDropdown] = useState<string | null>(null);
  const [editingPost, setEditingPost] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState<string>('');
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportingPost, setReportingPost] = useState<string | null>(null);
  const [reportReason, setReportReason] = useState('');
  const [reportDescription, setReportDescription] = useState('');
  const [submittingReport, setSubmittingReport] = useState(false);

  // Memoized task data processing for components
  const processedTaskData = React.useMemo(() => {
    console.log(`🔄 Processing ${tasks.length} tasks...`);

    // ✅ FIX: Eliminar duplicados ANTES de procesar
    const uniqueTasks = tasks.filter((task, index, self) =>
      index === self.findIndex(t => t.id === task.id)
    );

    if (uniqueTasks.length !== tasks.length) {
      console.warn(`⚠️ DUPLICADOS ENCONTRADOS: ${tasks.length} tareas, ${uniqueTasks.length} únicas`);
      console.warn(`   Duplicados removidos: ${tasks.length - uniqueTasks.length}`);
    }

    // Mapear Task a Tarea (estructura canonical)
    const transformedTasks = uniqueTasks.map(task => ({
      tarea_id: task.id,
      titulo: task.titulo,
      descripcion: task.descripcion,
      fecha_limite: task.fechaVencimiento,
      fecha_creacion: task.fechaCreacion,
      puntuacion_maxima: task.puntos,
      estado: (() => {
        const now = new Date();
        const deadline = task.fechaVencimiento ? new Date(task.fechaVencimiento) : null;
        const isExpired = deadline && deadline < now;

        if (task.estado === 'calificado') return EstadoTarea.CALIFICADA;
        if (task.estado === 'entregado') return EstadoTarea.ENTREGADA;
        if (isExpired && task.estado === 'pendiente') return EstadoTarea.VENCIDA;
        return EstadoTarea.ASIGNADA;
      })(),
      archivos_adjuntos: task.archivos?.map(a => ({
        archivo_id: a.id,
        nombre: a.name,
        tipo: a.type,
        tamaño: a.size,
        url: a.url
      })) || [],
      prioridad: 'media',
      tipo: 'otro',
      grupo_id: '',
      docente_id: '',
      clase_id: '',
      permite_entrega_tardia: false,
      penalizacion_tardia: 0,
      intentos_maximos: 1,
      tamano_maximo_mb: 10,
      peso_evaluacion: 1,
      habilitar_retroalimentacion_ia: false,
      visible_estudiantes: true,
      requiere_confirmacion_lectura: false,
    }));

    // Agrupar por EstadoTarea
    const grouped: Record<EstadoTarea, any[]> = {
      [EstadoTarea.ASIGNADA]: [],
      [EstadoTarea.EN_PROGRESO]: [],
      [EstadoTarea.ENTREGADA]: [],
      [EstadoTarea.CALIFICADA]: [],
      [EstadoTarea.VENCIDA]: [],
      [EstadoTarea.CERRADA]: [],
    };
    transformedTasks.forEach(task => {
      grouped[task.estado]?.push(task);
    });

    console.log(`✅ Processed ${transformedTasks.length} unique tasks`);

    return {
      tareas: transformedTasks,
      tareasPorEstado: grouped
    };
  }, [tasks]); // ✅ FIX: Removed courseId - only depend on tasks array

  // Helper para obtener email del usuario desde el token
  const getCurrentUserEmail = () => {
    // Intentar obtener desde localStorage (diferentes claves posibles)
    const storedEmails = [
      localStorage.getItem('userEmail'),
      localStorage.getItem('user_email'),
      localStorage.getItem('email')
    ].filter(Boolean);

    if (storedEmails.length > 0) {
      return storedEmails[0];
    }

    // Intentar extraer del token JWT
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.email || payload.user_email || payload.sub;
      }
    } catch (error) {
      console.warn('Error decodificando token:', error);
    }

    return null;
  };

  // Memoized boolean to check if current user is professor to avoid repeated log spam
  const isCurrentUserProfessor = React.useMemo(() => {
    try {
      const currentUserEmail = getCurrentUserEmail();
      console.log('🔍 DEBUG: Verificando permisos de profesor');
      console.log('  - Email del usuario actual:', currentUserEmail);
      console.log('  - Profesores del curso:', course?.personas?.profesores?.map(p => ({ id: p.id, correo: p.correo, nombre: p.nombre_completo })));

      if (!currentUserEmail || !course?.personas?.profesores) {
        console.log('❌ DEBUG: Faltan datos - currentUserEmail:', !!currentUserEmail, 'profesores:', !!course?.personas?.profesores);
        return false;
      }

      const isProfessor = course.personas.profesores.some(profesor => {
        const profesorEmail = profesor.correo?.toLowerCase().trim();
        const userEmail = currentUserEmail.toLowerCase().trim();
        const match = profesorEmail === userEmail;
        console.log(`  - Comparando: "${profesorEmail}" === "${userEmail}" => ${match}`);
        return match;
      });

      console.log('🎯 DEBUG: Resultado final - usuario ES profesor:', isProfessor);
      return isProfessor;
    } catch (error) {
      console.error('❌ DEBUG: Error verificando permisos de profesor:', error);
      return false;
    }
  }, [course?.personas?.profesores]);

  // Debug log for rendering
  console.log('🎨 DEBUG: Renderizando CourseDetail - isCurrentUserProfessor:', isCurrentUserProfessor);

  useEffect(() => {
    loadCourseData();
  }, [courseId]);


  // Cerrar dropdown de personas al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (openDropdown) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [openDropdown]);

  // Cerrar menú de tres puntos de posts al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // Buscar si el click fue fuera del menú de post (busca clase especial)
      const target = event.target as Element;
      if (!target.closest('.post-dropdown-menu') && openPostDropdown) {
        setOpenPostDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [openPostDropdown]);

  // Cerrar emoji picker al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.emoji-picker-container')) {
        setShowEmojiPicker({});
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Cambiar el tipo de post por defecto si no es profesor
  useEffect(() => {
    if (course) {
      // Si es profesor y el tipo por defecto es comentario, cambiar a anuncio
      if (isCurrentUserProfessor && newPostType === 'comentario') {
        setNewPostType('anuncio');
      }
      // Si no es profesor y tiene anuncio seleccionado, cambiar a comentario
      else if (!isCurrentUserProfessor && newPostType === 'anuncio') {
        setNewPostType('comentario');
      }
    }
  }, [course]); // Se ejecuta cuando se carga el curso

  // Funciones para manejar acciones del menú
  const handleViewProfile = (person: Person, event?: React.MouseEvent) => {
    console.log('🔍 CLICK EN VER PERFIL:', {
      nombre: person.nombre_completo,
      id: person.id,
      evento: event?.type,
      navigate: typeof navigate
    });

    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    // Cerrar el dropdown primero
    setOpenDropdown(null);

    // Usar setTimeout para asegurar que la navegación ocurra después del cierre del menú
    setTimeout(() => {
      console.log('🔄 NAVEGANDO A:', `/perfil/${person.id}`);
      console.log('🔄 ESTADO DE NAVIGATE:', navigate);
      try {
        navigate(`/perfil/${person.id}`);
        console.log('✅ NAVEGACIÓN EJECUTADA');
      } catch (error) {
        console.error('❌ ERROR EN NAVEGACIÓN:', error);
      }
    }, 100);
  };

  const handleSendEmail = (person: Person) => {
    console.log('Enviar email a:', person.correo);
    window.open(`mailto:${person.correo}`, '_blank');
    setOpenDropdown(null);
  };

  const handleSendMessage = (person: Person) => {
    console.log('Enviar mensaje a:', person.nombre_completo);
    setOpenDropdown(null);
    // Aquí podrías abrir un chat o modal de mensaje
  };

  // Función para determinar si un usuario está activo (online)
  const isUserOnline = (lastAccess?: string, userEmail?: string) => {
    console.log(`🔍 Verificando estado online para: ${userEmail}, último acceso: ${lastAccess}`);

    if (!lastAccess) {
      console.log(`❌ No hay fecha de último acceso para ${userEmail}`);
      return false;
    }

    // Verificar si es el usuario actual (siempre debe aparecer como activo)
    const currentUserEmail = getCurrentUserEmail();
    if (userEmail && userEmail === currentUserEmail) {
      console.log(`✅ Usuario actual ${userEmail} - marcando como activo`);
      return true;
    }

    try {
      const lastAccessDate = new Date(lastAccess);
      const now = new Date();
      const diffInMinutes = (now.getTime() - lastAccessDate.getTime()) / (1000 * 60);

      console.log(`⏰ ${userEmail}: último acceso hace ${diffInMinutes.toFixed(1)} minutos`);

      // Considerar activo si ha accedido en las últimas 24 horas (más permisivo para testing)
      const isOnline = diffInMinutes <= 1440; // 24 horas = 1440 minutos
      console.log(`${isOnline ? '✅' : '❌'} ${userEmail} ${isOnline ? 'ACTIVO' : 'INACTIVO'}`);

      return isOnline;
    } catch (error) {
      console.error(`❌ Error parseando fecha para ${userEmail}:`, error);
      return false;
    }
  };

  const isCurrentUser = (userEmail?: string) => {
    const currentUserEmail = getCurrentUserEmail();
    return userEmail === currentUserEmail;
  };

  // Filtrar estudiantes basado en la búsqueda
  const filteredStudents = course?.personas?.estudiantes.filter(estudiante =>
    estudiante.nombre_completo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    estudiante.correo.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // Lógica para mostrar estudiantes (filtrados o no)
  const studentsToShow = searchTerm
    ? filteredStudents
    : (showAllStudents ? course?.personas?.estudiantes || [] : course?.personas?.estudiantes.slice(0, 12) || []);

  const loadCourseData = async () => {
    try {
      const startTime = performance.now();
      setLoading(true);
      setError(null);

      console.log(`🔄 Cargando datos del curso ${courseId}...`);

      // Cargar datos del curso desde la API real
      const courseResponse = await courseService.getCourseById(courseId);
      // Mostrar el contenido real del objeto recibido para depuración
      console.log('📊 Respuesta completa del curso:', JSON.stringify(courseResponse, null, 2));

      const loadTime = performance.now() - startTime;
      console.log(`⏱️ Tiempo de carga total: ${loadTime.toFixed(2)}ms`);

      // El backend devuelve directamente el objeto del curso
      // Permitir respuesta directa o envuelta en { data: ... }
      let courseData: any = courseResponse;
      // Si viene envuelto en { data: ... }
      if (courseResponse && typeof courseResponse === 'object' && 'data' in courseResponse && (courseResponse as any).data) {
        courseData = (courseResponse as any).data;
      }

      // Mapeo robusto y seguro para todos los campos esperados
      const id = courseData.id ?? courseData.curso_id ?? courseData.cursoID ?? courseData.cursoId ?? '';
      const nombre = courseData.nombre ?? courseData.titulo ?? courseData.name ?? '';
      const codigo = courseData.codigo ?? courseData.codigo_acceso ?? courseData.code ?? '';
      const profesor = typeof courseData.profesor === 'string'
        ? courseData.profesor
        : courseData.profesor?.nombre || courseData.profesor?.name || courseData.docente || courseData.teacher || courseData.institucion_nombre || 'Sin asignar';
      const descripcion = courseData.descripcion ?? courseData.description ?? '';
      const estudiantes = courseData.estudiantes ?? courseData.total_estudiantes ?? 0;
      const estado = courseData.estado ?? courseData.status ?? '';
      const fechaInicio = courseData.fecha_inicio ?? (courseData.fecha_creacion ? courseData.fecha_creacion.split('T')[0] : undefined) ?? courseData.inicio ?? '';
      const fechaFin = courseData.fecha_fin ?? courseData.fin ?? '';
      const progreso = courseData.progreso ?? courseData.progress ?? 0;
      // Personas puede no venir, poner estructura vacía
      const personas = courseData.personas ?? {
        estudiantes: [],
        profesores: [],
        total_estudiantes: 0,
        total_profesores: 0
      };

      // Si hay id y nombre, se considera válido
      if (!id || !nombre) {
        console.warn('⚠️ Estructura inesperada en respuesta de curso:', courseData);
        throw new Error('No se pudo obtener el curso: la respuesta no contiene un id o nombre válido. Consulta la consola para ver la estructura real.');
      }

      setCourse({
        id,
        nombre,
        codigo,
        profesor,
        descripcion,
        estudiantes,
        estado,
        fechaInicio,
        fechaFin,
        progreso,
        personas
      });

      // Obtener grupo_id y docente_id del curso
      if (courseData.grupo_id) {
        setGrupoId(courseData.grupo_id);
      }
      if (courseData.docente_id) {
        setDocenteId(courseData.docente_id);
      } else if (currentUser?.usuario_id) {
        setDocenteId(currentUser.usuario_id);
      }

      await loadCurrentUser({
        id,
        nombre,
        codigo,
        profesor,
        descripcion,
        estudiantes,
        estado,
        fechaInicio,
        fechaFin,
        progreso,
        personas
      });
      await loadStreamData();
      await loadTasks();

    } catch (error) {
      console.error('❌ Error cargando curso:', error);
      setError(`Error cargando el curso: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setLoading(false);
    }
  };

  const loadStreamData = async () => {
    try {
      const posts: StreamPost[] = [];

      // Cargar comentarios
      try {
        const commentsResponse = await courseService.getCourseComments(courseId);
        if (commentsResponse.success) {
          console.log('📄 Comentarios recibidos:', commentsResponse.data.length);

          console.log('📦 Comentarios raw (para debug attachments):', commentsResponse.data.map((c: any) => ({ id: c.comentario_id || c.id, archivos_adjuntos: c.archivos_adjuntos })));
          const commentPosts: StreamPost[] = commentsResponse.data.map((comment: any) => {
            // El backend devuelve campos: id, contenido, tipo, autor, fecha_creacion, archivos_adjuntos, respuestas
            return {
              id: comment.comentario_id || comment.id,
              tipo: comment.tipo || 'comentario',
              titulo: comment.tipo === 'anuncio' ? 'Anuncio del curso' : comment.tipo === 'pregunta' ? 'Pregunta' : 'Comentario',
              contenido: comment.contenido,
              autor: (comment.autor && typeof comment.autor === 'object') ? `${comment.autor.nombre} ${comment.autor.apellido}` : (comment.autor?.email || 'Desconocido'),
              autor_id: comment.autor_id || (comment.autor?.usuario_id ?? null),
              editado: comment.editado || false,
              fecha: comment.fecha_creacion || comment.fecha || '',
              comentarios: 0,
              archivos: (comment.archivos_adjuntos || []).map((a: any) => ({
                id: a.id || a.nombre || a.name || '',
                archivo_id: a.archivo_id || a.id || '',
                name: a.nombre || a.name || '',
                size: a.tamaño || a.size || 0,
                type: a.tipo || a.type || '',
                url: a.url || ''
              })),
              respuestas: (comment.respuestas || []).map((r: any) => ({
                id: r.comentario_id || r.id,
                autor: (r.autor && typeof r.autor === 'object') ? `${r.autor.nombre} ${r.autor.apellido}` : (r.autor?.email || 'Desconocido'),
                autor_id: r.autor_id || (r.autor?.usuario_id ?? null),
                contenido: r.contenido,
                fecha: r.fecha_creacion || r.fecha || '',
                tipo: r.tipo || 'respuesta',
                archivos: (r.archivos_adjuntos || []).map((a: any) => ({
                  id: a.id || a.nombre || a.name || '',
                  archivo_id: a.archivo_id || a.id || '',
                  name: a.nombre || a.name || '',
                  size: a.tamaño || a.size || 0,
                  type: a.tipo || a.type || '',
                  url: a.url || ''
                })),
                editado: r.editado || false
              }))
            };
          });
          posts.push(...commentPosts);
        }
      } catch (error) {
        console.warn('⚠️ Error cargando comentarios:', error);
      }

      // Cargar tareas
      try {
        const tasksResponse = await courseService.getCourseTasks(courseId);
        if (tasksResponse.success) {
          const taskPosts: StreamPost[] = tasksResponse.data.map((task: any) => {
            // backend puede devolver 'tarea_id' en lugar de 'id'
            const tareaId = task.id ?? task.tarea_id ?? task.tareaId ?? task.tareaID ?? undefined;
            return {
              id: `task-${tareaId}`,
              tipo: 'tarea' as const,
              titulo: task.titulo,
              contenido: task.descripcion,
              autor: task.profesor,
              fecha: task.fecha_asignacion ?? task.fecha_creacion ?? task.fecha_limite ?? '',
              adjuntos: task.archivo_adjunto ? [task.archivo_adjunto] : [],
              comentarios: task.entregas ?? 0,
              respuestas: [] // Inicializar array vacío para respuestas
            };
          });
          posts.push(...taskPosts);
        }
      } catch (error) {
        console.warn('⚠️ Error cargando tareas:', error);
      }

      // Ordenar posts por fecha (más recientes primero)
      posts.sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime());

      // Eliminar duplicados basados en ID
      const uniquePosts = posts.filter((post, index, self) =>
        self.findIndex(p => p.id === post.id) === index
      );

      setStreamPosts(uniquePosts);

      console.log(`✅ ${uniquePosts.length} posts únicos cargados en el stream (${posts.length - uniquePosts.length} duplicados removidos)`);

      // Cargar reacciones para cada post
      for (const post of uniquePosts) {
        await loadPostReactions(post.id);
      }

    } catch (error) {
      console.warn('⚠️ Error cargando datos del stream:', error);
    }
  };

  const loadTasks = async () => {
    if (!courseId) return;

    try {
      console.log('🔄 Cargando tareas del curso desde la base de datos...');
      console.log(`   courseId: ${courseId}`);
      setLoadingTasks(true);

      // Usar courseService en lugar de academicAPI directamente
      const response = await courseService.getCourseTasks(courseId);

      if (response.success) {
        console.log(`📦 API Response: ${response.data.length} tareas recibidas`);
        console.log(`   Tareas: ${response.data.map((t: any) => t.titulo || t.id).join(', ')}`);

        const tasksData = response.data.map((task: any) => ({
          id: task.id ?? task.tarea_id ?? task.tareaId ?? null,
          titulo: task.titulo,
          descripcion: task.descripcion,
          fechaCreacion: task.fechaCreacion ?? task.fecha_creacion ?? '',
          fechaVencimiento: task.fechaVencimiento ?? task.fecha_limite ?? '',
          puntos: task.puntos ?? task.puntos_base ?? 0,
          estado: task.estado ?? task.estado_tiempo ?? '',
          archivos: task.archivos || [],
          entrega: task.entrega || null
        }));

        setTasks(tasksData);
        console.log(`✅ ${tasksData.length} tareas cargadas desde la base de datos`);
      } else {
        console.error('Error en respuesta de tareas:', response.message);
        setTasks([]);
      }
    } catch (error) {
      console.error('❌ Error cargando tareas del curso:', error);
      // En caso de error, usar datos por defecto o vacío
      setTasks([]);
    } finally {
      setLoadingTasks(false);
    }
  };

  const loadCurrentUser = async (courseData: any) => {
    try {
      console.log('🔄 Cargando información del usuario actual...');

      // Usar getUserInfo para obtener datos del usuario desde el token JWT
      const userInfo = getUserInfo();

      if (userInfo) {
        // Normalizar campos esperados por la UI
        const normalized = {
          ...userInfo,
          usuario_id: userInfo.usuario_id || userInfo.id || userInfo.sub || userInfo.user_id || userInfo.userId || null,
          nombre_completo: userInfo.nombre_completo || userInfo.nombre || userInfo.full_name || userInfo.name || `${userInfo.first_name || ''} ${userInfo.last_name || ''}`.trim() || null,
          email: userInfo.email || userInfo.user_email || userInfo.email_address || null
        };
        setCurrentUser(normalized);
        console.log('✅ Usuario actual cargado (normalizado):', normalized.email, normalized.usuario_id);
      } else {
        console.warn('⚠️ No se pudo obtener información del usuario');
        setCurrentUser(null);
      }
    } catch (error) {
      console.error('❌ Error cargando usuario actual:', error);
      setCurrentUser(null);
    }
  };

  // Función para crear nueva tarea
  const handleCreateTask = async () => {
    if (!taskFormData.titulo.trim() || !taskFormData.descripcion.trim()) {
      alert('Título y descripción son requeridos');
      return;
    }

    try {
      setCreatingTask(true);
      console.log('🔄 Creando nueva tarea...');

      const response = await courseService.createTask(courseId!, taskFormData as any);

      if (response.success) {
        console.log('✅ Tarea creada exitosamente:', response.data);

        // Limpiar formulario
        setTaskFormData({
          titulo: '',
          descripcion: '',
          fechaVencimiento: '',
          puntos: 100
        });

        // Cerrar modal
        setShowCreateTask(false);

        // Recargar tareas
        await loadTasks();

        console.log('Tarea creada y lista actualizada');
      } else {
        console.error('Error creando tarea:', response.message);
        // Mostrar error específico al usuario
        if (response.message.includes('403') || response.message.includes('Solo los docentes')) {
          alert('No tienes permisos para crear tareas en este curso. Solo los profesores pueden crear tareas.');
        } else {
          alert(`Error creando tarea: ${response.message}`);
        }
      }
    } catch (error) {
      console.error('❌ Error creando tarea:', error);
      alert('Error inesperado al crear la tarea. Por favor, intenta de nuevo.');
    } finally {
      setCreatingTask(false);
    }
  };

  // Funciones del calendario
  const handleCreateEvent = () => {
    if (!eventFormData.titulo.trim() || !eventFormData.fecha) {
      alert('Título y fecha son requeridos');
      return;
    }

    const newEvent = {
      id: Date.now().toString(),
      titulo: eventFormData.titulo,
      descripcion: eventFormData.descripcion,
      fecha: eventFormData.fecha,
      tipo: eventFormData.tipo,
      createdBy: localStorage.getItem('userEmail') || 'Desconocido'
    };

    setCalendarEvents(prev => [...prev, newEvent]);

    // Limpiar formulario
    setEventFormData({
      titulo: '',
      descripcion: '',
      fecha: '',
      tipo: 'evaluacion'
    });

    setShowCreateEvent(false);

    // Simulamos el guardado en el backend
    console.log('📅 Evento creado:', newEvent);
  };

  const getEventTypeColor = (tipo: string) => {
    switch (tipo) {
      case 'evaluacion': return 'bg-red-100 text-red-800 border-red-200';
      case 'entrega': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'clase': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getEventTypeIcon = (tipo: string) => {
    switch (tipo) {
      case 'evaluacion': return <AlertCircle className="w-4 h-4" />;
      case 'entrega': return <Send className="w-4 h-4" />;
      case 'clase': return <Book className="w-4 h-4" />;
      default: return <Calendar className="w-4 h-4" />;
    }
  };

  // Funciones para manejo de archivos
  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const fileArray = Array.from(files);
      console.log('📎 Archivos seleccionados:', fileArray.map(f => f.name));
      setAttachedFiles(prev => [...prev, ...fileArray]);
    }
  };

  const removeFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleCreatePost = async () => {
    if (!newPostContent.trim() || creatingPost) return;

    // Validar permisos según el tipo de post
    if (newPostType === 'anuncio' && !isCurrentUserProfessor) {
      alert('❌ Solo los profesores pueden crear anuncios. Cambiando a comentario...');
      setNewPostType('comentario');
      return;
    }

    try {
      setCreatingPost(true);
      console.log(`🔄 Creando ${newPostType}...`);

      // Si hay archivos adjuntos, subir primero usando courseService
      let uploadedFiles: any[] = [];
      if (attachedFiles.length > 0) {
        setUploadingFiles(true);
        console.log('📤 Subiendo archivos adjuntos a la API...');

        try {
          // Subir cada archivo individualmente
          for (const file of attachedFiles) {
            const uploadResponse = await courseService.uploadFile(courseId, file, newPostType);

            if (uploadResponse.success) {
              // Formato estándar para archivos (compatible con backend)
              // IMPORTANTE: Siempre usar el archivo_id del backend, nunca generar uno aleatorio
              const archivoId = uploadResponse.data.archivo_id;
              if (!archivoId) {
                console.error('❌ El backend no retornó archivo_id para el archivo:', file.name);
                throw new Error(`Error: El servidor no retornó un ID válido para el archivo ${file.name}`);
              }

              uploadedFiles.push({
                archivo_id: archivoId,
                id: archivoId, // Usar el mismo archivo_id del backend
                nombre: uploadResponse.data.nombre || file.name,
                url: uploadResponse.data.url,
                tamaño: uploadResponse.data.tamaño || file.size,
                tipo: file.type,
                fecha_subida: new Date().toISOString() // Fecha actual si no viene del backend
              });
              console.log(`✅ Archivo subido: ${file.name} con ID: ${archivoId}`, uploadedFiles[uploadedFiles.length - 1]);
            } else {
              throw new Error(`Error subiendo ${file.name}: ${uploadResponse.message}`);
            }
          }

          console.log(`✅ Todos los archivos subidos: ${uploadedFiles.length} archivos`);
        } catch (uploadError) {
          console.error('❌ Error subiendo archivos:', uploadError);
          throw new Error(`Error subiendo archivos: ${uploadError instanceof Error ? uploadError.message : 'Error desconocido'}`);
        }
      }

      // Crear el post/anuncio con los archivos subidos
      // Solo enviar { archivo_id } de cada archivo
      const archivosAdjuntos = uploadedFiles.map(f => ({ archivo_id: f.archivo_id || f.id }));
      const postData = {
        contenido: newPostContent,
        tipo: newPostType,
        archivos_adjuntos: archivosAdjuntos
      };
      console.log('🟢 Payload comentario:', postData);
      const response = await courseService.createComment(courseId, postData);

      if (response.success && response.data) {
        console.log('✅ Post creado exitosamente en la base de datos');

        // Agregar el nuevo post al stream
        // Asegurarnos de tener currentUser para normalizar correctamente
        if (!currentUser) {
          try {
            await loadCurrentUser(course ?? {});
          } catch (e) {
            // no bloquear si falla, usaremos getUserInfo() como fallback
            console.warn('No se pudo cargar currentUser antes de normalizar post:', e);
          }
        }

        const fallbackUser = currentUser || getUserInfo();
        const newPost = normalizePost(response.data, fallbackUser);
        // Asegurar que el tipo y archivos reflejen lo esperado
        newPost.tipo = newPostType as any;
        newPost.archivos = uploadedFiles;

        // Insertar y eliminar duplicados por id (por si hubo optimistic update)
        setStreamPosts(prev => {
          const merged = [newPost, ...prev];
          const unique: StreamPost[] = [];
          const seen = new Set<string>();
          for (const p of merged) {
            if (!seen.has(String(p.id))) {
              seen.add(String(p.id));
              unique.push(p);
            }
          }
          return unique;
        });
        // Cerrar cualquier dropdown abierto para evitar estados extraños
        setOpenPostDropdown(null);
        setNewPostContent('');
        setAttachedFiles([]);

        // Mostrar mensaje de éxito
        console.log(`📝 ${newPostType.toUpperCase()} creado con ${uploadedFiles.length} archivos adjuntos`);

      } else {
        throw new Error(response.message || 'Error creando el post');
      }

    } catch (error) {
      console.error('❌ Error creando post:', error);
      setError(`Error creando el ${newPostType}: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setCreatingPost(false);
      setUploadingFiles(false);
    }
  };

  // Funciones para manejo de comentarios
  const toggleComments = async (postId: string) => {
    if (expandedPost === postId) {
      setExpandedPost(null);
    } else {
      setExpandedPost(postId);
      // No necesitamos cargar comentarios adicionales aquí
      // Las respuestas ya están incluidas en post.respuestas desde loadStreamData
    }
  };

  const handleAddComment = async (postId: string) => {
    const commentContent = newComment[postId];
    if (!commentContent?.trim()) return;

    try {
      console.log(`🔄 Agregando comentario al post ${postId}...`);
      // Crear comentario usando el API
      const commentData = {
        contenido: commentContent,
        tipo: 'comentario',
        archivos_adjuntos: [], // SIEMPRE usar la clave correcta aunque esté vacío
        comentario_padre_id: postId // Indicar que es una respuesta al post
      };
      // DEBUG extra: log para asegurar que la clave es correcta
      console.log('🟢 Payload respuesta:', commentData);
      const response = await courseService.createComment(courseId, commentData as any);
      if (response.success && response.data) {
        console.log('✅ Comentario guardado en la base de datos');
        // Normalizar la respuesta recibida
        const commentData: any = response.data;
        const newResponse: Reply = {
          id: commentData.id ?? String(Date.now()),
          autor: commentData.autor ?? (currentUser?.nombre_completo ?? 'Usuario'),
          autor_id: commentData.autor_id ?? (currentUser?.usuario_id ?? null),
          contenido: commentData.contenido ?? '',
          fecha: commentData.fecha ?? new Date().toISOString(),
          tipo: 'respuesta',
          archivos: (commentData.archivos_adjuntos || []).map((a: any) => ({
            id: a.id ?? a.archivo_id ?? String(Math.random()),
            name: a.nombre ?? a.name ?? 'Archivo',
            size: a.tamaño ?? a.size ?? 0,
            type: a.tipo ?? a.type ?? '',
            url: a.url ?? ''
          })),
          editado: commentData.editado ?? false
        };
        // Agregar la respuesta al post correspondiente en streamPosts
        setStreamPosts(prev => prev.map(post => {
          if (post.id === postId) {
            return {
              ...post,
              respuestas: [...(post.respuestas || []), newResponse]
            };
          }
          return post;
        }));
        // Limpiar el campo de comentario
        setNewComment(prev => ({
          ...prev,
          [postId]: ''
        }));
      } else {
        throw new Error(response.message || 'Error creando comentario');
      }
    } catch (error) {
      console.error('Error agregando comentario:', error);
      // Mostrar error al usuario
      alert(`Error agregando comentario: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  // Funciones para manejar posts
  const handleEditPost = async (postId: string) => {
    if (!editingContent.trim()) return;

    try {
      console.log(`🔄 Editando post ${postId}...`);

      const response = await courseService.updateComment(postId, {
        contenido: editingContent
      });

      if (response.success) {
        console.log('✅ Post editado exitosamente');

        // Actualizar el post en el stream
        setStreamPosts(prev => prev.map(post => {
          if (post.id === postId) {
            return {
              ...post,
              contenido: editingContent,
              editado: true
            };
          }
          return post;
        }));

        setEditingPost(null);
        setEditingContent('');
      } else {
        throw new Error(response.message || 'Error editando post');
      }
    } catch (error) {
      console.error('❌ Error editando post:', error);
      alert(`Error editando post: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  const handleDeletePost = async (postId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este post? Esta acción no se puede deshacer.')) {
      return;
    }

    try {
      console.log(`🔄 Eliminando post ${postId}...`);

      const response = await courseService.deleteComment(postId);

      if (response.success) {
        console.log('✅ Post eliminado exitosamente');

        // Remover el post del stream
        setStreamPosts(prev => prev.filter(post => post.id !== postId));
      } else {
        throw new Error(response.message || 'Error eliminando post');
      }
    } catch (error) {
      console.error('❌ Error eliminando post:', error);
      alert(`Error eliminando post: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  const startEditingPost = (postId: string, currentContent: string) => {
    setEditingPost(postId);
    setEditingContent(currentContent);
    setOpenPostDropdown(null);
  };

  const cancelEditingPost = () => {
    setEditingPost(null);
    setEditingContent('');
  };

  // Función para abrir modal de reporte
  const handleReportPost = (postId: string) => {
    setReportingPost(postId);
    setReportReason('');
    setReportDescription('');
    setShowReportModal(true);
    setOpenPostDropdown(null);
  };

  // Función para enviar reporte
  const submitReport = async () => {
    if (!reportingPost || !reportReason.trim()) return;

    try {
      setSubmittingReport(true);
      console.log(`🔄 Enviando reporte para post ${reportingPost}...`);

      const reportData = {
        comentario_id: reportingPost,
        razon: reportReason,
        descripcion: reportDescription.trim() || undefined
      };

      // Usar courseService para enviar el reporte
      const response = await courseService.reportComment(reportingPost, reportData);

      if (response.success) {
        console.log('✅ Reporte enviado exitosamente');

        // Cerrar modal y limpiar estado
        setShowReportModal(false);
        setReportingPost(null);
        setReportReason('');
        setReportDescription('');

        // Mostrar mensaje de éxito
        alert('Reporte enviado exitosamente. Gracias por ayudar a mantener la comunidad segura.');
      } else {
        throw new Error(response.message || 'Error enviando reporte');
      }

    } catch (error) {
      console.error('❌ Error enviando reporte:', error);
      alert(`Error enviando reporte: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setSubmittingReport(false);
    }
  };

  const loadPostReactions = async (postId: string) => {
    try {
      const response = await courseService.getPostReactions(postId);
      if (response.success) {
        setPostReactions(prev => ({
          ...prev,
          [postId]: response.data || []
        }));
      }
    } catch (error) {
      console.error('Error cargando reacciones:', error);
    }
  };

  const handleEmojiSelect = async (postId: string, emoji: string) => {
    try {
      const response = await courseService.addReaction(postId, emoji, 'like');
      if (response.success) {
        await loadPostReactions(postId);
        setShowEmojiPicker(prev => ({ ...prev, [postId]: false }));
      }
    } catch (error) {
      console.error('Error agregando reacción:', error);
    }
  };

  const toggleEmojiPicker = (postId: string) => {
    setShowEmojiPicker(prev => ({
      ...prev,
      [postId]: !prev[postId]
    }));
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  /**
   * Helpers para permisos y normalización de posts/respuestas.
   * Separar esta lógica facilita tests unitarios y evita bugs por campos faltantes
   * (p. ej. autor_id o fecha) cuando se hacen optimistic updates.
   */
  const normalizePost = (raw: any, fallbackCurrentUser: any): StreamPost => {
    const id = raw.id ?? raw.comentario_id ?? String(Date.now());
    const fecha = raw.fecha ?? raw.fecha_creacion ?? new Date().toISOString();
    const autor_id = raw.autor_id ?? raw.autor?.usuario_id ?? (fallbackCurrentUser?.usuario_id ?? null);
    const autor = raw.autor?.nombre ? `${raw.autor.nombre} ${raw.autor.apellido || ''}`.trim() : (raw.autor || (fallbackCurrentUser?.nombre_completo ?? 'Usuario'));
    const archivos = (raw.archivos || raw.archivos_adjuntos || []).map((a: any) => ({
      id: a.id ?? a.archivo_id ?? a.nombre ?? a.name ?? String(Math.random()),
      archivo_id: a.archivo_id ?? a.id ?? null,
      name: a.nombre ?? a.name ?? 'Archivo',
      tamaño: a.tamaño ?? a.size ?? 0,
      type: a.tipo ?? a.type ?? '',
      url: a.url ?? a.url ?? ''
    }));

    return {
      id: String(id),
      tipo: raw.tipo ?? raw.type ?? 'comentario',
      titulo: raw.titulo ?? (raw.tipo === 'anuncio' ? 'Anuncio del curso' : raw.titulo) ?? 'Comentario',
      contenido: raw.contenido ?? raw.mensaje ?? '',
      autor,
      autor_id: autor_id ?? null,
      editado: raw.editado ?? false,
      fecha,
      comentarios: raw.comentarios ?? 0,
      archivos,
      respuestas: (raw.respuestas || []).map((r: any) => ({
        id: r.id ?? r.comentario_id ?? String(Date.now()),
        autor: r.autor?.nombre ? `${r.autor.nombre} ${r.autor.apellido || ''}`.trim() : (r.autor || 'Usuario'),
        autor_id: r.autor_id ?? r.autor?.usuario_id ?? null,
        contenido: r.contenido ?? r.mensaje ?? '',
        fecha: r.fecha ?? r.fecha_creacion ?? new Date().toISOString(),
        tipo: r.tipo ?? 'respuesta',
        archivos: (r.archivos_adjuntos || []).map((a: any) => ({
          id: a.id ?? a.archivo_id ?? a.nombre ?? a.name ?? String(Math.random()),
          archivo_id: a.archivo_id ?? a.id ?? null,
          name: a.nombre ?? a.name ?? 'Archivo',
          tamaño: a.tamaño ?? a.size ?? 0,
          type: a.tipo ?? a.type ?? '',
          url: a.url ?? ''
        })),
        editado: r.editado ?? false
      }))
    } as StreamPost;
  };

  const canModifyByAuthorAndTime = (post: StreamPost, currentUserLocal: any, windowMinutes = 30) => {
    if (!currentUserLocal) return { canEdit: false, canDelete: false };
    const currentId = currentUserLocal.usuario_id != null ? String(currentUserLocal.usuario_id) : null;
    const postAutorId = post.autor_id != null ? String(post.autor_id) : (typeof post.autor === 'string' ? post.autor : null);
    const isAuthor = currentId && postAutorId ? currentId === postAutorId : false;
    try {
      const postDate = new Date(post.fecha);
      if (isNaN(postDate.getTime())) return { canEdit: false, canDelete: false };
      const now = new Date();
      const diffMinutes = (now.getTime() - postDate.getTime()) / (1000 * 60);
      return { canEdit: isAuthor && diffMinutes <= windowMinutes, canDelete: isAuthor && diffMinutes <= windowMinutes };
    } catch {
      return { canEdit: false, canDelete: false };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-emerald-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Cargando curso...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={onBack}
            className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            Volver a cursos
          </button>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">Curso no encontrado</p>
          <button
            onClick={onBack}
            className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            Volver a cursos
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 mt-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {course.nombre}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {course.codigo} • {course.profesor}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowCourseSettings(true)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Configuración del curso"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Course Banner */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <div className="mb-4">
                {course.programa && (
                  <div className="flex items-center space-x-2 mb-3">
                    <div className="bg-emerald-600/30 px-3 py-1 rounded-full">
                      <span className="text-emerald-100 text-sm font-medium">
                        <Book className="w-4 h-4 mr-2 text-blue-600" />
                        {course.programa.codigo} - {course.programa.nombre}
                      </span>
                    </div>
                    {course.programa.facultad && (
                      <div className="bg-emerald-700/30 px-3 py-1 rounded-full">
                        <span className="text-emerald-200 text-xs">
                          <Home className="w-4 h-4 mr-2 text-purple-600" />
                          {course.programa.facultad}
                        </span>
                      </div>
                    )}
                  </div>
                )}
                {/* Temporalmente agregando programa por defecto */}
                <div className="flex items-center space-x-2 mb-3">
                  <div className="bg-emerald-600/30 px-3 py-1 rounded-full">
                    <span className="text-emerald-100 text-sm font-medium">
                      <Book className="w-4 h-4 mr-2 text-blue-600" />
                      ISYS - Ingeniería de Sistemas
                    </span>
                  </div>
                  <div className="bg-emerald-700/30 px-3 py-1 rounded-full">
                    <span className="text-emerald-200 text-xs">
                      <Home className="w-4 h-4 mr-2 text-purple-600" />
                      Facultad de Ingeniería
                    </span>
                  </div>
                </div>
              </div>
              <h2 className="text-3xl font-bold mb-4">{course.nombre}</h2>
              <p className="text-emerald-100 mb-6 text-lg">
                {course.descripcion}
              </p>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>{course.estudiantes} estudiantes</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5" />
                  <span>{course.fechaInicio} - {course.fechaFin}</span>
                </div>
              </div>
            </div>
            <div className="flex justify-center items-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-xl flex items-center justify-center mb-2">
                  <Book className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
                <p className="text-emerald-100">Estado: {course.estado}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-8">
            {[
              { key: 'stream', label: 'Stream', icon: MessageCircle },
              { key: 'classwork', label: 'Trabajos', icon: BookOpen },
              { key: 'people', label: 'Personas', icon: Users },
              { key: 'calendar', label: 'Calendario', icon: Calendar }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center space-x-2 px-4 py-4 border-b-2 font-medium transition-colors ${activeTab === tab.key
                  ? 'border-emerald-600 text-emerald-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                  }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'stream' && (
          <div className="space-y-6">
            {/* Create Post */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center text-white font-bold">
                  {course.profesor.charAt(0)}
                </div>
                <div className="flex-1">
                  <div className="mb-4">
                    <select
                      value={newPostType}
                      onChange={(e) => setNewPostType(e.target.value as 'anuncio' | 'pregunta' | 'comentario')}
                      className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white mr-4"
                    >
                      {/* Solo profesores pueden hacer anuncios */}
                      {course && isCurrentUserProfessor && <option value="anuncio">📢 Anuncio</option>}
                      <option value="pregunta">❓ Pregunta</option>
                      <option value="comentario">💬 Comentario</option>
                    </select>
                  </div>
                  <textarea
                    value={newPostContent}
                    onChange={(e) => setNewPostContent(e.target.value)}
                    placeholder={`Escribe un ${newPostType}...`}
                    className="w-full p-4 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    rows={3}
                  />

                  {/* Vista previa de archivos adjuntos */}
                  {attachedFiles.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Archivos adjuntos ({attachedFiles.length})
                      </h4>
                      <div className="space-y-2">
                        {attachedFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-white dark:bg-gray-600 rounded border">
                            <div className="flex items-center space-x-2">
                              <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900 rounded flex items-center justify-center">
                                {file.type.startsWith('image/') ? <Image className="w-4 h-4 text-emerald-600" /> :
                                  file.type.startsWith('video/') ? <Video className="w-4 h-4 text-emerald-600" /> :
                                    file.type.includes('pdf') ? <File className="w-4 h-4 text-emerald-600" /> : <Paperclip className="w-4 h-4 text-emerald-600" />}
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-white">{file.name}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">{formatFileSize(file.size)}</p>
                              </div>
                            </div>
                            <button
                              onClick={() => removeFile(index)}
                              className="text-red-500 hover:text-red-700 p-1"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-4">
                    <div className="flex items-center space-x-3">
                      <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        onChange={handleFileChange}
                        className="hidden"
                        accept="*/*"
                      />
                      <button
                        onClick={handleFileSelect}
                        disabled={uploadingFiles}
                        className="flex items-center space-x-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
                      >
                        <Paperclip className="w-5 h-5" />
                        <span>Adjuntar archivo</span>
                      </button>
                    </div>
                    <button
                      onClick={handleCreatePost}
                      disabled={!newPostContent.trim() || creatingPost}
                      className="flex items-center space-x-2 px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {creatingPost ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          <span>Publicando...</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          <span>Publicar</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Posts */}
            {streamPosts.length === 0 ? (
              <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">No hay publicaciones aún</p>
                <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">
                  Sé el primero en publicar algo en este curso
                </p>
              </div>
            ) : (
              streamPosts.map((post, index) => (
                <motion.div
                  key={`stream-post-${post.id}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.3 }}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6"
                >
                  <div className="flex items-start space-x-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${post.tipo === 'anuncio' ? 'bg-blue-600' :
                      post.tipo === 'tarea' ? 'bg-orange-600' : 'bg-green-600'
                      }`}>
                      {post.tipo === 'anuncio' ? <Bell className="w-4 h-4" /> :
                        post.tipo === 'tarea' ? <Clipboard className="w-4 h-4" /> :
                          <File className="w-4 h-4" />}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {post.titulo}
                          </h4>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {(() => {
                              if (typeof post.autor === 'object' && (post.autor as any)?.nombre) {
                                return `${(post.autor as any).nombre} ${(post.autor as any).apellido || ''}`.trim();
                              } else if (typeof post.autor === 'string') {
                                return post.autor;
                              } else {
                                return 'Usuario';
                              }
                            })()} • {formatDate(post.fecha)}
                          </p>
                        </div>
                        <button
                          onMouseDown={(e) => e.stopPropagation()} // Evitar que el mousedown cierre inmediatamente el dropdown
                          onClick={() => setOpenPostDropdown(openPostDropdown === post.id ? null : post.id)}
                          className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                        >
                          <MoreVertical className="w-5 h-5" />
                        </button>

                        {/* Menú desplegable del post */}
                        {openPostDropdown === post.id && (
                          <div
                            data-post-dropdown={post.id}
                            onMouseDown={(e) => e.stopPropagation()} // Evitar que clicks dentro del menú lo cierren
                            className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50 post-dropdown-menu"
                          >
                            <div className="py-1">
                              {/* Solo mostrar opciones si el usuario actual es el autor */}
                              {(() => {
                                const { canEdit, canDelete } = canModifyByAuthorAndTime(post, currentUser, 30);
                                return (
                                  <>
                                    {canEdit && (
                                      <button
                                        onClick={() => startEditingPost(post.id, post.contenido)}
                                        className="w-full px-4 py-2 text-left text-sm flex items-center text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                                      >
                                        <Edit3 className="w-4 h-4 mr-2" />
                                        Editar
                                      </button>
                                    )}

                                    {canDelete && (
                                      <button
                                        onClick={() => handleDeletePost(post.id)}
                                        className="w-full px-4 py-2 text-left text-sm flex items-center text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900"
                                      >
                                        <Trash2 className="w-4 h-4 mr-2" />
                                        Eliminar
                                      </button>
                                    )}

                                    <button
                                      onClick={() => handleReportPost(post.id)}
                                      className="w-full px-4 py-2 text-left text-sm text-orange-600 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900 flex items-center"
                                    >
                                      <Flag className="w-4 h-4 mr-2" />
                                      Reportar
                                    </button>
                                  </>
                                );
                              })()}
                            </div>
                          </div>
                        )}
                      </div>

                      {editingPost === post.id ? (
                        <div className="space-y-3">
                          <textarea
                            value={editingContent}
                            onChange={(e) => setEditingContent(e.target.value)}
                            className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            rows={3}
                          />
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleEditPost(post.id)}
                              disabled={!editingContent.trim()}
                              className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                            >
                              Guardar
                            </button>
                            <button
                              onClick={cancelEditingPost}
                              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 text-sm"
                            >
                              Cancelar
                            </button>
                          </div>
                        </div>
                      ) : (
                        <p className="text-gray-700 dark:text-gray-300 mb-4">
                          {post.contenido}
                          {post.editado && (
                            <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">(editado)</span>
                          )}
                        </p>
                      )}

                      {/* Archivos adjuntos mejorados con descarga */}
                      {post.archivos && post.archivos.length > 0 && (
                        <div className="space-y-2 mb-4">
                          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                            <Paperclip className="w-4 h-4 mr-2" />
                            Archivos adjuntos ({post.archivos.length})
                          </h4>
                          {post.archivos.map((archivo) => (
                            <motion.div
                              key={archivo.id}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-all duration-200 border border-gray-200 dark:border-gray-600"
                            >
                              <div className="flex items-center space-x-3 flex-1">
                                <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                                  {(archivo.type)?.includes('image') ? (
                                    <Image className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                  ) : (archivo.type)?.includes('pdf') ? (
                                    <File className="w-5 h-5 text-red-600 dark:text-red-400" />
                                  ) : (archivo.type)?.includes('video') ? (
                                    <Video className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                                  ) : (
                                    <Paperclip className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                                  )}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                    {archivo.name || 'Archivo'}
                                  </p>
                                  <p className="text-xs text-gray-500 dark:text-gray-400">
                                    {formatFileSize(archivo.tamaño || archivo.size || 0)}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                {(archivo.tipo || archivo.type)?.includes('image') && (
                                  <button
                                    onClick={async () => {
                                      // Vista previa de imagen usando URL directa del backend
                                      const archivoId = archivo.archivo_id || archivo.id;
                                      if (!archivoId) {
                                        console.error('❌ No hay archivo_id para vista previa');
                                        return;
                                      }

                                      try {
                                        console.log('👁️ ABRIENDO VISTA PREVIA:');
                                        console.log('  Archivo ID:', archivoId);
                                        console.log('  Tipo:', archivo.type);

                                        // Construir URL directa del backend con autenticación
                                        const token = localStorage.getItem('access_token');
                                        if (!token) {
                                          alert('Debes iniciar sesión para ver archivos');
                                          return;
                                        }

                                        // URL directa para vista previa (el backend maneja la autenticación)
                                        const previewUrl = `${API_BASE_URL}/api/cursos/archivos/descargar/${archivoId}`;

                                        // Abrir en nueva pestaña directamente
                                        const newWindow = window.open(previewUrl, '_blank');
                                        if (!newWindow) {
                                          console.warn('⚠️ Popup bloqueado, intentando descarga');
                                          // Fallback: usar el método de descarga del courseService
                                          await courseService.downloadFile(archivoId);
                                        } else {
                                          console.log('✅ Vista previa abierta directamente');
                                        }
                                      } catch (error) {
                                        console.error('❌ Error en vista previa:', error);
                                        alert(`Error al cargar imagen: ${error instanceof Error ? error.message : 'Error desconocido'}`);
                                      }
                                    }}
                                    className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                                    title="Vista previa"
                                  >
                                    <Eye className="w-4 h-4" />
                                  </button>
                                )}
                                <button
                                  onClick={async () => {
                                    // Descargar archivo usando courseService
                                    const archivoId = archivo.archivo_id || archivo.id;
                                    if (!archivoId) {
                                      console.error('❌ No hay archivo_id para descargar');
                                      return;
                                    }

                                    try {
                                      console.log('📥 DESCARGANDO ARCHIVO:');
                                      console.log('  Archivo ID:', archivoId);
                                      console.log('  Nombre:', archivo.name);

                                      // Usar courseService para descargar
                                      await courseService.downloadFile(archivoId);

                                      console.log('✅ Descarga completada');
                                    } catch (error) {
                                      console.error('❌ Error descargando archivo:', error);
                                      alert(`Error al descargar archivo: ${error instanceof Error ? error.message : 'Error desconocido'}`);
                                    }
                                  }}
                                  className="p-2 text-blue-500 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-lg transition-colors"
                                  title="Descargar archivo"
                                >
                                  <Download className="w-4 h-4" />
                                </button>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                          <button
                            onClick={() => toggleComments(post.id)}
                            className="flex items-center space-x-1 hover:text-gray-700 dark:hover:text-gray-200"
                          >
                            <MessageCircle className="w-4 h-4" />
                            <span>
                              {post.respuestas?.length || 0} comentarios
                            </span>
                          </button>

                          {/* Mostrar reacciones al lado del botón de comentarios */}
                          {post.id && (
                            <div className="ml-2">
                              <EmojiReactions
                                comentarioId={post.id}
                                currentUserId={currentUser?.usuario_id}
                                apiBaseUrl={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
                                initialReactions={postReactions[post.id] || []}
                                postType={post.tipo}
                                onChange={(reactions) => setPostReactions(prev => {
                                  try {
                                    const prevList = prev?.[post.id] ?? [];
                                    const normalize = (arr: any[]) => (arr || []).map((r: any) => ({ emoji: r.emoji, cantidad: r.cantidad, users: (r.usuarios || []).map((u: any) => String(u.usuario_id)).sort() })).sort((a, b) => a.emoji.localeCompare(b.emoji));
                                    const a = JSON.stringify(normalize(prevList));
                                    const b = JSON.stringify(normalize(reactions as any[]));
                                    if (a === b) return prev; // no change
                                  } catch { }
                                  return { ...prev, [post.id]: reactions };
                                })}
                              />
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Las reacciones ahora se gestionan en EmojiReactions */}

                      {/* Sección de comentarios expandida */}
                      {expandedPost === post.id && (
                        <div className="mt-4 border-t border-gray-200 dark:border-gray-600 pt-4">
                          {/* Lista de respuestas */}
                          {post.respuestas && post.respuestas.length > 0 && (
                            <div className="space-y-3 mb-4">
                              {post.respuestas.map((respuesta) => (
                                <div key={`response-${respuesta.id}`} className="flex space-x-3">
                                  <UserAvatar
                                    userId={typeof respuesta.autor === 'object' ? (respuesta.autor as any).usuario_id : respuesta.autor as any}
                                    nombres={typeof respuesta.autor === 'object' ? (respuesta.autor as any).nombre : 'Usuario'}
                                    apellidos={typeof respuesta.autor === 'object' ? (respuesta.autor as any).apellido : ''}
                                    size="sm"
                                  />
                                  <div className="flex-1 bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                                    <div className="flex items-center space-x-2 mb-1">
                                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                                        {typeof respuesta.autor === 'object' && (respuesta.autor as any)?.nombre
                                          ? `${(respuesta.autor as any).nombre} ${(respuesta.autor as any).apellido || ''}`.trim()
                                          : typeof respuesta.autor === 'string'
                                            ? respuesta.autor
                                            : 'Usuario'}
                                      </span>
                                      <span className="text-xs text-gray-500 dark:text-gray-400">
                                        {formatDate(respuesta.fecha)}
                                      </span>
                                    </div>
                                    <p className="text-sm text-gray-700 dark:text-gray-300">
                                      {respuesta.contenido}
                                    </p>
                                    {/* Mostrar archivos de la respuesta si los hay */}
                                    {respuesta.archivos && respuesta.archivos.length > 0 && (
                                      <div className="mt-2 space-y-1">
                                        {respuesta.archivos.map((archivo: any, archivoIndex: number) => (
                                          <div key={archivoIndex} className="flex items-center space-x-2 text-xs text-blue-600 dark:text-blue-400">
                                            <Paperclip className="w-3 h-3" />
                                            <span>{archivo.nombre || archivo.name || 'Archivo adjunto'}</span>
                                          </div>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Formulario para agregar nueva respuesta */}
                          <div className="flex space-x-3">
                            <UserAvatar
                              userId="current-user"
                              nombres="Usuario"
                              apellidos="Actual"
                              size="sm"
                            />
                            <div className="flex-1">
                              <textarea
                                value={newComment[post.id] || ''}
                                onChange={(e) => setNewComment(prev => ({
                                  ...prev,
                                  [post.id]: e.target.value
                                }))}
                                placeholder="Escribe una respuesta..."
                                className="w-full p-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                rows={2}
                              />
                              <div className="flex justify-end mt-2">
                                <button
                                  onClick={() => handleAddComment(post.id)}
                                  disabled={!(newComment[post.id]?.trim())}
                                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                                >
                                  Responder
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}

        {activeTab === 'classwork' && (
          <div className="space-y-6">
            {/* Estadísticas de tareas */}
            <TareasStatistics
              tareas={processedTaskData.tareas as any}
              tareasPorEstado={processedTaskData.tareasPorEstado}
            />

            {/* Acordeón de tareas agrupadas */}
            {/* Acordeón de tareas agrupadas */}
            <TareasAccordion
              tareasPorEstado={processedTaskData.tareasPorEstado}
              onSelectTarea={async (task: any) => {
                console.log('📋 Seleccionando tarea:', task);
                try {
                  // Mostrar modal inmediatamente con datos básicos mientras carga
                  setSelectedTarea(task);
                  setShowTaskDetail(true);

                  // Cargar información completa de la tarea desde el backend
                  console.log('🔄 Cargando detalles completos de tarea:', task.tarea_id || task.id);
                  const tareaDet: any = await apiClientTareas.obtenerTarea(task.tarea_id || task.id);

                  // Actualizar con datos completos
                  setSelectedTarea(tareaDet);
                } catch (error) {
                  console.error('Error cargando detalles de tarea:', error);
                  // Mantener los datos básicos si falla la carga completa
                }
              }}
            />



            {/* Botón flotante para crear tarea (solo profesores) */}
            {isCurrentUserProfessor && activeTab === 'classwork' && (
              <div className="fixed bottom-6 right-6 z-50">
                <button
                  onClick={() => setShowCreateTask(true)}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
                  title="Crear nueva tarea"
                >
                  <Plus className="w-6 h-6" />
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'people' && (
          <div className="space-y-8">
            {course?.personas ? (
              <>
                {/* Profesores Section */}
                {course.personas.profesores.length > 0 && (
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                          <Users className="w-5 h-5 mr-2 text-emerald-600" />
                          Profesores
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {course.personas.profesores.length} {course.personas.profesores.length === 1 ? 'profesor' : 'profesores'}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {course.personas.profesores.map((profesor) => (
                        <motion.div
                          key={profesor.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                        >
                          <div className="relative">
                            <UserAvatar
                              userId={profesor.id}
                              nombres={profesor.nombres}
                              apellidos={profesor.apellidos}
                              size="md"
                              className=""
                            />
                            <div
                              className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white dark:border-gray-700 ${isUserOnline(profesor.ultimo_acceso, profesor.correo) ? 'bg-emerald-500' : 'bg-gray-400'
                                }`}
                              title={isUserOnline(profesor.ultimo_acceso, profesor.correo) ? 'En línea' : 'Desconectado'}
                            ></div>
                          </div>

                          <div className="ml-3 flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {profesor.nombre_completo}
                              {isCurrentUser(profesor.correo) && (
                                <span className="ml-2 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded-full">
                                  Tú
                                </span>
                              )}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                              {profesor.correo}
                            </p>
                            <div className="flex items-center space-x-2 mt-1">
                              <span className="inline-block px-2 py-1 text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 rounded-full">
                                Docente
                              </span>
                              <span className={`inline-block px-2 py-1 text-xs rounded-full ${isUserOnline(profesor.ultimo_acceso, profesor.correo)
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                                }`}>
                                {isUserOnline(profesor.ultimo_acceso, profesor.correo) ? 'En línea' : 'Desconectado'}
                              </span>
                            </div>
                          </div>

                          <div className="ml-2 relative">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setOpenDropdown(openDropdown === `prof-${profesor.id}` ? null : `prof-${profesor.id}`);
                              }}
                              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                            >
                              <MoreVertical className="w-4 h-4" />
                            </button>

                            {/* Menú desplegable para profesor */}
                            {openDropdown === `prof-${profesor.id}` && (
                              <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                                <div className="py-1">
                                  <button
                                    onClick={(e) => handleViewProfile(profesor, e)}
                                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                                  >
                                    <User className="w-4 h-4 mr-2" />
                                    Ver perfil
                                  </button>
                                  <button
                                    onClick={() => handleSendEmail(profesor)}
                                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                                  >
                                    <Mail className="w-4 h-4 mr-2" />
                                    Enviar email
                                  </button>
                                  <button
                                    onClick={() => handleSendMessage(profesor)}
                                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                                  >
                                    <MessageCircle className="w-4 h-4 mr-2" />
                                    Enviar mensaje
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Estudiantes Section */}
                {course.personas.estudiantes.length > 0 && (
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                          <Users className="w-5 h-5 mr-2 text-blue-600" />
                          Estudiantes
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {searchTerm ? `${filteredStudents.length} de ${course.personas.estudiantes.length}` : course.personas.estudiantes.length} {course.personas.estudiantes.length === 1 ? 'estudiante' : 'estudiantes'} {searchTerm ? 'encontrado' + (filteredStudents.length !== 1 ? 's' : '') : 'inscritos'}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="relative">
                          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                          <input
                            type="text"
                            placeholder="Buscar estudiante..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Mensaje cuando no hay resultados de búsqueda */}
                    {searchTerm && filteredStudents.length === 0 && (
                      <div className="text-center py-8">
                        <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500 dark:text-gray-400">
                          No se encontraron estudiantes con el término "{searchTerm}"
                        </p>
                      </div>
                    )}

                    {/* Grid de estudiantes */}
                    {filteredStudents.length > 0 && (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {(showAllStudents ? filteredStudents : filteredStudents.slice(0, 12)).map((estudiante) => (
                          <motion.div
                            key={estudiante.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                          >
                            <div className="relative">
                              <UserAvatar
                                userId={estudiante.id}
                                nombres={estudiante.nombres}
                                apellidos={estudiante.apellidos}
                                size="sm"
                                className="w-10 h-10"
                              />
                              <div
                                className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white dark:border-gray-700 ${isUserOnline(estudiante.ultimo_acceso, estudiante.correo) ? 'bg-green-500' : 'bg-gray-400'
                                  }`}
                                title={isUserOnline(estudiante.ultimo_acceso, estudiante.correo) ? 'En línea' : 'Desconectado'}
                              ></div>
                            </div>

                            <div className="ml-3 flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                {estudiante.nombre_completo}
                                {isCurrentUser(estudiante.correo) && (
                                  <span className="ml-2 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-1 py-0.5 rounded">
                                    Tú
                                  </span>
                                )}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                                {estudiante.correo}
                              </p>
                              <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${isUserOnline(estudiante.ultimo_acceso, estudiante.correo)
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                                }`}>
                                {isUserOnline(estudiante.ultimo_acceso, estudiante.correo) ? 'En línea' : 'Desconectado'}
                              </span>
                            </div>

                            <div className="ml-2 relative">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setOpenDropdown(openDropdown === `student-${estudiante.id}` ? null : `student-${estudiante.id}`);
                                }}
                                className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                              >
                                <MoreVertical className="w-4 h-4" />
                              </button>

                              {/* Menú desplegable para estudiante */}
                              {openDropdown === `student-${estudiante.id}` && (
                                <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                                  <div className="py-1">
                                    <button
                                      onClick={(e) => handleViewProfile(estudiante, e)}
                                      className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                                    >
                                      <User className="w-4 h-4 mr-2" />
                                      Ver perfil
                                    </button>
                                    <button
                                      onClick={() => handleSendEmail(estudiante)}
                                      className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                                    >
                                      <Mail className="w-4 h-4 mr-2" />
                                      Enviar email
                                    </button>
                                    <button
                                      onClick={() => handleSendMessage(estudiante)}
                                      className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                                    >
                                      <MessageCircle className="w-4 h-4 mr-2" />
                                      Enviar mensaje
                                    </button>
                                  </div>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    )}

                    {/* Mostrar botón "Ver más" si hay más de 12 estudiantes filtrados */}
                    {filteredStudents.length > 12 && !showAllStudents && (
                      <div className="mt-4 text-center">
                        <button
                          onClick={() => setShowAllStudents(true)}
                          className="px-4 py-2 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                        >
                          Mostrar todos {searchTerm ? 'los resultados' : 'los estudiantes'} ({filteredStudents.length - 12} más)
                        </button>
                      </div>
                    )}

                    {/* Botón "Ver menos" si se están mostrando todos */}
                    {showAllStudents && filteredStudents.length > 12 && (
                      <div className="mt-4 text-center">
                        <button
                          onClick={() => setShowAllStudents(false)}
                          className="px-4 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                        >
                          Mostrar menos
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Empty State */}
                {(!course.personas.profesores.length && !course.personas.estudiantes.length) && (
                  <div className="text-center py-20">
                    <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400 text-lg">
                      No hay personas inscritas en este curso
                    </p>
                    <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">
                      Los estudiantes aparecerán aquí cuando se inscriban al curso
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-20">
                <Loader2 className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-spin" />
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                  Cargando información de personas...
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'calendar' && (
          <div className="space-y-6">
            {/* Calendar Header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Calendario del Curso
                </h2>
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                    <Calendar className="w-4 h-4" />
                    <span>{course.fechaInicio} - {course.fechaFin}</span>
                  </div>
                  {isCurrentUserProfessor && (
                    <button
                      onClick={() => setShowCreateEvent(true)}
                      className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Agregar Evento</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Course Timeline */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Cronograma del Curso
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Start Date */}
                  <div className="flex items-center space-x-4 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                    <div className="flex-shrink-0 w-12 h-12 bg-emerald-100 dark:bg-emerald-800 rounded-lg flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-emerald-900 dark:text-emerald-200">
                        Fecha de Inicio
                      </p>
                      <p className="text-lg font-semibold text-emerald-800 dark:text-emerald-300">
                        {course.fechaInicio}
                      </p>
                    </div>
                  </div>

                  {/* End Date */}
                  <div className="flex items-center space-x-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-800 rounded-lg flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-blue-900 dark:text-blue-200">
                        Fecha de Finalización
                      </p>
                      <p className="text-lg font-semibold text-blue-800 dark:text-blue-300">
                        {course.fechaFin}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Custom Events */}
            {calendarEvents.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Eventos Programados
                </h3>

                <div className="space-y-3">
                  {calendarEvents
                    .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime())
                    .map((event) => (
                      <div key={event.id} className={`flex items-center justify-between p-4 rounded-lg border ${getEventTypeColor(event.tipo)}`}>
                        <div className="flex items-center space-x-3">
                          {getEventTypeIcon(event.tipo)}
                          <div>
                            <p className="font-medium">
                              {event.titulo}
                            </p>
                            {event.descripcion && (
                              <p className="text-sm opacity-75">
                                {event.descripcion}
                              </p>
                            )}
                            <p className="text-xs opacity-60">
                              {formatDate(event.fecha)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium capitalize">
                            {event.tipo}
                          </p>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Upcoming Tasks */}
            {tasks.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Próximas Fechas Importantes
                </h3>

                <div className="space-y-3">
                  {tasks
                    .filter(task => new Date(task.fechaVencimiento) >= new Date())
                    .sort((a, b) => new Date(a.fechaVencimiento).getTime() - new Date(b.fechaVencimiento).getTime())
                    .slice(0, 5)
                    .map((task) => {
                      const daysUntil = Math.ceil((new Date(task.fechaVencimiento).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
                      const isUrgent = daysUntil <= 3;

                      return (

                        <div
                          key={task.id}
                          onClick={async () => {
                            // Buscar la tarea procesada correspondiente para tener el formato correcto
                            const processedTask = processedTaskData.tareas.find(t => t.tarea_id === task.id);
                            if (processedTask) {
                              setSelectedTarea(processedTask as any);
                              setShowTaskDetail(true);

                              try {
                                const tareaDet: any = await apiClientTareas.obtenerTarea(task.id);
                                setSelectedTarea(tareaDet);
                              } catch (e) {
                                console.error("Error loading task details", e);
                              }
                            }
                          }}
                          className={`flex items-center justify-between p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${isUrgent
                            ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 hover:bg-red-100 dark:hover:bg-red-900/30'
                            : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/30'
                            }`}
                        >
                          <div className="flex items-center space-x-3">
                            <div className={`flex-shrink-0 w-3 h-3 rounded-full ${isUrgent ? 'bg-red-500' : 'bg-yellow-500'
                              }`}></div>
                            <div>
                              <p className={`font-medium ${isUrgent
                                ? 'text-red-900 dark:text-red-200'
                                : 'text-yellow-900 dark:text-yellow-200'
                                }`}>
                                {task.titulo}
                              </p>
                              <p className={`text-sm ${isUrgent
                                ? 'text-red-700 dark:text-red-300'
                                : 'text-yellow-700 dark:text-yellow-300'
                                }`}>
                                Vence: {formatDate(task.fechaVencimiento)}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className={`text-sm font-medium ${isUrgent
                              ? 'text-red-800 dark:text-red-300'
                              : 'text-yellow-800 dark:text-yellow-300'
                              }`}>
                              {daysUntil === 0 ? 'Hoy' : daysUntil === 1 ? 'Mañana' : `${daysUntil} días`}
                            </p>
                            <p className={`text-xs ${isUrgent
                              ? 'text-red-600 dark:text-red-400'
                              : 'text-yellow-600 dark:text-yellow-400'
                              }`}>
                              {task.puntos} puntos
                            </p>
                          </div>
                        </div>
                      );
                    })}

                  {tasks.filter(task => new Date(task.fechaVencimiento) >= new Date()).length === 0 && (
                    <div className="text-center py-8">
                      <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500 dark:text-gray-400">
                        No hay tareas próximas
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Course Progress */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Progreso del Curso
              </h3>

              <div className="space-y-4">
                {/* Progress Bar */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Progreso General
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {course.progreso ?? 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${course.progreso ?? 0}%` }}
                    ></div>
                  </div>
                </div>

                {/* Time Information */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                      {(() => {
                        const startDate = new Date(course.fechaInicio);
                        const now = new Date();
                        const diffTime = now.getTime() - startDate.getTime();
                        const diffDays = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
                        return diffDays;
                      })()}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Días transcurridos</p>
                  </div>

                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {(() => {
                        const endDate = new Date(course.fechaFin);
                        const now = new Date();
                        const diffTime = endDate.getTime() - now.getTime();
                        const diffDays = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
                        return diffDays;
                      })()}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Días restantes</p>
                  </div>

                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {tasks.length + calendarEvents.length}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Eventos totales</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Configuración del Curso */}
      {
        showCourseSettings && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
            >
              {/* Header del Modal */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                  <Settings className="w-6 h-6 mr-3 text-blue-600" />
                  Configuración del Curso
                </h2>
                <button
                  onClick={() => setShowCourseSettings(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Contenido del Modal */}
              <div className="p-6 space-y-6">
                {/* Notificaciones */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Bell className="w-5 h-5 mr-2 text-blue-600" />
                    Notificaciones
                  </h3>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Nuevas publicaciones</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Recibir notificaciones de nuevas publicaciones del profesor</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Nuevas tareas</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Notificar cuando se asignen nuevas tareas</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Fechas límite</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Recordatorios de fechas límite de entrega</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Privacidad */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Shield className="w-5 h-5 mr-2 text-green-600" />
                    Privacidad
                  </h3>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Mostrar actividad online</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Permitir que otros vean cuando estás en línea</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Compartir progreso</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Permitir que otros estudiantes vean tu progreso</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Preferencias de Visualización */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Eye className="w-5 h-5 mr-2 text-purple-600" />
                    Visualización
                  </h3>

                  <div className="space-y-3">
                    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                        Vista por defecto del curso
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-600 text-gray-900 dark:text-white">
                        <option value="stream">Transmisión</option>
                        <option value="classwork">Trabajo de clase</option>
                        <option value="people">Personas</option>
                        <option value="calendar">Calendario</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Modo compacto</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Mostrar más contenido en pantalla</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer del Modal */}
              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setShowCourseSettings(false)}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => {
                    // Aquí guardarías las configuraciones
                    setShowCourseSettings(false);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Guardar Cambios
                </button>
              </div>
            </motion.div>
          </div>
        )
      }


      {/* Modal de Crear Tarea */}
      {
        showCreateTask && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header del Modal */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Crear Nueva Tarea
                </h3>
                <button
                  onClick={() => setShowCreateTask(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Contenido del Modal */}
              <div className="p-6 space-y-6">
                {/* Título */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Título de la tarea *
                  </label>
                  <input
                    type="text"
                    value={taskFormData.titulo}
                    onChange={(e) => setTaskFormData(prev => ({ ...prev, titulo: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Ej: Ensayo sobre historia mundial"
                  />
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Descripción e instrucciones *
                  </label>
                  <textarea
                    value={taskFormData.descripcion}
                    onChange={(e) => setTaskFormData(prev => ({ ...prev, descripcion: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Describe las instrucciones y requisitos de la tarea..."
                  />
                </div>

                {/* Fecha de vencimiento y puntos */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Calendar className="w-4 h-4 inline mr-2" />
                      Fecha límite
                    </label>
                    <div className="relative">
                      <input
                        type="datetime-local"
                        value={taskFormData.fechaVencimiento}
                        onChange={(e) => setTaskFormData(prev => ({ ...prev, fechaVencimiento: e.target.value }))}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white transition-all duration-200 shadow-sm hover:shadow-md"
                        min={new Date().toISOString().slice(0, 16)}
                      />
                      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                        <Calendar className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Selecciona fecha y hora de entrega
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Star className="w-4 h-4 inline mr-2" />
                      Puntos totales
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        value={taskFormData.puntos}
                        onChange={(e) => setTaskFormData(prev => ({ ...prev, puntos: parseInt(e.target.value) || 0 }))}
                        min="0"
                        max="1000"
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white transition-all duration-200 shadow-sm hover:shadow-md"
                        placeholder="100"
                      />
                      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                        <span className="text-gray-400 text-sm">pts</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Puntuación máxima de la tarea
                    </p>
                  </div>
                </div>
              </div>

              {/* Footer del Modal */}
              <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setShowCreateTask(false)}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateTask}
                  disabled={creatingTask || !taskFormData.titulo.trim() || !taskFormData.descripcion.trim()}
                  className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  {creatingTask ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creando...
                    </>
                  ) : (
                    'Crear Tarea'
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )
      }

      {/* Modal de Crear Evento del Calendario */}
      {
        showCreateEvent && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header del Modal */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Agregar Evento al Calendario
                </h3>
                <button
                  onClick={() => setShowCreateEvent(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Contenido del Modal */}
              <div className="p-6 space-y-4">
                {/* Título */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Título del evento *
                  </label>
                  <input
                    type="text"
                    value={eventFormData.titulo}
                    onChange={(e) => setEventFormData(prev => ({ ...prev, titulo: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Ej: Examen Final de Matemáticas"
                  />
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Descripción
                  </label>
                  <textarea
                    value={eventFormData.descripcion}
                    onChange={(e) => setEventFormData(prev => ({ ...prev, descripcion: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Describe los detalles del evento..."
                  />
                </div>

                {/* Fecha y Tipo */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Fecha y hora *
                    </label>
                    <input
                      type="datetime-local"
                      value={eventFormData.fecha}
                      onChange={(e) => setEventFormData(prev => ({ ...prev, fecha: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-gray-700 dark:text-white"
                      min={new Date().toISOString().slice(0, 16)}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tipo de evento
                    </label>
                    <select
                      value={eventFormData.tipo}
                      onChange={(e) => setEventFormData(prev => ({ ...prev, tipo: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="evaluacion">📝 Evaluación</option>
                      <option value="entrega">📤 Entrega</option>
                      <option value="clase">📚 Clase</option>
                      <option value="otro">📅 Otro</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Footer del Modal */}
              <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setShowCreateEvent(false)}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateEvent}
                  disabled={!eventFormData.titulo.trim() || !eventFormData.fecha}
                  className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Crear Evento
                </button>
              </div>
            </motion.div>
          </div>
        )
      }

      {/* Modal de Reportar Post */}
      {
        showReportModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header del Modal */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <Flag className="w-5 h-5 text-orange-600 mr-3" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Reportar Publicación
                  </h3>
                </div>
                <button
                  onClick={() => setShowReportModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Contenido del Modal */}
              <div className="p-6 space-y-4">
                <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                  <div className="flex items-start">
                    <AlertCircle className="w-5 h-5 text-orange-600 mr-3 mt-0.5" />
                    <div className="text-sm text-orange-800 dark:text-orange-200">
                      <p className="font-medium mb-1">Ayúdanos a mantener la comunidad segura</p>
                      <p>Reporta contenido que viole las normas de la plataforma. Todos los reportes son confidenciales y serán revisados por nuestro equipo.</p>
                    </div>
                  </div>
                </div>

                {/* Razón del reporte */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Razón del reporte *
                  </label>
                  <select
                    value={reportReason}
                    onChange={(e) => setReportReason(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="">Selecciona una razón...</option>
                    <option value="contenido_inapropiado">Contenido inapropiado o ofensivo</option>
                    <option value="spam">Spam o publicidad no solicitada</option>
                    <option value="acoso">Acoso o intimidación</option>
                    <option value="informacion_falsa">Información falsa o engañosa</option>
                    <option value="contenido_duplicado">Contenido duplicado o irrelevante</option>
                    <option value="violacion_derechos">Violación de derechos de autor</option>
                    <option value="otro">Otro motivo</option>
                  </select>
                </div>

                {/* Descripción adicional */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Descripción adicional (opcional)
                  </label>
                  <textarea
                    value={reportDescription}
                    onChange={(e) => setReportDescription(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Proporciona más detalles sobre el motivo del reporte..."
                  />
                </div>
              </div>

              {/* Footer del Modal */}
              <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setShowReportModal(false)}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={submitReport}
                  disabled={submittingReport || !reportReason.trim()}
                  className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  {submittingReport ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Flag className="w-4 h-4 mr-2" />
                      Enviar Reporte
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )
      }

      {/* Modal de Crear Tarea */}
      {
        showCreateTask && (
          <div className="fixed inset-0 bg-black/50 dark:bg-black/70 z-[9999] flex items-start justify-center pt-8 overflow-y-auto">
            <div className="w-full max-w-4xl pb-8">
              <CrearTareaForm
                cursoId={courseId}
                grupoId={grupoId || courseId}
                docenteId={docenteId || currentUser?.usuario_id || ''}
                onSuccess={async (tarea) => {
                  setShowCreateTask(false);
                  await loadTasks();
                }}
                onCancel={() => setShowCreateTask(false)}
              />
            </div>
          </div>
        )
      }

      {/* Modal de Detalle de Tarea (Mejorado) */}
      {
        showTaskDetail && selectedTarea && (
          <TareaPreviewModal
            isOpen={showTaskDetail}
            onClose={() => {
              setShowTaskDetail(false);
              setSelectedTarea(null);
            }}
            tarea={selectedTarea}
            isStudentUser={!isCurrentUserProfessor}
            cursoId={courseId}
          />
        )
      }
    </div >
  );
}