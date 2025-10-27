// Utilidades de autenticación
export interface AuthStatus {
  isAuthenticated: boolean;
  token: string | null;
  needsLogin: boolean;
  tokenExpired: boolean;
}

export const checkAuthStatus = (): AuthStatus => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return {
      isAuthenticated: false,
      token: null,
      needsLogin: true,
      tokenExpired: false
    };
  }

  // Verificar formato básico del token JWT
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      localStorage.removeItem('access_token');
      return {
        isAuthenticated: false,
        token: null,
        needsLogin: true,
        tokenExpired: false
      };
    }

    // Decodificar payload para verificar expiración
    const payload = JSON.parse(atob(parts[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    
    if (payload.exp && payload.exp < currentTime) {
      localStorage.removeItem('access_token');
      return {
        isAuthenticated: false,
        token: null,
        needsLogin: true,
        tokenExpired: true
      };
    }

    return {
      isAuthenticated: true,
      token: token,
      needsLogin: false,
      tokenExpired: false
    };
  } catch (error) {
    console.warn('Error verificando token:', error);
    localStorage.removeItem('access_token');
    return {
      isAuthenticated: false,
      token: null,
      needsLogin: true,
      tokenExpired: false
    };
  }
};

export const getUserInfo = () => {
  const token = localStorage.getItem('access_token');
  if (!token) return null;

  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = JSON.parse(atob(parts[1]));
    return payload;
  } catch (error) {
    console.warn('Error decodificando token:', error);
    return null;
  }
};

export const clearAuth = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_info');
};