// Servicio para manejar las operaciones de cursos con la API
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Configurar axios para academic
const academicAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000
});

// Variable para controlar si ya estamos refrescando el token
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

// Función para procesar la cola de peticiones fallidas
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token!);
    }
  });

  failedQueue = [];
};

// Función para refrescar el token
const refreshToken = async (): Promise<string | null> => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    console.log('🔄 REFRESH TOKEN - Intentando refrescar token...');

    const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
      refresh_token: refreshToken
    });

    const { access_token } = response.data;
    console.log('✅ REFRESH TOKEN - Token refrescado exitosamente');

    // Guardar el nuevo token
    localStorage.setItem('access_token', access_token);

    return access_token;
  } catch (error: any) {
    console.error('❌ REFRESH TOKEN - Error refrescando token:', error);

    // Limpiar tokens inválidos
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Redirigir al login
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }

    return null;
  }
};

// Agregar interceptor de request para debugging
academicAPI.interceptors.request.use(
  (config) => {
    // If sending FormData, ensure we do not force a JSON Content-Type so the
    // browser/axios can set the correct multipart/form-data boundary. This
    // prevents FastAPI from returning 422 when form fields are missing.
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      // Remove any explicit Content-Type so the browser attaches the boundary
      if (config.headers && Object.prototype.hasOwnProperty.call(config.headers, 'Content-Type')) {
        try { delete (config.headers as any)['Content-Type']; } catch { }
      }
      console.log('🚀 REQUEST INTERCEPTOR - Sending FormData request to', config.url);
    }

    console.log('🚀 REQUEST INTERCEPTOR - Configuración de request:', {
      url: config.url,
      method: config.method,
      headers: {
        ...config.headers,
        // Ocultar token completo por seguridad
        Authorization: config.headers.Authorization ?
          `${(config.headers.Authorization as string).substring(0, 20)}...` :
          'NO AUTH HEADER'
      },
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('❌ REQUEST INTERCEPTOR ERROR:', error);
    return Promise.reject(error);
  }
);

// Agregar interceptor de response para debugging y refresh automático
academicAPI.interceptors.response.use(
  (response) => {
    console.log('✅ RESPONSE INTERCEPTOR - Respuesta exitosa:', {
      status: response.status,
      url: response.config.url,
      method: response.config.method
    });
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    console.error('❌ RESPONSE INTERCEPTOR ERROR:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method,
      headers: error.config?.headers,
      data: error.response?.data
    });

    // Si es error 401 y no hemos intentado refrescar aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('🔑 TOKEN EXPIRADO - Intentando refresh automático...');

      if (isRefreshing) {
        // Si ya estamos refrescando, agregar a la cola
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return academicAPI(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshToken();

        if (newToken) {
          // Procesar la cola con el nuevo token
          processQueue(null, newToken);

          // Reintentar la petición original con el nuevo token
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return academicAPI(originalRequest);
        } else {
          // No se pudo refrescar, rechazar todas las peticiones en cola
          processQueue(error, null);
          return Promise.reject(error);
        }
      } catch (refreshError) {
        // Error al refrescar, rechazar todas las peticiones en cola
        processQueue(refreshError, null);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Para otros errores, rechazar directamente
    return Promise.reject(error);
  }
);

export interface Course {
  id: string;
  nombre: string;
  codigo: string;
  descripcion: string;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  modalidad?: string;
  creditos?: number;
  horas_academicas?: number;
  profesor: string;
  estudiantes: number;
  progreso?: number;
  estado: string;
  personas?: {
    estudiantes: Person[];
    profesores: Person[];
    total_estudiantes: number;
    total_profesores: number;
  };
}

export interface Person {
  id: string;
  nombres: string;
  apellidos: string;
  nombre_completo: string;
  correo: string;
  avatar_url?: string;
  fecha_vinculacion?: string;
  fecha_asignacion?: string;
  rol: 'estudiante' | 'docente';
}

export interface CourseResponse {
  success: boolean;
  data: Course[];
  total: number;
  message: string;
  source: string;
  error?: string;
  empty_state?: boolean;
  empty_message?: string;
  user_role?: string;
}

export interface CourseDetailResponse {
  success: boolean;
  data: Course;
  message: string;
}

export interface Comment {
  id: string;
  autor: string;
  contenido: string;
  fecha: string;
  tipo: 'anuncio' | 'pregunta' | 'comentario';
}

export interface CommentsResponse {
  success: boolean;
  data: Comment[];
  total: number;
  message: string;
}

export interface Task {
  id: string;
  titulo: string;
  descripcion: string;
  fecha_asignacion: string;
  fecha_limite: string;
  archivo_adjunto?: string;
  profesor: string;
  entregas: number;
}

export interface TasksResponse {
  success: boolean;
  data: Task[];
  total: number;
  message: string;
}

export interface CreateCommentData {
  contenido: string;
  tipo: 'anuncio' | 'pregunta' | 'comentario';
  archivos_adjuntos?: any[];
  comentario_padre_id?: string; // Para respuestas (replies)
}

export interface CreateTaskData {
  titulo: string;
  descripcion?: string;
  fecha_limite: string;
  puntos_max?: number;
  tipo?: string;
  prioridad?: string;
}

export interface Group {
  id: string;
  nombre: string;
  curso: string;
  estudiantes: number;
  profesor: string;
  horario: string;
  aula: string;
}

export interface GroupsResponse {
  success: boolean;
  data: Group[];
  total: number;
  message: string;
  source: string;
}

export const courseService = {
  // Obtener todos los cursos
  async getCourses(): Promise<CourseResponse> {
    try {
      console.log('🔄 Obteniendo cursos desde API...');
      console.log('🌐 URL de request:', `${API_BASE_URL}/api/cursos/`);

      const response = await academicAPI.get<CourseResponse>('/api/cursos/');
      console.log('✅ Respuesta API cursos:', response.data);

      // Asegurar que tenga la estructura correcta
      return {
        ...response.data,
        source: response.data.source || 'database'
      };
    } catch (error) {
      console.error('❌ Error obteniendo cursos:', error);
      console.error('❌ Detalles del error:', {
        message: error instanceof Error ? error.message : 'Error desconocido',
        config: (error as any)?.config,
        response: (error as any)?.response?.data
      });

      // Fallback a datos mock si la API falla
      return {
        success: false,
        data: [],
        total: 0,
        message: "Error conectando con la API",
        source: "error",
        error: error instanceof Error ? error.message : 'Error desconocido'
      };
    }
  },

  // Obtener cursos del usuario actual (solo inscritos para estudiantes)
  async getMyCourses(): Promise<CourseResponse> {
    try {
      console.log('🔄 Obteniendo MIS cursos desde API...');

      // Agregar token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('❌ No hay token de autenticación');
        return {
          success: true,
          data: [],
          total: 0,
          message: "Debes iniciar sesión para ver tus cursos",
          source: "auth_error",
          empty_state: true,
          empty_message: "Inicia sesión para ver tus cursos inscritos"
        };
      }

      // Usar el endpoint correcto de mis cursos
      const response = await academicAPI.get<CourseResponse>('/api/cursos/mis-cursos', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Respuesta API mis cursos:', response.data);

      return {
        ...response.data,
        source: response.data.source || 'database'
      };
    } catch (error: any) {
      console.error('❌ Error obteniendo mis cursos:', error);
      console.error('📊 Error details:', {
        status: error?.response?.status,
        data: error?.response?.data,
        message: error?.message
      });

      // Distinguir tipos de error
      if (error?.response?.status === 401) {
        console.warn('🔑 Token expirado o inválido');
        // Limpiar token inválido
        localStorage.removeItem('access_token');
        return {
          success: true,
          data: [],
          total: 0,
          message: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente",
          source: "auth_expired",
          empty_state: true,
          empty_message: "Tu sesión ha expirado. Inicia sesión para ver tus cursos"
        };
      }

      if (error?.response?.status === 403) {
        console.warn('🚫 Sin permisos para acceder a cursos');
        return {
          success: true,
          data: [],
          total: 0,
          message: "No tienes permisos para ver cursos",
          source: "permission_error",
          empty_state: true,
          empty_message: "No tienes permisos para acceder a esta sección"
        };
      }

      if (error?.response?.status === 405) {
        console.warn('⚠️ Método HTTP no permitido - El endpoint podría no existir o estar deshabilitado');
        return {
          success: true,
          data: [],
          total: 0,
          message: "Este endpoint no está disponible actualmente",
          source: "endpoint_error",
          empty_state: true,
          empty_message: "El sistema de cursos está en mantenimiento. Intenta más tarde."
        };
      }

      // Error de conexión o servidor
      return {
        success: false,
        data: [],
        total: 0,
        message: "Error de conexión. Verifica tu conexión a internet e intenta nuevamente",
        source: "connection_error",
        error: error instanceof Error ? error.message : 'Error de conexión'
      };
    }
  },

  // Inscribirse a un curso usando código
  async joinCourse(codigo: string): Promise<{ success: boolean; message: string; data?: any }> {
    try {
      console.log(`🔄 Intentando inscribirse con código: ${codigo}`);

      // Agregar token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.post('/api/cursos/inscripciones/inscribir',
        { codigo_acceso: codigo },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log('✅ Inscripción exitosa:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Error en inscripción:', error);
      console.error('📊 Detalles completos:', error?.response?.data);

      // Manejar diferentes tipos de errores
      let errorMessage = 'Error desconocido al inscribirse';

      if (error?.response?.data?.detail) {
        const detail = error.response.data.detail;

        // Si es un array de errores de validación
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error?.message) {
        errorMessage = error.message;
      }

      return {
        success: false,
        message: errorMessage
      };
    }
  },

  // Obtener todos los grupos
  async getGroups(): Promise<GroupsResponse> {
    try {
      console.log('🔄 Obteniendo grupos desde API...');
      console.log('🌐 URL de request:', `${API_BASE_URL}/api/cursos/disponibles`);

      const response = await academicAPI.get<GroupsResponse>('/api/cursos/disponibles');
      console.log('✅ Respuesta API grupos:', response.data);

      return {
        ...response.data,
        source: response.data.source || 'database'
      };
    } catch (error) {
      console.error('❌ Error obteniendo grupos:', error);

      // Fallback a datos mock si la API falla
      return {
        success: false,
        data: [],
        total: 0,
        message: "Error conectando con la API - grupos",
        source: "error"
      };
    }
  },

  // Obtener un curso específico por ID
  async getCourseById(id: string): Promise<CourseDetailResponse> {
    try {
      console.log(`🔄 Obteniendo curso ${id}...`);
      console.log(`🌐 URL de request: ${API_BASE_URL}/api/cursos/${id}`);

      // Agregar token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }
      console.log(`🔑 Token presente: ${token ? 'SÍ' : 'NO'}`);

      const response = await academicAPI.get<CourseDetailResponse>(`/api/cursos/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Respuesta API curso específico:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error obteniendo curso ${id}:`, error);
      console.error(`❌ Error details:`, {
        message: error?.message,
        status: error?.response?.status,
        statusText: error?.response?.statusText,
        data: error?.response?.data
      });
      throw new Error(`No se pudo obtener el curso: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`);
    }
  },

  // Obtener comentarios de un curso
  async getCourseComments(courseId: string, limit: number = 20, offset: number = 0): Promise<CommentsResponse> {
    try {
      console.log(`🔄 Obteniendo comentarios del curso ${courseId}...`);

      // Agregar token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('❌ No hay token de autenticación para comentarios');
        return {
          success: false,
          data: [],
          total: 0,
          message: "Debes iniciar sesión para ver los comentarios"
        };
      }

      const response = await academicAPI.get<CommentsResponse>(`/api/cursos/${courseId}/comentarios`, {
        params: { limit, offset },
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('✅ Comentarios obtenidos:', response.data);
      return response.data;
    } catch (error) {
      console.error(`❌ Error obteniendo comentarios del curso ${courseId}:`, error);
      return {
        success: false,
        data: [],
        total: 0,
        message: `Error obteniendo comentarios: ${error instanceof Error ? error.message : 'Error desconocido'}`
      };
    }
  },

  // Crear comentario en un curso
  async createComment(courseId: string, commentData: CreateCommentData): Promise<{ success: boolean; data?: Comment; message: string }> {
    try {
      console.log(`🔄 Creando comentario en curso ${courseId}...`);
      console.log('📝 Datos del comentario:', commentData);

      const token = localStorage.getItem('access_token');
      console.log('🔑 TOKEN DEBUG - Token en localStorage:', {
        exists: !!token,
        length: token?.length,
        prefix: token?.substring(0, 20) + '...'
      });

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      // Preparar headers
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Preparar datos - enviar archivos_adjuntos como lista de objetos
      const requestData = {
        contenido: commentData.contenido,
        tipo: commentData.tipo,
        archivos_adjuntos: commentData.archivos_adjuntos || [],
        ...(commentData.comentario_padre_id && { comentario_padre_id: commentData.comentario_padre_id }) // Solo incluir si existe
      };

      console.log('📤 CREATE COMMENT - Preparando request:', {
        url: `/api/cursos/${courseId}/comentarios`,
        headers: {
          ...headers,
          Authorization: headers.Authorization.substring(0, 30) + '...' // Ocultar token completo
        },
        data: requestData
      });

      // Hacer la petición
      const response = await academicAPI.post(`/api/cursos/${courseId}/comentarios`, requestData, { headers });

      console.log('✅ CREATE COMMENT - Respuesta exitosa:', {
        status: response.status,
        data: response.data
      });

      return response.data;
    } catch (error: any) {
      console.error('❌ CREATE COMMENT - Error completo:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          headers: error.config?.headers
        }
      });

      return {
        success: false,
        message: `Error creando comentario: ${error.response?.status || ''} ${error.response?.statusText || error.message || 'Error desconocido'}`
      };
    }
  },

  // Obtener tareas de un curso
  async getCourseTasks(courseId: string, incluirVencidas: boolean = true): Promise<TasksResponse> {
    try {
      console.log(`🔄 Obteniendo tareas del curso ${courseId}... (incluir_vencidas=${incluirVencidas})`);

      // Agregar token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('❌ No hay token de autenticación para tareas');
        return {
          success: false,
          data: [],
          total: 0,
          message: "Debes iniciar sesión para ver las tareas"
        };
      }

      const response = await academicAPI.get<TasksResponse>(`/api/cursos/tareas/${courseId}/tareas`, {
        params: { incluir_vencidas: incluirVencidas },
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('✅ Tareas obtenidas:', response.data);
      return response.data;
    } catch (error) {
      console.error(`❌ Error obteniendo tareas del curso ${courseId}:`, error);
      return {
        success: false,
        data: [],
        total: 0,
        message: `Error obteniendo tareas: ${error instanceof Error ? error.message : 'Error desconocido'}`
      };
    }
  },

  // Auto-vinculación inteligente de estudiante (por dominio de email o código)
  async autoLinkStudentProfile(): Promise<{
    success: boolean;
    message: string;
    programa?: string;
    institucion?: string;
    metodo?: string;
    requires_invitation?: boolean;
    user_email?: string;
    dominio?: string;
  }> {
    try {
      console.log('🔄 Auto-vinculando perfil de estudiante...');

      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.post('/api/cursos/auto-vincular-estudiante', {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Auto-vinculación exitosa:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Error en auto-vinculación:', error);

      if (error?.response?.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
      }

      const errorMessage = error?.response?.data?.detail ||
        error?.message ||
        'Error desconocido en auto-vinculación';

      throw new Error(errorMessage);
    }
  },

  // Vinculación por código de invitación
  async linkByInvitationCode(invitationCode: string): Promise<{
    success: boolean;
    message: string;
    programa?: string;
    institucion?: string;
    metodo?: string;
  }> {
    try {
      console.log(`🔄 Vinculando con código: ${invitationCode}...`);

      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.post('/api/cursos/vincular-por-codigo', {
        codigo_invitacion: invitationCode
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Vinculación por código exitosa:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Error en vinculación por código:', error);

      if (error?.response?.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
      }

      if (error?.response?.status === 404) {
        throw new Error('Código de invitación inválido o expirado');
      }

      const errorMessage = error?.response?.data?.detail ||
        error?.message ||
        'Error desconocido al vincular con código';

      throw new Error(errorMessage);
    }
  },

  // Generar código de invitación (para coordinadores)
  async generateInvitationCode(programaId: string, descripcion?: string): Promise<{
    success: boolean;
    codigo_invitacion: string;
    programa: string;
    institucion: string;
    instrucciones: string;
  }> {
    try {
      console.log(`🔄 Generando código de invitación para programa ${programaId}...`);

      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.post('/api/cursos/generar-codigo-invitacion', {
        programa_id: programaId,
        descripcion
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Código de invitación generado:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Error generando código de invitación:', error);

      if (error?.response?.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
      }

      const errorMessage = error?.response?.data?.detail ||
        error?.message ||
        'Error desconocido al generar código';

      throw new Error(errorMessage);
    }
  },

  // Crear tarea en un curso
  async createTask(courseId: string, taskData: CreateTaskData): Promise<{ success: boolean; data?: Task; message: string }> {
    try {
      console.log(`🔄 Creando tarea en curso ${courseId}...`);
      console.log('📤 Datos de tarea a enviar:', JSON.stringify(taskData, null, 2));

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const requestData = taskData; // No incluir curso_id, viene en la URL

      console.log('📤 Request completo:', JSON.stringify(requestData, null, 2));

      const response = await academicAPI.post(`/api/cursos/tareas/${courseId}/tareas`, requestData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
      });

      console.log('✅ Tarea creada:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error creando tarea:`, error);
      console.error('❌ Detalles del error:', {
        status: error?.response?.status,
        statusText: error?.response?.statusText,
        data: error?.response?.data,
        message: error?.message
      });
      return {
        success: false,
        message: `Error creando tarea: ${error?.response?.status || ''} ${error?.response?.statusText || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Subir archivo a un curso
  async uploadFile(courseId: string, file: File, tipo: string): Promise<{ success: boolean; data?: any; message: string }> {
    try {
      console.log(`🔄 Subiendo archivo ${file.name} al curso ${courseId}...`);

      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const formData = new FormData();
      formData.append('archivo', file); // El backend espera 'archivo', no 'file'
      formData.append('descripcion', tipo); // Puedes cambiar 'tipo' por una descripción real si lo deseas

      // URL corregida según backend: /api/cursos/archivos/{curso_id}/subir
      const response = await academicAPI.post(`/api/cursos/archivos/${courseId}/subir`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        },
      });

      console.log('✅ Archivo subido:', response.data);
      return response.data;
    } catch (error) {
      console.error(`❌ Error subiendo archivo:`, error);
      return {
        success: false,
        message: `Error subiendo archivo: ${error instanceof Error ? error.message : 'Error desconocido'}`
      };
    }
  },

  // Descargar archivo
  async downloadFile(archivoId: string): Promise<void> {
    try {
      console.log(`🔄 Descargando archivo ${archivoId}...`);

      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.get(`/api/cursos/archivos/descargar/${archivoId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        responseType: 'blob' // Importante para archivos binarios
      });

      // Crear URL del blob y descargar
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);

      // Obtener nombre del archivo desde headers o usar genérico
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'archivo_descargado';

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }

      // Crear enlace de descarga
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // Limpiar
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log('✅ Archivo descargado exitosamente');
    } catch (error: any) {
      console.error(`❌ Error descargando archivo:`, error);
      throw new Error(`Error descargando archivo: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`);
    }
  },

  // Agregar reacción emoji a un post
  async addReaction(comentarioId: string, emoji: string, tipo: string = '', action: 'add' | 'remove' = 'add'): Promise<{ success: boolean; data?: any; message: string }> {
    try {
      console.log(`🔄 Agregando reacción ${emoji} al comentario ${comentarioId} con action=${action}...`);
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No hay token de autenticación');
      }
      // Siempre enviar tipo_reaccion como string válido (emoji si no hay otro tipo)
      const tipoReaccionFinal = (typeof tipo === 'string' && tipo.trim().length > 0) ? tipo : emoji;
      const form = new FormData();
      form.append('emoji', emoji);
      form.append('tipo_reaccion', tipoReaccionFinal); // Nunca vacío
      form.append('action', action);
      const response = await academicAPI.post(`/api/cursos/reacciones/comentarios/${comentarioId}`, form, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('✅ Reacción agregada:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error agregando reacción:`, error);
      return {
        success: false,
        message: `Error agregando reacción: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Obtener reacciones de un post
  async getPostReactions(comentarioId: string): Promise<{ success: boolean; data?: any[]; message: string }> {
    try {
      console.log(`🔄 Obteniendo reacciones del comentario ${comentarioId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        console.warn('❌ No hay token de autenticación para reacciones');
        return {
          success: false,
          data: [],
          message: "Debes iniciar sesión para ver las reacciones"
        };
      }

      // Use the 'cursos/reacciones' namespace to get canonical list grouped by emoji
      const response = await academicAPI.get(`/api/cursos/reacciones/comentarios/${comentarioId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Reacciones obtenidas:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error obteniendo reacciones:`, error);
      return {
        success: false,
        data: [],
        message: `Error obteniendo reacciones: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Eliminar reacción
  async removeReaction(reaccionId: string): Promise<{ success: boolean; message: string }> {
    try {
      console.log(`🔄 Eliminando reacción ${reaccionId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      // Use the safer endpoint that deletes a single reaction by its id.
      const response = await academicAPI.delete(`/api/cursos/reacciones/comentarios/reaccion/${reaccionId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Reacción eliminada:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error eliminando reacción:`, error);
      return {
        success: false,
        message: `Error eliminando reacción: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // === FUNCIONES PARA RESPUESTAS ===

  // Crear respuesta a un comentario
  async createReply(comentarioId: string, replyData: { contenido: string }): Promise<{ success: boolean; data?: any; message: string }> {
    try {
      console.log(`🔄 Creando respuesta al comentario ${comentarioId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.post(`/api/cursos/comentarios/${comentarioId}/respuestas`, replyData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
      });

      console.log('✅ Respuesta creada:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error creando respuesta:`, error);
      return {
        success: false,
        message: `Error creando respuesta: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Obtener respuestas de un comentario
  async getReplies(comentarioId: string): Promise<{ success: boolean; data?: any[]; message: string }> {
    try {
      console.log(`🔄 Obteniendo respuestas del comentario ${comentarioId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        console.warn('❌ No hay token de autenticación para respuestas');
        return {
          success: false,
          data: [],
          message: "Debes iniciar sesión para ver las respuestas"
        };
      }

      const response = await academicAPI.get(`/api/cursos/comentarios/${comentarioId}/respuestas`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Respuestas obtenidas:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error obteniendo respuestas:`, error);
      return {
        success: false,
        data: [],
        message: `Error obteniendo respuestas: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Actualizar comentario
  async updateComment(comentarioId: string, commentData: { contenido: string }): Promise<{ success: boolean; data?: any; message: string }> {
    try {
      console.log(`🔄 Actualizando comentario ${comentarioId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.put(`/api/cursos/comentarios/${comentarioId}`, commentData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
      });

      console.log('✅ Comentario actualizado:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error actualizando comentario:`, error);
      return {
        success: false,
        message: `Error actualizando comentario: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Eliminar comentario
  async deleteComment(comentarioId: string): Promise<{ success: boolean; message: string }> {
    try {
      console.log(`🔄 Eliminando comentario ${comentarioId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.delete(`/api/cursos/comentarios/${comentarioId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Comentario eliminado:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error eliminando comentario:`, error);
      return {
        success: false,
        message: `Error eliminando comentario: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Actualizar respuesta
  async updateReply(respuestaId: string, replyData: { contenido: string }): Promise<{ success: boolean; data?: any; message: string }> {
    try {
      console.log(`🔄 Actualizando respuesta ${respuestaId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.put(`/api/cursos/respuestas/${respuestaId}`, replyData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
      });

      console.log('✅ Respuesta actualizada:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error actualizando respuesta:`, error);
      return {
        success: false,
        message: `Error actualizando respuesta: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Eliminar respuesta
  async deleteReply(respuestaId: string): Promise<{ success: boolean; message: string }> {
    try {
      console.log(`🔄 Eliminando respuesta ${respuestaId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.delete(`/api/cursos/respuestas/${respuestaId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('✅ Respuesta eliminada:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error eliminando respuesta:`, error);
      return {
        success: false,
        message: `Error eliminando respuesta: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  },

  // Reportar comentario
  async reportComment(comentarioId: string, reportData: { razon: string; descripcion?: string }): Promise<{ success: boolean; data?: any; message: string }> {
    try {
      console.log(`🚨 Reportando comentario ${comentarioId}...`);

      const token = localStorage.getItem('access_token');

      if (!token) {
        throw new Error('No hay token de autenticación');
      }

      const response = await academicAPI.post(`/api/cursos/comentarios/${comentarioId}/reportes`, reportData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
      });

      console.log('✅ Reporte enviado:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Error enviando reporte:`, error);
      return {
        success: false,
        message: `Error enviando reporte: ${error?.response?.data?.detail || error?.message || 'Error desconocido'}`
      };
    }
  }
};

export default courseService;