# 🛠️ Tools Configuration - Copilot Agent

> **Configuración de herramientas habilitadas/deshabilitadas para el agente**

---

## ✅ HERRAMIENTAS HABILITADAS

### **File Operations (Alta Prioridad)**

| Tool | Propósito | Uso Recomendado |
|------|-----------|-----------------|
| `read_file` | Leer contenido de archivos | Antes de editar, para contexto completo |
| `replace_string_in_file` | Editar archivos existentes | Cambios quirúrgicos, incluir 3-5 líneas de contexto |
| `create_file` | Crear nuevos archivos | Nuevos componentes, servicios, tests |
| `file_search` | Buscar archivos por glob pattern | Encontrar archivos por nombre/extensión |
| `grep_search` | Buscar texto en archivos | Encontrar implementaciones, imports, usos |
| `semantic_search` | Búsqueda semántica en codebase | Encontrar funcionalidad similar, patrones |
| `list_dir` | Listar contenido de directorio | Explorar estructura de carpetas |

**Precauciones**:
- Siempre **leer archivo completo** antes de editar
- En `replace_string_in_file`, incluir **contexto único** (3-5 líneas antes/después)
- **Nunca** usar marcadores como `...existing code...` en oldString/newString

---

### **Error Detection & Validation**

| Tool | Propósito | Uso Recomendado |
|------|-----------|-----------------|
| `get_errors` | Obtener errores de compilación/lint | **Siempre** después de editar archivos |
| `runTests` | Ejecutar tests unitarios | Validar cambios críticos |
| `test_failure` | Información de tests fallidos | Debugging de tests |

**Best Practice**:
- Ejecutar `get_errors` **inmediatamente** después de cada edit
- Correr tests relevantes antes de marcar tarea como completa
- Si hay errores, **priorizar su corrección** antes de continuar

---

### **Terminal & Execution**

| Tool | Propósito | Uso Recomendado |
|------|-----------|-----------------|
| `run_in_terminal` | Ejecutar comandos shell | Instalar deps, migrations, linting, builds |
| `get_terminal_output` | Ver output de comando background | Verificar servidor corriendo, logs |

**Comandos Comunes**:

```bash
# Backend
cd backend && uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend && pnpm dev

# Migrations
cd backend && alembic upgrade head

# Tests
cd backend && pytest tests/test_auth.py -v
cd frontend && pnpm test

# Linting
cd backend && ruff check src/ --fix
cd frontend && pnpm lint:fix
```

**Precauciones**:
- **No ejecutar comandos destructivos** sin confirmación (rm -rf, drop table, etc.)
- Para servidores, usar `isBackground: true`
- **Limitar output** con filters (head, tail, grep) para evitar overflow

---

### **Python Environment Management**

| Tool | Propósito | Uso Recomendado |
|------|-----------|-----------------|
| `configure_python_environment` | Configurar entorno Python | **Siempre primero** antes de ops Python |
| `get_python_environment_details` | Ver detalles del entorno | Verificar versión, packages instalados |
| `get_python_executable_details` | Ruta al ejecutable Python | Construir comandos Python correctos |
| `install_python_packages` | Instalar paquetes Python | Agregar dependencias nuevas |

**Workflow Python**:
1. `configure_python_environment` (obligatorio primero)
2. `get_python_environment_details` (verificar setup)
3. `install_python_packages` (si faltan deps)
4. `run_in_terminal` con ruta correcta de Python

---

### **Code Navigation & Analysis**

| Tool | Propósito | Uso Recomendado |
|------|-----------|-----------------|
| `list_code_usages` | Encontrar usos de función/clase | Antes de renombrar/refactorizar |
| `get_search_view_results` | Resultados de búsqueda en UI | Ver búsquedas activas del usuario |

**Casos de Uso**:
- Antes de renombrar función → buscar todos los usos
- Antes de cambiar signature → verificar callers
- Encontrar ejemplos de uso de patrón específico

---

### **Task Management**

| Tool | Propósito | Uso Recomendado |
|------|-----------|-----------------|
| `manage_todo_list` | Gestionar lista de tareas | **Obligatorio** para tareas multi-paso |

**Workflow**:
1. **Read** current todo list
2. **Write** todo list con tareas específicas (título, descripción, status)
3. Marcar tarea `in-progress` antes de trabajar en ella
4. Marcar `completed` **inmediatamente** al terminar
5. **Nunca** batches de completions → marcar una por una

---

### **Git & Version Control**

| Tool | Propósito | Uso Recomendado |
|------|-----------|-----------------|
| `get_changed_files` | Ver cambios git | Antes de commit, revisar diffs |

**No Incluido** (usar terminal):
- `git add`, `git commit`, `git push` → usar `run_in_terminal`
- Commits deben ser **explícitos**, no automáticos

---

## ❌ HERRAMIENTAS DESHABILITADAS

| Tool | Razón | Alternativa |
|------|-------|-------------|
| `create_new_workspace` | Proyecto ya existe | N/A |
| `create_new_jupyter_notebook` | No usado en proyecto | N/A |
| `install_extension` | Manual por usuario | Sugerir ID de extensión |
| `run_vscode_command` | Solo para workspace setup | N/A |
| `create_and_run_task` | Ya hay scripts en package.json | `run_in_terminal` |

---

## 🎯 PRIORIDADES DE USO

### **Alta Frecuencia (usar siempre)**
1. `read_file` → antes de editar
2. `replace_string_in_file` → editar código
3. `get_errors` → después de editar
4. `manage_todo_list` → tareas multi-paso

### **Media Frecuencia (según necesidad)**
5. `run_in_terminal` → comandos, tests, builds
6. `file_search` / `grep_search` → buscar código
7. `semantic_search` → buscar patrones/funcionalidad
8. `runTests` → validar cambios

### **Baja Frecuencia (casos específicos)**
9. `list_code_usages` → antes de refactor grande
10. `install_python_packages` → nuevas dependencias
11. `get_terminal_output` → debug de background processes

---

## 🚨 LIMITACIONES Y PRECAUCIONES

### **File Operations**

1. **replace_string_in_file**:
   - ❌ **No usar** `...existing code...` o similares
   - ✅ **Incluir** 3-5 líneas de contexto exacto antes/después
   - ✅ **Verificar** que `oldString` sea único en el archivo
   - ✅ **Ejecutar** `get_errors` después

2. **create_file**:
   - ✅ Verificar que archivo **no existe** primero
   - ✅ Crear directorios automáticamente (tool lo hace)
   - ✅ Usar encoding UTF-8 siempre

3. **read_file**:
   - Para archivos grandes (>2000 líneas), usar `offset` y `limit`
   - Preferir leer **chunks grandes** en lugar de múltiples pequeños

### **Terminal Operations**

1. **run_in_terminal**:
   - ❌ **No ejecutar** comandos destructivos (drop, rm -rf)
   - ❌ **No ejecutar** múltiples comandos en paralelo
   - ✅ Usar `isBackground: true` para servidores
   - ✅ Limitar output con filters (`head -n 50`, `tail -n 100`)

2. **get_terminal_output**:
   - Output truncado a 60KB automáticamente
   - Para logs grandes, filtrar en el comando mismo

### **Python Environment**

1. **configure_python_environment**:
   - ✅ **Siempre llamar primero** antes de cualquier operación Python
   - ✅ Pasar `resourcePath` cuando sea posible

2. **install_python_packages**:
   - ✅ Verificar que paquete no existe antes de instalar
   - ✅ Instalar con versiones específicas cuando sea crítico

---

## 📋 CHECKLIST PRE-ACCIÓN

### **Antes de Editar Archivo**
- [ ] Leer archivo completo con `read_file`
- [ ] Entender contexto y estructura
- [ ] Identificar sección exacta a cambiar
- [ ] Preparar `oldString` con contexto único

### **Después de Editar Archivo**
- [ ] Ejecutar `get_errors` para validar
- [ ] Si hay errores → corregir inmediatamente
- [ ] Si cambio crítico → ejecutar `runTests`
- [ ] Verificar cambio con `read_file` si es necesario

### **Antes de Terminal Command**
- [ ] Verificar comando es correcto (syntax)
- [ ] Verificar no es destructivo
- [ ] Agregar filters si output puede ser grande
- [ ] Usar `isBackground` apropiadamente

### **Durante Tarea Multi-Paso**
- [ ] Crear todo list con `manage_todo_list`
- [ ] Marcar tarea actual como `in-progress`
- [ ] Completar una tarea a la vez
- [ ] Marcar `completed` inmediatamente

---

## 🎓 EJEMPLOS DE USO CORRECTO

### **Editar Función Existente**

```typescript
// 1. Leer archivo primero
read_file("/path/to/file.ts")

// 2. Identificar sección exacta
// 3. Preparar oldString con contexto

replace_string_in_file({
  filePath: "/path/to/file.ts",
  oldString: `
export function calculateTotal(items: CartItem[]): number {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  const tax = subtotal * 0.16;
  return subtotal + tax;
}
  `.trim(),
  newString: `
export function calculateTotal(items: CartItem[], taxRate: number = 0.16): number {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  const tax = subtotal * taxRate;
  return subtotal + tax;
}
  `.trim()
})

// 4. Validar cambio
get_errors({ filePaths: ["/path/to/file.ts"] })
```

### **Crear Nuevo Componente**

```typescript
// 1. Verificar que no existe
file_search({ query: "**/UserAvatar.tsx" })

// 2. Crear archivo
create_file({
  filePath: "/frontend/src/components/UserAvatar.tsx",
  content: `
import React from 'react';

interface UserAvatarProps {
  user: { name: string; avatar_url?: string };
  size?: 'sm' | 'md' | 'lg';
}

export function UserAvatar({ user, size = 'md' }: UserAvatarProps) {
  // Implementation...
}
  `.trim()
})

// 3. Validar
get_errors({ filePaths: ["/frontend/src/components/UserAvatar.tsx"] })
```

### **Ejecutar Tests**

```typescript
// 1. Correr tests específicos
runTests({
  files: ["/backend/tests/test_auth.py"],
  mode: "run"
})

// 2. Si fallan, ver detalles
test_failure()

// 3. Correr con coverage
runTests({
  files: ["/backend/tests/test_auth.py"],
  mode: "coverage",
  coverageFiles: ["/backend/src/services/auth/auth_service.py"]
})
```

---

## 🎯 MÉTRICAS DE ÉXITO

El uso correcto de tools se mide por:

1. ✅ **Cero errores** después de edits (validado con `get_errors`)
2. ✅ **Tests passing** en primera corrida
3. ✅ **Context switches mínimos** (leer archivo completo de una vez)
4. ✅ **Output limpio** en terminal (sin spam de logs)
5. ✅ **Todo list actualizado** correctamente (tareas marcadas en tiempo real)

---

**Versión**: 1.0.0  
**Última actualización**: Noviembre 2025
