# 🚀 Stack Tecnológico Acadify

Documentación completa de todas las tecnologías, frameworks y librerías utilizadas en el proyecto Acadify.

---

## 📋 Índice
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Backend Stack](#backend-stack)
3. [Frontend Stack](#frontend-stack)
4. [Base de Datos](#base-de-datos)
5. [DevOps y Herramientas](#devops-y-herramientas)
6. [Integraciones Externas](#integraciones-externas)
7. [Justificación de Decisiones](#justificación-de-decisiones)

---

## 🎯 Resumen Ejecutivo

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│         React + TypeScript + Vite + TailwindCSS             │
│                    (Port: 5173)                             │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST + WebSockets
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│              Python + FastAPI + SQLAlchemy                  │
│                    (Port: 8000)                             │
└────────────────────┬────────────────────────────────────────┘
                     │ PostgreSQL Protocol
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      BASE DE DATOS                          │
│                    PostgreSQL 14+                           │
│                    (Port: 5432)                             │
└─────────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    SERVICIOS EXTERNOS                       │
│   Redis Cache | Email Service | Google Gemini AI           │
└─────────────────────────────────────────────────────────────┘
```

### Stack Principal

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| **Frontend** | React | 18.3+ | UI Library |
| **Lenguaje Frontend** | TypeScript | 5.0+ | Type Safety |
| **Build Tool** | Vite | 5.0+ | Dev Server & Bundler |
| **Styling** | TailwindCSS | 3.4+ | Utility-First CSS |
| **Backend Framework** | FastAPI | 0.116+ | REST API |
| **Lenguaje Backend** | Python | 3.12+ | Core Language |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM |
| **Base de Datos** | PostgreSQL | 14+ | Relational Database |
| **Cache** | Redis | 6.4+ | Caching & Sessions |
| **AI Service** | Google Gemini | 0.8+ | AI Integration |

---

## 🐍 Backend Stack

### 1. **Python 3.12+**

**¿Qué es?**  
Lenguaje de programación de alto nivel, interpretado, de propósito general.

**¿Por qué Python?**
- ✅ Sintaxis limpia y legible
- ✅ Ecosistema rico en librerías
- ✅ Excelente para desarrollo rápido
- ✅ Gran comunidad y soporte
- ✅ Ideal para integración con IA/ML

**Uso en el proyecto:**
- Core del backend
- Lógica de negocio
- Scripts de utilidad
- Integración con servicios de IA

---

### 2. **FastAPI 0.116+**

**¿Qué es?**  
Framework web moderno y de alto rendimiento para construir APIs con Python basado en type hints.

**Características clave:**
- ✅ **Alto rendimiento:** Comparable a NodeJS y Go
- ✅ **Type hints:** Validación automática con Pydantic
- ✅ **Async/Await:** Soporte nativo para operaciones asíncronas
- ✅ **Documentación automática:** Swagger UI y ReDoc integrados
- ✅ **Validación automática:** Request y Response validation
- ✅ **Dependency Injection:** Sistema robusto de inyección

**Ejemplo de uso:**
```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item
```

**Ventajas para Acadify:**
- ⚡ Performance excepcional para operaciones en tiempo real
- 📚 Documentación automática sin esfuerzo extra
- 🔒 Type safety reduce bugs en producción
- 🚀 Desarrollo rápido con menos código boilerplate

**Librerías complementarias:**
- `uvicorn==0.35.0` - ASGI server de alto rendimiento
- `starlette==0.46.2` - Framework base de FastAPI
- `python-multipart==0.0.20` - Soporte para form data y file uploads

---

### 3. **SQLAlchemy 2.0+**

**¿Qué es?**  
ORM (Object-Relational Mapping) más popular de Python para interactuar con bases de datos.

**Características clave:**
- ✅ **ORM completo:** Mapeo objeto-relacional
- ✅ **Query Builder:** Constructor de queries SQL
- ✅ **Async support:** Soporte completo para operaciones asíncronas
- ✅ **Migrations:** Integración con Alembic
- ✅ **Múltiples DBs:** PostgreSQL, MySQL, SQLite, etc.

**Ejemplo de uso:**
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
```

**Ventajas para Acadify:**
- 🔧 Abstracción completa de SQL
- 🔄 Migraciones automáticas con Alembic
- 📊 Relationships complejas simplificadas
- ⚡ Query optimization automática

**Librerías complementarias:**
- `alembic==1.16.5` - Migraciones de base de datos
- `greenlet==3.2.4` - Soporte para async/await
- `psycopg2-binary==2.9.10` - Driver PostgreSQL

---

### 4. **Pydantic 2.11+**

**¿Qué es?**  
Librería de validación de datos usando Python type hints.

**Características clave:**
- ✅ **Data validation:** Validación automática de tipos
- ✅ **Serialization:** Conversión a/desde JSON
- ✅ **Settings management:** Gestión de configuración
- ✅ **IDE support:** Autocompletado en IDEs
- ✅ **Performance:** Implementado en Rust (core)

**Ejemplo de uso:**
```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    nombre: str = Field(..., min_length=2, max_length=100)
    edad: int = Field(..., ge=18, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "nombre": "Juan Pérez",
                "edad": 25
            }
        }
```

**Ventajas para Acadify:**
- ✅ Menos bugs por validación automática
- ✅ Documentación OpenAPI automática
- ✅ Type safety en toda la aplicación
- ✅ Configuración con variables de entorno

**Librerías complementarias:**
- `pydantic-core==2.33.2` - Core en Rust para performance
- `pydantic-settings==2.10.1` - Gestión de configuración
- `pydantic-extra-types==2.10.5` - Tipos adicionales (PhoneNumber, Color, etc.)
- `email_validator==2.2.0` - Validación de emails

---

### 5. **Autenticación y Seguridad**

#### 5.1 **PyJWT 2.10+**
**¿Qué es?**  
Implementación de JSON Web Tokens (JWT) para Python.

**Características:**
- ✅ Tokens seguros y stateless
- ✅ Claims personalizados
- ✅ Múltiples algoritmos (HS256, RS256, etc.)
- ✅ Validación automática de expiración

**Ejemplo:**
```python
import jwt
from datetime import datetime, timedelta

payload = {
    "sub": user_id,
    "exp": datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

#### 5.2 **passlib 1.7+**
**¿Qué es?**  
Librería de hashing de passwords con múltiples algoritmos.

**Características:**
- ✅ Bcrypt para passwords
- ✅ Salting automático
- ✅ Verificación de passwords
- ✅ Múltiples algoritmos soportados

**Ejemplo:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("mi_password_segura")

# Verificar password
pwd_context.verify("mi_password_segura", hashed)  # True
```

#### 5.3 **python-jose 3.5+**
**¿Qué es?**  
Implementación de JOSE (Javascript Object Signing and Encryption).

**Uso:**
- Firma y verificación de JWTs
- Integración con OAuth2
- Tokens seguros

#### 5.4 **Authlib 1.6+**
**¿Qué es?**  
Librería completa de autenticación (OAuth2, OpenID Connect).

**Características:**
- ✅ OAuth2 client/server
- ✅ OpenID Connect
- ✅ Integración con providers (Google, GitHub, etc.)

**Librerías complementarias:**
- `bcrypt==4.3.0` - Hashing de passwords
- `pyotp==2.9.0` - Two-factor authentication (2FA)
- `qrcode==8.2` - Generación de QR codes para 2FA

---

### 6. **Librerías de Utilidad**

#### 6.1 **Python-dotenv 1.1+**
**¿Qué es?**  
Carga variables de entorno desde archivos `.env`.

**Ejemplo:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```

#### 6.2 **Python-dateutil 2.9+**
**¿Qué es?**  
Extensión del módulo datetime de Python.

**Características:**
- ✅ Parsing flexible de fechas
- ✅ Timezone handling
- ✅ Relative deltas

#### 6.3 **Redis 6.4+**
**¿Qué es?**  
Cliente Python para Redis (cache y message broker).

**Uso en Acadify:**
- 🚀 Cache de queries frecuentes
- 💾 Sesiones de usuario
- 📬 Message queue para tasks asíncronas
- 🔄 Rate limiting

**Ejemplo:**
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
r.set('user:1:points', 1000)
points = r.get('user:1:points')
```

#### 6.4 **Email (aiosmtplib 4.0+)**
**¿Qué es?**  
Cliente SMTP asíncrono para envío de emails.

**Uso:**
- 📧 Verificación de email
- 🔐 Reset de contraseña
- 📨 Notificaciones
- 🎓 Certificados

---

### 7. **Inteligencia Artificial**

#### 7.1 **Google Generative AI 0.8+**
**¿Qué es?**  
SDK oficial de Google para Gemini AI.

**Uso en Acadify:**
- 🤖 Corrección automática de tareas
- 💬 Asistente virtual
- 📝 Generación de preguntas de examen
- 🎯 Recomendaciones personalizadas

**Ejemplo:**
```python
import google.generativeai as genai

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Explica qué es FastAPI")
```

#### 7.2 **OpenAI 1.102+**
**¿Qué es?**  
SDK oficial de OpenAI (GPT-4, DALL-E, Whisper).

**Uso:**
- 🧠 Alternativa a Gemini
- 🎨 Generación de imágenes (avatares custom)
- 🗣️ Transcripción de audio

**Librerías de procesamiento de documentos:**
- `PyPDF2==3.0.1` - Procesamiento de PDFs
- `python-docx==1.1.2` - Procesamiento de Word
- `openpyxl==3.1.5` - Procesamiento de Excel
- `python-pptx==1.0.2` - Procesamiento de PowerPoint

---

### 8. **Data Processing**

#### 8.1 **Pandas 2.2+**
**¿Qué es?**  
Librería de análisis y manipulación de datos.

**Uso en Acadify:**
- 📊 Reportes académicos
- 📈 Análisis de calificaciones
- 📉 Estadísticas de gamificación
- 💾 Export de datos (CSV, Excel)

**Ejemplo:**
```python
import pandas as pd

# Análisis de calificaciones
df = pd.DataFrame(calificaciones)
promedio = df['nota'].mean()
aprobados = len(df[df['nota'] >= 60])
```

#### 8.2 **NumPy 1.26+**
**¿Qué es?**  
Librería fundamental para computación científica.

**Uso:**
- 🔢 Cálculos matemáticos
- 📊 Estadísticas avanzadas
- 🎯 Algoritmos de recomendación

#### 8.3 **Matplotlib 3.10+**
**¿Qué es?**  
Librería de visualización de datos.

**Uso:**
- 📈 Gráficos de progreso
- 📊 Reportes visuales
- 🎓 Estadísticas académicas

**Librerías complementarias:**
- `pandasql==0.7.3` - SQL queries sobre DataFrames
- `tabulate==0.9.0` - Pretty printing de tablas

---

### 9. **Testing**

#### 9.1 **Pytest 7.4+**
**¿Qué es?**  
Framework de testing más popular para Python.

**Características:**
- ✅ Sintaxis simple y expresiva
- ✅ Fixtures para setup/teardown
- ✅ Parametrización de tests
- ✅ Plugins extensibles

**Ejemplo:**
```python
import pytest
from src.services import TiendaService

def test_comprar_item_exitoso():
    service = TiendaService()
    result = service.comprar_item(user_id, item_id)
    assert result.success == True
    assert result.puntos_gastados == 100
```

**Librerías complementarias:**
- `pytest-asyncio==0.21.1` - Testing de código asíncrono
- `pytest-cov==4.1.0` - Code coverage
- `pytest-mock==3.12.0` - Mocking simplificado
- `faker==20.1.0` - Generación de datos fake
- `factory-boy==3.3.0` - Factories para modelos
- `freezegun==1.4.0` - Mock de datetime

---

### 10. **Utilidades Generales**

#### 10.1 **Rich 14.0+**
**¿Qué es?**  
Librería para output bonito en terminal.

**Uso:**
- 🎨 Logs coloridos
- 📊 Progress bars
- 🖥️ Pretty printing
- 🐛 Debugging mejorado

#### 10.2 **Typer 0.16+**
**¿Qué es?**  
Framework para crear CLIs (Command Line Interfaces).

**Uso:**
- 🔧 Scripts de administración
- 📦 Comandos de deployment
- 🗄️ Gestión de base de datos

#### 10.3 **Jinja2 3.1+**
**¿Qué es?**  
Motor de templates para Python.

**Uso:**
- 📧 Templates de emails HTML
- 📄 Generación de reportes
- 🎨 Renderizado dinámico

**Librerías complementarias:**
- `emoji==2.10.1` - Soporte de emojis
- `Pygments==2.19.2` - Syntax highlighting
- `markdown-it-py==3.0.0` - Parsing de Markdown
- `click==8.2.1` - CLI framework (base de Typer)
- `tqdm==4.67.1` - Progress bars
- `colorama==0.4.6` - Colores en terminal

---

## ⚛️ Frontend Stack

### 1. **React 18.3+**

**¿Qué es?**  
Librería de JavaScript para construir interfaces de usuario.

**Características clave:**
- ✅ **Component-based:** Componentes reutilizables
- ✅ **Virtual DOM:** Renderizado eficiente
- ✅ **Hooks:** useState, useEffect, custom hooks
- ✅ **Ecosystem:** Enorme comunidad y plugins
- ✅ **React Server Components:** SSR y SSG

**¿Por qué React?**
- 🚀 Performance excepcional
- 📚 Documentación extensa
- 🔧 Herramientas de desarrollo robustas
- 👥 Comunidad masiva
- 🎯 Ideal para aplicaciones complejas

**Ejemplo:**
```tsx
import { useState, useEffect } from 'react';

function UserProfile() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch('/api/users/me')
      .then(res => res.json())
      .then(data => setUser(data));
  }, []);
  
  return (
    <div>
      <h1>{user?.nombre}</h1>
      <p>Puntos: {user?.puntos}</p>
    </div>
  );
}
```

**Librerías React populares:**
- `react-router-dom` - Routing
- `react-query` / `@tanstack/react-query` - Data fetching
- `zustand` / `redux` - State management
- `react-hook-form` - Formularios
- `framer-motion` - Animaciones

---

### 2. **TypeScript 5.0+**

**¿Qué es?**  
Superset de JavaScript con tipado estático.

**Características clave:**
- ✅ **Type Safety:** Prevención de bugs en compile-time
- ✅ **IntelliSense:** Autocompletado en IDE
- ✅ **Refactoring:** Refactorización segura
- ✅ **Modern JS:** Todas las features de ES2023+
- ✅ **JSX Support:** Tipado para React components

**¿Por qué TypeScript?**
- 🐛 Menos bugs en producción
- 📝 Código autodocumentado
- 🔧 Mejor experiencia de desarrollo
- 🏢 Estándar en equipos profesionales

**Ejemplo:**
```typescript
interface Usuario {
  id: string;
  nombre: string;
  email: string;
  puntos: number;
}

interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

async function fetchUsuario(id: string): Promise<ApiResponse<Usuario>> {
  const response = await fetch(`/api/usuarios/${id}`);
  return response.json();
}
```

**Ventajas para Acadify:**
- ✅ Type safety entre frontend y backend (schemas compartidos)
- ✅ Detección temprana de errores
- ✅ Mejor mantenibilidad a largo plazo
- ✅ Refactoring seguro

---

### 3. **Vite 5.0+**

**¿Qué es?**  
Build tool de próxima generación para desarrollo frontend.

**Características clave:**
- ⚡ **HMR ultra-rápido:** Hot Module Replacement instantáneo
- 📦 **ESM nativo:** Usa ES modules del navegador
- 🚀 **Build optimizado:** Rollup para producción
- 🔧 **Zero config:** Funciona out-of-the-box
- 🎯 **TypeScript integrado:** Sin configuración extra

**¿Por qué Vite?**
- 🚀 10-100x más rápido que Webpack/CRA
- ⚡ Arranque instantáneo del servidor
- 🔥 HMR sin perder estado
- 📦 Bundle size optimizado automáticamente

**Configuración típica:**
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

**Comparación con alternativas:**

| Feature | Vite | Webpack | Create React App |
|---------|------|---------|------------------|
| **Dev Server Start** | <1s | 10-30s | 15-45s |
| **HMR Speed** | <50ms | 1-3s | 1-5s |
| **Build Speed** | Rápido | Medio | Lento |
| **Config** | Mínima | Compleja | Zero (limitada) |
| **Bundle Size** | Optimizado | Bueno | Grande |

---

### 4. **TailwindCSS 3.4+**

**¿Qué es?**  
Framework CSS utility-first para diseño rápido y consistente.

**Características clave:**
- ✅ **Utility-First:** Clases de utilidad en lugar de CSS custom
- ✅ **Responsive:** Mobile-first design
- ✅ **Customizable:** Configuración completa vía config
- ✅ **Tree-shaking:** Solo CSS usado en producción
- ✅ **Dark mode:** Soporte nativo
- ✅ **JIT mode:** Just-In-Time compilation

**¿Por qué TailwindCSS?**
- 🚀 Desarrollo ultra-rápido
- 📦 Bundle size mínimo en producción
- 🎨 Design system consistente
- 🔧 No más naming de clases CSS
- 📱 Responsive design simplificado

**Ejemplo:**
```tsx
function Button({ children, variant = 'primary' }) {
  const baseClasses = 'px-4 py-2 rounded-lg font-semibold transition-all';
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    danger: 'bg-red-600 hover:bg-red-700 text-white'
  };
  
  return (
    <button className={`${baseClasses} ${variants[variant]}`}>
      {children}
    </button>
  );
}

// Uso
<Button variant="primary">Comprar Item</Button>
```

**Ejemplo responsive:**
```tsx
<div className="
  grid 
  grid-cols-1 
  md:grid-cols-2 
  lg:grid-cols-3 
  gap-4 
  p-4
">
  {/* Contenido */}
</div>
```

**Configuración:**
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#8B5CF6',
        acadify: {
          blue: '#1E40AF',
          purple: '#7C3AED'
        }
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
}
```

**Plugins recomendados:**
- `@tailwindcss/forms` - Estilos para formularios
- `@tailwindcss/typography` - Estilos para contenido
- `@tailwindcss/aspect-ratio` - Aspect ratios
- `tailwindcss-animate` - Animaciones predefinidas

---

### 5. **Librerías Frontend Adicionales**

#### 5.1 **React Router DOM**
**¿Qué es?**  
Routing declarativo para React.

**Ejemplo:**
```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cursos" element={<Cursos />} />
        <Route path="/tienda" element={<Tienda />} />
        <Route path="/perfil" element={<Perfil />} />
      </Routes>
    </BrowserRouter>
  );
}
```

#### 5.2 **TanStack Query (React Query)**
**¿Qué es?**  
Gestión de estado del servidor (API calls, cache, etc.).

**Ejemplo:**
```tsx
import { useQuery } from '@tanstack/react-query';

function MisCursos() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['cursos'],
    queryFn: () => fetch('/api/cursos').then(res => res.json())
  });
  
  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;
  
  return (
    <div>
      {data.cursos.map(curso => (
        <CursoCard key={curso.id} {...curso} />
      ))}
    </div>
  );
}
```

**Ventajas:**
- ✅ Cache automático
- ✅ Refetch en segundo plano
- ✅ Optimistic updates
- ✅ Paginación y infinite scroll

#### 5.3 **Zustand / Redux**
**¿Qué es?**  
State management global.

**Ejemplo Zustand:**
```typescript
import create from 'zustand';

interface AuthStore {
  user: Usuario | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  login: async (email, password) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    set({ user: data.user, token: data.token });
  },
  logout: () => set({ user: null, token: null })
}));
```

#### 5.4 **React Hook Form**
**¿Qué es?**  
Gestión de formularios con validación.

**Ejemplo:**
```tsx
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Mínimo 8 caracteres')
});

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema)
  });
  
  const onSubmit = (data) => {
    console.log(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <p>{errors.email.message}</p>}
      
      <input type="password" {...register('password')} />
      {errors.password && <p>{errors.password.message}</p>}
      
      <button type="submit">Login</button>
    </form>
  );
}
```

#### 5.5 **Framer Motion**
**¿Qué es?**  
Librería de animaciones para React.

**Ejemplo:**
```tsx
import { motion } from 'framer-motion';

function Card({ item }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="bg-white rounded-lg shadow-lg p-6"
    >
      <h3>{item.nombre}</h3>
      <p>{item.precio} puntos</p>
    </motion.div>
  );
}
```

#### 5.6 **Axios / Fetch**
**¿Qué es?**  
Cliente HTTP para requests.

**Ejemplo con interceptors:**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
});

// Request interceptor (agregar token)
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (manejar errores)
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // Logout automático
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### 5.7 **Socket.IO Client**
**¿Qué es?**  
WebSockets para comunicación en tiempo real.

**Ejemplo:**
```tsx
import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

function Chat({ roomId }) {
  const [messages, setMessages] = useState([]);
  const [socket, setSocket] = useState(null);
  
  useEffect(() => {
    const newSocket = io('http://localhost:8000');
    newSocket.emit('join_room', roomId);
    
    newSocket.on('new_message', (message) => {
      setMessages(prev => [...prev, message]);
    });
    
    setSocket(newSocket);
    
    return () => newSocket.close();
  }, [roomId]);
  
  const sendMessage = (text) => {
    socket.emit('send_message', { roomId, text });
  };
  
  return (
    <div>
      {messages.map(msg => (
        <div key={msg.id}>{msg.text}</div>
      ))}
    </div>
  );
}
```

#### 5.8 **Recharts / Chart.js**
**¿Qué es?**  
Librerías de gráficos para visualización de datos.

**Ejemplo:**
```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

function ProgressChart({ data }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <XAxis dataKey="fecha" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="puntos" stroke="#3B82F6" />
    </LineChart>
  );
}
```

#### 5.9 **React Icons**
**¿Qué es?**  
Colección de iconos para React.

**Ejemplo:**
```tsx
import { FaShoppingCart, FaTrophy, FaStar } from 'react-icons/fa';

function IconExample() {
  return (
    <>
      <FaShoppingCart className="text-blue-600 text-2xl" />
      <FaTrophy className="text-yellow-500 text-3xl" />
      <FaStar className="text-purple-600" />
    </>
  );
}
```

---

## 🗄️ Base de Datos

### **PostgreSQL 14+**

**¿Qué es?**  
Sistema de gestión de base de datos relacional open-source.

**Características clave:**
- ✅ **ACID Compliance:** Transacciones seguras
- ✅ **JSONB:** Soporte de datos semi-estructurados
- ✅ **Full-Text Search:** Búsqueda de texto integrada
- ✅ **Extensions:** PostGIS, pg_trgm, uuid-ossp, etc.
- ✅ **Performance:** Excelente para queries complejas
- ✅ **Constraints:** Foreign keys, checks, unique
- ✅ **Triggers:** Automatización de lógica
- ✅ **Views:** Vistas materializadas

**¿Por qué PostgreSQL?**
- 🚀 Performance excepcional
- 🔒 Seguridad robusta
- 📊 Soporte de tipos avanzados (arrays, JSON, etc.)
- 🔧 Extensible con plugins
- 👥 Comunidad activa
- 💰 Open source y gratuito

**Ejemplo de tabla:**
```sql
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Índices para performance
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);
```

**Features usadas en Acadify:**

1. **JSONB para datos flexibles:**
```sql
CREATE TABLE insignias (
    id UUID PRIMARY KEY,
    nombre VARCHAR(100),
    requisitos JSONB,  -- Flexible requirements
    metadata JSONB     -- Additional data
);

-- Query JSONB
SELECT * FROM insignias 
WHERE requisitos->>'tipo' = 'nivel' 
AND (requisitos->>'valor')::int >= 10;
```

2. **Full-Text Search:**
```sql
-- Agregar columna tsvector
ALTER TABLE cursos ADD COLUMN search_vector tsvector;

-- Crear índice
CREATE INDEX idx_cursos_search ON cursos USING GIN(search_vector);

-- Búsqueda full-text
SELECT * FROM cursos 
WHERE search_vector @@ to_tsquery('spanish', 'python | javascript');
```

3. **Triggers para audit:**
```sql
CREATE TRIGGER update_timestamp
BEFORE UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

4. **Partitioning para grandes volúmenes:**
```sql
CREATE TABLE transacciones_puntos (
    id UUID,
    usuario_id UUID,
    cantidad INT,
    fecha DATE
) PARTITION BY RANGE (fecha);

CREATE TABLE transacciones_2025_01 PARTITION OF transacciones_puntos
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

**Extensions usadas:**
- `uuid-ossp` - Generación de UUIDs
- `pg_trgm` - Búsqueda fuzzy (trigram)
- `pgcrypto` - Funciones criptográficas
- `hstore` - Key-value store

---

## 🔧 DevOps y Herramientas

### 1. **Docker**

**¿Qué es?**  
Plataforma de contenedores para empaquetar aplicaciones.

**Uso en Acadify:**
```dockerfile
# Dockerfile backend
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/acadify
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
  
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: acadify
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

### 2. **Git**

**Workflow:**
```bash
# Branches principales
main          # Producción
develop       # Desarrollo
feature/*     # Features nuevas
hotfix/*      # Fixes urgentes

# Ejemplo workflow
git checkout -b feature/panel-admin-badges
git add .
git commit -m "feat: agregar panel admin badges"
git push origin feature/panel-admin-badges
# Pull Request en GitHub
```

---

### 3. **GitHub Actions (CI/CD)**

**Ejemplo pipeline:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deploy commands
```

---

### 4. **Postman / Thunder Client**

**¿Qué es?**  
Cliente de API para testing de endpoints.

**Uso:**
- 🧪 Testing manual de APIs
- 📝 Documentación de endpoints
- 🔄 Colecciones compartidas del equipo
- 🤖 Tests automatizados

---

### 5. **pgAdmin / DBeaver**

**¿Qué es?**  
Herramientas GUI para gestión de PostgreSQL.

**Uso:**
- 🗄️ Explorar estructura de base de datos
- 🔍 Queries SQL
- 📊 Análisis de datos
- 🔧 Mantenimiento de BD

---

## 🌐 Integraciones Externas

### 1. **Google Gemini AI**
- Corrección automática de tareas
- Generación de contenido educativo
- Asistente virtual

### 2. **Email Service (SMTP)**
- SendGrid / Mailgun
- Verificación de email
- Notificaciones

### 3. **Cloud Storage**
- AWS S3 / Google Cloud Storage
- Archivos de tareas
- Imágenes de avatares

### 4. **Payment Gateway** (Futuro)
- Stripe / PayPal
- Compra de coins
- Suscripciones premium

---

## 🎯 Justificación de Decisiones

### ¿Por qué FastAPI sobre Django/Flask?

| Feature | FastAPI | Django | Flask |
|---------|---------|--------|-------|
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Type Safety** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Async Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Auto Docs** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Learning Curve** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ecosystem** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Decisión:** FastAPI por performance y type safety.

---

### ¿Por qué React sobre Vue/Angular?

| Feature | React | Vue | Angular |
|---------|-------|-----|---------|
| **Popularidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ecosystem** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **TypeScript** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Job Market** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**Decisión:** React por ecosystem y job market.

---

### ¿Por qué Vite sobre Webpack/CRA?

**Vite:**
- ✅ 100x más rápido en desarrollo
- ✅ HMR instantáneo
- ✅ Build optimizado automático
- ✅ Zero config

**Webpack:**
- ❌ Lento para proyectos grandes
- ❌ Configuración compleja
- ✅ Maduro y estable

**Decisión:** Vite por velocidad de desarrollo.

---

### ¿Por qué PostgreSQL sobre MySQL/MongoDB?

**PostgreSQL:**
- ✅ JSONB para flexibilidad
- ✅ Full-text search nativo
- ✅ Constraints robustos
- ✅ Extensions poderosas

**MySQL:**
- ❌ Menos features avanzadas
- ✅ Más simple

**MongoDB:**
- ❌ Sin relaciones robustas
- ❌ Difícil para queries complejas

**Decisión:** PostgreSQL por robustez y features.

---

## 📊 Comparativa de Rendimiento

### Backend Performance

| Framework | Requests/sec | Latencia (ms) |
|-----------|--------------|---------------|
| **FastAPI** | 25,000 | 10-20 |
| Django | 10,000 | 30-50 |
| Flask | 15,000 | 20-30 |
| Express.js | 22,000 | 15-25 |

### Frontend Bundle Size

| Tool | Initial Load | Build Time |
|------|--------------|------------|
| **Vite** | 150KB | 30s |
| Webpack | 250KB | 90s |
| CRA | 300KB | 120s |

### Database Performance

| Database | Reads/sec | Writes/sec |
|----------|-----------|------------|
| **PostgreSQL** | 40,000 | 15,000 |
| MySQL | 35,000 | 12,000 |
| MongoDB | 30,000 | 20,000 |

---

## 🔄 Actualizaciones y Versiones

### Policy de Actualizaciones

- **Dependencies:** Actualizar mensualmente
- **Security patches:** Actualizar inmediatamente
- **Major versions:** Evaluar antes de actualizar

### Comando para actualizar:
```bash
# Backend
pip list --outdated
pip install --upgrade <package>

# Frontend
npm outdated
npm update
```

---

## 📚 Recursos de Aprendizaje

### Backend
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

### Frontend
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)

### Database
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/)
- [SQL Performance Tips](https://use-the-index-luke.com/)

---

## 🎯 Conclusión

Acadify utiliza un stack moderno, performante y escalable:

- ✅ **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- ✅ **Frontend:** React + TypeScript + Vite + TailwindCSS
- ✅ **DevOps:** Docker + Git + GitHub Actions
- ✅ **AI:** Google Gemini + OpenAI

Este stack permite:
- 🚀 Desarrollo rápido
- ⚡ Performance excepcional
- 🔧 Mantenibilidad a largo plazo
- 📈 Escalabilidad para millones de usuarios

---

**Última actualización:** 10 de Noviembre de 2025  
**Versión:** 1.0  
**Mantenida por:** Equipo Backend Acadify
