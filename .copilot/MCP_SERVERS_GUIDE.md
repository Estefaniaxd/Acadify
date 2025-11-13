# 🔌 MCP Servers Guide - Acadify

> **Guía completa de Model Context Protocol (MCP) Servers para GitHub Copilot** > **Fecha**: 12 de noviembre de 2025
> **Versión**: 1.0.0

---

## 📋 Tabla de Contenidos

- [¿Qué son los MCP Servers?](#-qué-son-los-mcp-servers)
- [MCPs Actualmente Configurados](#-mcps-actualmente-configurados)
- [MCPs Recomendados por Prioridad](#-mcps-recomendados-por-prioridad)
- [Configuración Completa](#-configuración-completa)
- [Instalación Rápida](#-instalación-rápida)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 ¿Qué son los MCP Servers?

**Model Context Protocol (MCP) Servers** son **herramientas externas** que extienden las capacidades de GitHub Copilot más allá de las herramientas built-in de VS Code.

### **Diferencia con Tools Built-in**

| Tipo               | Ejemplos                                 | Propósito                            |
| ------------------ | ---------------------------------------- | ------------------------------------ |
| **Built-in Tools** | `edit`, `problems`, `runTests`, `search` | Herramientas nativas de VS Code      |
| **MCP Servers**    | PostgreSQL, Git, Docker, Puppeteer       | Herramientas externas especializadas |

### **Ventajas de MCPs**

✅ **Especializados**: Cada MCP está diseñado para UNA tarea específica
✅ **Extensibles**: Puedes crear tus propios MCPs
✅ **Potentes**: Acceso a APIs externas (databases, cloud, browsers)
✅ **Actualizables**: Independientes de VS Code
✅ **Composables**: Puedes combinar múltiples MCPs

---

## ✅ MCPs Actualmente Configurados

### **1. 🌐 Chrome DevTools MCP**

**Estado**: ✅ Activo
**Archivo**: `.vscode/mcp-settings.json`
**Documentación**: `MCP-CHROME-SETUP.md`

**Configuración**:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://localhost:9222"],
      "env": {
        "NODE_ENV": "production",
        "DEBUG": "*"
      }
    }
  }
}
```

**Capacidades**:

- ✅ Ver logs de consola del browser
- ✅ Inspeccionar Network (requests, 404, 422, CORS)
- ✅ Evaluar JavaScript en runtime
- ✅ Inspeccionar Storage (localStorage, sessionStorage, cookies)
- ✅ Tomar screenshots
- ✅ Medir performance

**Cómo Iniciar**:

```bash
# Opción 1: Script automático
./start-chrome-debug.sh

# Opción 2: Manual
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

**Ejemplo de Uso**:

```
Muéstrame los logs de consola del browser y detecta si hay errores relacionados con autenticación.

Inspecciona el localStorage y muéstrame el access_token guardado.

Toma screenshot de la página de login después de intentar login fallido.
```

---

### **2. 🐍 Pylance MCP**

**Estado**: ✅ Built-in (Python Extension)
**Documentación**: [Pylance Docs](https://github.com/microsoft/pylance-release)

**Herramientas**:

- `pylanceRunCodeSnippet` - Ejecutar código Python sin terminal
- `pylanceFileSyntaxErrors` - Validar sintaxis
- `pylanceImports` - Analizar imports del workspace
- `pylanceInstalledTopLevelModules` - Ver módulos instalados
- `pylanceInvokeRefactoring` - Refactors automáticos:
  - `source.unusedImports` - Remover imports no usados
  - `source.convertImportFormat` - Convertir imports abs/rel
  - `source.fixAll.pylance` - Aplicar todos los fixes
- `pylanceSettings` - Ver configuración Pylance
- `pylanceWorkspaceUserFiles` - Listar archivos Python
- `pylanceWorkspaceRoots` - Ver workspace roots
- `pylanceDocuments` - Buscar documentación

**Ejemplo de Uso**:

````
Usa pylanceRunCodeSnippet para verificar que la función _hash_password funciona:

```python
from src.services.auth_service import _hash_password
result = _hash_password("test123")
print(f"Hash: {result[:20]}...")
print(f"Length: {len(result)}")
````

Ejecuta pylanceInvokeRefactoring con source.unusedImports en src/services/usuario_service.py.

Muéstrame pylanceImports del workspace y detecta imports no resueltos.

```

---

### **3. 🕹️ Console Ninja MCP**
**Estado**: ✅ Activo (si tienes la extensión)
**Herramientas**:
- `runtime-errors` - Errores de ejecución
- `runtime-logs` - Logs completos
- `runtime-logs-and-errors` - Ambos
- `runtime-logs-by-location` - Logs de archivo:línea específico

**Ejemplo de Uso**:
```

Muéstrame runtime-logs-and-errors del último minuto.

Filtra runtime-errors que contengan "TypeError" o "undefined".

Muéstrame runtime-logs-by-location de src/components/AuthForm.tsx línea 45.

````

---

### **4. 🗄️ PostgreSQL MCP**
**Estado**: ✅ Instalado (npm install completado)
**Pendiente**: Configurar en `.vscode/mcp-settings.json`

---

## 🚀 MCPs Recomendados por Prioridad

### **PRIORIDAD ALTA** (Instalar Ya)

#### **📊 1. PostgreSQL MCP** ✅ Instalado
```bash
npm install -g @modelcontextprotocol/server-postgres
````

**Configuración**:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "PGHOST": "localhost",
        "PGPORT": "5432",
        "PGUSER": "acadify_user",
        "PGPASSWORD": "tu_password",
        "PGDATABASE": "acadify"
      }
    }
  }
}
```

**Capacidades**:

- ✅ Ejecutar queries SQL (SELECT, INSERT, UPDATE, DELETE)
- ✅ Inspeccionar schema (tablas, columnas, tipos, constraints)
- ✅ Analizar índices y performance
- ✅ Ver estadísticas de tablas
- ✅ Ejecutar EXPLAIN para optimización
- ✅ Listar foreign keys y relaciones

**Ejemplo de Uso**:

```sql
-- Ver usuarios con rachas activas > 7 días
SELECT u.id, u.nombre, r.dias_consecutivos, r.fecha_ultima_actualizacion
FROM usuarios u
INNER JOIN rachas_usuario r ON u.id = r.usuario_id
WHERE r.activa = true AND r.dias_consecutivos > 7
ORDER BY r.dias_consecutivos DESC;

-- Inspeccionar schema de tabla usuarios
\d+ usuarios

-- Analizar performance de query
EXPLAIN ANALYZE
SELECT c.*, d.nombre as docente_nombre
FROM cursos c
LEFT JOIN usuarios d ON c.docente_id = d.id
WHERE c.institucion_id = 1;

-- Ver índices de la tabla cursos
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'cursos';
```

---

#### **📁 2. Filesystem MCP**

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Configuración**:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify"
      ]
    }
  }
}
```

**Capacidades**:

- ✅ Watch archivos (detectar cambios automáticamente)
- ✅ Bulk file operations (crear/editar múltiples archivos)
- ✅ Templating avanzado (scaffolding)
- ✅ File tree manipulation
- ✅ Glob patterns para búsqueda masiva
- ✅ Operaciones atómicas (todo o nada)

**Ejemplo de Uso**:

````
Crea archivos de test para todos los servicios en backend/src/services/ siguiendo este template:

Template (test_{service_name}.py):
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.{service_name} import {ServiceClass}

@pytest.fixture
def service(db: AsyncSession) -> {ServiceClass}:
    return {ServiceClass}(db)

@pytest.mark.asyncio
async def test_{service_name}_basic(service: {ServiceClass}):
    # TODO: Implementar test
    pass
````

Servicios a crear tests:

- auth_service.py → test_auth_service.py
- institucion_service.py → test_institucion_service.py
- gamificacion_service.py → test_gamificacion_service.py
- avatar_service.py → test_avatar_service.py

Observa cambios en backend/src/models/ y notifícame cuando se modifique un modelo.

````

---

#### **🔀 3. Git MCP**
```bash
npm install -g @modelcontextprotocol/server-git
````

**Configuración**:

```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify"
      ]
    }
  }
}
```

**Capacidades**:

- ✅ Git blame (quién cambió cada línea)
- ✅ Git log con búsqueda semántica
- ✅ Diffs semánticos (cambios lógicos vs sintácticos)
- ✅ Cherry-pick inteligente
- ✅ Stash management
- ✅ Branch analysis y comparación
- ✅ Buscar en historial por mensaje/autor/fecha
- ✅ Detectar conflictos antes de merge

**Ejemplo de Uso**:

```bash
# Git blame para encontrar autor de implementación
Muéstrame el git blame de backend/src/services/auth_service.py líneas 45-80 y encuentra quién implementó la autenticación 2FA.

# Buscar en historial
Busca en el git log commits relacionados con "gamificación" o "puntos" de los últimos 2 meses.

# Comparar branches
Compara la branch develop con main y muéstrame:
- Archivos modificados
- Líneas agregadas/eliminadas
- Commits únicos en develop

# Cherry-pick específico
Cherry-pick el commit abc123def que arregla el bug de avatares, pero solo aplica los cambios de avatar_service.py, ignora cambios de config.py.

# Detectar conflictos
Analiza si hay conflictos potenciales al mergear feature/videollamadas en develop.
```

---

#### **🧠 4. Sequential Thinking MCP**

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

**Capacidades**:

- ✅ Razonamiento paso a paso estructurado
- ✅ Análisis de trade-offs (pros/cons de cada opción)
- ✅ Diseño de arquitectura compleja
- ✅ Debugging de problemas complejos
- ✅ Refactoring grandes con plan detallado
- ✅ Documentar decisiones arquitectónicas con justificación

**Ejemplo de Uso**:

```
Usa sequential thinking para diseñar el sistema de misiones diarias completo:

Contexto:
- Los usuarios deben tener misiones diarias que se renuevan cada 24h
- Tipos: completar N clases, obtener X puntos, racha de Y días
- Rewards: puntos, badges, acceso a contenido premium
- Debe ser escalable (10,000+ usuarios concurrentes)

Analiza paso a paso:

1. **Modelos de BD**:
   - ¿Mission, UserMission, MissionReward?
   - ¿Cómo manejar recurrencia?
   - ¿Campos necesarios?

2. **Sistema de verificación**:
   - ¿Triggers de BD vs background jobs vs eventos?
   - ¿Tiempo real vs batch?
   - Trade-offs de cada enfoque

3. **Performance**:
   - ¿Caching strategy? (Redis keys, TTL)
   - ¿Índices necesarios?
   - ¿Paginación de misiones?

4. **Rewards**:
   - ¿Transaccional? (atomic)
   - ¿Notifications push?
   - ¿Historial de rewards?

5. **Testing**:
   - ¿Unit tests de lógica de verificación?
   - ¿Integration tests con DB?
   - ¿E2E del flujo completo?

6. **Rollout**:
   - ¿Feature flag?
   - ¿A/B testing?
   - ¿Migración de datos?

Para cada paso, justifica decisiones y menciona alternativas descartadas.
```

---

#### **📝 5. Memory MCP**

```bash
npm install -g @modelcontextprotocol/server-memory
```

**Configuración**:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_STORE_PATH": "${workspaceFolder}/.copilot/memory.json"
      }
    }
  }
}
```

**Capacidades**:

- ✅ Guardar decisiones arquitectónicas
- ✅ Recordar patrones usados en el proyecto
- ✅ Contexto de largo plazo entre sesiones
- ✅ Preferencias del equipo
- ✅ Lecciones aprendidas de bugs/incidentes
- ✅ Roadmap y features planificadas

**Ejemplo de Uso**:

```
# Guardar decisión arquitectónica
Guarda en memoria:
"Sistema de gamificación usa patrón Strategy para calcular puntos. Cada tipo de actividad (completar_clase, entregar_tarea, racha_diaria) tiene su propio StrategyCalculator con multiplicadores configurables en Redis."

# Guardar preferencia de código
Guarda en memoria:
"Preferimos Pydantic schemas en lugar de dataclasses por validación automática y serialización JSON. Siempre usar Field() para documentación de campos."

# Guardar patrón de testing
Guarda en memoria:
"Tests de servicios siempre usan fixture 'service' que inyecta CRUDs mockeados. Ejemplo en test_auth_service.py."

# Consultar memoria
¿Qué decisiones arquitectónicas tenemos sobre el sistema de avatares?

¿Cuáles son las convenciones de naming que seguimos?

¿Qué lecciones aprendimos del bug de autenticación 2FA del mes pasado?
```

---

### **PRIORIDAD MEDIA** (Muy Útiles)

#### **🐳 6. Docker MCP**

```bash
npm install -g @modelcontextprotocol/server-docker
```

**Configuración**:

```json
{
  "mcpServers": {
    "docker": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-docker"]
    }
  }
}
```

**Capacidades**:

- ✅ Listar containers, images, volumes, networks
- ✅ Ver logs de containers
- ✅ Ejecutar comandos en containers
- ✅ Inspeccionar estado de servicios
- ✅ Build y push de images
- ✅ Docker Compose management (up, down, restart)

**Ejemplo de Uso**:

```bash
# Ver logs de container
Muéstrame los logs del container acadify-backend de las últimas 100 líneas y filtra errores.

# Listar containers
Lista todos los containers de docker-compose.yml y su estado (running, exited).

# Ejecutar comando en container
Ejecuta "python -m pytest tests/api/test_auth.py -v" dentro del container acadify-backend.

# Inspeccionar volumen
Inspecciona el volumen postgres-data y muéstrame:
- Tamaño total
- Ubicación en host
- Containers que lo usan

# Docker Compose
Reinicia solo el servicio redis sin afectar backend ni postgres.
```

---

#### **🌐 7. Brave Search MCP**

```bash
npm install -g @modelcontextprotocol/server-brave-search
```

**Configuración**:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "tu-api-key-aqui"
      }
    }
  }
}
```

**Nota**: Requiere API key de [Brave Search API](https://brave.com/search/api/) (gratis hasta 2,000 queries/mes)

**Capacidades**:

- ✅ Búsqueda web en tiempo real
- ✅ Encontrar documentación actualizada
- ✅ Buscar soluciones a errores específicos
- ✅ Investigar librerías/paquetes nuevos
- ✅ Comparar alternativas (tech stack decisions)

**Ejemplo de Uso**:

```
Busca en web las mejores prácticas para implementar WebRTC con FastAPI en 2025.

Investiga cómo otros proyectos implementan rate limiting con Redis y FastAPI.

Encuentra la documentación oficial de React Query 5 sobre invalidación de queries después de mutations.

Compara las librerías de validación de Python: Pydantic vs Marshmallow vs attrs (performance, features, comunidad).

Busca soluciones al error "sqlalchemy.exc.InvalidRequestError: Object is already attached to session".
```

---

#### **📦 8. Puppeteer MCP**

```bash
npm install -g @modelcontextprotocol/server-puppeteer
```

**Configuración**:

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

**Capacidades**:

- ✅ Automatizar testing E2E en browser
- ✅ Tomar screenshots de la UI en diferentes estados
- ✅ Ejecutar flujos completos (login → navegación → acción)
- ✅ Extraer data del DOM
- ✅ Llenar formularios automáticamente
- ✅ Simular interacciones de usuario (click, type, scroll)

**Ejemplo de Uso**:

```javascript
// Test E2E completo
Automatiza el flujo de crear un curso:

1. Abre http://localhost:5173
2. Login con test@example.com / password123
3. Navega a /dashboard
4. Click en "Crear Curso"
5. Llena formulario:
   - Nombre: "Matemáticas 101"
   - Descripción: "Curso de álgebra básica"
   - Cupo: 30
6. Submit form
7. Verifica que aparezca mensaje "Curso creado exitosamente"
8. Toma screenshot de la página de confirmación
9. Verifica en DB PostgreSQL que el curso se creó:
   SELECT * FROM cursos WHERE nombre = 'Matemáticas 101';

// Extraer datos del DOM
Abre http://localhost:5173/instituciones y extrae todos los nombres de instituciones del listado.

// Test de diferentes estados
Toma screenshots de la página de login en estos estados:
1. Estado inicial (vacío)
2. Después de ingreso válido (loading)
3. Error de credenciales inválidas
4. Error de red (disconnect backend)
```

---

#### **📊 9. SQLite MCP** (para tests)

```bash
npm install -g @modelcontextprotocol/server-sqlite
```

**Configuración**:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/tmp/test-acadify.db"]
    }
  }
}
```

**Uso**: Similar a PostgreSQL MCP pero para base de datos SQLite de tests.

---

### **PRIORIDAD AVANZADA** (Casos Específicos)

#### **📧 10. Gmail MCP** (testing de emails)

```bash
npm install -g @modelcontextprotocol/server-gmail
```

**Configuración**:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gmail"],
      "env": {
        "GMAIL_CLIENT_ID": "tu-client-id",
        "GMAIL_CLIENT_SECRET": "tu-client-secret",
        "GMAIL_REFRESH_TOKEN": "tu-refresh-token"
      }
    }
  }
}
```

**Capacidades**:

- ✅ Leer emails de prueba
- ✅ Verificar emails de 2FA en testing
- ✅ Enviar emails de notificaciones
- ✅ Buscar emails por remitente/asunto/fecha

**Ejemplo de Uso**:

```
Lee el último email recibido en test.acadify@gmail.com y extrae el código de verificación 2FA.

Verifica que el email de bienvenida se envió a juan.perez@example.com después de registro.

Busca emails enviados en las últimas 24h con asunto que contenga "Nuevo curso disponible".
```

---

#### **🔔 11. Slack MCP** (notificaciones al equipo)

```bash
npm install -g @modelcontextprotocol/server-slack
```

**Configuración**:

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-tu-token",
        "SLACK_TEAM_ID": "T12345678"
      }
    }
  }
}
```

**Capacidades**:

- ✅ Enviar mensajes a canales
- ✅ Notificar errores críticos
- ✅ Buscar mensajes históricos
- ✅ Crear threads
- ✅ Reaccionar a mensajes

**Ejemplo de Uso**:

```
Envía mensaje al canal #dev:
"🚀 Backend deployed to staging
✅ Tests: 127/127 passing (100%)
⏱️ Deploy time: 3m 42s
📦 Version: v1.5.0"

Busca en el historial de #bugs mensajes sobre "autenticación" o "login" de la última semana.

Crea thread en el mensaje con ID 1234.56 respondiendo con análisis del bug.
```

---

#### **📈 12. Sentry MCP** (monitoring de errores)

```bash
npm install -g @modelcontextprotocol/server-sentry
```

**Configuración**:

```json
{
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sentry"],
      "env": {
        "SENTRY_AUTH_TOKEN": "tu-token",
        "SENTRY_ORG": "acadify",
        "SENTRY_PROJECT": "backend"
      }
    }
  }
}
```

**Capacidades**:

- ✅ Ver errores recientes en producción
- ✅ Analizar stack traces completos
- ✅ Ver frecuencia de errores
- ✅ Buscar errores por tipo/endpoint/usuario
- ✅ Resolver/ignorar issues

**Ejemplo de Uso**:

```
Muéstrame los 10 errores más frecuentes en producción de las últimas 24 horas ordenados por ocurrencias.

Analiza el error SENTRY-ABC123XYZ y dame:
- Stack trace completo
- Request context (URL, método, headers)
- Usuario afectado
- Breadcrumbs (eventos previos)
- Variables locales

Busca errores relacionados con el endpoint /api/cursos/{id}/estudiantes que ocurrieron en la última semana.

¿Cuántos errores de tipo "SQLAlchemy InvalidRequestError" tuvimos en el último mes? Gráfica la tendencia.
```

---

#### **🐳 13. AWS MCP** (si usas AWS)

```bash
npm install -g @modelcontextprotocol/server-aws
```

**Configuración**:

```json
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-aws"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "tu-access-key",
        "AWS_SECRET_ACCESS_KEY": "tu-secret-key"
      }
    }
  }
}
```

**Capacidades**:

- ✅ Listar recursos (EC2, S3, RDS, Lambda)
- ✅ Ver logs de CloudWatch
- ✅ Ejecutar comandos en Lambda
- ✅ Consultar DynamoDB
- ✅ Gestionar S3 buckets

---

#### **🗂️ 14. Google Drive MCP** (assets management)

```bash
npm install -g @modelcontextprotocol/server-google-drive
```

**Uso**: Gestionar assets educativos (PDFs, imágenes, videos) almacenados en Google Drive.

---

#### **🎨 15. Figma MCP** (design system)

```bash
npm install -g @modelcontextprotocol/server-figma
```

**Uso**: Extraer diseños de Figma, obtener colores/tipografías del design system, exportar assets.

---

#### **📚 16. Notion MCP** (documentación)

```bash
npm install -g @modelcontextprotocol/server-notion
```

**Uso**: Buscar en documentación del equipo, crear/actualizar páginas, extraer requisitos.

---

#### **🔐 17. 1Password MCP** (secrets management)

```bash
npm install -g @modelcontextprotocol/server-1password
```

**Uso**: Obtener secrets de vault, rotar passwords automáticamente.

---

#### **🧪 18. Playwright MCP** (testing cross-browser)

```bash
npm install -g @modelcontextprotocol/server-playwright
```

**Uso**: Similar a Puppeteer pero más robusto para testing en Chrome, Firefox, Safari.

---

#### **🌍 19. EverArt MCP** (generación de imágenes)

```bash
npm install -g @modelcontextprotocol/server-everart
```

**Uso**: Generar assets de UI, ilustraciones para documentación.

---

#### **🔍 20. Google Search MCP**

```bash
npm install -g @modelcontextprotocol/server-google-search
```

**Uso**: Similar a Brave Search pero usa Google. Requiere API key.

---

## ⚙️ Configuración Completa

### **Archivo: `.vscode/mcp-settings.json`**

Este es el archivo completo con TODOS los MCPs recomendados configurados:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://localhost:9222"],
      "env": {
        "NODE_ENV": "production",
        "DEBUG": "*"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "PGHOST": "localhost",
        "PGPORT": "5432",
        "PGUSER": "acadify_user",
        "PGPASSWORD": "your_password_here",
        "PGDATABASE": "acadify"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify"
      ]
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_STORE_PATH": "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/.copilot/memory.json"
      }
    },
    "docker": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-docker"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA-YOUR-API-KEY-HERE"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/tmp/test-acadify.db"]
    }
  }
}
```

**Nota**: Reemplaza los valores de environment variables con tus credenciales reales.

---

## 🚀 Instalación Rápida

### **Script de Instalación Completa**

Crea este script `install-mcps.sh`:

```bash
#!/bin/bash
# install-mcps.sh - Instalación completa de MCPs para Acadify

echo "🔌 Instalando MCP Servers para Acadify..."
echo ""

# Prioridad Alta (Instalar Ya)
echo "📦 Instalando MCPs de Prioridad Alta..."
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-memory

echo ""
echo "📦 Instalando MCPs de Prioridad Media..."
npm install -g @modelcontextprotocol/server-docker
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-puppeteer
npm install -g @modelcontextprotocol/server-sqlite

echo ""
echo "✅ Instalación completada!"
echo ""
echo "📝 Próximos pasos:"
echo "1. Edita .vscode/mcp-settings.json y configura credenciales"
echo "2. Reinicia VS Code: Ctrl+Shift+P → 'Reload Window'"
echo "3. Verifica MCPs activos en Copilot Chat"
echo ""
echo "📚 Documentación: .copilot/MCP_SERVERS_GUIDE.md"
```

**Ejecutar**:

```bash
chmod +x install-mcps.sh
./install-mcps.sh
```

---

### **Instalación Individual**

Si prefieres instalar uno por uno:

```bash
# Prioridad Alta
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-memory

# Prioridad Media
npm install -g @modelcontextprotocol/server-docker
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-puppeteer
npm install -g @modelcontextprotocol/server-sqlite
```

---

## 💡 Ejemplos de Uso

### **Ejemplo 1: Debugging con Múltiples MCPs**

```
Hay un error al crear un curso nuevo. Investiga usando todos los MCPs disponibles:

1. **Chrome DevTools**: Muéstrame los logs de consola del browser y network requests fallidos.

2. **PostgreSQL**: Ejecuta query para ver los últimos 5 cursos creados:
   SELECT * FROM cursos ORDER BY fecha_creacion DESC LIMIT 5;

3. **Git**: Muéstrame git blame de backend/src/api/routers/cursos.py líneas del endpoint POST /api/cursos.

4. **Docker**: Muéstrame los logs del container backend-acadify de las últimas 50 líneas y filtra errores.

5. **Sequential Thinking**: Analiza paso a paso cuál puede ser la causa del error considerando:
   - Validación de Pydantic
   - Constraints de BD (NOT NULL, FK)
   - Permisos de usuario
   - Rate limiting

6. **Memory**: ¿Hay alguna decisión arquitectónica guardada sobre creación de cursos que pueda estar relacionada?
```

---

### **Ejemplo 2: Crear Feature Completa con MCPs**

```
Implementa sistema de badges (insignias) para gamificación usando MCPs:

1. **Sequential Thinking**: Diseña la arquitectura paso a paso:
   - Modelos de BD (Badge, UserBadge)
   - Criterios de desbloqueo
   - Sistema de notificaciones
   - UI de showcase

2. **Filesystem**: Crea estructura de archivos:
   backend/src/models/badge.py
   backend/src/services/badge_service.py
   backend/src/api/routers/badges.py
   backend/tests/test_badge_service.py
   frontend/src/hooks/useBadges.ts
   frontend/src/components/BadgeCard.tsx

3. **PostgreSQL**: Ejecuta migrations para crear tablas:
   CREATE TABLE badges (...);
   CREATE TABLE user_badges (...);

4. **Git**: Crea branch feature/badges-system y commitea cambios.

5. **Puppeteer**: Crea test E2E del flujo completo:
   - Login
   - Completar actividad que desbloquea badge
   - Verificar notificación de badge desbloqueado
   - Navegar a perfil y verificar badge visible

6. **Memory**: Guarda decisión arquitectónica:
   "Sistema de badges usa observer pattern. BadgeObserver escucha eventos de UserActivity y verifica criterios de badges en background job cada 5 minutos."
```

---

### **Ejemplo 3: Análisis de Performance**

```
Optimiza el endpoint GET /api/cursos que está lento:

1. **PostgreSQL**: Ejecuta EXPLAIN ANALYZE del query actual:
   EXPLAIN ANALYZE
   SELECT c.*, d.nombre as docente_nombre, COUNT(i.id) as num_inscritos
   FROM cursos c
   LEFT JOIN usuarios d ON c.docente_id = d.id
   LEFT JOIN inscripciones i ON c.id = i.curso_id
   WHERE c.institucion_id = 1
   GROUP BY c.id, d.nombre;

2. **PostgreSQL**: Verifica índices existentes:
   SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'cursos';

3. **Sequential Thinking**: Analiza opciones de optimización:
   - Agregar índice en (institucion_id, activo)
   - Usar materialized view para counts
   - Cachear resultado en Redis
   - Eager loading con selectinload
   Compara trade-offs de cada opción.

4. **Docker**: Ejecuta benchmark con Apache Bench dentro del container:
   docker exec backend-acadify ab -n 1000 -c 10 http://localhost:8000/api/cursos

5. **Memory**: Guarda optimización aplicada:
   "Endpoint /api/cursos optimizado agregando índice compuesto (institucion_id, activo, fecha_creacion) y cache Redis con TTL 5 minutos. Latencia p95 bajó de 850ms a 45ms."
```

---

## 🚨 Troubleshooting

### **MCP no aparece en Copilot Chat**

**Solución**:

```bash
# 1. Verifica instalación
npm list -g @modelcontextprotocol/server-<nombre>

# 2. Reinstala si es necesario
npm install -g @modelcontextprotocol/server-<nombre>

# 3. Verifica configuración en .vscode/mcp-settings.json
cat .vscode/mcp-settings.json

# 4. Reinicia VS Code completamente
# Ctrl+Shift+P → "Reload Window"

# 5. Verifica en Copilot Chat
Verifica que el MCP <nombre> esté activo y muéstrame sus capacidades.
```

---

### **MCP falla con error de credenciales**

**Solución**:

```bash
# PostgreSQL
# Verifica que las credenciales sean correctas en .vscode/mcp-settings.json
# Prueba conexión manual:
psql -h localhost -U acadify_user -d acadify

# Brave Search
# Verifica que BRAVE_API_KEY sea válido en .vscode/mcp-settings.json
# Obtén nueva key en: https://brave.com/search/api/

# Gmail
# Regenera OAuth tokens en Google Cloud Console
# Actualiza GMAIL_REFRESH_TOKEN en .vscode/mcp-settings.json
```

---

### **MCP responde lento**

**Posibles causas**:

- Network latency (APIs externas)
- Query SQL costoso (PostgreSQL)
- Puppeteer timeout (browser lento)

**Solución**:

```
# PostgreSQL: Optimiza queries
EXPLAIN ANALYZE <tu-query>;

# Puppeteer: Aumenta timeout
{
  "puppeteer": {
    "env": {
      "PUPPETEER_TIMEOUT": "60000"
    }
  }
}

# Docker: Limpia containers/images no usados
docker system prune -a
```

---

### **Chrome DevTools MCP no conecta**

**Solución**:

```bash
# 1. Verifica que Chrome esté corriendo con debugging
curl http://localhost:9222/json/version

# 2. Si falla, reinicia Chrome
pkill -9 chrome
./start-chrome-debug.sh

# 3. Verifica puerto 9222 no esté ocupado
lsof -i :9222

# 4. Reinicia VS Code
```

Ver guía completa: `MCP-CHROME-SETUP.md`

---

## 📊 Resumen de MCPs

### **Tabla Completa**

| #   | MCP                     | Prioridad | Estado       | Uso Principal                               |
| --- | ----------------------- | --------- | ------------ | ------------------------------------------- |
| 1   | **Chrome DevTools**     | Alta      | ✅ Activo    | Frontend debugging (logs, network)          |
| 2   | **Pylance**             | Alta      | ✅ Built-in  | Python analysis (execute, syntax, refactor) |
| 3   | **Console Ninja**       | Alta      | ✅ Activo    | Runtime logs/errors                         |
| 4   | **PostgreSQL**          | Alta      | ✅ Instalado | SQL queries, schema, performance            |
| 5   | **Filesystem**          | Alta      | ⏳ Instalar  | Bulk ops, templating, scaffolding           |
| 6   | **Git**                 | Alta      | ⏳ Instalar  | Blame, history, diffs, cherry-pick          |
| 7   | **Sequential Thinking** | Alta      | ⏳ Instalar  | Step-by-step reasoning, architecture        |
| 8   | **Memory**              | Alta      | ⏳ Instalar  | Context persistence, decisions              |
| 9   | **Docker**              | Media     | ⏳ Instalar  | Containers, logs, exec                      |
| 10  | **Brave Search**        | Media     | ⏳ Instalar  | Web search, docs, solutions                 |
| 11  | **Puppeteer**           | Media     | ⏳ Instalar  | E2E testing, screenshots                    |
| 12  | **SQLite**              | Media     | ⏳ Instalar  | Test DB queries                             |
| 13  | **Gmail**               | Avanzada  | ⏳ Opcional  | Email testing, 2FA codes                    |
| 14  | **Slack**               | Avanzada  | ⏳ Opcional  | Team notifications                          |
| 15  | **Sentry**              | Avanzada  | ⏳ Opcional  | Error monitoring                            |
| 16  | **AWS**                 | Avanzada  | ⏳ Opcional  | Cloud resources                             |
| 17  | **Google Drive**        | Avanzada  | ⏳ Opcional  | Assets management                           |
| 18  | **Figma**               | Avanzada  | ⏳ Opcional  | Design system                               |
| 19  | **Notion**              | Avanzada  | ⏳ Opcional  | Documentation                               |
| 20  | **1Password**           | Avanzada  | ⏳ Opcional  | Secrets management                          |

---

## 🎯 Recomendación Final

### **Instalar en este orden**:

**Semana 1** (Prioridad Alta):

```bash
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-memory
```

**Semana 2** (Prioridad Media):

```bash
npm install -g @modelcontextprotocol/server-docker
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-puppeteer
```

**Semana 3+** (Según necesidad):

- Gmail (si testing de emails 2FA)
- Slack (si notificaciones al equipo)
- Sentry (si monitoring en producción)
- AWS (si hosting en AWS)

---

## 📚 Referencias

- **MCP Protocol**: https://modelcontextprotocol.io/
- **MCP Servers GitHub**: https://github.com/modelcontextprotocol/servers
- **Chrome DevTools MCP**: `MCP-CHROME-SETUP.md`
- **Copilot Agent Config**: `.copilot/README.md`
- **Configuración Completa**: `.copilot/CONFIGURATION_COMPLETE.md`

---

**¡Con estos MCPs, Copilot tendrá superpoderes! 🚀🔥**

---

**Última actualización**: 12 de noviembre de 2025
**Versión**: 1.0.0
**Mantenedor**: Equipo Acadify
