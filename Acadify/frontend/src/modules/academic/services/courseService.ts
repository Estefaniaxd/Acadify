// Servicio para manejar las operaciones de cursos con la API
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Configurar axios para academic
const academicAPI = axios.create({
  baseURL: `${API_BASE_URL}/academic`,
  headers: {
    'Content-Type': 'application/json'
  }
});

export interface Course {
  id: string;
  nombre: string;
  codigo: string;
  descripcion: string;
  activo: boolean;
  fecha_creacion: string;
  creditos: number;
  horas_academicas: number;
  profesor: string;
  estudiantes: number;
  progreso: number;
  estado: string;
}

export interface CourseResponse {
  success: boolean;
  data: Course[];
  total: number;
  message: string;
  error?: string;
}

export const courseService = {
  // Obtener todos los cursos - por ahora usar endpoint público
  async getCourses(): Promise<CourseResponse> {
    try {
      console.log('🔄 Obteniendo cursos desde API...');
      const response = await academicAPI.get<CourseResponse>('/cursos/public');
      console.log('✅ Respuesta API cursos:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error obteniendo cursos:', error);
      
      // Fallback a datos mock si la API falla
      return {
        success: false,
        data: [
          {
            id: "1",
            nombre: "Matemáticas Avanzadas",
            codigo: "MAT301", 
            descripcion: "Curso de cálculo diferencial e integral",
            activo: true,
            fecha_creacion: "2024-01-15T10:00:00",
            creditos: 4,
            horas_academicas: 64,
            profesor: "Dr. García Rodríguez",
            estudiantes: 28,
            progreso: 65,
            estado: "activo"
          },
          {
            id: "2",
            nombre: "Historia Universal",
            codigo: "HIS201",
            descripcion: "Historia desde la antigüedad hasta la era moderna", 
            activo: true,
            fecha_creacion: "2024-01-15T10:00:00",
            creditos: 3,
            horas_academicas: 48,
            profesor: "Dra. Martínez López",
            estudiantes: 32,
            progreso: 45,
            estado: "activo"
          },
          {
            id: "3",
            nombre: "Programación Orientada a Objetos",
            codigo: "POO301",
            descripcion: "Fundamentos de programación orientada a objetos",
            activo: true,
            fecha_creacion: "2024-01-15T10:00:00",
            creditos: 4,
            horas_academicas: 64,
            profesor: "Ing. Santos Pérez",
            estudiantes: 24,
            progreso: 80,
            estado: "activo"
          }
        ],
        total: 3,
        message: "Usando datos de fallback - API no disponible",
        error: error instanceof Error ? error.message : 'Error desconocido'
      };
    }
  },

  // Obtener un curso específico por ID
  async getCourseById(id: string): Promise<Course | null> {
    try {
      const response = await this.getCourses();
      const course = response.data.find(course => course.id === id);
      return course || null;
    } catch (error) {
      console.error('❌ Error obteniendo curso por ID:', error);
      return null;
    }
  }
};

export default courseService;