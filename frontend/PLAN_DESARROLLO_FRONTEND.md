# 🎨 PLAN DE DESARROLLO FRONTEND - FLUJO INSTITUCIONES

**Fecha**: 7 de Noviembre 2025  
**Estado Actual**: Estructura parcial existente, necesita completarse e integrarse  
**Backend**: ✅ 100% Funcional (verificado)

---

## 📊 ANÁLISIS DEL ESTADO ACTUAL

### ✅ **LO QUE YA EXISTE Y FUNCIONA**

#### **1. Estructura de Carpetas (Bien organizada)**
```
frontend/src/
├── modules/              ✅ Modularización por feature
│   ├── instituciones/   ✅ Estructura creada
│   ├── programas/       ✅ Estructura creada
│   ├── invitaciones/    ✅ Estructura creada
│   ├── cursos/          ✅ Implementado (funcional)
│   └── ...
├── pages/               ✅ Páginas por rol/función
├── components/          ✅ Componentes reutilizables
├── hooks/               ✅ Custom hooks
├── utils/               ✅ Utilidades
└── context/             ✅ Context API
```

#### **2. Módulo de Instituciones (Parcial)**
- ✅ Tipos TypeScript definidos (`types.ts`)
- ✅ Servicio API (`institucionService.ts`)
- ✅ Custom hooks (`useInstituciones.ts`)
- ✅ Componente ListaInstituciones
- ⚠️ FormularioInstitucion (incompleto)
- ❌ DetalleInstitucion (falta)
- ❌ Modal InvitarCoordinador (falta)
- ❌ Integración con invitaciones (falta)

#### **3. Módulo de Cursos (Referencia)**
- ✅ Totalmente funcional
- ✅ CRUD completo
- ✅ Detalle de curso
- ✅ Pestañas (Tablón, Materiales, Tareas, Calificaciones, Personas, Chat)
- **Usar como template para instituciones**

#### **4. Sistema de Diseño**
- ✅ Tailwind CSS configurado
- ✅ Dark mode implementado
- ✅ Componentes UI base (Button, Modal, Spinner, Alert, etc.)
- ✅ Lucide React icons
- ✅ Framer Motion para animaciones

#### **5. Infraestructura**
- ✅ React Router DOM configurado
- ✅ React Query (@tanstack/react-query)
- ✅ Axios para HTTP
- ✅ Context API para estado global
- ✅ Lazy loading implementado

---

## ❌ **PROBLEMAS IDENTIFICADOS**

### **1. Configuración de API** 🔴 **CRÍTICO**

**Problema**: URLs no coinciden con el backend real

**Frontend (`institucionService.ts`):**
```typescript
const BASE_URL = '/api/v1/academic/instituciones';  // ❌ INCORRECTO
```

**Backend REAL (verificado):**
```python
# Admin
router.prefix = "/admin"
POST /admin/instituciones
POST /admin/instituciones/{id}/invitar-coordinador

# Coordinador
router.prefix = "/api/instituciones"
GET /api/instituciones/mis-instituciones/list
PUT /api/instituciones/{id}
GET /api/instituciones/{id}/estadisticas

# Público
router.prefix = "/invitaciones"
GET /invitaciones/validar/{codigo}
POST /invitaciones/aceptar
```

**Solución**: Crear servicios separados para cada rol con URLs correctas.

---

### **2. Falta Integración con Invitaciones** 🔴 **CRÍTICO**

**Lo que necesita el flujo:**
1. Admin crea institución ✅ (parcial)
2. Admin invita coordinador ❌ **FALTA**
3. Coordinador recibe email con código ✅ (backend)
4. Coordinador valida código en página pública ❌ **FALTA**
5. Coordinador acepta invitación y se registra ❌ **FALTA**
6. Coordinador ve su dashboard ❌ **FALTA**
7. Coordinador gestiona y personaliza institución ❌ **FALTA**

---

### **3. Tipos TypeScript Incorrectos** ⚠️ **IMPORTANTE**

**Frontend (`types.ts`):**
```typescript
export interface Institucion {
  id: string;
  nombre: string;
  // ...
}
```

**Backend REAL:**
```python
class InstitucionResponse(BaseModel):
    institucion_id: UUID  # ← Nombre diferente
    nombre: str
    estado: EstadoInstitucion  # ← Falta en frontend
    tipo_institucion: TipoInstitucion
    nivel_educativo: NivelEducativo
    # ...
```

**Solución**: Actualizar tipos para que coincidan exactamente con el backend.

---

### **4. Rutas Incompletas** ⚠️ **IMPORTANTE**

**App.tsx actual:**
```tsx
// ✅ Existe
<Route path="/admin/instituciones" element={<ListaInstituciones />} />
<Route path="/admin/instituciones/crear" element={<FormularioInstitucion />} />

// ❌ FALTA
<Route path="/admin/instituciones/:id" element={<DetalleInstitucion />} />
<Route path="/coordinador/instituciones" element={<DashboardCoordinador />} />
<Route path="/registro-coordinador" element={<RegistroCoordinador />} />
```

---

### **5. Componentes Duplicados/Inconsistentes** ⚠️ **MENOR**

**Problema**: Hay inconsistencias de estilo entre módulos
- Módulo `cursos`: Usa un estilo
- Módulo `instituciones`: Usa otro estilo
- Módulo `programas`: Usa otro estilo diferente

**Solución**: Definir Design System consistente y refactorizar.

---

## 🎯 PLAN DE ACCIÓN PASO A PASO

### **FASE 1: CORRECCIONES CRÍTICAS** (2-3 horas)

#### **1.1. Corregir Servicios API** ✅

**Archivo**: `src/modules/instituciones/services/institucionService.ts`

**Cambios necesarios:**

```typescript
// ❌ ANTES (INCORRECTO)
const BASE_URL = '/api/v1/academic/instituciones';

// ✅ DESPUÉS (CORRECTO - separar por rol)

// Para admin
const ADMIN_BASE_URL = '/admin/instituciones';

// Para coordinador
const COORD_BASE_URL = '/api/instituciones';

// Para público
const PUBLIC_BASE_URL = '/invitaciones';
```

**Crear 3 servicios separados:**
1. `adminInstitucionService.ts` - CRUD admin
2. `coordinadorInstitucionService.ts` - Gestión coordinador
3. `invitacionService.ts` - Flujo público

---

#### **1.2. Actualizar Tipos TypeScript** ✅

**Archivo**: `src/modules/instituciones/types.ts`

**Cambios necesarios:**

```typescript
// ✅ Actualizar para coincidir con backend EXACTO

export interface Institucion {
  institucion_id: string;  // ← Cambiar de 'id' a 'institucion_id'
  nombre: string;
  sigla?: string;
  lema?: string;
  tipo_institucion?: TipoInstitucion;  // ← Agregar enum
  nivel_educativo?: NivelEducativo;   // ← Agregar enum
  sector?: SectorInstitucion;         // ← Agregar enum
  estado: EstadoInstitucion;          // ← Agregar (pendiente/activa/suspendida/inactiva)
  
  // Nuevos campos del backend
  direccion?: string;
  ciudad?: string;
  pais?: string;
  correo_institucional?: string;
  telefono?: string;
  nit?: string;
  dominio_principal?: string;
  dominios_adicionales?: string[];
  logo_url?: string;
  color_primario?: string;
  color_secundario?: string;
  redes_sociales?: Record<string, string>;
  
  // Fechas
  fecha_creacion: string;
  fecha_activacion?: string;
  
  // Estadísticas (opcional)
  estadisticas?: EstadisticasInstitucion;
}

// ✅ Agregar enums faltantes
export enum TipoInstitucion {
  COLEGIO = 'colegio',
  INSTITUTO = 'instituto',
  UNIVERSIDAD = 'universidad',
  INSTITUTO_TECNICO = 'instituto_tecnico',
  CENTRO_FORMACION = 'centro_formacion'
}

export enum NivelEducativo {
  PREESCOLAR = 'preescolar',
  PRIMARIA = 'primaria',
  BASICA = 'basica',
  MEDIA = 'media',
  TECNICA = 'tecnica',
  TECNOLOGICA = 'tecnologica',
  PROFESIONAL = 'profesional',
  POSTGRADO = 'postgrado'
}

export enum SectorInstitucion {
  PUBLICO = 'publico',
  PRIVADO = 'privado',
  MIXTO = 'mixto'
}

export enum EstadoInstitucion {
  PENDIENTE = 'pendiente',
  ACTIVA = 'activa',
  SUSPENDIDA = 'suspendida',
  INACTIVA = 'inactiva'
}

// ✅ Tipos para invitaciones (NUEVO)
export interface InvitacionInfo {
  valido: boolean;
  invitacion: {
    id: string;
    codigo: string;
    email_destino: string;
    fecha_expiracion: string;
  };
  institucion: {
    id: string;
    nombre: string;
    sigla?: string;
    tipo_institucion?: string;
    nivel_educativo?: string;
    ciudad?: string;
    pais?: string;
  };
}

export interface AceptarInvitacionRequest {
  codigo: string;
  nombre: string;
  apellido: string;
  password: string;
}

export interface AceptarInvitacionResponse {
  success: boolean;
  message: string;
  usuario: {
    id: string;
    email: string;
    username: string;
    nombre: string;
    apellido: string;
    rol: string;
  };
  institucion: {
    id: string;
    nombre: string;
    sigla?: string;
    estado: string;
    fecha_activacion?: string;
  };
}
```

---

#### **1.3. Crear Servicios Correctos** ✅

**Crear**: `src/modules/instituciones/services/adminInstitucionService.ts`

```typescript
import axios from 'axios';
import type { Institucion, CrearInstitucionDTO } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BASE_URL = '/admin/instituciones';

// ✅ Configurar axios con token
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export class AdminInstitucionService {
  // ✅ Admin crea institución
  async crear(data: CrearInstitucionDTO): Promise<Institucion> {
    const response = await apiClient.post<Institucion>(BASE_URL, data);
    return response.data;
  }

  // ✅ Admin lista todas
  async listar(skip = 0, limit = 100): Promise<Institucion[]> {
    const response = await apiClient.get<Institucion[]>(BASE_URL, {
      params: { skip, limit }
    });
    return response.data;
  }

  // ✅ Admin invita coordinador
  async invitarCoordinador(institucionId: string, email: string) {
    const response = await apiClient.post(
      `${BASE_URL}/${institucionId}/invitar-coordinador`,
      { email_destino: email }
    );
    return response.data; // {codigo, email_destino, fecha_expiracion}
  }

  // ... otros métodos
}

export const adminInstitucionService = new AdminInstitucionService();
```

**Crear**: `src/modules/invitaciones/services/invitacionService.ts`

```typescript
import axios from 'axios';
import type {
  InvitacionInfo,
  AceptarInvitacionRequest,
  AceptarInvitacionResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BASE_URL = '/invitaciones';

// ✅ SIN autenticación (público)
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export class InvitacionService {
  // ✅ Validar código (público)
  async validarCodigo(codigo: string): Promise<InvitacionInfo> {
    const response = await apiClient.get<InvitacionInfo>(
      `${BASE_URL}/validar/${codigo}`
    );
    return response.data;
  }

  // ✅ Aceptar invitación (público)
  async aceptar(data: AceptarInvitacionRequest): Promise<AceptarInvitacionResponse> {
    const response = await apiClient.post<AceptarInvitacionResponse>(
      `${BASE_URL}/aceptar`,
      data
    );
    return response.data;
  }
}

export const invitacionService = new InvitacionService();
```

**Crear**: `src/modules/instituciones/services/coordinadorInstitucionService.ts`

```typescript
import axios from 'axios';
import type { Institucion, EstadisticasInstitucion } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BASE_URL = '/api/instituciones';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export class CoordinadorInstitucionService {
  // ✅ Mis instituciones
  async misInstituciones(incluirEstadisticas = false) {
    const response = await apiClient.get(`${BASE_URL}/mis-instituciones/list`, {
      params: { incluir_estadisticas: incluirEstadisticas }
    });
    return response.data; // {success: true, data: [...], total: 1}
  }

  // ✅ Actualizar institución
  async actualizar(id: string, data: any): Promise<Institucion> {
    const response = await apiClient.put(`${BASE_URL}/${id}`, data);
    return response.data;
  }

  // ✅ Estadísticas
  async obtenerEstadisticas(id: string): Promise<EstadisticasInstitucion> {
    const response = await apiClient.get(`${BASE_URL}/${id}/estadisticas`);
    return response.data;
  }

  // ✅ Actualizar branding
  async actualizarBranding(id: string, data: {
    logo_url?: string;
    color_primario?: string;
    color_secundario?: string;
  }) {
    const response = await apiClient.put(`${BASE_URL}/${id}/branding`, data);
    return response.data;
  }

  // ✅ Agregar dominio
  async agregarDominio(id: string, dominio: string) {
    const response = await apiClient.post(`${BASE_URL}/${id}/dominios`, { dominio });
    return response.data;
  }

  // ✅ Estado onboarding
  async obtenerEstadoOnboarding(id: string) {
    const response = await apiClient.get(`${BASE_URL}/${id}/onboarding-status`);
    return response.data;
  }
}

export const coordinadorInstitucionService = new CoordinadorInstitucionService();
```

---

### **FASE 2: COMPONENTES FALTANTES** (4-6 horas)

#### **2.1. Modal InvitarCoordinador** ✅

**Crear**: `src/modules/instituciones/components/InvitarCoordinadorModal.tsx`

```tsx
import { useState } from 'react';
import { X, Mail, Send } from 'lucide-react';
import { adminInstitucionService } from '../services/adminInstitucionService';
import type { Institucion } from '../types';

interface Props {
  institucion: Institucion;
  onClose: () => void;
  onSuccess: (codigo: string) => void;
}

export function InvitarCoordinadorModal({ institucion, onClose, onSuccess }: Props) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const resultado = await adminInstitucionService.invitarCoordinador(
        institucion.institucion_id,
        email
      );
      
      onSuccess(resultado.codigo);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al enviar invitación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Invitar Coordinador
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Institución:
          </p>
          <p className="font-semibold text-lg text-gray-900 dark:text-white">
            {institucion.nombre}
          </p>
          {institucion.sigla && (
            <p className="text-sm text-gray-500">({institucion.sigla})</p>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Correo del Coordinador <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                placeholder="coordinador@example.com"
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Se enviará un código de invitación de 6 dígitos a este correo.
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              {loading ? 'Enviando...' : 'Enviar Invitación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

#### **2.2. Página Registro Coordinador** ✅

**Crear**: `src/modules/invitaciones/pages/RegistroCoordinadorPage.tsx`

```tsx
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { invitacionService } from '../services/invitacionService';
import type { InvitacionInfo } from '../types';
import { Building, Mail, User, Lock, Loader } from 'lucide-react';

export function RegistroCoordinadorPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const codigo = searchParams.get('codigo') || '';
  
  const [invitacionInfo, setInvitacionInfo] = useState<InvitacionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    password: '',
    confirmPassword: '',
  });

  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (codigo) {
      validarCodigo();
    } else {
      setError('No se proporcionó un código de invitación');
      setLoading(false);
    }
  }, [codigo]);

  const validarCodigo = async () => {
    try {
      setLoading(true);
      const data = await invitacionService.validarCodigo(codigo);
      
      if (data.valido) {
        setInvitacionInfo(data);
        setError(null);
      } else {
        setError('Código de invitación inválido');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al validar el código de invitación');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones
    if (formData.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      
      const result = await invitacionService.aceptar({
        codigo,
        nombre: formData.nombre,
        apellido: formData.apellido,
        password: formData.password,
      });

      if (result.success) {
        alert(`¡Registro exitoso! Bienvenido ${result.usuario.nombre}. Ya puedes iniciar sesión.`);
        navigate('/login');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al completar el registro');
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-neutral-950 dark:via-violet-950/20 dark:to-neutral-900">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Validando código de invitación...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !invitacionInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/20 mb-4">
              <X className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Código Inválido
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Ir al Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Success state - Form
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-neutral-950 dark:via-violet-950/20 dark:to-neutral-900 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Building className="mx-auto h-12 w-12 text-blue-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Registro de Coordinador
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Has sido invitado a gestionar
          </p>
        </div>

        {/* Información de la institución */}
        {invitacionInfo && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h3 className="font-semibold text-lg text-blue-900 dark:text-blue-100">
              {invitacionInfo.institucion.nombre}
            </h3>
            {invitacionInfo.institucion.sigla && (
              <p className="text-sm text-blue-700 dark:text-blue-300">
                ({invitacionInfo.institucion.sigla})
              </p>
            )}
            <div className="mt-2 text-sm text-blue-600 dark:text-blue-400 space-y-1">
              {invitacionInfo.institucion.tipo_institucion && (
                <p>Tipo: {invitacionInfo.institucion.tipo_institucion}</p>
              )}
              {invitacionInfo.institucion.nivel_educativo && (
                <p>Nivel: {invitacionInfo.institucion.nivel_educativo}</p>
              )}
              {invitacionInfo.institucion.ciudad && (
                <p>Ubicación: {invitacionInfo.institucion.ciudad}, {invitacionInfo.institucion.pais}</p>
              )}
            </div>
            <div className="mt-3 text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 p-2 rounded">
              <p><strong>Email:</strong> {invitacionInfo.invitacion.email_destino}</p>
              <p><strong>Código:</strong> {invitacionInfo.invitacion.codigo}</p>
            </div>
          </div>
        )}

        {/* Formulario de registro */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Nombre */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nombre(s) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  required
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="Juan Carlos"
                />
              </div>
            </div>

            {/* Apellido */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Apellido(s) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  required
                  value={formData.apellido}
                  onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="Pérez Gómez"
                />
              </div>
            </div>

            {/* Contraseña */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Contraseña <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="Mínimo 8 caracteres"
                />
              </div>
            </div>

            {/* Confirmar contraseña */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirmar Contraseña <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="Repite tu contraseña"
                />
              </div>
            </div>
          </div>

          {/* Mensajes de error */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Validación de contraseña */}
          {formData.password && formData.password.length < 8 && (
            <p className="text-xs text-yellow-600 dark:text-yellow-400">
              La contraseña debe tener al menos 8 caracteres
            </p>
          )}
          {formData.password && formData.confirmPassword && formData.password !== formData.confirmPassword && (
            <p className="text-xs text-red-600 dark:text-red-400">
              Las contraseñas no coinciden
            </p>
          )}

          {/* Botón submit */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full flex justify-center items-center gap-2 py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Registrando...
              </>
            ) : (
              'Completar Registro'
            )}
          </button>
        </form>

        {/* Link a login */}
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            ¿Ya tienes cuenta?{' '}
            <button
              onClick={() => navigate('/login')}
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Iniciar sesión
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

Continuará con más fases en el próximo mensaje...

---

**Estado actual del documento**: Fase 1 y Fase 2.1-2.2 completadas  
**Próximas fases**: Dashboard Coordinador, Onboarding, Testing
