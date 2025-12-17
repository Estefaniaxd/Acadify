import { createContext, useContext, useEffect, useState, useMemo, useCallback, ReactNode } from 'react';

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
  logoutAllDevices: () => Promise<void>;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Pequeña función para decodificar JWT sin dependencias externas.
// Maneja correctamente payload UTF-8.
const base64UrlToBase64 = (value: string): string => {
  let normalized = value.replace(/-/g, '+').replace(/_/g, '/');
  const padding = normalized.length % 4;
  if (padding) {
    normalized += '='.repeat(4 - padding);
  }
  return normalized;
};

const parseUserFromToken = (token: string): User | null => {
  try {
    if (!token || typeof token !== 'string') {
      console.warn('AuthContext: Token inválido o vacío');
      return null;
    }
    const parts = token.split('.');
    if (parts.length < 2) {
      console.warn('AuthContext: Token malformado (menos de 2 partes)');
      return null;
    }

    const payloadSegment = parts[1];
    const base64Payload = base64UrlToBase64(payloadSegment);

    try {
      const json = decodeURIComponent(
        Array.prototype.map
          .call(atob(base64Payload), (c: string) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const decoded: Record<string, unknown> = JSON.parse(json);

      console.log('AuthContext: Token decodificado correctamente', {
        sub: decoded.sub,
        exp: decoded.exp,
        roles: decoded.roles
      });

      const rawRoles = decoded.roles;
      const rawRole = decoded.role || decoded.rol || decoded.perfil;
      let roleCandidate: string | undefined;

      if (typeof rawRole === 'string') {
        roleCandidate = rawRole;
      } else if (Array.isArray(rawRoles) && rawRoles.length > 0 && typeof rawRoles[0] === 'string') {
        roleCandidate = rawRoles[0];
      }

      let role = roleCandidate || 'estudiante';

      const roleMap: Record<string, string> = {
        administrador: 'admin',
        ADMINISTRADOR: 'admin',
        Admin: 'admin',
        ADMIN: 'admin',
        estudiante: 'estudiante',
        ESTUDIANTE: 'estudiante',
        Estudiante: 'estudiante',
        profesor: 'profesor',
        PROFESOR: 'profesor',
        Profesor: 'profesor',
        coordinador: 'coordinador',
        COORDINADOR: 'coordinador',
        Coordinador: 'coordinador',
        docente: 'profesor',
        DOCENTE: 'profesor',
      };

      role = roleMap[role] || role.toLowerCase();

      const username = (decoded.username || decoded.name || decoded.nombres || '') as string;
      const email = (decoded.email || decoded.correo_institucional || decoded.preferred_username || '') as string;

      return {
        id: String(decoded.sub || decoded.user_id || ''),
        username,
        email,
        role,
      };
    } catch (e) {
      console.error('AuthContext: Error al decodificar payload JSON', e);
      return null;
    }
  } catch (error) {
    console.warn('AuthContext: Error general al procesar token:', error);
    return null;
  }
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  const login = useCallback((accessToken: string, refreshToken?: string) => {
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
    const u = parseUserFromToken(accessToken);
    setUser(u);
    setIsAuthenticated(!!u);
    setLoading(false);
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    setLoading(false);
    window.location.href = '/login';
  }, [])

  const logoutAllDevices = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        // Llamar al endpoint para cerrar sesión en todos los dispositivos
        await fetch('/api/v1/auth/logout-all-devices', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('Error al cerrar sesión en todos los dispositivos:', error);
    } finally {
      // Limpiar estado local de todas formas
      logout();
    }
  }, [logout])

  useEffect(() => {
    const token = localStorage.getItem('access_token');
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
    setLoading(false);

    // Escuchar eventos de token expirado
    const handleTokenExpired = () => {
      logout();
    };

    window.addEventListener('auth-token-expired', handleTokenExpired);

    return () => {
      window.removeEventListener('auth-token-expired', handleTokenExpired);
    };
  }, [logout]);

  // Memoizar el valor del contexto para evitar re-renders innecesarios
  const contextValue = useMemo(
    () => ({ user, isAuthenticated, login, logout, logoutAllDevices, loading }),
    [user, isAuthenticated, login, logout, logoutAllDevices, loading]
  );

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
