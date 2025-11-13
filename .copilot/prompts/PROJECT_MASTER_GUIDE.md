# 🎓 Acadify - Guía Maestra del Proyecto

> **Sistema educativo completo con backend FastAPI, frontend React/Vite y mobile React Native/Expo**
> 
> **Fecha de creación**: Noviembre 2025  
> **Versión**: 1.0.0  
> **Stack Principal**: Python 3.12 · TypeScript 5.2 · React 18 · FastAPI 0.116 · PostgreSQL · Redis

---

## 📋 ÍNDICE RÁPIDO

1. [Arquitectura General](#arquitectura-general)
2. [Stack Tecnológico Completo](#stack-tecnológico)
3. [Estructura de Directorios](#estructura-de-directorios)
4. [Comandos de Inicio Rápido](#comandos-de-inicio)
5. [Convenciones de Código](#convenciones-de-código)
6. [Flujos Críticos del Sistema](#flujos-críticos)
7. [Referencias a Guías Especializadas](#guías-especializadas)

---

## 🏗️ ARQUITECTURA GENERAL

### **Monorepo Multi-Plataforma**

```
Acadify/
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL + Redis
├── frontend/         # React + Vite + TypeScript + TailwindCSS
├── mobile/           # React Native + Expo + Zustand
├── avatares/         # Assets SVG para sistema de avatares
├── docs/             # Documentación del proyecto
└── dev-tools/        # Herramientas de desarrollo
```

### **Principios Arquitectónicos**

1. **Clean Architecture**: Separación en capas (API → Services → CRUD → Models → DB)
2. **SOLID Principles**: Aplicados en servicios, componentes y hooks
3. **DRY (Don't Repeat Yourself)**: Reutilización agresiva de componentes y servicios
4. **Type Safety First**: TypeScript strict mode + Python type hints completos
5. **API-First Design**: Backend como fuente única de verdad
6. **Real-time Ready**: WebSockets para comunicación y videollamadas
7. **Offline Capability**: React Query cache + Zustand persistence

---

## 🛠️ STACK TECNOLÓGICO

### **Backend (Python)**

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **FastAPI** | 0.116.1 | Framework web asíncrono, API REST |
| **SQLAlchemy** | 2.0.43 | ORM para PostgreSQL |
| **Alembic** | 1.16.5 | Migraciones de base de datos |
| **Pydantic** | 2.11.7 | Validación de datos y schemas |
| **PostgreSQL** | 15+ | Base de datos relacional principal |
| **Redis** | 7+ | Cache, sesiones, colas de tareas |
| **PyJWT** | 2.10.1 | Autenticación JWT |
| **bcrypt** | 4.3.0 | Hash de contraseñas |
| **pyotp** | 2.9.0 | 2FA con TOTP |
| **aiosmtplib** | 4.0.2 | Envío de emails asíncrono |
| **opencv-python** | 4.11.0 | Procesamiento de imágenes (proctoring) |
| **google-generativeai** | 0.8.3 | Integración con Gemini AI |

**Herramientas de Desarrollo Backend:**
- **Ruff** (linting + formatting súper rápido)
- **Black** (code formatter)
- **Pytest** (testing framework)
- **Bandit** (security linting)

### **Frontend (TypeScript + React)**

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **React** | 18.2.0 | Biblioteca UI |
| **TypeScript** | 5.2.2 | Type safety |
| **Vite** | 5.1.5 | Build tool + dev server |
| **React Router** | 6.30.1 | Navegación SPA |
| **TanStack Query** | 5.90.5 | Data fetching + cache inteligente |
| **Axios** | 1.12.2 | Cliente HTTP |
| **TailwindCSS** | 3.4.7 | Utility-first CSS |
| **Framer Motion** | 10.18.0 | Animaciones |
| **Socket.io Client** | 4.8.1 | WebSocket real-time |
| **React Hook Form** | 7.63.0 | Manejo de formularios |
| **Recharts** | 3.3.0 | Gráficos y visualizaciones |

**Herramientas de Desarrollo Frontend:**
- **ESLint** 9 (linting)
- **Prettier** (formatting)
- **Vitest** (unit testing)
- **Testing Library** (component testing)

### **Mobile (React Native + Expo)**

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **React Native** | 0.81.5 | Framework mobile |
| **Expo** | ~54.0 | Toolchain y SDK |
| **Zustand** | 5.0.8 | State management |
| **TanStack Query** | 5.90.5 | Data fetching |
| **Expo Router** | ~6.0 | File-based routing |
| **NativeWind** | - | TailwindCSS para RN |
| **React Hook Form** | 7.66.0 | Formularios |
| **Zod** | 4.1.12 | Validación de esquemas |

---

## 📁 ESTRUCTURA DE DIRECTORIOS

### **Backend** (`/backend`)

```
backend/
├── src/
│   ├── main.py                    # 🚀 Punto de entrada FastAPI
│   ├── api/
│   │   ├── routes/                # Routers por dominio
│   │   │   ├── auth_main.py      # Auth completo (login, register, 2FA)
│   │   │   ├── academic/         # Instituciones, programas, cursos, clases
│   │   │   ├── gamification/     # Logros, puntos, misiones, tienda
│   │   │   ├── communication/    # Chat, notificaciones, videollamadas
│   │   │   ├── avatar.py         # Sistema de avatares
│   │   │   └── evaluaciones/     # Proctoring, calificaciones
│   │   ├── routes.py             # ⚙️ Configuración central de routers
│   │   └── deps.py               # Dependencias inyectables (DB, auth)
│   ├── services/                  # Lógica de negocio
│   │   ├── auth/                 # AuthService, EmailService, Redis
│   │   ├── academic/             # InstitucionService, CursoService
│   │   ├── gamification/         # GamificacionService
│   │   └── communication/        # ChatService, NotificationService
│   ├── crud/                      # Operaciones CRUD (Repository Pattern)
│   │   ├── academic/
│   │   ├── gamification/
│   │   └── base.py               # Base CRUD class
│   ├── models/                    # SQLAlchemy models
│   │   ├── auth/                 # Usuario, Rol, Session2FA
│   │   ├── academic/             # Institucion, Programa, Curso, Clase
│   │   ├── gamification/         # Logro, Puntos, Racha, Mision
│   │   └── communication/        # Mensaje, Notificacion
│   ├── schemas/                   # Pydantic schemas (request/response)
│   │   ├── auth/
│   │   ├── academic/
│   │   └── gamification/
│   ├── core/
│   │   ├── config.py             # ⚙️ Settings (DATABASE_URL, REDIS, JWT, etc)
│   │   ├── security.py           # Hash, JWT, token management
│   │   └── redis_manager.py      # Redis connection pool
│   ├── db/
│   │   ├── session.py            # Database session factory
│   │   └── base.py               # Declarative base
│   ├── enums/                     # Python Enums para tipos
│   └── utils/                     # Utilidades generales
├── alembic/                       # Migraciones de DB
│   └── versions/                 # Scripts de migración
├── tests/                         # Tests unitarios e integración
├── requirements.txt               # 📦 Dependencias Python
├── pyproject.toml                # ⚙️ Config Ruff, Black, Pytest
└── .env                          # Variables de entorno (no commiteado)
```

**Archivo Crítico**: `src/core/config.py`
- DATABASE_URL, REDIS_HOST/PORT
- JWT settings (SECRET_KEY, ALGORITHM, expiry)
- SMTP config para emails
- Feature flags (ENABLE_2FA, ENABLE_GAMIFICATION)

### **Frontend** (`/frontend`)

```
frontend/
├── src/
│   ├── main.tsx                   # 🚀 Punto de entrada React
│   ├── App.tsx                    # Router principal con lazy loading
│   ├── pages/                     # Páginas por ruta
│   │   ├── home/                 # Landing page
│   │   ├── auth/                 # Login, Register, Recover
│   │   ├── dashboard/            # Dashboards por rol (Admin, Coord, Prof, Alum)
│   │   ├── cursos/               # Lista cursos, detalle
│   │   ├── clase/                # Tablón, materiales, tareas, chat
│   │   ├── gamificacion/         # Logros, puntos, tienda
│   │   ├── comunicacion/         # Mensajes, notificaciones
│   │   ├── admin/                # Gestión instituciones, usuarios
│   │   └── avatar/               # Editor de avatares
│   ├── modules/                   # Módulos especializados (sub-features)
│   │   ├── instituciones/
│   │   ├── programas/
│   │   ├── invitaciones/
│   │   ├── logros/
│   │   └── comunicacion/
│   ├── components/                # Componentes reutilizables
│   │   ├── ui/                   # Design system (Button, Input, Modal, etc)
│   │   ├── layout/               # Layout, AuthLayout, Navbar, Sidebar
│   │   ├── nav/                  # Navegación contextual
│   │   └── [domain]/             # Componentes por dominio
│   ├── services/                  # API clients (axios wrappers)
│   │   ├── auth.service.ts
│   │   ├── instituciones.service.ts
│   │   ├── gamificacion.service.ts
│   │   └── notificaciones.service.ts
│   ├── hooks/                     # Custom hooks (React Query + lógica)
│   │   ├── useAuth.ts
│   │   ├── useInstituciones.ts
│   │   └── useAdminData.ts
│   ├── context/                   # React Context (AuthContext, ToastContext)
│   ├── types/                     # TypeScript types/interfaces
│   ├── utils/                     # Funciones auxiliares
│   ├── config/
│   │   └── api.config.ts         # ⚙️ API_BASE_URL, endpoints, interceptors
│   └── lib/                       # Third-party configs
├── public/                        # Assets estáticos
├── vite.config.ts                 # ⚙️ Config Vite (proxy, build, chunks)
├── tailwind.config.cjs            # Config TailwindCSS
├── tsconfig.json                  # Config TypeScript
├── package.json                   # 📦 Dependencias npm
└── .env.local                     # Variables de entorno (no commiteado)
```

**Archivo Crítico**: `src/config/api.config.ts`
- API_BASE_URL: `http://localhost:8000` (desarrollo)
- WS_BASE_URL: `ws://localhost:8000` (WebSockets)
- Axios interceptors (token refresh, error handling)

### **Mobile** (`/mobile`)

```
mobile/
├── app/                           # Expo Router (file-based routing)
│   ├── _layout.tsx               # Root layout con providers
│   ├── index.tsx                 # Landing/Splash
│   ├── (auth)/                   # Auth stack
│   │   ├── login.tsx
│   │   └── register.tsx
│   └── (app)/                    # Main app (tabs)
│       ├── _layout.tsx           # Tab navigation
│       ├── index.tsx             # Dashboard
│       ├── courses.tsx
│       ├── messages.tsx
│       └── profile.tsx
├── src/
│   ├── components/
│   │   └── ui/                   # Design system mobile
│   ├── services/                 # API services (Repository Pattern)
│   │   ├── auth.service.ts
│   │   ├── course.service.ts
│   │   └── message.service.ts
│   ├── hooks/                    # React Query hooks
│   ├── store/                    # Zustand stores (theme, notifications, filters)
│   ├── context/                  # AuthContext
│   ├── utils/                    # Utilities (api client, auth helpers)
│   ├── theme/                    # Colors, typography
│   └── types/                    # TypeScript types
├── assets/                       # Images, fonts
├── app.json                      # Expo config
├── babel.config.js               # Babel (NativeWind + Reanimated)
├── metro.config.js               # Metro bundler
└── package.json                  # 📦 Dependencias npm
```

---

## 🚀 COMANDOS DE INICIO RÁPIDO

### **Backend**

```bash
# Navegar al directorio backend
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (crear archivo .env)
cp .env.example .env  # Editar con tus valores

# Ejecutar migraciones de base de datos
alembic upgrade head

# Iniciar servidor de desarrollo
uvicorn src.main:app --reload --port 8000

# URL: http://127.0.0.1:8000
# Docs: http://127.0.0.1:8000/docs
```

**Variables de Entorno Requeridas** (`.env`):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/acadify_db
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-super-secret-key-min-32-chars
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FRONTEND_URL=http://localhost:5173
```

### **Frontend**

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install
# o con pnpm (más rápido)
pnpm install

# Iniciar servidor de desarrollo
npm run dev
# o
pnpm dev

# URL: http://localhost:5173
# Proxy automático a backend configurado en vite.config.ts
```

**Variables de Entorno** (`.env.local`):
```bash
VITE_API_URL=http://localhost:8000
```

### **Mobile**

```bash
# Navegar al directorio mobile
cd mobile

# Instalar dependencias
npm install

# Iniciar Expo
npm start

# Opciones:
# - Presionar 'a' para Android
# - Presionar 'i' para iOS (solo macOS)
# - Escanear QR con Expo Go app
```

### **Docker (Opcional - Servicios)**

```bash
# Iniciar PostgreSQL + Redis con docker-compose
docker-compose up -d

# Detener servicios
docker-compose down
```

---

## 📝 CONVENCIONES DE CÓDIGO

### **Python (Backend)**

#### **Naming Conventions**
```python
# Classes: PascalCase
class UserService:
    pass

# Functions/methods: snake_case
def get_user_by_id(user_id: UUID) -> Usuario | None:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5
SECRET_KEY = "..."

# Private methods: _leading_underscore
def _validate_credentials(self, username: str) -> bool:
    pass

# Variables: snake_case
user_profile = get_profile()
is_authenticated = check_auth()
```

#### **Type Hints (Obligatorios)**
```python
from typing import Any
from uuid import UUID

# Siempre incluir tipos de retorno
def get_user(db: Session, user_id: UUID) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.usuario_id == user_id).first()

# Usar | para Union types (Python 3.10+)
def process_data(data: dict[str, Any]) -> str | int:
    pass
```

#### **Docstrings (Google Style)**
```python
def create_institucion(
    db: Session,
    institucion_data: InstitucionCreate,
    coordinador: Usuario
) -> Institucion:
    """Crea una nueva institución en el sistema.

    Args:
        db: Sesión de base de datos SQLAlchemy.
        institucion_data: Datos de la institución a crear.
        coordinador: Usuario que será coordinador principal.

    Returns:
        Institucion: La institución creada con su ID generado.

    Raises:
        ValueError: Si el código de institución ya existe.
        PermissionError: Si el usuario no tiene permisos de admin.
    """
    pass
```

#### **Error Handling**
```python
from fastapi import HTTPException, status

# Usar HTTPException con status codes apropiados
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )

# Logging de errores
import logging
logger = logging.getLogger(__name__)

try:
    result = dangerous_operation()
except Exception as e:
    logger.error(f"Error en operación: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Error interno")
```

### **TypeScript (Frontend + Mobile)**

#### **Naming Conventions**
```typescript
// Interfaces/Types: PascalCase
interface UserProfile {
  userId: string;
  name: string;
  email: string;
}

// Components: PascalCase
export function UserCard({ user }: { user: UserProfile }) {
  return <div>...</div>;
}

// Hooks: camelCase con prefijo 'use'
export function useUserProfile(userId: string) {
  return useQuery({ ... });
}

// Services: camelCase con sufijo 'Service'
export const authService = {
  login: async (credentials) => { ... }
};

// Constants: UPPER_SNAKE_CASE
export const API_BASE_URL = 'http://localhost:8000';
export const MAX_FILE_SIZE = 10 * 1024 * 1024;

// Functions/variables: camelCase
const isAuthenticated = checkAuth();
const fetchUserData = async () => { ... };
```

#### **Type Safety**
```typescript
// Evitar 'any' - usar tipos específicos o unknown
// ❌ Malo
function processData(data: any) { ... }

// ✅ Bueno
function processData(data: Record<string, unknown>) { ... }
// o mejor aún, define interface
interface ApiResponse {
  success: boolean;
  data: UserProfile;
}
function processData(data: ApiResponse) { ... }

// Usar enums para constantes relacionadas
enum UserRole {
  ADMIN = 'admin',
  COORDINADOR = 'coordinador',
  PROFESOR = 'profesor',
  ESTUDIANTE = 'estudiante'
}
```

#### **React Patterns**
```typescript
// Props interface definida
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

// Component con destructuring
export function Button({ 
  variant = 'primary', 
  size = 'md', 
  loading = false,
  children,
  onClick 
}: ButtonProps) {
  return <button className={...} onClick={onClick}>...</button>;
}

// Custom hooks siempre retornan objetos o arrays
export function useCourses(filters?: CourseFilters) {
  const { data, isLoading, error } = useQuery({ ... });
  
  return {
    courses: data,
    isLoading,
    error
  };
}
```

#### **Async/Await**
```typescript
// Siempre manejar errores en async
async function fetchUserProfile(userId: string): Promise<UserProfile> {
  try {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Error fetching profile');
    }
    throw error;
  }
}
```

---

## 🔄 FLUJOS CRÍTICOS DEL SISTEMA

### **1. Autenticación JWT + 2FA**

**Flujo Login:**
```
1. POST /auth/login { identifier, password }
   ↓
2. Backend valida credenciales
   ↓
3. Si 2FA activado:
   - Retorna { requires_2fa: true, session_token }
   - Frontend solicita código 2FA
   - POST /auth/2fa/verify { session_token, codigo }
   ↓
4. Backend genera tokens:
   - access_token (15 min) JWT con user_id, rol
   - refresh_token (30 días) guardado en Redis
   ↓
5. Frontend guarda tokens en localStorage
   - Configura interceptor axios con Bearer token
   - Navega a dashboard según rol
```

**Flujo Refresh Token:**
```
1. Request falla con 401 Unauthorized
   ↓
2. Interceptor axios captura error
   ↓
3. POST /auth/refresh { refresh_token }
   ↓
4. Backend valida refresh_token en Redis
   - Genera nuevo access_token
   ↓
5. Frontend actualiza token en localStorage
   ↓
6. Retry request original con nuevo token
```

### **2. Jerarquía Académica**

**Estructura:**
```
Institución (ej: Universidad Nacional)
  ↓
Programas (ej: Ingeniería de Sistemas, Medicina)
  ↓
Cursos (ej: Programación I, Álgebra)
  ↓
Grupos Curso (ej: Grupo A - Mañana, Grupo B - Tarde)
  ↓
Clases (ej: Clase 1: Introducción, Clase 2: Variables)
```

**Flujo Creación Curso:**
```
1. Coordinador crea curso
   POST /api/cursos
   {
     nombre: "Programación I",
     institucion_id: "uuid",
     programa_id: "uuid" (opcional),
     creditos: 4,
     modalidad: "presencial"
   }
   ↓
2. Backend valida:
   - Coordinador pertenece a institución
   - Programa existe (si se especifica)
   - Código curso único
   ↓
3. Crea registro en tabla Curso
   ↓
4. Frontend actualiza lista con React Query
   - Invalida cache: ['cursos', institucion_id]
```

### **3. Sistema de Gamificación**

**Otorgamiento de Puntos:**
```
1. Usuario completa actividad (tarea, quiz, clase)
   ↓
2. Backend detecta evento
   - Trigger: completar_tarea()
   ↓
3. GamificacionService.otorgar_puntos()
   - Calcula puntos según actividad
   - Actualiza UsuarioPuntos
   - Verifica rachas (días consecutivos)
   - Verifica logros desbloqueados
   ↓
4. Si logro desbloqueado:
   - Crea UsuarioLogro
   - Envía notificación push
   ↓
5. Frontend muestra toast animado
   - "¡+50 puntos! 🎉"
   - "¡Logro desbloqueado: Primer Paso!"
```

**Rachas Diarias:**
```
- Usuario debe realizar ≥1 actividad cada día
- Ventana: 04:00 AM a 03:59 AM del día siguiente
- Si no hay actividad en 24h → racha se pierde
- Racha máxima histórica se guarda
- Bonificación: +10% puntos si racha ≥7 días
```

### **4. Comunicación Real-Time (WebSocket)**

**Conexión WebSocket:**
```
1. Frontend se conecta al login
   const socket = io('ws://localhost:8000/api/communication', {
     auth: { token: access_token }
   });
   ↓
2. Backend valida JWT en handshake
   - Extrae user_id del token
   - Asocia socket.id con user_id en Redis
   ↓
3. Usuario se une a rooms:
   socket.emit('join_conversation', { conversation_id })
   ↓
4. Envío de mensaje:
   socket.emit('send_message', {
     conversation_id,
     content: "Hola",
     type: "text"
   })
   ↓
5. Backend:
   - Guarda mensaje en PostgreSQL
   - Emite a todos los usuarios en room
   socket.to(conversation_id).emit('new_message', message)
   ↓
6. Frontend recibe y actualiza UI en tiempo real
```

### **5. Sistema de Avatares**

**Composición de Avatar:**
```
1. Usuario elige partes en editor
   {
     base: "base-man-01",
     hair: "hair-short-brown",
     eyes: "eyes-blue",
     clothes: "shirt-casual"
   }
   ↓
2. POST /avatar/preview (genera preview temporal)
   - Backend compone SVG en memoria
   - Cachea en Redis (TTL 1h)
   - Retorna URL de preview
   ↓
3. Usuario confirma
   POST /avatar/save
   ↓
4. Backend:
   - Genera SVG final
   - Guarda en /static/avatars/{user_id}.svg
   - Actualiza Usuario.avatar_url
   - Cachea composición final en Redis (TTL 7 días)
   ↓
5. Frontend muestra avatar en navbar
   <Avatar src={user.avatar_url} />
```

---

## 📚 GUÍAS ESPECIALIZADAS

Consulta estos archivos para información detallada por dominio:

1. **[BACKEND_GUIDE.md](./BACKEND_GUIDE.md)**
   - Modelos SQLAlchemy completos
   - Servicios y CRUD patterns
   - Endpoints API REST
   - Migraciones Alembic
   - Testing con Pytest

2. **[FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md)**
   - Componentes UI reutilizables
   - React Query hooks
   - Servicios API clients
   - Routing y lazy loading
   - Testing con Vitest

3. **[MOBILE_GUIDE.md](./MOBILE_GUIDE.md)**
   - Arquitectura Clean + SOLID
   - Zustand stores
   - React Query hooks mobile
   - Expo Router navigation
   - NativeWind styling

4. **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)**
   - Diagrama ER completo
   - Tablas y columnas
   - Relaciones y foreign keys
   - Índices y constraints
   - Triggers y vistas

5. **[GAMIFICATION_GUIDE.md](./GAMIFICATION_GUIDE.md)**
   - Sistema de puntos
   - Logros y criterios
   - Rachas diarias
   - Misiones
   - Tienda de recompensas

6. **[COMMUNICATION_GUIDE.md](./COMMUNICATION_GUIDE.md)**
   - WebSocket setup
   - Chat en tiempo real
   - Notificaciones push
   - Videollamadas WebRTC
   - Email templates

7. **[AVATAR_SYSTEM.md](./AVATAR_SYSTEM.md)**
   - Estructura de assets SVG
   - Composición de avatares
   - Cache Redis
   - Editor frontend

8. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)**
   - Unit tests (Pytest, Vitest)
   - Integration tests
   - E2E tests
   - Coverage reports
   - CI/CD pipeline

---

## ⚡ MEJORES PRÁCTICAS OBLIGATORIAS

### **Backend**

1. ✅ **Siempre usar type hints** en funciones
2. ✅ **Validar datos con Pydantic schemas** antes de procesar
3. ✅ **Usar transacciones** para operaciones multi-tabla
4. ✅ **Implementar idempotencia** en endpoints críticos
5. ✅ **Cachear queries frecuentes** en Redis (instituciones, cursos)
6. ✅ **Log de errores** con contexto (user_id, request_id)
7. ✅ **Rate limiting** en endpoints sensibles (login, registro)
8. ✅ **Sanitizar inputs** para prevenir SQL injection
9. ✅ **Usar enums** para estados y tipos (evitar strings mágicos)
10. ✅ **Escribir tests** para servicios críticos (auth, gamificación)

### **Frontend**

1. ✅ **Lazy loading** de páginas y componentes pesados
2. ✅ **React Query** para todas las requests (nunca useState + useEffect)
3. ✅ **Memoization** con useMemo/useCallback en listas grandes
4. ✅ **Error boundaries** en rutas principales
5. ✅ **Loading states** siempre visibles
6. ✅ **Optimistic updates** en mutaciones simples
7. ✅ **Debounce** en búsquedas y autocomplete
8. ✅ **Validación** con React Hook Form + Zod
9. ✅ **Accessibility** (roles, aria-labels, keyboard nav)
10. ✅ **Code splitting** por feature (vite.config.ts manualChunks)

### **Código Limpio**

1. ✅ **DRY**: Si copias código 2+ veces → extrae función/componente
2. ✅ **KISS**: Prefiere soluciones simples sobre complejas
3. ✅ **YAGNI**: No implementes features "por si acaso"
4. ✅ **Single Source of Truth**: Backend es la fuente, frontend cachea
5. ✅ **Fail Fast**: Valida inputs al inicio de funciones
6. ✅ **Naming**: Nombres descriptivos > comentarios explicativos
7. ✅ **Pure Functions**: Evita side effects innecesarios
8. ✅ **Early Returns**: Reduce indentación con guard clauses
9. ✅ **Comments**: Solo para "por qué", no "qué" hace el código
10. ✅ **Refactor**: Si tocas archivo viejo, mejora su calidad

---

## 🔧 HERRAMIENTAS DE DESARROLLO

### **Linting y Formatting**

```bash
# Backend - Ruff (súper rápido)
cd backend
ruff check src/          # Linting
ruff check --fix src/    # Auto-fix
ruff format src/         # Formatting

# Frontend - ESLint + Prettier
cd frontend
npm run lint             # Linting
npm run lint:fix         # Auto-fix
npm run format           # Formatting
npm run type-check       # TypeScript check
```

### **Testing**

```bash
# Backend - Pytest
cd backend
pytest                   # Run all tests
pytest -v                # Verbose
pytest --cov=src         # Con coverage
pytest tests/test_auth.py -k test_login  # Test específico

# Frontend - Vitest
cd frontend
npm run test             # Watch mode
npm run test:run         # Single run
npm run test:coverage    # Con coverage
```

### **Base de Datos**

```bash
# Crear migración
cd backend
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Rollback
alembic downgrade -1

# Ver historial
alembic history
```

---

## 🐛 DEBUGGING COMÚN

### **Backend no inicia**
```bash
# Verificar variables de entorno
cat backend/.env

# Verificar PostgreSQL
psql -U acadify_user -d acadify_db -h localhost

# Verificar Redis
redis-cli ping  # Debe retornar PONG

# Ver logs detallados
uvicorn src.main:app --reload --log-level debug
```

### **Frontend no conecta con backend**
```bash
# Verificar backend está corriendo
curl http://localhost:8000/

# Verificar proxy en vite.config.ts
# Verificar VITE_API_URL en .env.local

# Ver network tab en DevTools (F12)
```

### **Errores de CORS**
```python
# backend/src/core/config.py
BACKEND_CORS_ORIGINS = [
    "http://localhost:5173",  # Frontend dev
    "http://localhost:3000"   # Alternativo
]
```

---

## 📞 CONTACTO Y SOPORTE

- **Repositorio**: Acadify @ GitHub
- **Documentación**: `/docs`
- **Issues**: GitHub Issues
- **Stack Overflow**: Tag `acadify`

---

**Última actualización**: Noviembre 2025  
**Mantenido por**: Equipo Acadify

---

