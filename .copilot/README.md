# 🤖 Configuración Copilot Agent - Acadify

> **Sistema de configuración profesional para GitHub Copilot Agent** > **Última actualización**: 12 de noviembre de 2025

---

## 📋 Tabla de Contenidos

- [Introducción](#-introducción)
- [Estructura de Archivos](#-estructura-de-archivos)
- [Cómo Funciona](#-cómo-funciona)
- [Guías de Uso](#-guías-de-uso)
  - [Para Desarrollo General](#1--desarrollo-general)
  - [Para Backend Python/FastAPI](#2--backend-pythonfastapi)
  - [Para Frontend React/TypeScript](#3--frontend-reacttypescript)
  - [Para Mobile React Native/Expo](#4--mobile-react-nativeexpo)
  - [Para Debugging](#5--debugging)
  - [Para Refactoring](#6--refactoring)
- [Activación de Toolsets](#-activación-de-toolsets)
- [Activación de Modes](#-activación-de-modes)
- [MCP Servers Configurados](#-mcp-servers-configurados)
- [Ejemplos de Prompts Efectivos](#-ejemplos-de-prompts-efectivos)
- [Mejores Prácticas](#-mejores-prácticas)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Introducción

Este directorio contiene la **configuración completa** de GitHub Copilot Agent para el proyecto **Acadify**. Los archivos aquí definen:

- **Comportamiento del agente** (cómo piensa, qué principios sigue)
- **Conocimiento del proyecto** (arquitectura, stack, ubicaciones)
- **Herramientas disponibles** (qué puede y no puede hacer)
- **Modos operativos** (diferentes perfiles según el contexto)
- **Guías especializadas** (referencias detalladas por dominio)

**Objetivo**: Que Copilot trabaje como un **desarrollador senior full-stack** que conoce Acadify al dedillo, aplica mejores prácticas, sugiere mejoras proactivamente, y nunca repite código.

---

## 📁 Estructura de Archivos

```
.copilot/
│
├── README.md                       # 👈 Este archivo (guía de uso)
│
├── AGENT_INSTRUCTIONS.md           # 🧠 Instrucciones principales del agente
│   ├── Identidad y rol
│   ├── Principios fundamentales (SOLID, DRY, Type Safety)
│   ├── Conocimiento del proyecto (ubicaciones, comandos)
│   ├── Flujo de trabajo (6 pasos)
│   ├── Convenciones de código (Python/TypeScript)
│   ├── Anti-patrones a evitar
│   ├── Patrones recomendados
│   └── Mejoras proactivas
│
├── TOOLS_CONFIGURATION.md          # 🛠️ Herramientas habilitadas/deshabilitadas
│   ├── Herramientas de edición (read_file, replace_string_in_file, create_file)
│   ├── Herramientas de validación (get_errors, runTests)
│   ├── Herramientas de terminal (run_in_terminal)
│   ├── Python environment (configure_python_environment)
│   ├── Precauciones y limitaciones
│   └── Ejemplos de uso correcto
│
├── MODES_CONFIGURATION.md          # 🎭 Modos operativos especializados
│   ├── Development Mode (default, edita libremente)
│   ├── Review Mode (solo lectura, detecta problemas)
│   ├── Refactor Mode (reestructura código)
│   ├── Debug Mode (investiga bugs)
│   ├── Documentation Mode (genera docs)
│   └── Testing Mode (crea tests)
│
├── prompts/                        # 📚 Guías especializadas de referencia
│   ├── PROJECT_MASTER_GUIDE.md    # Arquitectura general del proyecto
│   ├── BACKEND_GUIDE.md           # Python/FastAPI/SQLAlchemy/Alembic
│   ├── FRONTEND_GUIDE.md          # React/TypeScript/Vite/React Query
│   ├── MOBILE_GUIDE.md            # React Native/Expo/Zustand
│   ├── DATABASE_SCHEMA.md         # Tablas, relaciones, índices
│   ├── GAMIFICATION_GUIDE.md      # Sistema de puntos, logros, rachas
│   ├── COMMUNICATION_GUIDE.md     # WebSockets, chat, videollamadas
│   ├── AVATAR_SYSTEM.md           # SVG customization, cache Redis
│   └── TESTING_GUIDE.md           # Pytest, Vitest, coverage
│
├── modes/                          # 🎭 Archivos .chatmode para VS Code
│   └── (archivos individuales si se crean)
│
└── context/                        # 📦 Contextos reutilizables (próximo)
    ├── API_PATTERNS.md
    ├── COMMON_ERRORS.md
    ├── REFACTOR_RECIPES.md
    └── TESTING_TEMPLATES.md
```

---

## 🔄 Cómo Funciona

### **1. AGENT_INSTRUCTIONS.md - Leído Automáticamente**

Este archivo es **leído al inicio de CADA sesión** de Copilot. Define:

- **Quién es el agente**: "Eres un desarrollador full-stack senior..."
- **Qué principios sigue**: SOLID, DRY, Type Safety First, Testing Obligatorio
- **Qué conoce del proyecto**: Ubicación de archivos clave (main.py, config.py, App.tsx)
- **Cómo debe trabajar**: Flujo de 6 pasos (comprender → analizar → planificar → implementar → revisar → testing)

**No necesitas referenciar este archivo manualmente**, Copilot lo carga automáticamente.

---

### **2. TOOLS_CONFIGURATION.md - Referencia Interna**

Define qué herramientas están habilitadas/deshabilitadas y cómo usarlas:

- ✅ **Habilitadas**: read_file, replace_string_in_file, create_file, get_errors, runTests, run_in_terminal, etc.
- ❌ **Deshabilitadas**: create_new_workspace (proyecto ya existe), install_extension (manual)

Copilot **consulta esta guía internamente** cuando necesita usar una herramienta.

---

### **3. MODES_CONFIGURATION.md - Adaptación por Contexto**

Define 6 modos operativos con comportamientos específicos:

| Mode              | Edita Código  | Corre Tests    | Crea Archivos | Uso Terminal | Propósito                                  |
| ----------------- | ------------- | -------------- | ------------- | ------------ | ------------------------------------------ |
| **Development**   | ✅            | ✅             | ✅            | ✅           | Desarrollo activo de features              |
| **Review**        | ❌            | ❌             | ❌            | ❌           | Code review y análisis de calidad          |
| **Refactor**      | ✅            | ✅ Obligatorio | ❌            | ❌           | Reestructuración sin cambiar funcionalidad |
| **Debug**         | ✅ Quirúrgico | ✅ Obligatorio | ❌            | ✅           | Investigación y fix de bugs                |
| **Documentation** | ✅ Solo docs  | ❌             | ✅ README     | ❌           | Generar/actualizar documentación           |
| **Testing**       | ✅ Solo tests | ✅             | ✅ Test files | ✅           | Crear tests unitarios/integración          |

Copilot **detecta automáticamente** el mode según tu prompt, o puedes **activarlo manualmente** (ver sección [Activación de Modes](#-activación-de-modes)).

---

### **4. prompts/\*.md - Referencias Especializadas**

Guías técnicas detalladas por dominio. Copilot puede:

- **Buscarlas automáticamente** cuando necesita contexto específico
- **Ser referenciadas manualmente** con `#file` en tu prompt

Ejemplo:

```
Implementa el endpoint de crear logro siguiendo las convenciones de #file:.copilot/prompts/BACKEND_GUIDE.md
```

---

## 📖 Guías de Uso

### **1. 🚀 Desarrollo General**

**Objetivo**: Crear o modificar features completas (backend + frontend).

**Toolset Recomendado**: `@acadify-development` o `@acadify-full-stack`

**Prompt Efectivo**:

```
Implementa el sistema de misiones diarias para gamificación:

Backend:
- Modelo Mission en SQLAlchemy
- Service MissionService con lógica de verificación
- Router /api/misiones con endpoints CRUD
- Tests en test_missions.py

Frontend:
- Hook useMissions con React Query
- Componente MissionCard para mostrar misiones
- Página MissionsPage con listado y progreso
- Tests en MissionCard.test.tsx

Sigue las convenciones de AGENT_INSTRUCTIONS.md y aplica SOLID principles.
```

**Flujo Esperado**:

1. Copilot crea todo list con 8 tareas
2. Lee archivos relacionados (modelos similares, servicios existentes)
3. Implementa backend primero (modelo → service → router → tests)
4. Valida con `get_errors` después de cada archivo
5. Corre tests backend: `pytest tests/test_missions.py -v`
6. Implementa frontend (hook → componente → página → tests)
7. Valida con `get_errors` y tests frontend: `vitest run MissionCard.test.tsx`
8. Marca tareas completadas

---

### **2. 🐍 Backend Python/FastAPI**

**Objetivo**: Desarrollo exclusivo de backend (modelos, servicios, endpoints).

**Toolset Recomendado**: `@acadify-backend-only`

**Prompt Efectivo**:

```
Crea el endpoint para actualizar la configuración de proctoring de un curso:

1. Agrega campo `proctoring_config` JSONB a modelo Curso
2. Schema Pydantic ProctoringConfig con validación
3. Endpoint PATCH /api/cursos/{id}/proctoring
4. Servicio CursoService.update_proctoring_config
5. Tests unitarios e integración
6. Migración Alembic

Referencia: #file:.copilot/prompts/BACKEND_GUIDE.md
```

**Herramientas Principales**:

- `configurePythonEnvironment` (automático si detecta Python)
- `getPythonEnvironmentInfo` (verifica paquetes instalados)
- `pylanceRunCodeSnippet` (ejecuta código Python sin terminal)
- `pylanceFileSyntaxErrors` (valida sintaxis antes de guardar)
- `pylanceInvokeRefactoring` (refactors automáticos como remove unused imports)

**Comandos Útiles**:

```bash
# Crear migración Alembic
alembic revision --autogenerate -m "Add proctoring_config to Curso"

# Aplicar migración
alembic upgrade head

# Correr tests específicos
pytest tests/api/test_cursos.py::test_update_proctoring_config -v

# Verificar sintaxis con Ruff
ruff check src/

# Formatear código
ruff format src/
```

---

### **3. ⚛️ Frontend React/TypeScript**

**Objetivo**: Desarrollo exclusivo de frontend (componentes, hooks, páginas).

**Toolset Recomendado**: `@acadify-frontend-only`

**Prompt Efectivo**:

```
Implementa el sistema de notificaciones push en tiempo real:

1. Hook useNotifications con React Query + WebSocket
2. Componente NotificationBell con badge de contador
3. Componente NotificationList con scroll infinito
4. Service notificationService.ts con API calls
5. Integrar Socket.io para updates real-time
6. Tests con Vitest + Testing Library

Referencia: #file:.copilot/prompts/FRONTEND_GUIDE.md
```

**Herramientas Principales**:

- `console-ninja` (runtime logs del browser)
- `runtime-errors` (errores de ejecución React)
- `runtime-logs-by-location` (logs específicos de archivo:línea)
- `runTests` (ejecuta Vitest tests)

**Comandos Útiles**:

```bash
# Iniciar dev server (puerto 5173)
pnpm dev

# Correr tests en watch mode
pnpm test

# Correr tests con coverage
pnpm test:coverage

# Build optimizado
pnpm build

# Lint + fix automático
pnpm lint --fix

# Formatear código
pnpm format
```

**MCP Console Ninja** (ya configurado):

- Ver logs en tiempo real del browser
- Detectar errores React (boundary, hooks)
- Inspeccionar variables en runtime
- Network requests (404, 422, CORS)

---

### **4. 📱 Mobile React Native/Expo**

**Objetivo**: Desarrollo de app móvil (stores, componentes, navegación).

**Toolset Recomendado**: `@acadify-mobile-development`

**Prompt Efectivo**:

```
Implementa la pantalla de perfil de usuario en mobile:

1. Store userProfileStore con Zustand
2. Hook useUserProfile con React Query
3. Componente ProfileScreen con Expo Router
4. Componentes ProfileHeader, ProfileStats, ProfileSettings
5. Navegación desde menu lateral
6. Tests con Jest + Testing Library

Referencia: #file:.copilot/prompts/MOBILE_GUIDE.md
Sigue Clean Architecture del proyecto.
```

**Comandos Útiles**:

```bash
# Iniciar Expo dev server
npm start

# Abrir en Android emulator
npm run android

# Abrir en iOS simulator
npm run ios

# Correr tests
npm test

# Build para producción
eas build --platform all
```

---

### **5. 🐛 Debugging**

**Objetivo**: Investigar y resolver bugs, analizar stack traces.

**Toolset Recomendado**: `@acadify-debug`

**Mode**: Activa **Debug Mode** explícitamente

**Prompt Efectivo**:

```
DEBUG MODE: Hay un error 500 al intentar crear un logro para un usuario.

Stack trace:
```

sqlalchemy.exc.IntegrityError: (psycopg2.errors.NotNullViolation) null value in column "usuario_id" violates not-null constraint

```

Investiga:
1. Revisa el endpoint POST /api/logros/asignar
2. Verifica el servicio LogroService.asignar_logro
3. Revisa el schema LogroAsignarRequest
4. Reproduce el error en test
5. Aplica fix quirúrgico
6. Valida con test

Referencias:
- #file:.copilot/prompts/BACKEND_GUIDE.md (LogroService)
- #file:.copilot/TOOLS_CONFIGURATION.md (debugging workflow)
```

**Herramientas Principales**:

- `runtime-errors` (errores frontend)
- `runtime-logs-by-location` (logs específicos)
- `testFailure` (información de tests fallidos)
- `pylanceFileSyntaxErrors` (errores sintaxis Python)

**Workflow Debug Mode**:

1. Lee error completo (stack trace, línea, archivo)
2. Busca implementación del código afectado
3. Reproduce error en test (crea test si no existe)
4. Identifica causa raíz (no síntoma)
5. Aplica **fix quirúrgico** (mínimo cambio necesario)
6. Valida con test + get_errors
7. No refactoriza ni optimiza (solo fix)

---

### **6. 🔧 Refactoring**

**Objetivo**: Reestructurar código sin cambiar funcionalidad.

**Toolset Recomendado**: `@acadify-refactor`

**Mode**: Activa **Refactor Mode** explícitamente

**Prompt Efectivo**:

```
REFACTOR MODE: El servicio UsuarioService tiene 800 líneas y viola Single Responsibility.

Tareas:
1. Extrae AuthService (login, register, 2FA, JWT)
2. Extrae PerfilService (avatar, configuración, notificaciones)
3. Extrae GamificacionUsuarioService (puntos, rachas, logros)
4. Mantén UsuarioService solo para CRUD básico
5. Actualiza imports en routers
6. Tests obligatorios después de cada extracción

Principios:
- SOLID (Single Responsibility)
- DRY (no duplicar lógica)
- Tests deben pasar sin cambios
```

**Herramientas Principales**:

- `pylanceInvokeRefactoring` (refactors automáticos Pylance)
  - `source.unusedImports` (remover imports no usados)
  - `source.convertImportFormat` (convertir imports absolutos/relativos)
  - `source.fixAll.pylance` (aplicar fixes automáticos)
- `usages` (encontrar todos los usos de una función/clase)
- `runTests` (validar después de cada cambio)

**Refactors Comunes**:

1. **Extraer función**:

```python
# Antes (código duplicado)
def crear_usuario(data):
    password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())
    # ...

def actualizar_password(user_id, new_password):
    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    # ...

# Después (DRY)
def _hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def crear_usuario(data):
    password_hash = _hash_password(data.password)
    # ...

def actualizar_password(user_id, new_password):
    password_hash = _hash_password(new_password)
    # ...
```

2. **Extraer custom hook React**:

```typescript
// Antes (lógica duplicada en componentes)
function ProfilePage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get("/api/usuarios/me")
      .then((res) => setUser(res.data))
      .finally(() => setLoading(false));
  }, []);
  // ...
}

// Después (hook reutilizable)
function useCurrentUser() {
  return useQuery({
    queryKey: ["users", "me"],
    queryFn: () => apiClient.get("/api/usuarios/me").then((res) => res.data),
  });
}

function ProfilePage() {
  const { data: user, isLoading } = useCurrentUser();
  // ...
}
```

---

## 🛠️ Activación de Toolsets

Los **toolsets** son conjuntos predefinidos de herramientas. Se activan manualmente en el chat:

### **Comando**:

```
/tools @<toolset-name>
```

### **Toolsets Disponibles**:

| Toolset                       | Uso                       | Herramientas Clave                                      |
| ----------------------------- | ------------------------- | ------------------------------------------------------- |
| `@acadify-development`        | Desarrollo general        | edit, problems, runTests, runCommands, todos            |
| `@acadify-backend-only`       | Backend Python/FastAPI    | + configurePythonEnvironment, pylance\*                 |
| `@acadify-frontend-only`      | Frontend React/TypeScript | + console-ninja, runtime-logs                           |
| `@acadify-mobile-development` | Mobile React Native/Expo  | + runtime-logs, console-ninja                           |
| `@acadify-debug`              | Debugging                 | + testFailure, runtime-errors, runtime-logs-by-location |
| `@acadify-refactor`           | Refactoring               | + usages, pylanceInvokeRefactoring                      |
| `@acadify-testing`            | Testing                   | + runTests, testFailure, configurePythonEnvironment     |
| `@acadify-review`             | Code review (read-only)   | problems, search, usages, pylanceFileSyntaxErrors       |
| `@acadify-documentation`      | Documentación             | edit, search, pylanceDocuments                          |
| `@acadify-performance`        | Optimización              | + runtime-logs, console-ninja, usages                   |
| `@acadify-security`           | Auditoría seguridad       | problems, search, usages, pylanceFileSyntaxErrors       |
| `@acadify-database`           | DB y migraciones          | edit, runCommands, pylanceRunCodeSnippet                |
| `@acadify-api-endpoints`      | Routers FastAPI           | edit, problems, search, usages                          |
| `@acadify-gamification`       | Sistema gamificación      | edit, problems, runTests, usages                        |
| `@acadify-communication`      | Chat/WebSockets/WebRTC    | edit, problems, runTests, runtime-logs                  |
| `@acadify-avatar-system`      | Avatares SVG              | edit, problems, runTests, search                        |
| `@acadify-git-operations`     | Git                       | problems, changes, runCommands, search                  |
| `@acadify-ci-cd`              | CI/CD                     | problems, runTests, runCommands, changes                |
| `@acadify-full-stack`         | TODO habilitado           | Todas las herramientas                                  |
| `@acadify-minimal`            | Solo lectura              | problems, search                                        |
| `@acadify-quick-fix`          | Ediciones rápidas         | edit, problems                                          |

### **Ejemplo de Activación**:

```
/tools @acadify-backend-only

Ahora crea el servicio de notificaciones push con:
1. NotificacionService con método enviar_push
2. Integración con Firebase Cloud Messaging
3. Tests unitarios
```

### **Auto-selección**:

Copilot puede **detectar automáticamente** el toolset apropiado si mencionas:

- "backend" → `@acadify-backend-only`
- "frontend" → `@acadify-frontend-only`
- "mobile" → `@acadify-mobile-development`
- "debug" → `@acadify-debug`
- "refactor" → `@acadify-refactor`
- "tests" → `@acadify-testing`

---

## 🎭 Activación de Modes

Los **modes** ajustan el comportamiento del agente. Se activan **explícitamente** en el prompt:

### **Método 1: Prefijo en Prompt**

```
DEBUG MODE: Investiga por qué el login 2FA falla...
```

```
REFACTOR MODE: Extrae la lógica de cache Redis a un servicio separado...
```

```
REVIEW MODE: Analiza el código de UsuarioService y detecta problemas...
```

### **Método 2: Comando Explícito**

```
Activa TESTING MODE.

Crea tests para el servicio AuthService...
```

### **Detección Automática**:

Copilot puede detectar el mode por contexto:

| Tu Prompt Contiene                              | Mode Activado          |
| ----------------------------------------------- | ---------------------- |
| "implementa", "crea", "agrega"                  | **Development Mode**   |
| "revisa", "analiza", "detecta problemas"        | **Review Mode**        |
| "refactoriza", "extrae", "reestructura"         | **Refactor Mode**      |
| "hay un error", "debug", "investiga bug"        | **Debug Mode**         |
| "documenta", "genera JSDoc", "actualiza README" | **Documentation Mode** |
| "crea tests", "mejora coverage", "testing"      | **Testing Mode**       |

---

## 🔌 MCP Servers Configurados

Los **MCP (Model Context Protocol) Servers** extienden las capacidades de Copilot con herramientas especializadas.

### **Configuración**: `.vscode/mcp-settings.json`

### **MCPs Activos**:

#### **1. 🌐 Chrome DevTools MCP** (✅ Configurado)

**Propósito**: Debugging frontend en tiempo real.

**Archivo**: `MCP-CHROME-SETUP.md`

**Capacidades**:

- Ver logs de consola del browser
- Inspeccionar Network (requests, errors 404/422)
- Evaluar JavaScript en runtime
- Inspeccionar Storage (localStorage, cookies)
- Tomar screenshots
- Medir performance

**Cómo Usar**:

```bash
# Iniciar Chrome con debugging
./start-chrome-debug.sh

# Luego en Copilot:
Revisa los logs de consola en el browser y dime qué errores hay.
```

---

#### **2. 🐍 Pylance MCP** (✅ Built-in)

**Propósito**: Análisis avanzado de código Python.

**Herramientas**:

- `pylanceRunCodeSnippet` - Ejecutar código Python sin terminal
- `pylanceFileSyntaxErrors` - Validar sintaxis
- `pylanceImports` - Analizar imports
- `pylanceInvokeRefactoring` - Refactors automáticos
- `pylanceSettings` - Ver configuración Pylance
- `pylanceWorkspaceUserFiles` - Listar archivos Python del proyecto
- `pylanceDocuments` - Buscar documentación

**Ejemplo**:

```
Usa pylanceRunCodeSnippet para verificar que la función _hash_password funciona correctamente.
```

---

#### **3. 🕹️ Console Ninja MCP** (✅ Configurado)

**Propósito**: Runtime logs y debugging (complementa Chrome DevTools).

**Herramientas**:

- `runtime-errors` - Errores de ejecución
- `runtime-logs` - Logs completos
- `runtime-logs-and-errors` - Ambos
- `runtime-logs-by-location` - Logs específicos de archivo:línea

**Ejemplo**:

```
Muéstrame los runtime logs del archivo src/components/AuthForm.tsx línea 45.
```

---

### **MCPs Recomendados para Instalar**:

#### **4. 🗄️ PostgreSQL MCP** (Próximo)

**Propósito**: Queries SQL, inspección de schema, análisis de performance.

**Comandos**:

```bash
# Instalar
npm install -g @modelcontextprotocol/server-postgres
```

**Configuración en `.vscode/mcp-settings.json`**:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/acadify"
      }
    }
  }
}
```

**Uso**:

```
Ejecuta query SQL para ver todos los usuarios con rachas activas mayores a 7 días.
```

---

#### **5. 📁 Filesystem MCP** (Próximo)

**Propósito**: Operaciones avanzadas de archivos (watch, templating, bulk operations).

**Instalación**:

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Uso**:

```
Crea 10 archivos de test siguiendo el template test_*.py para todos los servicios en src/services/.
```

---

#### **6. 🧠 Sequential Thinking MCP** (Próximo)

**Propósito**: Razonamiento paso a paso para problemas complejos.

**Instalación**:

```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
```

**Uso**:

```
Usa sequential thinking para diseñar la arquitectura del sistema de misiones diarias considerando:
- Modelos de BD necesarios
- Servicios y lógica de negocio
- Endpoints de API
- Frontend hooks y componentes
- Testing strategy
```

---

#### **7. 🔀 Git MCP** (Próximo)

**Propósito**: Operaciones avanzadas de Git (diffs semánticos, blame, cherry-pick).

**Instalación**:

```bash
npm install -g @modelcontextprotocol/server-git
```

**Uso**:

```
Muéstrame el git blame del archivo src/services/auth_service.py y encuentra quién implementó la autenticación 2FA.
```

---

## 💡 Ejemplos de Prompts Efectivos

### **❌ Prompt Malo (Vago, Sin Contexto)**

```
Agrega notificaciones.
```

**Problemas**:

- No especifica backend/frontend/ambos
- No define tipo de notificaciones (push, email, in-app)
- No menciona requisitos técnicos
- Copilot tendrá que adivinar y podría equivocarse

---

### **✅ Prompt Bueno (Específico, Con Contexto)**

```
Implementa sistema de notificaciones push in-app:

Backend (FastAPI):
1. Modelo Notificacion en SQLAlchemy con campos:
   - id, usuario_id, tipo, titulo, mensaje, leida, fecha_creacion
2. Service NotificacionService con métodos:
   - crear_notificacion(usuario_id, tipo, titulo, mensaje)
   - marcar_leida(notificacion_id)
   - obtener_no_leidas(usuario_id)
3. Router /api/notificaciones con endpoints:
   - GET /api/notificaciones/me (mis notificaciones)
   - PATCH /api/notificaciones/{id}/leer
   - DELETE /api/notificaciones/{id}
4. Tests en test_notificaciones.py

Frontend (React):
1. Hook useNotificaciones con React Query
2. Componente NotificationBell con badge contador
3. Componente NotificationDropdown con lista scrolleable
4. Service notificationService.ts
5. Tests en Notification.test.tsx

Referencias:
- #file:.copilot/prompts/BACKEND_GUIDE.md (estructura de servicios)
- #file:.copilot/prompts/FRONTEND_GUIDE.md (custom hooks React Query)

Sigue AGENT_INSTRUCTIONS.md: SOLID, DRY, type safety, tests obligatorios.
```

**Ventajas**:

- Scope claro (backend + frontend)
- Modelos y campos definidos
- Servicios y métodos especificados
- Endpoints de API detallados
- Tests requeridos explícitamente
- Referencias a guías para contexto
- Menciona principios a seguir

---

### **Más Ejemplos**:

#### **Backend - Endpoint con Validación**

```
Crea endpoint POST /api/cursos/{id}/estudiantes para inscribir estudiantes en un curso.

Requisitos:
1. Schema Pydantic InscripcionRequest con:
   - estudiante_id: int
   - rol_estudiante: RolEstudiante (enum: REGULAR, OYENTE, MONITOR)
2. Validar que:
   - Curso existe y está activo
   - Usuario es docente del curso
   - Estudiante no está ya inscrito
   - Cupo disponible (max 50 estudiantes)
3. Crear registro en tabla inscripciones
4. Enviar notificación al estudiante
5. Tests con casos:
   - Inscripción exitosa
   - Curso sin cupo
   - Estudiante ya inscrito
   - Usuario sin permisos

Referencia: #file:.copilot/prompts/BACKEND_GUIDE.md (endpoint patterns)
```

---

#### **Frontend - Componente con Animaciones**

````
Crea componente AchievementCard para mostrar logros desbloqueados.

UI/UX:
- Card con imagen del logro (SVG)
- Título y descripción
- Progress bar si está en progreso
- Badge con fecha de desbloqueo si completado
- Animación de "unlock" con Framer Motion cuando se completa
- Hover effect con scale y sombra

Props:
```typescript
interface AchievementCardProps {
  logro: Logro;
  progreso?: number; // 0-100
  completado: boolean;
  fechaDesbloqueo?: Date;
  onClick?: () => void;
}
````

Animaciones Framer Motion:

- Fade in al montar
- Scale 1.05 en hover
- Shake + confetti al desbloquear (usar react-confetti-explosion)

Tests (Vitest + Testing Library):

- Render con logro completado
- Render con logro en progreso
- Click handler
- Animación de unlock

Referencia: #file:.copilot/prompts/FRONTEND_GUIDE.md (Framer Motion patterns)

```

---

#### **Refactoring - Extraer Servicio**
```

REFACTOR MODE

El archivo src/services/usuario_service.py tiene 950 líneas y viola Single Responsibility.

Tarea: Extraer lógica de gamificación a nuevo servicio.

1. Crear src/services/gamificacion_service.py
2. Mover estos métodos de UsuarioService:
   - calcular_puntos_actividad
   - actualizar_racha
   - verificar_logros
   - asignar_logro
   - obtener_estadisticas_gamificacion
3. GamificacionService debe inyectar CRUDUsuario, CRUDPuntos, CRUDLogro
4. Actualizar imports en:
   - src/api/routers/usuarios.py
   - src/api/routers/gamificacion.py
5. Tests de UsuarioService y GamificacionService deben pasar sin cambios

Principios:

- SOLID (Single Responsibility)
- Dependency Injection
- No duplicar código
- Tests son la especificación (deben pasar idénticos)

Referencia: #file:.copilot/prompts/BACKEND_GUIDE.md (Service Layer pattern)

```

---

#### **Debugging - Error Específico**
```

DEBUG MODE

Error al intentar actualizar avatar de usuario:

```
Traceback (most recent call last):
  File "src/services/avatar_service.py", line 87, in actualizar_avatar
    svg_content = self._generar_svg(componentes)
  File "src/services/avatar_service.py", line 142, in _generar_svg
    layer = self._cargar_asset(componente.categoria, componente.item_id)
  File "src/services/avatar_service.py", line 156, in _cargar_asset
    with open(asset_path, 'r') as f:
FileNotFoundError: [Errno 2] No such file or directory: '/static/avatares/hair/hair_long_01.svg'
```

Reproduce en test:

1. Test que intente actualizar avatar con hair_long_01
2. Verifica que el archivo existe en el filesystem
3. Verifica la configuración de AVATAR_ASSETS_PATH en config.py
4. Si el archivo existe, verifica permisos de lectura

Si el archivo no existe:

- Verifica que todos los assets en DB existan en filesystem
- Crea script de validación de assets

Fix quirúrgico: no refactorices, solo arregla el error.

Referencia: #file:.copilot/prompts/AVATAR_SYSTEM.md (estructura de assets)

```

---

## 🎯 Mejores Prácticas

### **1. Sé Específico en tus Prompts**
❌ "Agrega validación"
✅ "Agrega validación Pydantic en InscripcionRequest que verifique que email sea válido y password tenga mínimo 8 caracteres con al menos una mayúscula"

### **2. Referencia Guías Relevantes**
```

Implementa autenticación 2FA siguiendo las convenciones de:

- #file:.copilot/prompts/BACKEND_GUIDE.md (AuthService)
- #file:.copilot/AGENT_INSTRUCTIONS.md (security best practices)

```

### **3. Especifica Tests Requeridos**
Siempre incluye casos de test:
```

Tests obligatorios:

- Caso exitoso
- Usuario no existe (404)
- Credenciales inválidas (401)
- Token expirado (401)

```

### **4. Menciona Principios Arquitectónicos**
```

Sigue SOLID principles:

- Single Responsibility: un servicio por dominio
- Dependency Injection: inyecta CRUDs en servicios
- Interface Segregation: schemas específicos por operación

```

### **5. Divide Tareas Grandes**
Si la tarea es muy grande, divídela:
```

Paso 1: Implementa solo el backend del sistema de misiones.
[espera confirmación]

Paso 2: Implementa el frontend del sistema de misiones.

```

### **6. Valida Después de Cada Cambio**
```

Después de cada archivo creado/editado:

1. Ejecuta get_errors para validar sintaxis
2. Corre tests relevantes
3. Solo entonces continúa con el siguiente archivo

```

### **7. Usa Toolsets Específicos**
No uses `@acadify-full-stack` si solo necesitas backend:
```

/tools @acadify-backend-only

Implementa endpoint de crear curso...

```

### **8. Activa Modes Explícitamente para Tareas Especiales**
```

REFACTOR MODE
[tu tarea de refactoring]

DEBUG MODE
[descripción del bug]

TESTING MODE
[qué tests crear]

```

---

## 🚨 Troubleshooting

### **Problema: Copilot no lee AGENT_INSTRUCTIONS.md**
**Solución**:
- Reinicia VS Code completamente
- Verifica que el archivo esté en `.copilot/AGENT_INSTRUCTIONS.md` (no `.github/copilot-instructions.md`)
- En Windows, verifica que la extensión sea `.md` no `.md.txt`

---

### **Problema: Toolset no se activa**
**Solución**:
```

# Verifica sintaxis en TOOLS.toolsets.jsonc

# Debe ser JSON válido con comentarios

# Activa manualmente con /tools

/tools @acadify-development

````

---

### **Problema: MCP Chrome DevTools no conecta**
**Solución**:
```bash
# Verifica que Chrome esté corriendo con debugging
curl http://localhost:9222/json/version

# Reinicia Chrome con el script
./start-chrome-debug.sh

# Reinicia VS Code
````

Referencia: `MCP-CHROME-SETUP.md` sección Troubleshooting

---

### **Problema: Pylance MCP no aparece**

**Solución**:

- Pylance es built-in, no requiere instalación
- Verifica que Python extension esté instalada
- Configura Python environment primero:

```
Configura el Python environment para el backend.
```

---

### **Problema: Copilot repite código**

**Solución**:

```
Detente. Antes de continuar:
1. Busca si ya existe una función similar con semantic_search
2. Si existe, reutilízala en lugar de duplicar
3. Si no existe, créala genérica y reutilizable

Principio DRY en AGENT_INSTRUCTIONS.md.
```

---

### **Problema: Tests fallan después de refactoring**

**Solución**:

```
REFACTOR MODE

Los tests fallan porque cambiaste los imports.

Workflow correcto:
1. Corre tests ANTES del refactor (baseline)
2. Refactoriza el código
3. Actualiza imports en tests
4. Corre tests DESPUÉS
5. Si fallan, revierte y refactoriza de nuevo

Tests son la especificación: deben pasar idénticos.
```

---

### **Problema: Copilot no encuentra archivos**

**Solución**:

```
# Usa rutas absolutas desde la raíz del workspace
/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/src/...

# O rutas relativas desde el workspace root
backend/src/...
frontend/src/...
```

---

### **Problema: Ediciones masivas fallan**

**Solución**:

```
Divide la tarea en ediciones pequeñas:

En lugar de:
"Refactoriza todo UsuarioService"

Usa:
"Paso 1: Extrae solo AuthService de UsuarioService"
[espera]
"Paso 2: Extrae solo PerfilService de UsuarioService"
[espera]
...
```

---

## 📚 Referencias

- **Arquitectura General**: `.copilot/prompts/PROJECT_MASTER_GUIDE.md`
- **Backend Python/FastAPI**: `.copilot/prompts/BACKEND_GUIDE.md`
- **Frontend React/TypeScript**: `.copilot/prompts/FRONTEND_GUIDE.md`
- **Mobile React Native/Expo**: `.copilot/prompts/MOBILE_GUIDE.md`
- **Comportamiento del Agente**: `.copilot/AGENT_INSTRUCTIONS.md`
- **Herramientas Disponibles**: `.copilot/TOOLS_CONFIGURATION.md`
- **Modos Operativos**: `.copilot/MODES_CONFIGURATION.md`
- **Chrome DevTools MCP**: `MCP-CHROME-SETUP.md`
- **Toolsets Configurados**: `~/.config/Code/User/prompts/TOOLS.toolsets.jsonc`

---

## 🎓 Próximos Pasos

1. **Lee** `AGENT_INSTRUCTIONS.md` para entender el comportamiento del agente
2. **Familiarízate** con los toolsets en `TOOLS.toolsets.jsonc`
3. **Prueba** un prompt simple siguiendo los ejemplos de arriba
4. **Explora** las guías especializadas en `prompts/` según tu necesidad
5. **Configura** MCP servers adicionales (PostgreSQL, Filesystem, etc.)
6. **Refina** tus prompts iterativamente para mejores resultados

---

## 🚀 ¡Listo para Volar!

Con esta configuración, GitHub Copilot Agent:

✅ **Conoce Acadify** al dedillo (arquitectura, stack, ubicaciones)
✅ **Aplica mejores prácticas** (SOLID, DRY, Type Safety)
✅ **Sugiere mejoras** proactivamente
✅ **Nunca repite código** (busca antes de crear)
✅ **Valida automáticamente** (get_errors, runTests)
✅ **Trabaja como un senior** (profesional, riguroso, proactivo)

**¡Rómpela desarrollando! 🔥**

---

**Última actualización**: 12 de noviembre de 2025
**Versión**: 1.0.0
**Mantenedor**: Equipo Acadify
