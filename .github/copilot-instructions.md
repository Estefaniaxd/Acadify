# GitHub Copilot Instructions - Acadify

> **Instrucciones globales para autocompletado inteligente de GitHub Copilot**
> Este archivo es leído automáticamente por Copilot al generar sugerencias de código.

---

## 🎯 Proyecto: Acadify

**Tipo**: Plataforma educativa full-stack con gamificación
**Stack**: Python (FastAPI) + React (TypeScript) + React Native (Expo)
**Arquitectura**: Clean Architecture, SOLID principles, Repository Pattern

---

## 📚 Contexto del Proyecto

### **Backend**

- **Framework**: FastAPI 0.116.1 con async/await
- **ORM**: SQLAlchemy 2.0.43 con mapped_column
- **Database**: PostgreSQL 15+ con JSONB, arrays, enums
- **Cache**: Redis 7+ para sesiones, cache, pub/sub
- **Validación**: Pydantic 2.11.7 con strict mode
- **Auth**: JWT (PyJWT 2.10.1) + 2FA (TOTP/Email) + bcrypt
- **Testing**: Pytest 7.4.3 con fixtures, async tests
- **Linting**: Ruff (linting + formatting súper rápido)
- **Migrations**: Alembic 1.16.5

### **Frontend**

- **Framework**: React 18.2.0 con TypeScript 5.2.2 strict
- **Build Tool**: Vite 5.1.5 con manual chunks optimization
- **State Management**: TanStack Query 5.90.5 (server state)
- **Routing**: React Router 6.30.1 con lazy loading
- **Styling**: TailwindCSS 3.4.7 + Framer Motion 10.18.0
- **Real-time**: Socket.io Client 4.8.1
- **Testing**: Vitest 4.0.5 + Testing Library
- **Linting**: ESLint 9 + Prettier

### **Mobile**

- **Framework**: React Native 0.81.5 + Expo ~54.0
- **State Management**: Zustand 5.0.8
- **Data Fetching**: TanStack Query 5.90.5
- **Routing**: Expo Router ~6.0 (file-based)
- **Styling**: NativeWind (TailwindCSS for RN)

---

## 🏗️ Estructura de Directorios

```
backend/src/
├── api/routers/        # FastAPI routers
├── core/               # config.py, security.py, dependencies.py
├── models/             # SQLAlchemy models (Usuario, Institucion, etc.)
├── schemas/            # Pydantic schemas
├── services/           # Business logic (AuthService, InstitucionService)
├── crud/               # Data access (CRUDBase, CRUDUsuario)
├── db/                 # database.py, base.py
└── utils/              # Helpers, constants

frontend/src/
├── components/         # Componentes reutilizables UI
│   ├── ui/            # Button, Input, Modal, etc.
│   └── features/      # Componentes específicos de feature
├── hooks/              # Custom hooks (useAuth, useInstituciones)
├── services/           # API services (apiClient.ts, authService.ts)
├── pages/              # Páginas (lazy loaded)
├── contexts/           # React contexts (AuthContext)
├── store/              # Zustand stores (si se usa)
├── types/              # TypeScript interfaces/types
└── utils/              # Helpers, constants

mobile/src/
├── components/         # Componentes UI nativos
├── screens/            # Pantallas (equivalente a pages)
├── services/           # API services (repository pattern)
├── store/              # Zustand stores
├── hooks/              # Custom hooks
├── types/              # TypeScript types
└── utils/              # Helpers
```

---

## 🎨 Convenciones de Código

### **Python (Backend)**

#### **Naming**

```python
# snake_case para todo (funciones, variables, archivos)
def calcular_puntos_usuario(usuario_id: int, actividad: str) -> int:
    total_puntos = 0
    # ...
    return total_puntos

# PascalCase solo para clases
class UsuarioService:
    pass

# UPPER_CASE para constantes
MAX_INTENTOS_LOGIN = 5
```

#### **Type Hints Obligatorios**

```python
# ✅ SIEMPRE con type hints
def obtener_usuario(user_id: int) -> Usuario | None:
    pass

async def crear_institucion(data: InstitucionCreate) -> Institucion:
    pass

# ❌ NUNCA sin type hints
def obtener_usuario(user_id):  # ❌ Malo
    pass
```

#### **Docstrings (Google Style)**

```python
def verificar_racha_usuario(usuario_id: int, fecha: date) -> bool:
    """Verifica si el usuario mantiene su racha activa.

    Args:
        usuario_id: ID del usuario a verificar
        fecha: Fecha a verificar (por defecto hoy)

    Returns:
        True si la racha está activa, False otherwise

    Raises:
        ValueError: Si usuario_id es inválido
    """
    pass
```

#### **SQLAlchemy Models**

```python
# Usar mapped_column con Mapped[type]
class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    # Relationships
    instituciones: Mapped[list["Institucion"]] = relationship(back_populates="usuarios")
```

#### **Pydantic Schemas**

```python
# Base, Create, Update pattern
class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)

class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None

class UsuarioResponse(UsuarioBase):
    id: int
    activo: bool
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)
```

#### **FastAPI Routers**

```python
# Dependency Injection + response_model
@router.post("/", response_model=UsuarioResponse, status_code=201)
async def crear_usuario(
    data: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Autorización
) -> UsuarioResponse:
    """Crea un nuevo usuario."""
    service = UsuarioService(db)
    usuario = await service.crear_usuario(data)
    return usuario
```

---

### **TypeScript (Frontend/Mobile)**

#### **Naming**

```typescript
// camelCase para variables, funciones, parámetros
const fetchUsuarios = async () => { ... }
const usuarioActual = data.usuario;

// PascalCase para componentes, interfaces, types, enums
interface UsuarioData { ... }
type AuthState = "authenticated" | "unauthenticated";
enum RolUsuario { ADMIN = "ADMIN", DOCENTE = "DOCENTE" }
function AuthForm() { ... }

// UPPER_CASE para constantes
const MAX_FILE_SIZE = 5 * 1024 * 1024;
```

#### **Interfaces vs Types**

```typescript
// Interfaces para objetos (preferido para extensibilidad)
interface Usuario {
  id: number;
  email: string;
  nombre: string;
}

interface UsuarioConPermisos extends Usuario {
  permisos: string[];
}

// Types para unions, primitivos, utility types
type AuthStatus = "loading" | "authenticated" | "unauthenticated";
type UsuarioOpcional = Partial<Usuario>;
```

#### **React Components (Functional + TypeScript)**

```typescript
// Props interface + FC
interface ButtonProps {
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  onClick,
  children,
}: ButtonProps) {
  return (
    <button
      className={cn("rounded-md font-medium transition-colors", {
        "bg-blue-600 hover:bg-blue-700": variant === "primary",
        "bg-gray-200 hover:bg-gray-300": variant === "secondary",
      })}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
}
```

#### **Custom Hooks React Query**

```typescript
// Queries con queryKey factory
export function useInstituciones() {
  return useQuery({
    queryKey: ["instituciones"],
    queryFn: () => apiClient.get<Institucion[]>("/api/instituciones").then((res) => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

export function useInstitucion(id: number) {
  return useQuery({
    queryKey: ["instituciones", id],
    queryFn: () => apiClient.get<Institucion>(`/api/instituciones/${id}`).then((res) => res.data),
    enabled: !!id,
  });
}

// Mutations con invalidación automática
export function useCrearInstitucion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: InstitucionCreate) =>
      apiClient.post<Institucion>("/api/instituciones", data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["instituciones"] });
    },
  });
}
```

#### **API Services (Axios)**

```typescript
// apiClient.ts con interceptors
import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor (agregar token)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (refresh token automático)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Intentar refresh token
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        const res = await axios.post("/api/auth/refresh", { refresh_token: refreshToken });
        localStorage.setItem("access_token", res.data.access_token);

        // Reintentar request original
        error.config.headers.Authorization = `Bearer ${res.data.access_token}`;
        return axios(error.config);
      } catch {
        // Redirect a login
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 🔒 Seguridad y Mejores Prácticas

### **Backend**

#### **Validación de Inputs**

```python
# ✅ Siempre validar con Pydantic
class InstitucionCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    telefono: str | None = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")

    @field_validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('Nombre no puede estar vacío')
        return v.strip()
```

#### **Autorización**

```python
# Dependencies para verificar permisos
async def require_admin(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """Requiere que el usuario sea administrador."""
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    return current_user

async def require_docente_curso(
    curso_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Curso:
    """Verifica que el usuario sea docente del curso."""
    curso = await db.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    if curso.docente_id != current_user.id and current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="No eres docente de este curso")

    return curso

# Uso en endpoint
@router.patch("/{curso_id}")
async def actualizar_curso(
    data: CursoUpdate,
    curso: Curso = Depends(require_docente_curso)  # Autorización automática
):
    # curso ya está validado y autorizado
    pass
```

#### **SQL Injection Prevention**

```python
# ✅ SIEMPRE usar ORM o parámetros
result = await db.execute(
    select(Usuario).where(Usuario.email == email)
)

# ❌ NUNCA string interpolation
query = f"SELECT * FROM usuarios WHERE email = '{email}'"  # ❌ SQL Injection
```

#### **Secrets Management**

```python
# ✅ Variables de entorno con Pydantic Settings
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = Field(..., min_length=32)
    REDIS_HOST: str

    model_config = SettingsConfigDict(env_file=".env")

# ❌ NUNCA hardcodear secrets
SECRET_KEY = "mi-super-secret-key-12345"  # ❌ Malo
```

---

### **Frontend**

#### **XSS Prevention**

```typescript
// ✅ React escapa por defecto
<div>{usuario.nombre}</div>; // ✅ Safe

// ❌ dangerouslySetInnerHTML solo si es NECESARIO y está sanitizado
import DOMPurify from "dompurify";

<div
  dangerouslySetInnerHTML={{
    __html: DOMPurify.sanitize(htmlContent),
  }}
/>;
```

#### **CSRF Prevention**

```typescript
// ✅ Token en headers (automático con apiClient)
apiClient.post("/api/usuarios", data); // Incluye token JWT automáticamente
```

#### **Secrets en Frontend**

```typescript
// ✅ Variables de entorno (solo públicas)
const API_URL = import.meta.env.VITE_API_URL;

// ❌ NUNCA secrets en frontend
const API_KEY = "sk-1234567890abcdef"; // ❌ Visible en bundle
```

---

## 🧪 Testing

### **Backend (Pytest)**

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from httpx import AsyncClient

@pytest.fixture
async def db() -> AsyncSession:
    """Database session fixture."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client(db: AsyncSession) -> AsyncClient:
    """HTTP client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# tests/api/test_usuarios.py
async def test_crear_usuario(client: AsyncClient):
    """Test crear usuario exitosamente."""
    response = await client.post("/api/usuarios", json={
        "email": "test@example.com",
        "nombre": "Test",
        "password": "SecurePass123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data  # No debe retornar password
```

---

### **Frontend (Vitest + Testing Library)**

```typescript
// components/Button.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Button } from "./Button";

describe("Button", () => {
  it("renders children correctly", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    fireEvent.click(screen.getByText("Click"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled when loading", () => {
    render(<Button loading>Submit</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});

// hooks/useInstituciones.test.tsx
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useInstituciones } from "./useInstituciones";

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("useInstituciones", () => {
  it("fetches instituciones successfully", async () => {
    const { result } = renderHook(() => useInstituciones(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(3);
  });
});
```

---

## ⚡ Performance

### **Backend**

```python
# ✅ Usar índices en queries frecuentes
class Usuario(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    institucion_id: Mapped[int] = mapped_column(Integer, ForeignKey("instituciones.id"), index=True)

# ✅ Eager loading para evitar N+1
result = await db.execute(
    select(Curso)
    .options(selectinload(Curso.docente))  # Load relationship
    .where(Curso.institucion_id == institucion_id)
)

# ✅ Usar Redis para cache
@lru_cache(maxsize=100)
def obtener_configuracion(key: str) -> str:
    return redis_client.get(key)

# ✅ Paginación siempre
@router.get("/")
async def listar_cursos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    pass
```

---

### **Frontend**

```typescript
// ✅ Lazy loading de componentes
const CursosPage = lazy(() => import("./pages/CursosPage"));
const InstitucionesPage = lazy(() => import("./pages/InstitucionesPage"));

// ✅ React Query caching
const { data } = useQuery({
  queryKey: ["usuarios", filtros],
  queryFn: fetchUsuarios,
  staleTime: 5 * 60 * 1000, // Cache 5 minutos
});

// ✅ Memoization
const ListaUsuarios = memo(({ usuarios }: { usuarios: Usuario[] }) => {
  return usuarios.map((user) => <UsuarioCard key={user.id} usuario={user} />);
});

// ✅ useMemo para cálculos costosos
const estadisticas = useMemo(() => {
  return usuarios.reduce((acc, user) => {
    // cálculo costoso
  }, {});
}, [usuarios]);

// ✅ Virtualization para listas largas
import { VirtualList } from "react-virtualized";

<VirtualList
  rowCount={usuarios.length}
  rowHeight={60}
  rowRenderer={({ index }) => <UsuarioCard usuario={usuarios[index]} />}
/>;
```

---

## 🚀 Comandos Útiles

### **Backend**

```bash
# Iniciar servidor de desarrollo
cd backend
uvicorn src.main:app --reload --port 8000

# Crear migración Alembic
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Correr tests
pytest tests/ -v

# Coverage
pytest --cov=src --cov-report=html

# Lint + format
ruff check src/
ruff format src/
```

---

### **Frontend**

```bash
# Iniciar dev server (puerto 5173)
cd frontend
pnpm dev

# Build producción
pnpm build

# Preview build
pnpm preview

# Tests en watch mode
pnpm test

# Coverage
pnpm test:coverage

# Lint + fix
pnpm lint --fix

# Format
pnpm format
```

---

### **Mobile**

```bash
# Iniciar Expo dev server
cd mobile
npm start

# Android emulator
npm run android

# iOS simulator
npm run ios

# Tests
npm test

# Build producción
eas build --platform all
```

---

## 🎯 Principios Arquitectónicos

### **SOLID**

- **S**ingle Responsibility: Un servicio/componente hace UNA cosa
- **O**pen/Closed: Extensible sin modificar (inheritance, composition)
- **L**iskov Substitution: Subclases intercambiables
- **I**nterface Segregation: Interfaces pequeñas y específicas
- **D**ependency Inversion: Depender de abstracciones (Dependency Injection)

### **DRY (Don't Repeat Yourself)**

- Extraer funciones/componentes reutilizables
- Custom hooks para lógica compartida
- Services para API calls
- Utils para helpers

### **Type Safety First**

- Type hints en Python (100% coverage)
- TypeScript strict mode
- No usar `any` (usar `unknown` si es necesario)
- Schemas Pydantic para validación backend

---

## 📦 Imports Organization

### **Python**

```python
# Standard library
import os
from datetime import datetime, timedelta
from typing import List, Optional

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from pydantic import BaseModel, Field

# Local
from src.core.config import get_settings
from src.models.usuario import Usuario
from src.schemas.usuario import UsuarioCreate, UsuarioResponse
from src.services.usuario_service import UsuarioService
```

---

### **TypeScript**

```typescript
// React
import { useState, useEffect, useMemo } from "react";

// Third-party
import { useQuery, useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

// Services
import { apiClient } from "@/services/apiClient";
import { authService } from "@/services/authService";

// Components
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

// Types
import type { Usuario, InstitucionCreate } from "@/types";

// Utils
import { cn } from "@/utils/cn";
```

---

## 🎨 Code Style Summary

- **Indentación**: 4 espacios (Python), 2 espacios (TypeScript/TSX)
- **Strings**: Comillas dobles `"` (Python y TypeScript)
- **Line Length**: 88 caracteres (Python/Ruff), 100 caracteres (TypeScript/Prettier)
- **Trailing Commas**: Sí (facilita diffs)
- **Semicolons**: No (TypeScript/Prettier omite semicolons)

---

## 🚨 Anti-Patterns to Avoid

### **Backend**

```python
# ❌ Lógica de negocio en routers
@router.post("/")
async def crear_usuario(data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    # ❌ No hacer esto (lógica en router)
    usuario = Usuario(**data.model_dump())
    usuario.password_hash = bcrypt.hashpw(...)
    db.add(usuario)
    await db.commit()
    return usuario

# ✅ Lógica en servicios
@router.post("/")
async def crear_usuario(data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    service = UsuarioService(db)
    return await service.crear_usuario(data)
```

---

### **Frontend**

```typescript
// ❌ Fetch directo en componentes
function UsuariosPage() {
  const [usuarios, setUsuarios] = useState([]);

  useEffect(() => {
    fetch("/api/usuarios")
      .then((res) => res.json())
      .then(setUsuarios);
  }, []);
  // ...
}

// ✅ Usar React Query + service
function UsuariosPage() {
  const { data: usuarios, isLoading } = useUsuarios();
  // ...
}
```

---

## 🔗 Referencias Rápidas

- **Backend Guide**: `.copilot/prompts/BACKEND_GUIDE.md`
- **Frontend Guide**: `.copilot/prompts/FRONTEND_GUIDE.md`
- **Project Master Guide**: `.copilot/prompts/PROJECT_MASTER_GUIDE.md`
- **Agent Instructions**: `.copilot/AGENT_INSTRUCTIONS.md`

---

**Última actualización**: 12 de noviembre de 2025
**Versión**: 1.0.0
