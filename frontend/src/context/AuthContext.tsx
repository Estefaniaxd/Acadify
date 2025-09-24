import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

type User = {
  id: string;
  username: string;
  email: string;
  role: string;
};

type AuthContextType = {
  user: User | null;
  isAuthenticated: boolean;
  login: (accessToken: string, refreshToken?: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Pequeña función para decodificar JWT sin dependencias externas.
// Maneja correctamente payload UTF-8.
const parseUserFromToken = (token: string): User | null => {
  try {
    if (!token || typeof token !== 'string') return null
    const parts = token.split('.')
    if (parts.length < 2) return null
    const payload = parts[1]
    // atob puede lanzar si el payload no está bien formado
    const json = decodeURIComponent(
      Array.prototype.map
        .call(atob(payload), (c: string) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    const decoded: any = JSON.parse(json)
    return {
      id: decoded.sub || decoded.user_id || '',
      username: decoded.username || '',
      email: decoded.email || decoded.correo_institucional || '',
      role: decoded.role || decoded.rol || decoded.perfil || 'estudiante',
    }
  } catch {
    return null
  }
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    if (token) {
      const u = parseUserFromToken(token);
      if (u) {
        setUser(u);
        setIsAuthenticated(true);
      } else {
        // Token inválido, limpiarlo
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }

    // Escuchar eventos de token expirado
    const handleTokenExpired = () => {
      console.log('🔐 Token expired event received, logging out');
      logout();
    };

    window.addEventListener('auth-token-expired', handleTokenExpired);

    return () => {
      window.removeEventListener('auth-token-expired', handleTokenExpired);
    };
  }, []);

  const login = (accessToken: string, refreshToken?: string) => {
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
    const u = parseUserFromToken(accessToken);
    setUser(u);
    setIsAuthenticated(!!u);
  }

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = '/login';
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
