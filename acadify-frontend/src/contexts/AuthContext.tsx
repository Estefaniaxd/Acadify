import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService, { User } from '../services/authService';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (identifier: string, password: string, otp_code?: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (correo_institucional: string) => Promise<void>;
  resetPassword: (data: { correo_institucional: string; reset_code: string; new_password: string }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};




export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  const loadUser = async () => {
    try {
      const userData = await authService.getUserInfo();
      setUser(userData);
    } catch (error) {
      console.error('Error loading user:', error);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (identifier: string, password: string, otp_code?: string) => {
    await authService.login({ identifier, password, otp_code });
    await loadUser();
  };

  const register = async (data: any) => {
    await authService.register(data);
    await loadUser();
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const forgotPassword = async (correo_institucional: string) => {
    await authService.forgotPassword({ correo_institucional });
  };

  const resetPassword = async (data: { correo_institucional: string; reset_code: string; new_password: string }) => {
    await authService.resetPassword(data);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};