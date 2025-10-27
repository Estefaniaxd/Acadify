import axios from 'axios';
import { 
  Curso, CursoCreate, CursoUpdate, CursoDetallado, FiltrosCurso, EstadisticasCurso,
  Clase, ClaseCreate, ClaseUpdate, ClaseDetallada, EstudianteUnirse, RespuestaUnirse,
  MaterialEducativo, MaterialEducativoCreate, MaterialEducativoUpdate, MaterialEducativoDetallado, FiltrosMaterial, EstadisticasMaterial,
  Grupo, Programa,
  ModalidadCurso, CarpetaMaterial, TipoMaterialEducativo
} from './types.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Configuración de axios con interceptores
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Interceptor para agregar token de autorización
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de respuesta
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Disparar evento de token expirado
      window.dispatchEvent(new CustomEvent('auth-token-expired'));
      // Pequeño delay antes de redirigir
      setTimeout(() => {
        window.location.href = '/login';
      }, 1000);
    }
    return Promise.reject(error);
  }
);

// API para Cursos
export const cursosAPI = {
  // Crear nuevo curso
  crear: async (cursoData: CursoCreate): Promise<Curso> => {
    const response = await apiClient.post('/academic/cursos/', cursoData);
    return response.data;
  },

  // Obtener curso por ID
  obtenerPorId: async (cursoId: string): Promise<CursoDetallado> => {
    const response = await apiClient.get(`/academic/cursos/${cursoId}`);
    return response.data;
  },

  // Actualizar curso
  actualizar: async (cursoId: string, cursoData: CursoUpdate): Promise<Curso> => {
    const response = await apiClient.put(`/academic/cursos/${cursoId}`, cursoData);
    return response.data;
  },

  // Eliminar curso
  eliminar: async (cursoId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/academic/cursos/${cursoId}`);
    return response.data;
  },

  // Listar cursos con filtros
  listar: async (filtros: FiltrosCurso = {}): Promise<Curso[]> => {
    const response = await apiClient.get('/academic/cursos/', { params: filtros });
    return response.data;
  },

  // Buscar cursos
  buscar: async (termino: string, filtros: Partial<FiltrosCurso> = {}): Promise<Curso[]> => {
    const response = await apiClient.get(`/academic/cursos/buscar/${termino}`, { params: filtros });
    return response.data;
  },

  // Activar/Desactivar curso
  activarDesactivar: async (cursoId: string, activo: boolean): Promise<{ message: string }> => {
    const response = await apiClient.post(`/academic/cursos/${cursoId}/activar-desactivar`, { activo });
    return response.data;
  },

  // Obtener estadísticas de curso
  obtenerEstadisticas: async (cursoId: string): Promise<EstadisticasCurso> => {
    const response = await apiClient.get(`/academic/cursos/${cursoId}/estadisticas`);
    return response.data;
  },

  // Obtener cursos con inscripciones abiertas
  obtenerInscripcionesAbiertas: async (programaId?: string): Promise<Curso[]> => {
    const params = programaId ? { programa_id: programaId } : {};
    const response = await apiClient.get('/academic/cursos/inscripciones-abiertas/', { params });
    return response.data;
  },

  // Configurar Google Drive
  configurarDrive: async (cursoId: string, config: any): Promise<{ message: string }> => {
    const response = await apiClient.post(`/academic/cursos/${cursoId}/configurar-drive`, config);
    return response.data;
  },
};

// API para Clases
export const clasesAPI = {
  // Crear nueva clase
  crear: async (claseData: ClaseCreate): Promise<Clase> => {
    const response = await apiClient.post('/academic/clases/', claseData);
    return response.data;
  },

  // Obtener clase por ID
  obtenerPorId: async (claseId: string): Promise<ClaseDetallada> => {
    const response = await apiClient.get(`/academic/clases/${claseId}`);
    return response.data;
  },

  // Actualizar clase
  actualizar: async (claseId: string, claseData: ClaseUpdate): Promise<Clase> => {
    const response = await apiClient.put(`/academic/clases/${claseId}`, claseData);
    return response.data;
  },

  // Eliminar clase
  eliminar: async (claseId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/academic/clases/${claseId}`);
    return response.data;
  },

  // Regenerar código de acceso
  regenerarCodigo: async (claseId: string): Promise<{ codigo_acceso: string; fecha_generacion: string }> => {
    const response = await apiClient.post(`/academic/clases/${claseId}/regenerar-codigo`);
    return response.data;
  },

  // Unirse a clase con código
  unirse: async (datosUnion: EstudianteUnirse): Promise<RespuestaUnirse> => {
    const response = await apiClient.post('/academic/clases/unirse', datosUnion);
    return response.data;
  },

  // Obtener clases por grupo
  obtenerPorGrupo: async (grupoId: string, skip = 0, limit = 100): Promise<Clase[]> => {
    const response = await apiClient.get(`/academic/clases/grupo/${grupoId}`, {
      params: { skip, limit }
    });
    return response.data;
  },

  // Obtener clases por docente
  obtenerPorDocente: async (docenteId: string, skip = 0, limit = 100): Promise<Clase[]> => {
    const response = await apiClient.get(`/academic/clases/docente/${docenteId}`, {
      params: { skip, limit }
    });
    return response.data;
  },

  // Obtener estudiantes activos en clase
  obtenerEstudiantesActivos: async (claseId: string): Promise<any[]> => {
    const response = await apiClient.get(`/academic/clases/${claseId}/estudiantes-activos`);
    return response.data;
  },

  // Obtener historial de accesos
  obtenerHistorial: async (claseId: string): Promise<any[]> => {
    const response = await apiClient.get(`/academic/clases/${claseId}/historial`);
    return response.data;
  },

  // Obtener estadísticas de clase
  obtenerEstadisticas: async (claseId: string): Promise<any> => {
    const response = await apiClient.get(`/academic/clases/${claseId}/estadisticas`);
    return response.data;
  },
};

// API para Material Educativo
export const materialAPI = {
  // Crear material
  crear: async (materialData: MaterialEducativoCreate): Promise<MaterialEducativo> => {
    const response = await apiClient.post('/academic/material/', materialData);
    return response.data;
  },

  // Obtener material por ID
  obtenerPorId: async (materialId: string): Promise<MaterialEducativoDetallado> => {
    const response = await apiClient.get(`/academic/material/${materialId}`);
    return response.data;
  },

  // Actualizar material
  actualizar: async (materialId: string, materialData: MaterialEducativoUpdate): Promise<MaterialEducativo> => {
    const response = await apiClient.put(`/academic/material/${materialId}`, materialData);
    return response.data;
  },

  // Eliminar (archivar) material
  eliminar: async (materialId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/academic/material/${materialId}`);
    return response.data;
  },

  // Listar material con filtros
  listar: async (filtros: FiltrosMaterial = {}): Promise<MaterialEducativo[]> => {
    const response = await apiClient.get('/academic/material/', { params: filtros });
    return response.data;
  },

  // Buscar material
  buscar: async (termino: string, filtros: Partial<FiltrosMaterial> = {}): Promise<MaterialEducativo[]> => {
    const response = await apiClient.get(`/academic/material/buscar/${termino}`, { params: filtros });
    return response.data;
  },

  // Obtener material por carpeta
  obtenerPorCarpeta: async (carpeta: CarpetaMaterial, skip = 0, limit = 100): Promise<MaterialEducativo[]> => {
    const response = await apiClient.get(`/academic/material/carpeta/${carpeta}`, {
      params: { skip, limit }
    });
    return response.data;
  },

  // Obtener material popular
  obtenerPopular: async (limit = 10, carpeta?: CarpetaMaterial): Promise<MaterialEducativo[]> => {
    const params = { limit, ...(carpeta && { carpeta }) };
    const response = await apiClient.get('/academic/material/popular/', { params });
    return response.data;
  },

  // Subir nueva versión
  subirNuevaVersion: async (materialId: string, nuevaVersion: any): Promise<MaterialEducativo> => {
    const response = await apiClient.post(`/academic/material/${materialId}/nueva-version`, nuevaVersion);
    return response.data;
  },

  // Obtener versiones
  obtenerVersiones: async (materialId: string): Promise<MaterialEducativo[]> => {
    const response = await apiClient.get(`/academic/material/${materialId}/versiones`);
    return response.data;
  },

  // Obtener estadísticas
  obtenerEstadisticas: async (): Promise<EstadisticasMaterial> => {
    const response = await apiClient.get('/academic/material/estadisticas/');
    return response.data;
  },

  // Sincronizar con Google Drive
  sincronizarDrive: async (materialId: string, syncData: any): Promise<{ message: string }> => {
    const response = await apiClient.post(`/academic/material/${materialId}/sincronizar-drive`, syncData);
    return response.data;
  },
};

// API para Grupos y Programas (métodos básicos)
export const gruposAPI = {
  listar: async (): Promise<Grupo[]> => {
    const response = await apiClient.get('/academic/grupos/');
    return response.data;
  },

  obtenerPorId: async (grupoId: string): Promise<Grupo> => {
    const response = await apiClient.get(`/academic/grupos/${grupoId}`);
    return response.data;
  },
};

export const programasAPI = {
  listar: async (): Promise<Programa[]> => {
    const response = await apiClient.get('/academic/programas/');
    return response.data;
  },

  obtenerPorId: async (programaId: string): Promise<Programa> => {
    const response = await apiClient.get(`/academic/programas/${programaId}`);
    return response.data;
  },
};

// Utilidades
export const utils = {
  // Formatear modalidad de curso para mostrar
  formatearModalidad: (modalidad: ModalidadCurso): string => {
    const modalidades = {
      [ModalidadCurso.ANUAL]: 'Anual',
      [ModalidadCurso.SEMESTRAL]: 'Semestral',
      [ModalidadCurso.TRIMESTRAL]: 'Trimestral',
      [ModalidadCurso.CUATRIMESTRAL]: 'Cuatrimestral',
      [ModalidadCurso.BIMESTRAL]: 'Bimestral',
      [ModalidadCurso.MENSUAL]: 'Mensual',
      [ModalidadCurso.MODULAR]: 'Modular',
      [ModalidadCurso.FLEXIBLE]: 'Flexible',
      [ModalidadCurso.OTRO]: 'Otro',
    };
    return modalidades[modalidad] || modalidad;
  },

  // Formatear nombre de carpeta para mostrar
  formatearCarpeta: (carpeta: CarpetaMaterial): string => {
    const carpetas = {
      [CarpetaMaterial.LECTURAS]: 'Lecturas',
      [CarpetaMaterial.GUIAS]: 'Guías',
      [CarpetaMaterial.TAREAS]: 'Tareas',
      [CarpetaMaterial.EXAMENES]: 'Exámenes',
      [CarpetaMaterial.RECURSOS]: 'Recursos',
      [CarpetaMaterial.MULTIMEDIA]: 'Multimedia',
      [CarpetaMaterial.EJERCICIOS]: 'Ejercicios',
      [CarpetaMaterial.BIBLIOGRAFIAS]: 'Bibliografías',
      [CarpetaMaterial.OTROS]: 'Otros',
    };
    return carpetas[carpeta] || carpeta;
  },

  // Formatear tipo de material para mostrar
  formatearTipoMaterial: (tipo: TipoMaterialEducativo): string => {
    const tipos = {
      [TipoMaterialEducativo.PDF]: 'PDF',
      [TipoMaterialEducativo.VIDEO]: 'Video',
      [TipoMaterialEducativo.AUDIO]: 'Audio',
      [TipoMaterialEducativo.IMAGEN]: 'Imagen',
      [TipoMaterialEducativo.PRESENTACION]: 'Presentación',
      [TipoMaterialEducativo.DOCUMENTO]: 'Documento',
      [TipoMaterialEducativo.HOJA_DE_CALCULO]: 'Hoja de Cálculo',
      [TipoMaterialEducativo.ENLACE]: 'Enlace',
      [TipoMaterialEducativo.INTERACTIVO]: 'Interactivo',
      [TipoMaterialEducativo.CODIGO_FUENTE]: 'Código Fuente',
      [TipoMaterialEducativo.OTRO]: 'Otro',
    };
    return tipos[tipo] || tipo;
  },

  // Formatear fecha
  formatearFecha: (fecha: string): string => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  },

  // Formatear fecha y hora
  formatearFechaHora: (fecha: string): string => {
    return new Date(fecha).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  },
};

export default {
  cursos: cursosAPI,
  clases: clasesAPI,
  material: materialAPI,
  grupos: gruposAPI,
  programas: programasAPI,
  utils,
};