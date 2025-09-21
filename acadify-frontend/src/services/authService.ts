import { api } from './api';

export interface LoginData {
  identifier: string;
  password: string;
  otp_code?: string;
}

export interface RegisterData {
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

export interface User {
  usuario_id: string;
  correo_institucional?: string;
  username?: string;
  nombres: string;
  apellidos: string;
  tipo_documento: string;
  numero_documento: string;
  rol: 'estudiante' | 'docente' | 'coordinador' | 'administrador';
  estado_cuenta: string;
  email_verified: boolean;
  twofa_enabled: boolean;
  twofa_method?: string;
  telefono?: string;
  descripcion?: string;
  fecha_creacion: string;
  ultimo_acceso?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface ForgotPasswordData {
  correo_institucional: string;
}

export interface ResetPasswordData {
  correo_institucional: string;
  reset_code: string;
  new_password: string;
}

class AuthService {
  // Login de usuario
  async login(data: LoginData): Promise<AuthResponse> {
    try {
      const response = await api.post('/auth/login', {
        identifier: data.identifier,
        password: data.password,
        otp_code: data.otp_code
      });
      // Si el backend responde con tokens
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
        const userInfo = await this.getUserInfo();
        localStorage.setItem('user_data', JSON.stringify(userInfo));
        return {
          user: userInfo,
          access_token: response.data.access_token,
          refresh_token: response.data.refresh_token,
          expires_in: response.data.expires_in || 3600
        };
      }
      // Si el backend responde que requiere OTP (2FA)
      if (response.data.status === 'otp_required') {
        throw new Error('Se requiere código de verificación 2FA. Revisa tu email o SMS.');
      }
      throw new Error('No se recibieron los tokens de autenticación');
    } catch (error: any) {
      // Si el backend responde con error HTTP
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error en el login');
    }
  }

  // Registro de usuario
  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      await api.post('/auth/register', data);
      
      // El backend devuelve directamente la información del usuario
      // Necesitamos hacer login después del registro para obtener tokens
      return await this.login({
        identifier: data.correo_institucional || data.username || '',
        password: data.password
      });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error en el registro');
    }
  }

  // Obtener información del usuario actual
  async getUserInfo(): Promise<User> {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error obteniendo información del usuario');
    }
  }

  // Logout
  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      // El API solo acepta 1-2 argumentos, así que agregamos el token como body si es necesario
      await api.post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : {});
    } catch (error) {
      // Incluso si hay error en el backend, limpiar localStorage
      console.error('Error en logout:', error);
    } finally {
      // Limpiar localStorage siempre
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
    }
  }

  // Refresh token
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No hay refresh token disponible');
      }

      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      const newAccessToken = response.data.access_token;
      localStorage.setItem('access_token', newAccessToken);
      
      return newAccessToken;
    } catch (error: any) {
      // Si el refresh falla, limpiar tokens
      try { await this.logout(); } catch {}
      throw new Error('Sesión expirada');
    }
  }

  // Forgot password
  async forgotPassword(data: ForgotPasswordData): Promise<void> {
    try {
      await api.post('/auth/forgot-password', data);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error enviando email de recuperación');
    }
  }

  // Reset password
  async resetPassword(data: ResetPasswordData): Promise<void> {
    try {
      await api.post('/auth/reset-password', data);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error reseteando contraseña');
    }
  }

  // Verificar si el usuario está autenticado
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    return !!(token && userData);
  }

  // Obtener datos del usuario desde localStorage
  getUserData(): User | null {
    try {
      const userData = localStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  }

  // Obtener token
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // Verificar email
  async verifyEmail(userId: string, verificationCode: string): Promise<void> {
    try {
      await api.post('/auth/verify-email', {
        usuario_id: userId,
        verification_code: verificationCode
      });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error verificando email');
    }
  }
}

// Crear instancia singleton del servicio
const authService = new AuthService();

export default authService;