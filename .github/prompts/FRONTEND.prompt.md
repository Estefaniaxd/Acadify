---
mode: agent
---
# ⚛️ Frontend Guide - React + Vite + TypeScript

> **React 18 + TanStack Query + TailwindCSS + Framer Motion**

---

## 📂 ESTRUCTURA DETALLADA

```
frontend/src/
├── main.tsx              # 🚀 Entry point
├── App.tsx               # Router principal + lazy loading
├── pages/                # Páginas por ruta
│   ├── home/
│   ├── auth/            # Login, Register, Recover
│   ├── dashboard/       # Dashboards por rol
│   ├── cursos/          # Lista y detalle de cursos
│   ├── clase/           # Vista de clase (tablón, tareas, chat)
│   ├── gamificacion/    # Logros, puntos, tienda
│   ├── comunicacion/    # Mensajes, notificaciones
│   ├── admin/           # Panel admin (instituciones, usuarios)
│   └── avatar/          # Editor de avatares
├── modules/              # Módulos especializados (sub-features)
│   ├── instituciones/
│   ├── programas/
│   ├── invitaciones/
│   ├── logros/
│   └── comunicacion/
├── components/           # Componentes reutilizables
│   ├── ui/              # Design System
│   ├── layout/          # Layouts y navegación
│   ├── nav/
│   └── [domain]/        # Componentes por dominio
├── services/             # API clients (axios wrappers)
├── hooks/                # Custom hooks (React Query + lógica)
├── context/              # React Context (Auth, Toast)
├── types/                # TypeScript types/interfaces
├── utils/                # Helper functions
├── config/               # Configuración (API, constantes)
└── lib/                  # Third-party configs
```

---

## 🎨 DESIGN SYSTEM (`components/ui/`)

### **Button.tsx**

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  disabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  children,
  onClick,
  type = 'button'
}: ButtonProps) {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all';
  
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 disabled:bg-primary-300',
    secondary: 'bg-neutral-200 text-neutral-900 hover:bg-neutral-300 dark:bg-neutral-700 dark:text-white',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50',
    ghost: 'text-primary-600 hover:bg-primary-50',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
  
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        'disabled:cursor-not-allowed disabled:opacity-50'
      )}
    >
      {loading && <Spinner size="sm" className="mr-2" />}
      {!loading && leftIcon && <span className="mr-2">{leftIcon}</span>}
      {children}
      {rightIcon && <span className="ml-2">{rightIcon}</span>}
    </button>
  );
}
```

**Uso:**
```typescript
<Button variant="primary" size="lg" onClick={handleSubmit}>
  Guardar
</Button>

<Button variant="outline" leftIcon={<PlusIcon />} loading={isLoading}>
  Crear Institución
</Button>
```

---

### **Input.tsx**

```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Input({
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  className,
  ...props
}: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {leftIcon}
          </div>
        )}
        
        <input
          className={cn(
            'w-full px-4 py-2 border rounded-lg',
            'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'dark:bg-neutral-800 dark:border-neutral-700 dark:text-white',
            leftIcon && 'pl-10',
            rightIcon && 'pr-10',
            error && 'border-red-500 focus:ring-red-500',
            className
          )}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            {rightIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
      
      {helperText && !error && (
        <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">{helperText}</p>
      )}
    </div>
  );
}
```

**Uso:**
```typescript
<Input
  label="Email"
  type="email"
  placeholder="tu@email.com"
  leftIcon={<MailIcon />}
  error={errors.email?.message}
/>
```

---

### **Modal.tsx**

```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  size = 'md',
  children,
  footer
}: ModalProps) {
  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full'
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div
        className={cn(
          'relative w-full bg-white dark:bg-neutral-900 rounded-xl shadow-xl',
          'animate-fade-in-scale',
          sizes[size]
        )}
      >
        {/* Header */}
        {title && (
          <div className="px-6 py-4 border-b dark:border-neutral-800">
            <h3 className="text-lg font-semibold">{title}</h3>
            {description && (
              <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
                {description}
              </p>
            )}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600"
            >
              <XIcon className="w-5 h-5" />
            </button>
          </div>
        )}
        
        {/* Body */}
        <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
          {children}
        </div>
        
        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t dark:border-neutral-800 flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 🪝 CUSTOM HOOKS (React Query)

### **useAuth.ts** (AuthContext)

```typescript
import { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import { authService } from '@/services/auth.service';

interface AuthContextValue {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  updateUser: (user: UserProfile) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Verificar token al montar
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded = jwtDecode<{ sub: string }>(token);
        // Cargar perfil del usuario
        authService.getProfile().then(setUser).catch(() => {
          // Token inválido/expirado
          localStorage.removeItem('access_token');
        });
      } catch {
        localStorage.removeItem('access_token');
      }
    }
    setIsLoading(false);
  }, []);
  
  const login = async (credentials: LoginRequest) => {
    const response = await authService.login(credentials);
    
    if (response.requires_2fa) {
      // Redirigir a página de 2FA con session_token
      return;
    }
    
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    setUser(response.user);
  };
  
  const logout = () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      authService.logout(refreshToken).catch(() => {});
    }
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };
  
  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      updateUser: setUser
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

### **useInstituciones.ts** (React Query)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { institucionesService } from '@/services/instituciones.service';

// Query Keys
export const INSTITUCION_KEYS = {
  all: ['instituciones'] as const,
  lists: () => [...INSTITUCION_KEYS.all, 'list'] as const,
  list: (filters?: InstitucionFilters) => [...INSTITUCION_KEYS.lists(), filters] as const,
  details: () => [...INSTITUCION_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...INSTITUCION_KEYS.details(), id] as const,
  stats: (id: string) => [...INSTITUCION_KEYS.detail(id), 'stats'] as const
};

// Lista de instituciones
export function useInstituciones(filters?: InstitucionFilters) {
  return useQuery({
    queryKey: INSTITUCION_KEYS.list(filters),
    queryFn: () => institucionesService.getAll(filters),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

// Detalle de institución
export function useInstitucion(institucionId: string) {
  return useQuery({
    queryKey: INSTITUCION_KEYS.detail(institucionId),
    queryFn: () => institucionesService.getById(institucionId),
    enabled: !!institucionId,
    staleTime: 1000 * 60 * 5,
  });
}

// Estadísticas
export function useInstitucionStats(institucionId: string) {
  return useQuery({
    queryKey: INSTITUCION_KEYS.stats(institucionId),
    queryFn: () => institucionesService.getStats(institucionId),
    enabled: !!institucionId,
    staleTime: 1000 * 60 * 2, // 2 minutos
    refetchInterval: 1000 * 60 * 2, // Auto-refetch cada 2 min
  });
}

// Crear institución
export function useCrearInstitucion() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: InstitucionCreate) => institucionesService.create(data),
    onSuccess: () => {
      // Invalidar cache de listas
      queryClient.invalidateQueries({ queryKey: INSTITUCION_KEYS.lists() });
      
      // Toast de éxito
      toast.success('Institución creada exitosamente');
    },
    onError: (error: AxiosError<{ detail: string }>) => {
      toast.error(error.response?.data.detail || 'Error al crear institución');
    }
  });
}

// Actualizar institución
export function useActualizarInstitucion(institucionId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: InstitucionUpdate) => institucionesService.update(institucionId, data),
    onSuccess: (updatedData) => {
      // Actualizar cache del detalle (optimistic update)
      queryClient.setQueryData(
        INSTITUCION_KEYS.detail(institucionId),
        updatedData
      );
      
      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: INSTITUCION_KEYS.lists() });
      
      toast.success('Institución actualizada');
    }
  });
}

// Eliminar institución
export function useEliminarInstitucion() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (institucionId: string) => institucionesService.delete(institucionId),
    onSuccess: (_, institucionId) => {
      // Remover del cache
      queryClient.removeQueries({ queryKey: INSTITUCION_KEYS.detail(institucionId) });
      
      // Invalidar listas
      queryClient.invalidateQueries({ queryKey: INSTITUCION_KEYS.lists() });
      
      toast.success('Institución eliminada');
    }
  });
}

// Invitar coordinador
export function useInvitarCoordinador(institucionId: string) {
  return useMutation({
    mutationFn: (email: string) => institucionesService.invitarCoordinador(institucionId, email),
    onSuccess: () => {
      toast.success('Invitación enviada exitosamente');
    }
  });
}
```

**Uso en componente:**
```typescript
function AdminInstitucionesPage() {
  const { data: instituciones, isLoading, error } = useInstituciones();
  const crearInstitucion = useCrearInstitucion();
  const eliminarInstitucion = useEliminarInstitucion();
  
  const handleCrear = async (data: InstitucionCreate) => {
    await crearInstitucion.mutateAsync(data);
  };
  
  const handleEliminar = (id: string) => {
    if (confirm('¿Eliminar institución?')) {
      eliminarInstitucion.mutate(id);
    }
  };
  
  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div>
      {instituciones.map(inst => (
        <InstitucionCard
          key={inst.institucion_id}
          institucion={inst}
          onDelete={handleEliminar}
        />
      ))}
    </div>
  );
}
```

---

## 🌐 API SERVICES

### **api.config.ts** (Axios Setup)

```typescript
import axios from 'axios';
import { refreshToken } from './auth.service';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor - añadir token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - refresh token automático
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Si error 401 y no es retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');
        
        // Solicitar nuevo access_token
        const { access_token } = await refreshToken(refreshToken);
        localStorage.setItem('access_token', access_token);
        
        // Retry request original con nuevo token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh falló → logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

---

### **instituciones.service.ts**

```typescript
import { apiClient } from '@/config/api.config';

export const institucionesService = {
  async getAll(filters?: InstitucionFilters): Promise<Institucion[]> {
    const params = new URLSearchParams();
    if (filters?.tipo) params.append('tipo', filters.tipo);
    if (filters?.estado) params.append('estado', filters.estado);
    
    const response = await apiClient.get('/api/instituciones', { params });
    return response.data;
  },
  
  async getById(id: string): Promise<Institucion> {
    const response = await apiClient.get(`/api/instituciones/${id}`);
    return response.data;
  },
  
  async create(data: InstitucionCreate): Promise<Institucion> {
    const response = await apiClient.post('/api/instituciones', data);
    return response.data;
  },
  
  async update(id: string, data: InstitucionUpdate): Promise<Institucion> {
    const response = await apiClient.put(`/api/instituciones/${id}`, data);
    return response.data;
  },
  
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/instituciones/${id}`);
  },
  
  async getStats(id: string): Promise<InstitucionStats> {
    const response = await apiClient.get(`/api/instituciones/${id}/estadisticas`);
    return response.data;
  },
  
  async invitarCoordinador(id: string, email: string): Promise<void> {
    await apiClient.post(`/api/instituciones/${id}/invitar-coordinador`, { email });
  }
};
```

---

## 🎯 PÁGINAS Y ROUTING

### **App.tsx** (Lazy Loading)

```typescript
import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Spinner } from '@/components/ui';

// Carga inmediata (landing page)
import { Home } from './pages/home';

// Lazy loading de páginas pesadas
const Login = lazy(() => import('./pages/auth/Login'));
const DashboardAdmin = lazy(() => import('./pages/dashboard/DashboardAdmin'));
const AdminInstitucionesPage = lazy(() => import('./pages/admin/AdminInstitucionesPage'));
const CursosPage = lazy(() => import('./pages/cursos/CursosPage'));

// Loading fallback
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <Spinner size="lg" />
  </div>
);

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      
      <Route
        path="/login"
        element={
          <Suspense fallback={<PageLoader />}>
            <Login />
          </Suspense>
        }
      />
      
      <Route
        path="/dashboard-admin"
        element={
          <Suspense fallback={<PageLoader />}>
            <DashboardAdmin />
          </Suspense>
        }
      />
      
      <Route
        path="/admin/instituciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <AdminInstitucionesPage />
          </Suspense>
        }
      />
      
      <Route
        path="/cursos"
        element={
          <Suspense fallback={<PageLoader />}>
            <CursosPage />
          </Suspense>
        }
      />
    </Routes>
  );
}
```

---

### **Login.tsx** (Form con React Hook Form)

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/context/AuthContext';
import { Button, Input } from '@/components/ui';

const loginSchema = z.object({
  identifier: z.string().min(1, 'Usuario o email requerido'),
  password: z.string().min(6, 'Mínimo 6 caracteres')
});

type LoginForm = z.infer<typeof loginSchema>;

export default function Login() {
  const { login } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema)
  });
  
  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data);
      // AuthContext maneja redirección
    } catch (error) {
      toast.error('Credenciales inválidas');
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-purple-50">
      <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-lg">
        <h1 className="text-2xl font-bold text-center mb-6">Iniciar Sesión</h1>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Usuario o Email"
            placeholder="tu_usuario o tu@email.com"
            error={errors.identifier?.message}
            {...register('identifier')}
          />
          
          <Input
            label="Contraseña"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password')}
          />
          
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            loading={isSubmitting}
          >
            Ingresar
          </Button>
        </form>
        
        <div className="mt-4 text-center">
          <a href="/recover" className="text-sm text-primary-600 hover:underline">
            ¿Olvidaste tu contraseña?
          </a>
        </div>
      </div>
    </div>
  );
}
```

---

## 🎨 ANIMACIONES (Framer Motion)

### **Card con Hover Effect**

```typescript
import { motion } from 'framer-motion';

export function CursoCard({ curso }: { curso: Curso }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ duration: 0.2 }}
      className="bg-white dark:bg-neutral-800 rounded-xl shadow-md p-6"
    >
      <h3 className="text-xl font-semibold">{curso.nombre}</h3>
      <p className="text-neutral-600 dark:text-neutral-400 mt-2">
        {curso.descripcion}
      </p>
      <Button variant="outline" className="mt-4">
        Ver Detalles
      </Button>
    </motion.div>
  );
}
```

### **Modal con Fade In**

```typescript
import { motion, AnimatePresence } from 'framer-motion';

export function Modal({ isOpen, onClose, children }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />
          
          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', duration: 0.3 }}
            className="fixed inset-0 flex items-center justify-center z-50"
          >
            <div className="bg-white dark:bg-neutral-900 rounded-xl p-6 max-w-md w-full">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

---

## 🧪 TESTING (Vitest)

### **Test Setup** (`vitest.config.ts`)

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov']
    }
  }
});
```

### **Component Test**

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledOnce();
  });
  
  it('disables button when loading', () => {
    render(<Button loading>Submit</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
```

### **Hook Test (React Query)**

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useInstituciones } from '@/hooks/useInstituciones';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useInstituciones', () => {
  it('fetches instituciones successfully', async () => {
    const { result } = renderHook(() => useInstituciones(), {
      wrapper: createWrapper()
    });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toBeDefined();
    expect(Array.isArray(result.current.data)).toBe(true);
  });
});
```

---

## 📦 BUILD Y DEPLOYMENT

### **Vite Config** (Chunks Optimization)

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // React core bundle
          if (id.includes('react') || id.includes('react-dom')) {
            return 'react-vendor';
          }
          
          // React Query
          if (id.includes('@tanstack/react-query')) {
            return 'react-query';
          }
          
          // Framer Motion
          if (id.includes('framer-motion')) {
            return 'framer-motion';
          }
          
          // UI components
          if (id.includes('/src/components/ui/')) {
            return 'ui-components';
          }
          
          // Dashboard modules
          if (id.includes('/src/pages/dashboard/')) {
            return 'dashboard';
          }
          
          // Avatar editor (pesado)
          if (id.includes('/src/modules/avatar/')) {
            return 'avatar';
          }
        }
      }
    },
    chunkSizeWarningLimit: 600,
    minify: 'esbuild',
    sourcemap: false,
    cssCodeSplit: true
  }
});
```

### **Build Commands**

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Type check
npm run type-check

# Lint
npm run lint
npm run lint:fix

# Tests
npm run test
npm run test:coverage
```

---

## 🔑 MEJORES PRÁCTICAS

1. ✅ **Lazy loading** para todas las páginas excepto landing
2. ✅ **React Query** para TODAS las requests (nunca useState + useEffect)
3. ✅ **Memoization** con `useMemo`/`useCallback` en listas grandes
4. ✅ **Error boundaries** en rutas principales
5. ✅ **Loading states** siempre visibles y animados
6. ✅ **Optimistic updates** en mutaciones simples
7. ✅ **Debounce** en búsquedas (500ms)
8. ✅ **Validación** con React Hook Form + Zod
9. ✅ **Accessibility**: roles, aria-labels, keyboard nav
10. ✅ **Dark mode** con TailwindCSS dark: variant

---

**Next**: Ver [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) para estructura de BD.
