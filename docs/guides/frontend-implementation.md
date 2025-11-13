# 🎨 GUÍA DE IMPLEMENTACIÓN FRONTEND - FLUJO INSTITUCIONES

**Para**: Desarrollador Frontend  
**Backend Status**: ✅ 100% Completo y Funcional  
**Tu misión**: Conectar el frontend a los endpoints del backend

---

## 📍 PUNTO DE PARTIDA

El backend tiene TODO listo:
- ✅ 15+ endpoints funcionales
- ✅ Autenticación JWT
- ✅ Validaciones de permisos
- ✅ Documentación en Swagger: `http://localhost:8000/docs`

**Tu trabajo**: Crear las pantallas y conectarlas a estos endpoints.

---

## 🏗️ ESTRUCTURA DE CARPETAS RECOMENDADA

```
frontend/src/
├── api/
│   ├── auth.ts                    # Login, logout, refresh token
│   ├── admin.ts                   # Admin endpoints
│   ├── instituciones.ts           # Coordinador endpoints
│   └── invitaciones.ts            # Públicos (sin auth)
├── components/
│   ├── admin/
│   │   ├── InstitucionesTable.tsx
│   │   ├── CrearInstitucionModal.tsx
│   │   └── InvitarCoordinadorModal.tsx
│   ├── coordinador/
│   │   ├── DashboardCoordinador.tsx
│   │   ├── MisInstituciones.tsx
│   │   ├── EditarInstitucionModal.tsx
│   │   └── OnboardingWizard.tsx
│   └── public/
│       └── RegistroCoordinador.tsx
├── pages/
│   ├── admin/
│   │   └── InstitucionesAdmin.tsx
│   ├── coordinador/
│   │   └── DashboardPage.tsx
│   └── RegistroCoordinadorPage.tsx
├── hooks/
│   ├── useInstituciones.ts
│   ├── useAuth.ts
│   └── useInvitacion.ts
├── types/
│   ├── institucion.ts
│   └── invitacion.ts
└── utils/
    ├── api.ts                     # Axios/Fetch configurado
    └── storage.ts                 # LocalStorage helpers
```

---

## 🔧 CONFIGURACIÓN INICIAL

### **1. Instalar Dependencias**

```bash
cd frontend

# Si usas npm
npm install axios react-router-dom zustand

# Si usas yarn
yarn add axios react-router-dom zustand

# Para formularios (opcional)
npm install react-hook-form zod @hookform/resolvers

# Para UI (opcional, puedes usar lo que tengas)
npm install @headlessui/react @heroicons/react
```

### **2. Configurar API Client** (src/utils/api.ts)

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

// ⚠️ IMPORTANTE: Cambiar a tu URL de backend
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token automáticamente
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expirado, redirect a login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### **3. Definir Tipos TypeScript** (src/types/institucion.ts)

```typescript
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

export enum EstadoInstitucion {
  PENDIENTE = 'pendiente',
  ACTIVA = 'activa',
  SUSPENDIDA = 'suspendida',
  INACTIVA = 'inactiva'
}

export interface Institucion {
  institucion_id: string;
  nombre: string;
  sigla?: string;
  lema?: string;
  tipo_institucion?: TipoInstitucion;
  nivel_educativo?: NivelEducativo;
  sector?: string;
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
  estado: EstadoInstitucion;
  fecha_creacion: string;
  fecha_activacion?: string;
}

export interface InstitucionCreate {
  nombre: string;
  tipo_institucion: TipoInstitucion;
  nivel_educativo: NivelEducativo;
  sector: string;
  correo_institucional: string;
  usa_programas: boolean;
  sigla?: string;
  lema?: string;
  direccion?: string;
  ciudad?: string;
  pais?: string;
  telefono?: string;
  nit?: string;
}

export interface InstitucionUpdate {
  nombre?: string;
  sigla?: string;
  lema?: string;
  direccion?: string;
  ciudad?: string;
  pais?: string;
  telefono?: string;
  website?: string;
  redes_sociales?: Record<string, string>;
  dominio_principal?: string;
}

export interface Estadisticas {
  total_cursos: number;
  cursos_activos: number;
  total_docentes: number;
  total_estudiantes: number;
  total_programas: number;
  total_coordinadores: number;
}

export interface OnboardingStatus {
  onboarding_completo: boolean;
  pasos_completados: Record<string, boolean>;
  pasos_faltantes: string[];
  porcentaje_completado: number;
}
```

### **4. Definir Tipos de Invitación** (src/types/invitacion.ts)

```typescript
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

## 🚀 IMPLEMENTACIÓN POR MÓDULOS

## **MÓDULO 1: ADMIN - GESTIÓN DE INSTITUCIONES**

### **A. API Service** (src/api/admin.ts)

```typescript
import apiClient from '../utils/api';
import { Institucion, InstitucionCreate } from '../types/institucion';

export const adminApi = {
  // Crear institución
  async crearInstitucion(data: InstitucionCreate): Promise<Institucion> {
    const response = await apiClient.post<Institucion>('/admin/instituciones', data);
    return response.data;
  },

  // Listar todas las instituciones
  async listarInstituciones(skip = 0, limit = 100): Promise<Institucion[]> {
    const response = await apiClient.get<Institucion[]>('/admin/instituciones', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Obtener institución por ID
  async obtenerInstitucion(id: string): Promise<Institucion> {
    const response = await apiClient.get<Institucion>(`/admin/instituciones/${id}`);
    return response.data;
  },

  // Invitar coordinador
  async invitarCoordinador(institucionId: string, email: string) {
    const response = await apiClient.post(`/admin/instituciones/${institucionId}/invitar-coordinador`, {
      email_destino: email
    });
    return response.data;
  },
};
```

### **B. Página Principal** (src/pages/admin/InstitucionesAdmin.tsx)

```tsx
import React, { useState, useEffect } from 'react';
import { adminApi } from '../../api/admin';
import { Institucion } from '../../types/institucion';
import CrearInstitucionModal from '../../components/admin/CrearInstitucionModal';
import InvitarCoordinadorModal from '../../components/admin/InvitarCoordinadorModal';

const InstitucionesAdmin: React.FC = () => {
  const [instituciones, setInstituciones] = useState<Institucion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCrearModal, setShowCrearModal] = useState(false);
  const [selectedInstitucion, setSelectedInstitucion] = useState<Institucion | null>(null);
  const [showInvitarModal, setShowInvitarModal] = useState(false);

  useEffect(() => {
    cargarInstituciones();
  }, []);

  const cargarInstituciones = async () => {
    try {
      setLoading(true);
      const data = await adminApi.listarInstituciones();
      setInstituciones(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar instituciones');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCrearInstitucion = async (data: any) => {
    try {
      await adminApi.crearInstitucion(data);
      setShowCrearModal(false);
      cargarInstituciones(); // Recargar lista
      alert('Institución creada exitosamente');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al crear institución');
    }
  };

  const handleInvitarCoordinador = async (email: string) => {
    if (!selectedInstitucion) return;

    try {
      const result = await adminApi.invitarCoordinador(selectedInstitucion.institucion_id, email);
      setShowInvitarModal(false);
      alert(`Invitación enviada exitosamente. Código: ${result.codigo}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al enviar invitación');
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Gestión de Instituciones</h1>
        <button
          onClick={() => setShowCrearModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Nueva Institución
        </button>
      </div>

      {instituciones.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No hay instituciones registradas. Crea la primera.
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sigla</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {instituciones.map((inst) => (
                <tr key={inst.institucion_id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{inst.nombre}</div>
                    <div className="text-sm text-gray-500">{inst.correo_institucional}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{inst.sigla || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{inst.tipo_institucion || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${inst.estado === 'activa' ? 'bg-green-100 text-green-800' : 
                        inst.estado === 'pendiente' ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-gray-100 text-gray-800'}`}>
                      {inst.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {inst.estado === 'pendiente' && (
                      <button
                        onClick={() => {
                          setSelectedInstitucion(inst);
                          setShowInvitarModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        Invitar Coordinador
                      </button>
                    )}
                    <button className="text-gray-600 hover:text-gray-900">Ver Detalles</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCrearModal && (
        <CrearInstitucionModal
          onClose={() => setShowCrearModal(false)}
          onSubmit={handleCrearInstitucion}
        />
      )}

      {showInvitarModal && selectedInstitucion && (
        <InvitarCoordinadorModal
          institucion={selectedInstitucion}
          onClose={() => setShowInvitarModal(false)}
          onSubmit={handleInvitarCoordinador}
        />
      )}
    </div>
  );
};

export default InstitucionesAdmin;
```

### **C. Modal Crear Institución** (src/components/admin/CrearInstitucionModal.tsx)

```tsx
import React, { useState } from 'react';
import { InstitucionCreate, TipoInstitucion, NivelEducativo } from '../../types/institucion';

interface Props {
  onClose: () => void;
  onSubmit: (data: InstitucionCreate) => Promise<void>;
}

const CrearInstitucionModal: React.FC<Props> = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState<InstitucionCreate>({
    nombre: '',
    tipo_institucion: TipoInstitucion.COLEGIO,
    nivel_educativo: NivelEducativo.BASICA,
    sector: 'publico',
    correo_institucional: '',
    usa_programas: true,
  });

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6">Crear Nueva Institución</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Instituto Técnico San José"
            />
          </div>

          {/* Sigla */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sigla</label>
            <input
              type="text"
              value={formData.sigla || ''}
              onChange={(e) => setFormData({ ...formData, sigla: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="ITSJ"
            />
          </div>

          {/* Tipo Institución */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Institución <span className="text-red-500">*</span>
            </label>
            <select
              required
              value={formData.tipo_institucion}
              onChange={(e) => setFormData({ ...formData, tipo_institucion: e.target.value as TipoInstitucion })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value={TipoInstitucion.COLEGIO}>Colegio</option>
              <option value={TipoInstitucion.INSTITUTO}>Instituto</option>
              <option value={TipoInstitucion.UNIVERSIDAD}>Universidad</option>
              <option value={TipoInstitucion.INSTITUTO_TECNICO}>Instituto Técnico</option>
              <option value={TipoInstitucion.CENTRO_FORMACION}>Centro de Formación</option>
            </select>
          </div>

          {/* Nivel Educativo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nivel Educativo <span className="text-red-500">*</span>
            </label>
            <select
              required
              value={formData.nivel_educativo}
              onChange={(e) => setFormData({ ...formData, nivel_educativo: e.target.value as NivelEducativo })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value={NivelEducativo.PREESCOLAR}>Preescolar</option>
              <option value={NivelEducativo.PRIMARIA}>Primaria</option>
              <option value={NivelEducativo.BASICA}>Básica</option>
              <option value={NivelEducativo.MEDIA}>Media</option>
              <option value={NivelEducativo.TECNICA}>Técnica</option>
              <option value={NivelEducativo.TECNOLOGICA}>Tecnológica</option>
              <option value={NivelEducativo.PROFESIONAL}>Profesional</option>
              <option value={NivelEducativo.POSTGRADO}>Postgrado</option>
            </select>
          </div>

          {/* Sector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sector <span className="text-red-500">*</span>
            </label>
            <select
              required
              value={formData.sector}
              onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="publico">Público</option>
              <option value="privado">Privado</option>
              <option value="mixto">Mixto</option>
            </select>
          </div>

          {/* Correo Institucional */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Correo Institucional <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              required
              value={formData.correo_institucional}
              onChange={(e) => setFormData({ ...formData, correo_institucional: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="info@institucion.edu.co"
            />
          </div>

          {/* Usa Programas */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="usa_programas"
              checked={formData.usa_programas}
              onChange={(e) => setFormData({ ...formData, usa_programas: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="usa_programas" className="ml-2 block text-sm text-gray-900">
              Usa programas académicos (carreras, técnicos, etc.)
            </label>
          </div>

          {/* Botones */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Creando...' : 'Crear Institución'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CrearInstitucionModal;
```

### **D. Modal Invitar Coordinador** (src/components/admin/InvitarCoordinadorModal.tsx)

```tsx
import React, { useState } from 'react';
import { Institucion } from '../../types/institucion';

interface Props {
  institucion: Institucion;
  onClose: () => void;
  onSubmit: (email: string) => Promise<void>;
}

const InvitarCoordinadorModal: React.FC<Props> = ({ institucion, onClose, onSubmit }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(email);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full">
        <h2 className="text-2xl font-bold mb-4">Invitar Coordinador</h2>
        
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">Institución:</p>
          <p className="font-semibold text-lg">{institucion.nombre}</p>
          {institucion.sigla && <p className="text-sm text-gray-500">({institucion.sigla})</p>}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Correo del Coordinador <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="coordinador@example.com"
            />
            <p className="mt-1 text-xs text-gray-500">
              Se enviará un código de invitación de 6 dígitos a este correo.
            </p>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Enviando...' : 'Enviar Invitación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InvitarCoordinadorModal;
```

---

## **MÓDULO 2: PÚBLICO - REGISTRO DE COORDINADOR**

### **A. API Service** (src/api/invitaciones.ts)

```typescript
import apiClient from '../utils/api';
import { InvitacionInfo, AceptarInvitacionRequest, AceptarInvitacionResponse } from '../types/invitacion';

export const invitacionesApi = {
  // Validar código de invitación (sin consumirlo)
  async validarCodigo(codigo: string): Promise<InvitacionInfo> {
    const response = await apiClient.get<InvitacionInfo>(`/invitaciones/validar/${codigo}`);
    return response.data;
  },

  // Aceptar invitación y registrarse
  async aceptarInvitacion(data: AceptarInvitacionRequest): Promise<AceptarInvitacionResponse> {
    const response = await apiClient.post<AceptarInvitacionResponse>('/invitaciones/aceptar', data);
    return response.data;
  },
};
```

### **B. Página de Registro** (src/pages/RegistroCoordinadorPage.tsx)

```tsx
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { invitacionesApi } from '../api/invitaciones';
import { InvitacionInfo } from '../types/invitacion';

const RegistroCoordinadorPage: React.FC = () => {
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
      const data = await invitacionesApi.validarCodigo(codigo);
      
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

    // Validaciones client-side
    if (formData.password.length < 8) {
      alert('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }

    try {
      setSubmitting(true);
      const result = await invitacionesApi.aceptarInvitacion({
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
      alert(err.response?.data?.detail || 'Error al completar el registro');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Validando código de invitación...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Código Inválido</h2>
            <p className="text-gray-600">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="mt-6 w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Ir al Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Registro de Coordinador
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Has sido invitado a gestionar
          </p>
        </div>

        {/* Información de la institución */}
        {invitacionInfo && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-lg text-blue-900">{invitacionInfo.institucion.nombre}</h3>
            {invitacionInfo.institucion.sigla && (
              <p className="text-sm text-blue-700">({invitacionInfo.institucion.sigla})</p>
            )}
            <div className="mt-2 text-sm text-blue-600">
              <p>Tipo: {invitacionInfo.institucion.tipo_institucion || 'No especificado'}</p>
              <p>Nivel: {invitacionInfo.institucion.nivel_educativo || 'No especificado'}</p>
              {invitacionInfo.institucion.ciudad && (
                <p>Ubicación: {invitacionInfo.institucion.ciudad}, {invitacionInfo.institucion.pais}</p>
              )}
            </div>
            <div className="mt-3 text-xs text-gray-600 bg-white p-2 rounded">
              <p><strong>Email:</strong> {invitacionInfo.invitacion.email_destino}</p>
              <p><strong>Código:</strong> {invitacionInfo.invitacion.codigo}</p>
            </div>
          </div>
        )}

        {/* Formulario de registro */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            {/* Nombre */}
            <div>
              <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-1">
                Nombre(s) <span className="text-red-500">*</span>
              </label>
              <input
                id="nombre"
                name="nombre"
                type="text"
                required
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Juan Carlos"
              />
            </div>

            {/* Apellido */}
            <div>
              <label htmlFor="apellido" className="block text-sm font-medium text-gray-700 mb-1">
                Apellido(s) <span className="text-red-500">*</span>
              </label>
              <input
                id="apellido"
                name="apellido"
                type="text"
                required
                value={formData.apellido}
                onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Pérez Gómez"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña <span className="text-red-500">*</span>
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                minLength={8}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Mínimo 8 caracteres"
              />
            </div>

            {/* Confirmar Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar Contraseña <span className="text-red-500">*</span>
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Repite tu contraseña"
              />
            </div>
          </div>

          {/* Validación de contraseña */}
          {formData.password && formData.password.length < 8 && (
            <p className="text-xs text-red-500">La contraseña debe tener al menos 8 caracteres</p>
          )}
          {formData.password && formData.confirmPassword && formData.password !== formData.confirmPassword && (
            <p className="text-xs text-red-500">Las contraseñas no coinciden</p>
          )}

          {/* Botón submit */}
          <div>
            <button
              type="submit"
              disabled={submitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {submitting ? 'Registrando...' : 'Completar Registro'}
            </button>
          </div>
        </form>

        {/* Link a login */}
        <div className="text-center">
          <p className="text-sm text-gray-600">
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
};

export default RegistroCoordinadorPage;
```

---

## **MÓDULO 3: COORDINADOR - DASHBOARD Y GESTIÓN**

### **A. API Service** (src/api/instituciones.ts)

```typescript
import apiClient from '../utils/api';
import { Institucion, InstitucionUpdate, Estadisticas, OnboardingStatus } from '../types/institucion';

export const institucionesApi = {
  // Listar mis instituciones
  async misInstituciones(incluirEstadisticas = false) {
    const response = await apiClient.get('/api/instituciones/mis-instituciones/list', {
      params: { incluir_estadisticas: incluirEstadisticas }
    });
    return response.data; // {success: true, data: [...], total: 1}
  },

  // Obtener institución por ID
  async obtenerInstitucion(id: string): Promise<Institucion> {
    const response = await apiClient.get<Institucion>(`/api/instituciones/${id}`);
    return response.data;
  },

  // Actualizar institución
  async actualizarInstitucion(id: string, data: InstitucionUpdate) {
    const response = await apiClient.put(`/api/instituciones/${id}`, data);
    return response.data;
  },

  // Obtener estadísticas
  async obtenerEstadisticas(id: string) {
    const response = await apiClient.get(`/api/instituciones/${id}/estadisticas`);
    return response.data; // {success: true, data: {...}}
  },

  // Estado del onboarding
  async obtenerEstadoOnboarding(id: string): Promise<OnboardingStatus> {
    const response = await apiClient.get<OnboardingStatus>(`/api/instituciones/${id}/onboarding-status`);
    return response.data;
  },

  // Actualizar branding
  async actualizarBranding(id: string, data: { logo_url?: string; color_primario?: string; color_secundario?: string }) {
    const response = await apiClient.put(`/api/instituciones/${id}/branding`, data);
    return response.data;
  },

  // Agregar dominio adicional
  async agregarDominio(id: string, dominio: string) {
    const response = await apiClient.post(`/api/instituciones/${id}/dominios`, { dominio });
    return response.data;
  },
};
```

### **B. Hook Personalizado** (src/hooks/useInstituciones.ts)

```typescript
import { useState, useEffect } from 'react';
import { institucionesApi } from '../api/instituciones';

export const useInstituciones = () => {
  const [instituciones, setInstituciones] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cargar = async (incluirEstadisticas = false) => {
    try {
      setLoading(true);
      const response = await institucionesApi.misInstituciones(incluirEstadisticas);
      
      if (response.success && Array.isArray(response.data)) {
        setInstituciones(response.data);
        setError(null);
      } else {
        setError('Formato de respuesta inesperado');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar instituciones');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  return { instituciones, loading, error, reload: cargar };
};
```

### **C. Dashboard del Coordinador** (src/pages/coordinador/DashboardPage.tsx)

```tsx
import React from 'react';
import { useInstituciones } from '../../hooks/useInstituciones';
import { useNavigate } from 'react-router-dom';

const DashboardCoordinadorPage: React.FC = () => {
  const { instituciones, loading, error, reload } = useInstituciones();
  const navigate = useNavigate();

  if (loading) return <div className="p-6">Cargando...</div>;
  if (error) return <div className="p-6 text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard de Coordinador</h1>

      {instituciones.length === 0 ? (
        <div className="bg-white shadow-md rounded-lg p-12 text-center">
          <p className="text-gray-600 text-lg mb-4">No tienes instituciones asignadas</p>
          <p className="text-sm text-gray-500">
            Espera a que un administrador te asigne una institución o te envíe una invitación.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {instituciones.map((inst) => (
            <div
              key={inst.institucion_id}
              className="bg-white shadow-md rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/coordinador/instituciones/${inst.institucion_id}`)}
            >
              {/* Logo */}
              {inst.logo_url ? (
                <img src={inst.logo_url} alt={inst.nombre} className="w-full h-48 object-cover" />
              ) : (
                <div className="w-full h-48 bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                  <span className="text-white text-6xl font-bold">{inst.nombre.charAt(0)}</span>
                </div>
              )}

              {/* Content */}
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-2">{inst.nombre}</h2>
                {inst.sigla && <p className="text-sm text-gray-500 mb-4">({inst.sigla})</p>}
                
                <div className="flex items-center mb-2">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full 
                    ${inst.estado === 'activa' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {inst.estado}
                  </span>
                </div>

                {inst.estadisticas && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-gray-500">Cursos</p>
                        <p className="font-semibold">{inst.estadisticas.total_cursos || 0}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Docentes</p>
                        <p className="font-semibold">{inst.estadisticas.total_docentes || 0}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Estudiantes</p>
                        <p className="font-semibold">{inst.estadisticas.total_estudiantes || 0}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Programas</p>
                        <p className="font-semibold">{inst.estadisticas.total_programas || 0}</p>
                      </div>
                    </div>
                  </div>
                )}

                <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors">
                  Gestionar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DashboardCoordinadorPage;
```

---

## 🔗 CONFIGURAR RUTAS

### **src/App.tsx** (o donde tengas el router)

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import InstitucionesAdmin from './pages/admin/InstitucionesAdmin';
import DashboardCoordinadorPage from './pages/coordinador/DashboardPage';
import RegistroCoordinadorPage from './pages/RegistroCoordinadorPage';
import LoginPage from './pages/LoginPage';

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token');
  const userRole = JSON.parse(localStorage.getItem('user') || '{}').rol;

  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro-coordinador" element={<RegistroCoordinadorPage />} />

        {/* Rutas de admin */}
        <Route
          path="/admin/instituciones"
          element={
            isAuthenticated && userRole === 'administrador' ? (
              <InstitucionesAdmin />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* Rutas de coordinador */}
        <Route
          path="/coordinador/dashboard"
          element={
            isAuthenticated && userRole === 'coordinador' ? (
              <DashboardCoordinadorPage />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* Redirect por defecto */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              userRole === 'administrador' ? (
                <Navigate to="/admin/instituciones" />
              ) : (
                <Navigate to="/coordinador/dashboard" />
              )
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 🧪 TESTING MANUAL

### **1. Verificar Backend**
```bash
# Abrir Swagger UI
http://localhost:8000/docs

# Probar endpoint público
curl http://localhost:8000/api/instituciones
```

### **2. Flujo Completo**
1. Login como Admin
2. Ir a `/admin/instituciones`
3. Crear institución
4. Invitar coordinador
5. Copiar código de invitación
6. Abrir en otra ventana: `/registro-coordinador?codigo=ABC123`
7. Completar registro
8. Login como coordinador
9. Ver dashboard con institución

---

## 📝 CHECKLIST FINAL

### **Backend** ✅
- [x] Todos los endpoints funcionando
- [x] Documentación en Swagger
- [x] Validaciones implementadas

### **Frontend** (Tu trabajo)
- [ ] API client configurado
- [ ] Tipos TypeScript definidos
- [ ] Módulo Admin implementado
- [ ] Módulo Registro implementado
- [ ] Módulo Coordinador implementado
- [ ] Rutas configuradas
- [ ] Manejo de errores
- [ ] Estados de carga
- [ ] Tests manuales exitosos

---

## 🎯 SIGUIENTE PASO

**Copiar el código de esta guía y empezar a implementar paso a paso:**
1. Configuración inicial (API client, tipos)
2. Módulo Admin (crear institución, invitar)
3. Módulo Público (registro coordinador)
4. Módulo Coordinador (dashboard)

**¡Todo el backend está listo! Solo necesitas conectar el frontend.**

---

**Última actualización**: 7 de Noviembre 2025  
**Estado**: Guía completa para implementación frontend ✅
