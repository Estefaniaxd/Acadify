# 🚀 Configuración Completa de Copilot Agent - Acadify

> **Documento maestro de configuración profesional** > **Fecha**: 12 de noviembre de 2025
> **Estado**: ✅ Configuración base completada

---

## 📋 ¿Qué se ha Configurado?

### ✅ **Archivos Creados/Configurados**

| Archivo                                            | Propósito                            | Estado         |
| -------------------------------------------------- | ------------------------------------ | -------------- |
| `.copilot/README.md`                               | Guía completa de uso (9,500+ líneas) | ✅ Creado      |
| `.copilot/AGENT_INSTRUCTIONS.md`                   | Comportamiento del agente            | ✅ Existente   |
| `.copilot/TOOLS_CONFIGURATION.md`                  | Herramientas habilitadas             | ✅ Existente   |
| `.copilot/MODES_CONFIGURATION.md`                  | Modos operativos                     | ✅ Existente   |
| `.copilot/prompts/PROJECT_MASTER_GUIDE.md`         | Arquitectura general                 | ✅ Existente   |
| `.copilot/prompts/BACKEND_GUIDE.md`                | Guía backend Python/FastAPI          | ✅ Existente   |
| `.copilot/prompts/FRONTEND_GUIDE.md`               | Guía frontend React/TypeScript       | ✅ Existente   |
| `.github/copilot-instructions.md`                  | Autocompletado inteligente           | ✅ Creado      |
| `.vscode/settings.json`                            | Settings VS Code optimizados         | ✅ Mejorado    |
| `~/.config/Code/User/prompts/TOOLS.toolsets.jsonc` | 20 toolsets especializados           | ✅ Configurado |

---

## 🤖 Cómo Funciona la Configuración

### **1. Archivos Leídos Automáticamente**

Estos archivos son **cargados por Copilot al inicio de cada sesión**:

#### **`.copilot/AGENT_INSTRUCTIONS.md`**

- Define la **identidad** del agente: "Desarrollador full-stack senior"
- Establece **principios**: SOLID, DRY, Type Safety First
- Conoce **ubicaciones** de archivos clave
- Sigue **flujo de trabajo** de 6 pasos
- Aplica **convenciones** de código (snake_case Python, camelCase TS)

**No necesitas mencionarlo**, Copilot lo lee automáticamente.

---

#### **`.github/copilot-instructions.md`**

- Usado por el **autocompletado inteligente** (inline suggestions)
- Define **contexto del proyecto** (stack, estructura, convenciones)
- Proporciona **ejemplos de código** (SQLAlchemy models, React hooks, Pydantic schemas)
- **No es para chat**, es para sugerencias mientras escribes

---

### **2. Archivos de Referencia (Consultados Cuando Necesario)**

Copilot **busca automáticamente** o puedes **referenciar manualmente**:

#### **`.copilot/prompts/*.md`**

Guías técnicas especializadas:

- **PROJECT_MASTER_GUIDE.md**: Arquitectura completa, stack, comandos
- **BACKEND_GUIDE.md**: Modelos SQLAlchemy, Services, CRUD, Routers
- **FRONTEND_GUIDE.md**: Design System, Custom Hooks, API Services, Routing

**Cómo referenciar**:

```
Implementa el endpoint siguiendo las convenciones de #file:.copilot/prompts/BACKEND_GUIDE.md
```

---

#### **`.copilot/TOOLS_CONFIGURATION.md`**

Guía de **herramientas disponibles**:

- ✅ Habilitadas: read_file, replace_string_in_file, get_errors, runTests, etc.
- ❌ Deshabilitadas: create_new_workspace, install_extension
- Precauciones y limitaciones
- Checklist pre/post acción

Copilot consulta esta guía internamente cuando usa herramientas.

---

#### **`.copilot/MODES_CONFIGURATION.md`**

Define **6 modos operativos**:

| Mode              | Comportamiento                   | Activación                  |
| ----------------- | -------------------------------- | --------------------------- |
| **Development**   | Edita, crea, corre tests         | Default (o "Implementa...") |
| **Review**        | Solo lectura, detecta problemas  | "Revisa código..."          |
| **Refactor**      | Reestructura, tests obligatorios | "Refactoriza..."            |
| **Debug**         | Investiga bugs, fix quirúrgico   | "DEBUG MODE: ..."           |
| **Documentation** | Genera docs, no lógica           | "Documenta..."              |
| **Testing**       | Crea tests, coverage >80%        | "Crea tests..."             |

**Cómo activar**:

```
DEBUG MODE: Hay un error al crear logro...
```

---

### **3. Toolsets (Conjuntos de Herramientas)**

Configurados en `~/.config/Code/User/prompts/TOOLS.toolsets.jsonc`

**20 toolsets especializados** para diferentes escenarios:

```jsonc
{
  "acadify-development": { ... },       // Desarrollo general
  "acadify-backend-only": { ... },      // Solo backend Python/FastAPI
  "acadify-frontend-only": { ... },     // Solo frontend React/TS
  "acadify-mobile-development": { ... }, // Mobile React Native/Expo
  "acadify-debug": { ... },             // Debugging con Console Ninja
  "acadify-refactor": { ... },          // Refactoring con tests
  "acadify-testing": { ... },           // Testing Pytest/Vitest
  "acadify-gamification": { ... },      // Sistema gamificación
  "acadify-communication": { ... },     // Chat/WebSockets/WebRTC
  "acadify-database": { ... },          // Migraciones Alembic
  // ... 10 más
}
```

**Cómo activar**:

```
/tools @acadify-backend-only

Ahora implementa el servicio de notificaciones...
```

**Selección automática**: Si dices "backend" o "frontend", Copilot puede autoseleccionar.

---

### **4. VS Code Settings (`.vscode/settings.json`)**

Configuración **workspace-specific** que optimiza el IDE:

#### **Python**

- **Pylance**: Type checking standard, inlay hints
- **Ruff**: Linting + formatting automático
- **Pytest**: Auto-discovery de tests
- **Python path**: `backend/.venv/bin/python`

#### **TypeScript/JavaScript**

- **ESLint**: Auto-fix on save
- **Prettier**: Formatting automático
- **TypeScript Server**: Max memory 4GB
- **Inlay hints**: Tipos de parámetros, retornos

#### **TailwindCSS**

- Emmet completions
- Class regex para `cva()`, `cx()`

#### **GitHub Copilot**

- Habilitado para Python, TS, JS, React
- Locale español
- Auto-completions + code actions

#### **Terminal**

- Shell por defecto: fish (Linux)
- PYTHONPATH automático a `backend/src`

#### **Explorer**

- File nesting (tests con archivos fuente)
- Oculta `__pycache__`, `node_modules`, `dist`, etc.

---

## 🔌 MCP Servers Configurados

### **¿Qué son los MCP Servers?**

**Model Context Protocol (MCP) Servers** extienden las capacidades de Copilot con **herramientas especializadas** externas.

---

### **✅ MCPs Actualmente Activos**

#### **1. 🌐 Chrome DevTools MCP**

**Estado**: ✅ Configurado (ver `MCP-CHROME-SETUP.md`)

**Propósito**: Debugging frontend en tiempo real

**Capacidades**:

- Ver logs de consola del browser
- Inspeccionar Network (404, 422, CORS)
- Evaluar JavaScript en runtime
- Inspeccionar Storage (localStorage, cookies)
- Tomar screenshots
- Medir performance

**Archivo**: `.vscode/mcp-settings.json`

**Cómo usar**:

```bash
# 1. Iniciar Chrome con debugging
./start-chrome-debug.sh

# 2. En Copilot chat:
Muéstrame los logs de consola del browser y detecta errores.
```

---

#### **2. 🐍 Pylance MCP**

**Estado**: ✅ Built-in (parte de Python extension)

**Propósito**: Análisis avanzado de código Python

**Herramientas**:

- `pylanceRunCodeSnippet` - Ejecutar código Python sin terminal
- `pylanceFileSyntaxErrors` - Validar sintaxis
- `pylanceImports` - Analizar imports
- `pylanceInvokeRefactoring` - Refactors automáticos
  - `source.unusedImports`
  - `source.convertImportFormat`
  - `source.fixAll.pylance`
- `pylanceSettings` - Ver configuración
- `pylanceWorkspaceUserFiles` - Listar archivos Python
- `pylanceDocuments` - Buscar documentación

**Cómo usar**:

```
Usa pylanceRunCodeSnippet para verificar que la función _hash_password funciona correctamente.
```

---

#### **3. 🕹️ Console Ninja MCP**

**Estado**: ✅ Configurado

**Propósito**: Runtime logs y debugging (complementa Chrome DevTools)

**Herramientas**:

- `runtime-errors` - Errores de ejecución
- `runtime-logs` - Logs completos
- `runtime-logs-and-errors` - Ambos
- `runtime-logs-by-location` - Logs específicos de archivo:línea

**Cómo usar**:

```
Muéstrame los runtime logs del archivo src/components/AuthForm.tsx línea 45.
```

---

### **🔜 MCPs Recomendados para Instalar**

#### **4. 🗄️ PostgreSQL MCP**

**Propósito**: Queries SQL directas, inspección de schema

**Instalación**:

```bash
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
Ejecuta query SQL para ver todos los usuarios con rachas activas > 7 días.

SELECT u.id, u.nombre, r.dias_consecutivos
FROM usuarios u
JOIN rachas_usuario r ON u.id = r.usuario_id
WHERE r.activa = true AND r.dias_consecutivos > 7;
```

**Capacidades**:

- Ejecutar queries SELECT/INSERT/UPDATE/DELETE
- Inspeccionar schema (tablas, columnas, tipos, constraints)
- Analizar índices y performance
- Ver estadísticas de tablas
- Ejecutar EXPLAIN para optimización

---

#### **5. 📁 Filesystem MCP**

**Propósito**: Operaciones avanzadas de archivos (watch, bulk, templating)

**Instalación**:

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Configuración**:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    }
  }
}
```

**Uso**:

````
Crea 10 archivos de test siguiendo el template test_*.py para todos los servicios en src/services/:

- test_auth_service.py
- test_institucion_service.py
- test_gamificacion_service.py
- ...

Usa el template:
```python
import pytest
from src.services.{service_name} import {ServiceClass}

@pytest.fixture
def service(db):
    return {ServiceClass}(db)

def test_{service_name}_basic(service):
    pass
````

````

**Capacidades**:
- Watch archivos (detectar cambios automáticamente)
- Bulk operations (crear/editar múltiples archivos)
- Templating (scaffolding con plantillas)
- File tree manipulation

---

#### **6. 🔀 Git MCP**
**Propósito**: Operaciones avanzadas de Git

**Instalación**:
```bash
npm install -g @modelcontextprotocol/server-git
````

**Configuración**:

```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git", "${workspaceFolder}"]
    }
  }
}
```

**Uso**:

```
Muéstrame el git blame del archivo src/services/auth_service.py y encuentra quién implementó la autenticación 2FA.
```

**Capacidades**:

- Git blame (quién cambió qué línea)
- Git log con búsqueda semántica
- Diffs semánticos (cambios lógicos vs sintácticos)
- Cherry-pick automático
- Stash management
- Branch analysis

---

#### **7. 🧠 Sequential Thinking MCP**

**Propósito**: Razonamiento paso a paso para problemas complejos

**Instalación**:

```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
```

**Configuración**:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

**Uso**:

```
Usa sequential thinking para diseñar la arquitectura del sistema de misiones diarias considerando:

1. Modelos de BD necesarios
2. Servicios y lógica de negocio
3. Endpoints de API
4. Frontend hooks y componentes
5. Testing strategy
6. Performance y cache

Piensa paso a paso y explica cada decisión arquitectónica.
```

**Capacidades**:

- Razonamiento estructurado (paso a paso)
- Análisis de trade-offs
- Diseño de arquitectura
- Debugging complejo
- Refactoring grandes

---

#### **8. 📊 Memoria MCP** (Próximo)

**Propósito**: Persistir contexto entre sesiones

**Instalación**:

```bash
npm install -g @modelcontextprotocol/server-memory
```

**Uso**:

```
Guarda en memoria que el sistema de gamificación usa el patrón Strategy para calcular puntos, con multiplicadores por tipo de actividad.
```

**Capacidades**:

- Guardar decisiones arquitectónicas
- Recordar patrones usados
- Contexto de largo plazo
- Preferencias del proyecto

---

## 🎯 Cómo Instalar MCPs Adicionales

### **Paso 1: Instalar el MCP globalmente**

```bash
npm install -g @modelcontextprotocol/server-<nombre>
```

### **Paso 2: Configurar en `.vscode/mcp-settings.json`**

```json
{
  "mcpServers": {
    "nombre-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-<nombre>"],
      "env": {
        "VAR_OPCIONAL": "valor"
      }
    }
  }
}
```

### **Paso 3: Reiniciar VS Code**

```
Ctrl+Shift+P → "Reload Window"
```

### **Paso 4: Verificar en Copilot Chat**

```
Verifica que el MCP <nombre> esté activo y muéstrame sus capacidades.
```

---

## 📊 Resumen de Configuración Actual

### **Archivos de Configuración**

| Componente             | Archivos        | Total Líneas       |
| ---------------------- | --------------- | ------------------ |
| **Agent Instructions** | 1 archivo       | ~4,500             |
| **Prompt Guides**      | 3 archivos      | ~21,500            |
| **Tools & Modes**      | 2 archivos      | ~8,000             |
| **README & Docs**      | 2 archivos      | ~15,000            |
| **VS Code Settings**   | 1 archivo       | ~300               |
| **Toolsets**           | 1 archivo       | ~250               |
| **MCP Configs**        | 1 archivo       | ~20                |
| **TOTAL**              | **11 archivos** | **~49,570 líneas** |

---

### **MCPs Configurados**

| MCP                     | Estado       | Herramientas                        | Uso                 |
| ----------------------- | ------------ | ----------------------------------- | ------------------- |
| **Chrome DevTools**     | ✅ Activo    | Console, Network, Storage           | Frontend debugging  |
| **Pylance**             | ✅ Built-in  | RunCodeSnippet, Refactoring, Syntax | Python analysis     |
| **Console Ninja**       | ✅ Activo    | Runtime logs/errors                 | Runtime debugging   |
| **PostgreSQL**          | ⏳ Pendiente | SQL queries, schema                 | Database operations |
| **Filesystem**          | ⏳ Pendiente | Bulk ops, templating                | Scaffolding         |
| **Git**                 | ⏳ Pendiente | Blame, log, diffs                   | Advanced Git        |
| **Sequential Thinking** | ⏳ Pendiente | Step-by-step reasoning              | Complex problems    |
| **Memoria**             | ⏳ Futuro    | Context persistence                 | Long-term memory    |

---

### **Toolsets Disponibles**

20 toolsets especializados:

- **General**: development, review, refactor, debug, testing, documentation
- **Stack**: backend-only, frontend-only, mobile-development
- **Dominio**: gamification, communication, avatar-system, database, api-endpoints
- **Especializado**: performance, security, git-operations, ci-cd
- **Utilidad**: minimal, quick-fix, full-stack

---

## 🚀 Próximos Pasos Recomendados

### **Inmediato (Hoy)**

1. **Lee el README principal**:

   ```
   cat .copilot/README.md
   ```

2. **Prueba un prompt simple**:

   ```
   Implementa un endpoint GET /api/health que retorne:
   {
     "status": "ok",
     "timestamp": "2025-11-12T...",
     "services": {
       "database": "up",
       "redis": "up"
     }
   }

   Sigue las convenciones de BACKEND_GUIDE.md.
   ```

3. **Activa un toolset**:

   ```
   /tools @acadify-backend-only

   Crea el modelo HealthCheck con SQLAlchemy...
   ```

---

### **Corto Plazo (Esta Semana)**

4. **Instala MCPs recomendados**:

   ```bash
   # PostgreSQL MCP (más importante)
   npm install -g @modelcontextprotocol/server-postgres

   # Configura en .vscode/mcp-settings.json
   # (ver sección PostgreSQL MCP arriba)
   ```

5. **Crea guías especializadas faltantes**:

   - `.copilot/prompts/DATABASE_SCHEMA.md`
   - `.copilot/prompts/GAMIFICATION_GUIDE.md`
   - `.copilot/prompts/COMMUNICATION_GUIDE.md`
   - `.copilot/prompts/AVATAR_SYSTEM.md`
   - `.copilot/prompts/TESTING_GUIDE.md`
   - `.copilot/prompts/MOBILE_GUIDE.md`

6. **Familiarízate con los modes**:

   ```
   DEBUG MODE: Prueba investigar un error inventado...

   REFACTOR MODE: Prueba refactorizar un archivo pequeño...

   TESTING MODE: Crea tests para un servicio existente...
   ```

---

### **Medio Plazo (Este Mes)**

7. **Optimiza workflows**:

   - Identifica prompts que funcionan mejor
   - Crea shortcuts para prompts frecuentes
   - Refina convenciones en AGENT_INSTRUCTIONS.md

8. **Expande toolsets**:

   - Crea toolsets personalizados para tus flujos
   - Ajusta herramientas según necesidad

9. **Integra MCPs en workflow diario**:
   - Usa PostgreSQL MCP para queries frecuentes
   - Usa Sequential Thinking para decisiones arquitectónicas

---

## 🎓 Recursos de Aprendizaje

### **Documentación de Referencia**

- **Copilot Agent**: [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Pylance**: [Python Language Server](https://github.com/microsoft/pylance-release)
- **Ruff**: [Python Linter](https://docs.astral.sh/ruff/)
- **ESLint**: [JavaScript Linter](https://eslint.org/)

### **Guías Internas**

- **Arquitectura General**: `.copilot/prompts/PROJECT_MASTER_GUIDE.md`
- **Backend Python**: `.copilot/prompts/BACKEND_GUIDE.md`
- **Frontend React**: `.copilot/prompts/FRONTEND_GUIDE.md`
- **Comportamiento Agente**: `.copilot/AGENT_INSTRUCTIONS.md`
- **Uso Completo**: `.copilot/README.md` (👈 **COMIENZA AQUÍ**)

---

## 💡 Tips Pro

### **1. Prompts Específicos > Vagos**

❌ "Agrega validación"
✅ "Agrega validación Pydantic que verifique email válido y password mínimo 8 caracteres con mayúscula"

### **2. Siempre Referencia Guías**

```
Implementa siguiendo #file:.copilot/prompts/BACKEND_GUIDE.md
```

### **3. Especifica Tests**

```
Tests obligatorios:
- Caso exitoso
- Usuario no existe (404)
- Credenciales inválidas (401)
```

### **4. Divide Tareas Grandes**

```
Paso 1: Backend del sistema de misiones
[espera]
Paso 2: Frontend del sistema de misiones
```

### **5. Usa Toolsets Específicos**

No uses `@acadify-full-stack` si solo necesitas backend.

### **6. Activa Modes para Tareas Especiales**

```
REFACTOR MODE
DEBUG MODE
TESTING MODE
```

---

## 🎉 ¡Configuración Completa!

Tu Copilot Agent ahora:

✅ **Conoce Acadify** al dedillo (arquitectura, stack, ubicaciones)
✅ **Aplica mejores prácticas** (SOLID, DRY, Type Safety)
✅ **Sugiere mejoras** proactivamente
✅ **Nunca repite código** (busca antes de crear)
✅ **Valida automáticamente** (get_errors, runTests)
✅ **Trabaja como un senior** (profesional, riguroso, proactivo)
✅ **Tiene 20 toolsets** especializados
✅ **Usa 3 MCPs** activos (Chrome, Pylance, Console Ninja)
✅ **Settings optimizados** en VS Code

---

## 📞 Soporte

Si tienes dudas:

1. **Lee el README principal**: `.copilot/README.md`
2. **Consulta la guía específica**: `.copilot/prompts/<DOMINIO>_GUIDE.md`
3. **Pregunta a Copilot**:
   ```
   Explícame cómo usar el toolset @acadify-backend-only según la configuración de TOOLS.toolsets.jsonc
   ```

---

**¡A volar con Copilot! 🚀**

---

**Última actualización**: 12 de noviembre de 2025
**Versión**: 1.0.0
**Autor**: Equipo Acadify
