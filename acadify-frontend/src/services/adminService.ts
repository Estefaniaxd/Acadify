import { api } from './api';

export interface UserListFilters {
  search?: string;
  role?: 'estudiante' | 'docente' | 'coordinador' | 'administrador';
  skip?: number;
  limit?: number;
}

export interface UserCreateData {
  nombres: string;
  apellidos: string;
  correo_institucional?: string;
  username?: string;
  password: string;
  tipo_documento: 'cc' | 'ti' | 'ce' | 'pasaporte';
  numero_documento: string;
  rol: 'estudiante' | 'docente' | 'coordinador' | 'administrador';
  telefono?: string;
  descripcion?: string;
}

export interface UserUpdateData {
  nombres?: string;
  apellidos?: string;
  telefono?: string;
  descripcion?: string;
}

export interface Institution {
  institucion_id: string;
  nombre: string;
  sigla: string;
  lema?: string;
  tipo_institucion: string;
  usa_programas: boolean;
  nivel_educativo: string;
  sector: string;
  direccion?: string;
  ciudad: string;
  pais: string;
  correo_institucional: string;
  telefono?: string;
  nit?: string;
  estado: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface InstitutionCreateData {
  nombre: string;
  sigla: string;
  lema?: string;
  tipo_institucion: 'universidad' | 'colegio' | 'instituto' | 'centro_formacion';
  usa_programas: boolean;
  nivel_educativo: 'primaria' | 'secundaria' | 'universitario' | 'posgrado' | 'tecnico' | 'tecnologo';
  sector: 'publico' | 'privado' | 'mixto';
  direccion?: string;
  ciudad: string;
  pais: string;
  correo_institucional: string;
  telefono?: string;
  nit?: string;
}

export interface InstitutionUpdateData {
  nombre?: string;
  sigla?: string;
  lema?: string;
  tipo_institucion?: 'universidad' | 'colegio' | 'instituto' | 'centro_formacion';
  usa_programas?: boolean;
  nivel_educativo?: 'primaria' | 'secundaria' | 'universitario' | 'posgrado' | 'tecnico' | 'tecnologo';
  sector?: 'publico' | 'privado' | 'mixto';
  direccion?: string;
  ciudad?: string;
  pais?: string;
  correo_institucional?: string;
  telefono?: string;
  nit?: string;
}

export interface CoordinatorInvitation {
  email_destino: string;
}

export interface UserResponse {
  usuario_id: string;
  correo_institucional?: string;
  username?: string;
  nombres: string;
  apellidos: string;
  tipo_documento: string;
  numero_documento: string;
  rol: string;
  estado_cuenta: string;
  email_verified: boolean;
  twofa_enabled: boolean;
  telefono?: string;
  descripcion?: string;
  fecha_creacion: string;
  ultimo_acceso?: string;
}

class AdminService {
  // ========================
  // GESTIÓN DE USUARIOS
  // ========================

  // Obtener lista de usuarios con filtros y paginación
  async getUsers(filters: UserListFilters = {}): Promise<UserResponse[]> {
    try {
      const params = new URLSearchParams();
      
      if (filters.search) params.append('search', filters.search);
      if (filters.role) params.append('role', filters.role);
      if (filters.skip) params.append('skip', filters.skip.toString());
      if (filters.limit) params.append('limit', filters.limit.toString());

  const response = await api.get(`/auth/users?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error obteniendo lista de usuarios');
    }
  }

  // Obtener usuario por ID
  async getUserById(userId: string): Promise<UserResponse> {
    try {
  const response = await api.get(`/auth/users/${userId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error obteniendo datos del usuario');
    }
  }

  // Crear nuevo usuario
  async createUser(userData: UserCreateData): Promise<UserResponse> {
    try {
  const response = await api.post('/auth/users', userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error creando usuario');
    }
  }

  // Actualizar usuario
  async updateUser(userId: string, userData: UserUpdateData): Promise<UserResponse> {
    try {
  const response = await api.put(`/auth/users/${userId}`, userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error actualizando usuario');
    }
  }

  // Eliminar usuario
  async deleteUser(userId: string): Promise<void> {
    try {
  await api.delete(`/auth/users/${userId}`);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error eliminando usuario');
    }
  }

  // ========================
  // GESTIÓN DE INSTITUCIONES
  // ========================

  // Obtener lista de instituciones
  async getInstitutions(filters: { search?: string; estado?: string } = {}): Promise<Institution[]> {
    try {
      const params = new URLSearchParams();
      
      if (filters.search) params.append('search', filters.search);
      if (filters.estado) params.append('estado', filters.estado);

  const response = await api.get(`/admin/instituciones?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error obteniendo instituciones');
    }
  }

  // Obtener institución por ID
  async getInstitutionById(institutionId: string): Promise<Institution> {
    try {
  const response = await api.get(`/admin/instituciones/${institutionId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error obteniendo institución');
    }
  }

  // Crear nueva institución
  async createInstitution(institutionData: InstitutionCreateData): Promise<Institution> {
    try {
  const response = await api.post('/admin/instituciones/registrar', institutionData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error creando institución');
    }
  }

  // Actualizar institución
  async updateInstitution(institutionId: string, institutionData: InstitutionUpdateData): Promise<Institution> {
    try {
  const response = await api.put(`/admin/instituciones/${institutionId}`, institutionData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error actualizando institución');
    }
  }

  // Eliminar institución
  async deleteInstitution(institutionId: string): Promise<void> {
    try {
  await api.delete(`/admin/instituciones/${institutionId}`);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error eliminando institución');
    }
  }

  // Invitar coordinador a institución
  async inviteCoordinator(institutionId: string, invitationData: CoordinatorInvitation): Promise<{ message: string }> {
    try {
  const response = await api.post(`/admin/instituciones/${institutionId}/invitar-coordinador`, invitationData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error enviando invitación a coordinador');
    }
  }
}

// Crear instancia singleton del servicio
const adminService = new AdminService();

export default adminService;