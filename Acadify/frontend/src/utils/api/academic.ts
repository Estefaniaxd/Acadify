import { API_BASE_URL } from '../api';

// Tipos de datos para la API académica
export interface Curso {
  id: number;
  nombre: string;
  descripcion: string;
  codigo?: string;
  institucion_id: number;
  creado_por: number;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface Grupo {
  id: number;
  nombre: string;
  descripcion: string;
  curso_id: number;
  capacidad_maxima?: number;
  activo: boolean;
  fecha_creacion: string;
}

export interface Material {
  id: number;
  titulo: string;
  descripcion?: string;
  tipo: string;
  url_contenido?: string;
  curso_id: number;
  grupo_id?: number;
  fecha_creacion: string;
}

export interface Institucion {
  id: number;
  nombre: string;
  descripcion?: string;
  direccion?: string;
  telefono?: string;
  email?: string;
  activa: boolean;
  fecha_creacion: string;
}

// Funciones API para Cursos
export const cursoAPI = {
  async listar(): Promise<Curso[]> {
    const response = await fetch(`${API_BASE_URL}/academic/cursos/public`);
    if (!response.ok) {
      throw new Error(`Error al obtener cursos: ${response.statusText}`);
    }
    const result = await response.json();
    return result.data || [];
  },

  async obtenerPorId(id: number): Promise<Curso> {
    const response = await fetch(`${API_BASE_URL}/academic/cursos/${id}`);
    if (!response.ok) {
      throw new Error(`Error al obtener curso: ${response.statusText}`);
    }
    return response.json();
  },

  async crear(curso: Omit<Curso, 'id' | 'fecha_creacion' | 'fecha_actualizacion'>): Promise<Curso> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/cursos/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(curso),
    });
    if (!response.ok) {
      throw new Error(`Error al crear curso: ${response.statusText}`);
    }
    return response.json();
  },

  async actualizar(id: number, curso: Partial<Curso>): Promise<Curso> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/cursos/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(curso),
    });
    if (!response.ok) {
      throw new Error(`Error al actualizar curso: ${response.statusText}`);
    }
    return response.json();
  },

  async eliminar(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/cursos/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Error al eliminar curso: ${response.statusText}`);
    }
  }
};

// Funciones API para Grupos
export const grupoAPI = {
  async listar(): Promise<Grupo[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/grupos/`);
    if (!response.ok) {
      throw new Error(`Error al obtener grupos: ${response.statusText}`);
    }
    return response.json();
  },

  async listarPorCurso(cursoId: number): Promise<Grupo[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/grupos/curso/${cursoId}`);
    if (!response.ok) {
      throw new Error(`Error al obtener grupos del curso: ${response.statusText}`);
    }
    return response.json();
  },

  async obtenerPorId(id: number): Promise<Grupo> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/grupos/${id}`);
    if (!response.ok) {
      throw new Error(`Error al obtener grupo: ${response.statusText}`);
    }
    return response.json();
  },

  async crear(grupo: Omit<Grupo, 'id' | 'fecha_creacion'>): Promise<Grupo> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/grupos/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(grupo),
    });
    if (!response.ok) {
      throw new Error(`Error al crear grupo: ${response.statusText}`);
    }
    return response.json();
  }
};

// Funciones API para Material
export const materialAPI = {
  async listar(): Promise<Material[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/material/`);
    if (!response.ok) {
      throw new Error(`Error al obtener materiales: ${response.statusText}`);
    }
    return response.json();
  },

  async listarPorCurso(cursoId: number): Promise<Material[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/material/curso/${cursoId}`);
    if (!response.ok) {
      throw new Error(`Error al obtener materiales del curso: ${response.statusText}`);
    }
    return response.json();
  },

  async obtenerPorId(id: number): Promise<Material> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/material/${id}`);
    if (!response.ok) {
      throw new Error(`Error al obtener material: ${response.statusText}`);
    }
    return response.json();
  },

  async crear(material: Omit<Material, 'id' | 'fecha_creacion'>): Promise<Material> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/material/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(material),
    });
    if (!response.ok) {
      throw new Error(`Error al crear material: ${response.statusText}`);
    }
    return response.json();
  }
};

// Funciones API para Instituciones
export const institucionAPI = {
  async listar(): Promise<Institucion[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/instituciones/`);
    if (!response.ok) {
      throw new Error(`Error al obtener instituciones: ${response.statusText}`);
    }
    return response.json();
  },

  async obtenerPorId(id: number): Promise<Institucion> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/instituciones/${id}`);
    if (!response.ok) {
      throw new Error(`Error al obtener institución: ${response.statusText}`);
    }
    return response.json();
  },

  async crear(institucion: Omit<Institucion, 'id' | 'fecha_creacion'>): Promise<Institucion> {
    const response = await fetch(`${API_BASE_URL}/api/v1/academic/instituciones/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(institucion),
    });
    if (!response.ok) {
      throw new Error(`Error al crear institución: ${response.statusText}`);
    }
    return response.json();
  }
};

// Objeto principal de la API académica
export const academicAPI = {
  cursos: cursoAPI,
  grupos: grupoAPI,
  material: materialAPI,
  instituciones: institucionAPI
};

export default academicAPI;