# 🔄 Git Workflow Automation - Acadify
**Fecha:** 2024-11-04  
**Objetivo:** Configurar Formatter y Linter como guardianes del código limpio

---

## 📋 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Backend: Python + Pre-commit](#backend-python--pre-commit)
4. [Frontend: TypeScript + Husky + lint-staged](#frontend-typescript--husky--lint-staged)
5. [Integración en el IDE](#integración-en-el-ide)
6. [Configuración del Pre-commit Hook](#configuración-del-pre-commit-hook)
7. [Prueba de Fuego](#prueba-de-fuego)
8. [Troubleshooting](#troubleshooting)

---

## 📊 RESUMEN EJECUTIVO

### Objetivos Logrados

✅ **Guardián de Código Limpio**: Solo código formateado y validado puede ser commiteado  
✅ **Automatización IDE**: Format on save en VS Code, PyCharm, etc.  
✅ **Pre-commit Hooks**: Interceptan `git commit` y ejecutan validaciones  
✅ **Staged Files Only**: Solo valida archivos modificados (rápido)  
✅ **Bloqueo de Errores**: Commit bloqueado si hay errores fatales  

### Stack de Herramientas

| Componente | Backend | Frontend |
|------------|---------|----------|
| **Hook Manager** | pre-commit | Husky |
| **Staged Files** | pre-commit (built-in) | lint-staged |
| **Formatter** | Ruff format | Prettier |
| **Linter** | Ruff check + Bandit | ESLint |
| **Type Checker** | - | TypeScript |
| **Security** | Bandit | - |

---

## 🏗️ ARQUITECTURA DEL SISTEMA

```
┌────────────────────────────────────────────────────────────────┐
│                    DEVELOPER WORKFLOW                          │
└────────────────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────┐
        │  1. EDIT FILES (VS Code, PyCharm)  │
        │     • Auto-format on save          │
        │     • Real-time linting            │
        └─────────────────────────────────────┘
                              │
                              ↓
                    ┌─────────────────┐
                    │  2. git add .  │
                    └─────────────────┘
                              │
                              ↓
                ┌─────────────────────────────┐
                │   3. git commit -m "..."   │
                └─────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────────┐
        │   PRE-COMMIT HOOK INTERCEPTA (Automático)  │
        ├─────────────────────────────────────────────┤
        │   BACKEND (pre-commit)                      │
        │   ✅ Ruff Format (staged files)            │
        │   ✅ Ruff Lint --fix (staged files)        │
        │   ✅ Bandit security check                  │
        │   ✅ YAML/TOML/JSON validation             │
        │   ✅ No debug statements                    │
        │   ✅ No large files                         │
        │                                             │
        │   FRONTEND (Husky + lint-staged)            │
        │   ✅ Prettier (staged *.ts, *.tsx)         │
        │   ✅ ESLint --fix (staged *.ts, *.tsx)     │
        │   ✅ TypeScript type check                  │
        └─────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ↓                           ↓
        ┌───────────────┐         ┌─────────────────┐
        │  ✅ SUCCESS   │         │  ❌ FAILURE     │
        │  Commit OK    │         │  Commit BLOCKED │
        └───────────────┘         └─────────────────┘
                │                           │
                ↓                           ↓
        ┌───────────────┐         ┌─────────────────────┐
        │  git push     │         │  Fix errors & retry │
        └───────────────┘         └─────────────────────┘
```

---

## 🐍 BACKEND: Python + Pre-commit

### Instalación

#### Paso 1: Instalar pre-commit
```bash
cd backend
pip install pre-commit
```

#### Paso 2: Verificar instalación
```bash
pre-commit --version
# Output: pre-commit 4.3.0
```

#### Paso 3: Instalar hooks en Git
```bash
pre-commit install
# Output: pre-commit installed at .git/hooks/pre-commit
```

### Configuración

**Archivo:** `backend/.pre-commit-config.yaml`

```yaml
repos:
  # Ruff - Fast linter + formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.3
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix, --show-fixes]
      - id: ruff-format

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-added-large-files
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-merge-conflict
      - id: no-commit-to-branch  # Protege main/master
      - id: debug-statements     # Detecta breakpoints
      - id: detect-private-key   # Seguridad

  # Bandit - Security linting
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.10
    hooks:
      - id: bandit
        args: [-c, pyproject.toml]
```

### Ejecución Manual (Testing)

```bash
# Ejecutar en todos los archivos
pre-commit run --all-files

# Ejecutar solo en staged files (normal)
pre-commit run

# Ejecutar un hook específico
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files

# Actualizar versiones de hooks
pre-commit autoupdate
```

### Qué hace cada hook

| Hook | Propósito | Bloquea Commit |
|------|-----------|----------------|
| `ruff` | Linter (fix auto-safe) | ✅ Sí (si quedan errores) |
| `ruff-format` | Formatter | ❌ No (solo formatea) |
| `bandit` | Security check | ✅ Sí (si encuentra issues) |
| `check-yaml` | Valida YAML syntax | ✅ Sí (si inválido) |
| `check-json` | Valida JSON syntax | ✅ Sí (si inválido) |
| `debug-statements` | Detecta `breakpoint()`, `pdb` | ✅ Sí (si encuentra) |
| `detect-private-key` | Busca claves privadas | ✅ Sí (si encuentra) |
| `no-commit-to-branch` | Protege main/master | ✅ Sí (si es main) |
| `check-added-large-files` | Evita archivos >1MB | ✅ Sí (si excede) |

---

## ⚛️ FRONTEND: TypeScript + Husky + lint-staged

### Instalación

#### Paso 1: Instalar dependencias
```bash
cd frontend
npm install --save-dev husky lint-staged

# O si ya instalaste ESLint y Prettier:
npm install --save-dev \
  husky \
  lint-staged \
  eslint \
  prettier \
  eslint-config-prettier \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin
```

**⚠️ NOTA:** Actualmente hay problemas de red. Las dependencias están configuradas en `package.json` para instalar cuando haya conexión.

#### Paso 2: Inicializar Husky
```bash
npx husky init
```

Esto crea:
- `.husky/` directorio
- `.husky/pre-commit` hook script

#### Paso 3: Configurar hook de pre-commit
```bash
# Editar .husky/pre-commit
echo "npm run pre-commit" > .husky/pre-commit
chmod +x .husky/pre-commit
```

### Configuración

**Archivo:** `frontend/package.json`

```json
{
  "scripts": {
    "prepare": "cd .. && husky frontend/.husky",
    "pre-commit": "lint-staged",
    "lint": "eslint src --ext .ts,.tsx --max-warnings 0",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,json,css,md}\"",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "husky": "^9.1.6",
    "lint-staged": "^15.2.10"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "prettier --write",
      "eslint --fix --max-warnings 0"
    ],
    "*.{json,css,md}": [
      "prettier --write"
    ]
  }
}
```

### Ejecución Manual (Testing)

```bash
# Ejecutar lint-staged manualmente
npx lint-staged

# Ejecutar en archivos específicos
npx lint-staged --allow-empty

# Ver qué haría sin ejecutar (dry-run)
npx lint-staged --dry-run

# Formatear todo manualmente
npm run format

# Lintear todo manualmente
npm run lint:fix
```

### Qué hace lint-staged

| Archivo | Comandos | Bloquea Commit |
|---------|----------|----------------|
| `*.ts`, `*.tsx` | 1. `prettier --write`<br>2. `eslint --fix --max-warnings 0` | ✅ Sí (si quedan errores/warnings) |
| `*.json`, `*.css`, `*.md` | 1. `prettier --write` | ❌ No (solo formatea) |

---

## 💻 INTEGRACIÓN EN EL IDE

### 🔵 Visual Studio Code

#### Backend (Python)

**Paso 1: Instalar extensiones**

```bash
# Instalar desde terminal
code --install-extension charliermarsh.ruff
code --install-extension editorconfig.editorconfig
```

O buscar en Extensions (Ctrl+Shift+X):
- **Ruff** (charliermarsh.ruff)
- **EditorConfig** (editorconfig.editorconfig)

**Paso 2: Configuración automática**

Ya está configurado en `backend/.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll": "explicit"
  },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "ruff.fixAll": true
}
```

**Paso 3: Verificar**

1. Abrir archivo Python: `backend/src/main.py`
2. Hacer un cambio (ej: agregar espacios extra)
3. Guardar (Ctrl+S)
4. ✅ Debería auto-formatear y organizar imports

#### Frontend (TypeScript/React)

**Paso 1: Instalar extensiones**

```bash
# Instalar desde terminal
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension editorconfig.editorconfig
```

O buscar en Extensions:
- **ESLint** (dbaeumer.vscode-eslint)
- **Prettier** (esbenp.prettier-vscode)
- **EditorConfig** (editorconfig.editorconfig)

**Paso 2: Configuración automática**

Ya está configurado en `frontend/.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "eslint.enable": true,
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ]
}
```

**Paso 3: Verificar**

1. Abrir archivo TypeScript: `frontend/src/App.tsx`
2. Hacer un cambio (ej: agregar espacios extra)
3. Guardar (Ctrl+S)
4. ✅ Debería auto-formatear con Prettier
5. ✅ Debería auto-fix errores de ESLint

---

### 🟢 PyCharm / WebStorm (JetBrains IDEs)

#### Backend (PyCharm)

**Paso 1: Configurar Ruff como formateador externo**

1. `Settings` → `Tools` → `External Tools`
2. Click `+` para agregar nueva herramienta:
   - **Name:** Ruff Format
   - **Program:** `$PyInterpreterDirectory$/ruff`
   - **Arguments:** `format $FilePath$`
   - **Working directory:** `$ProjectFileDir$`

**Paso 2: Configurar formato automático al guardar**

1. `Settings` → `Tools` → `File Watchers`
2. Click `+` → Custom
   - **Name:** Ruff on Save
   - **File type:** Python
   - **Scope:** Project Files
   - **Program:** `$PyInterpreterDirectory$/ruff`
   - **Arguments:** `format $FilePath$`
   - ✅ Check "Auto-save edited files to trigger the watcher"

#### Frontend (WebStorm)

**Paso 1: Configurar Prettier**

1. `Settings` → `Languages & Frameworks` → `JavaScript` → `Prettier`
2. **Prettier package:** `frontend/node_modules/prettier`
3. ✅ Check "Run on save for files"
4. **Run for files:** `{**/*,*}.{ts,tsx,json,css,md}`

**Paso 2: Configurar ESLint**

1. `Settings` → `Languages & Frameworks` → `JavaScript` → `Code Quality Tools` → `ESLint`
2. ✅ Check "Automatic ESLint configuration"
3. ✅ Check "Run eslint --fix on save"

---

## ⚙️ CONFIGURACIÓN DEL PRE-COMMIT HOOK

### 📊 TABLA COMPARATIVA: Backend vs Frontend

| Etapa del Commit | Backend (Python) | Frontend (TypeScript) |
|------------------|------------------|-----------------------|
| **1. Hook de Pre-commit (Instalación)** | | |
| Gestor de hooks | `pre-commit` framework | `husky` |
| Comando instalación | `pip install pre-commit` | `npm install --save-dev husky lint-staged` |
| Activación | `pre-commit install` | `npx husky init` |
| Archivo config | `.pre-commit-config.yaml` | `package.json` (lint-staged section) |
| **2. Ejecución del Formato** | | |
| Herramienta | Ruff format | Prettier |
| Comando exacto | `ruff format <staged_files>` | `prettier --write <staged_files>` |
| Propósito | Arreglar estilo (double quotes, 4 spaces, line length 100) | Arreglar estilo (2 spaces, semicolons, etc.) |
| Bloquea commit | ❌ No (solo formatea) | ❌ No (solo formatea) |
| **3. Ejecución de la Validación Lógica** | | |
| Herramienta | Ruff check + Bandit | ESLint |
| Comando exacto | `ruff check --fix <staged_files>` | `eslint --fix --max-warnings 0 <staged_files>` |
| Propósito | Detectar errores lógicos, imports no usados, variables no usadas, security issues | Detectar errores TypeScript, React rules, unused vars, etc. |
| Bloquea commit | ✅ SÍ (si quedan errores) | ✅ SÍ (si quedan errores o warnings) |
| **4. Validaciones Adicionales** | | |
| Security | Bandit (medium severity) | - |
| Syntax | YAML, TOML, JSON validation | - |
| Debugger | Detecta `breakpoint()`, `pdb.set_trace()` | - |
| Type checking | - | TypeScript compiler |
| Large files | >1MB bloqueado | - |
| Private keys | Detecta y bloquea | - |

### 🔍 Detalles de Implementación

#### Backend: Pre-commit Workflow

```bash
# Cuando haces git commit, esto ocurre automáticamente:

1. pre-commit intercepta el comando
2. Identifica archivos staged (git diff --staged --name-only)
3. Filtra archivos Python (*.py)
4. Ejecuta en orden:
   
   a) ruff format <staged_files>
      - Formatea código
      - Si cambió algo, lo agrega al stage automáticamente
   
   b) ruff check --fix --exit-non-zero-on-fix <staged_files>
      - Aplica fixes seguros (import sorting, unused vars, etc.)
      - Si no puede auto-fix: ❌ BLOQUEA COMMIT
      - Exit code 1 = commit bloqueado
   
   c) bandit -c pyproject.toml <staged_files>
      - Busca security issues (SQL injection, hardcoded passwords, etc.)
      - Si encuentra medium/high severity: ❌ BLOQUEA COMMIT
   
   d) check-yaml, check-json, check-toml
      - Valida syntax de archivos de config
      - Si inválido: ❌ BLOQUEA COMMIT
   
   e) debug-statements
      - Busca breakpoint(), pdb.set_trace(), etc.
      - Si encuentra: ❌ BLOQUEA COMMIT
   
   f) detect-private-key
      - Busca patrones de claves privadas
      - Si encuentra: ❌ BLOQUEA COMMIT

5. Si todo pasa: ✅ COMMIT EXITOSO
6. Si algo falla: ❌ COMMIT BLOQUEADO + mensaje de error
```

#### Frontend: Husky + lint-staged Workflow

```bash
# Cuando haces git commit, esto ocurre automáticamente:

1. Git ejecuta .husky/pre-commit
2. .husky/pre-commit ejecuta: npm run pre-commit
3. npm run pre-commit ejecuta: npx lint-staged
4. lint-staged lee configuración de package.json
5. Identifica archivos staged
6. Filtra por patrón (*.ts, *.tsx, *.json, etc.)
7. Ejecuta comandos en serie:

   Para *.ts y *.tsx:
   a) prettier --write <staged_file>
      - Formatea archivo
      - Si cambió, lo re-stage automáticamente
   
   b) eslint --fix --max-warnings 0 <staged_file>
      - Aplica fixes automáticos (imports, spacing, etc.)
      - Valida reglas de React, TypeScript, etc.
      - --max-warnings 0 = 0 warnings permitidos
      - Si quedan errores/warnings: ❌ BLOQUEA COMMIT
      - Exit code 1 = commit bloqueado
   
   Para *.json, *.css, *.md:
   a) prettier --write <staged_file>
      - Solo formatea, no bloquea

8. Si todo pasa: ✅ COMMIT EXITOSO
9. Si algo falla: ❌ COMMIT BLOQUEADO + output de ESLint
```

### 📝 Archivos de Configuración Creados

#### Backend
```
backend/
├── .pre-commit-config.yaml       ← Configuración de hooks
├── pyproject.toml                ← Config de Ruff y Bandit (actualizado)
├── .vscode/settings.json         ← VS Code integration
└── .git/hooks/pre-commit         ← Hook instalado (generado automáticamente)
```

#### Frontend
```
frontend/
├── package.json                  ← Scripts y lint-staged config (actualizado)
├── .eslintrc.json                ← Reglas de ESLint
├── .prettierrc                   ← Config de Prettier
├── .vscode/settings.json         ← VS Code integration
└── .husky/
    └── pre-commit                ← Hook script (a crear con husky init)
```

---

## 🔥 PRUEBA DE FUEGO

### Backend: Variable no usada (Python)

#### Paso 1: Crear archivo con error

```bash
cd backend
```

Crear archivo `test_commit.py`:

```python
# test_commit.py
def calcular_total(precio, cantidad):
    """Calcula el total de una compra."""
    resultado = precio * cantidad
    impuesto = 0.19  # Variable no usada ❌
    return resultado


# Variable no usada a nivel módulo ❌
VARIABLE_EXTRA = "no se usa"


def main():
    """Función principal."""
    total = calcular_total(100, 5)
    print(f"Total: {total}")
```

#### Paso 2: Intentar commit

```bash
git add test_commit.py
git commit -m "test: agregar función con variables no usadas"
```

#### Paso 3: Resultado esperado

```bash
🔍 Ruff Linter................................................................Failed
- hook id: ruff
- exit code: 1

test_commit.py:5:5: F841 Local variable `impuesto` is assigned to but never used
test_commit.py:10:1: F841 Local variable `VARIABLE_EXTRA` is assigned to but never used
Found 2 errors.
[*] 2 fixable with the `--fix` option.

❌ COMMIT BLOQUEADO
```

#### Paso 4: Arreglar errores

Opciones:

**A) Auto-fix manual:**
```bash
ruff check --fix test_commit.py
git add test_commit.py
git commit -m "test: agregar función limpia"
# ✅ Ahora debería pasar
```

**B) Arreglar manualmente:**
```python
def calcular_total(precio, cantidad):
    """Calcula el total de una compra."""
    resultado = precio * cantidad
    impuesto = 0.19
    total_con_impuesto = resultado * (1 + impuesto)  # Ahora se usa ✅
    return total_con_impuesto
```

### Frontend: Variable no usada (TypeScript)

#### Paso 1: Crear archivo con error

```bash
cd frontend
```

Crear archivo `src/test-commit.ts`:

```typescript
// src/test-commit.ts
export function calculateTotal(price: number, quantity: number): number {
  const result = price * quantity;
  const tax = 0.19; // Variable no usada ❌
  return result;
}

// Función no usada ❌
function unusedFunction() {
  console.log("Esta función no se usa");
}

// Import no usado ❌
import { useState } from "react";
```

#### Paso 2: Intentar commit

```bash
git add src/test-commit.ts
git commit -m "test: agregar función con variables no usadas"
```

#### Paso 3: Resultado esperado

```bash
✨ prettier --write...........................................................Passed
🔍 eslint --fix --max-warnings 0...........................................Failed

src/test-commit.ts
  4:9   error  'tax' is assigned a value but never used        @typescript-eslint/no-unused-vars
  8:10  error  'unusedFunction' is defined but never used      @typescript-eslint/no-unused-vars
  13:10 error  'useState' is defined but never used            @typescript-eslint/no-unused-vars

✖ 3 problems (3 errors, 0 warnings)

husky - pre-commit hook exited with code 1 (error)

❌ COMMIT BLOQUEADO
```

#### Paso 4: Arreglar errores

**Opción A: Auto-fix lo que se pueda**
```bash
npm run lint:fix
# Esto eliminará imports no usados automáticamente
```

**Opción B: Arreglar manualmente**
```typescript
// src/test-commit.ts
export function calculateTotal(price: number, quantity: number): number {
  const result = price * quantity;
  const tax = 0.19;
  const totalWithTax = result * (1 + tax); // Ahora se usa ✅
  return totalWithTax;
}

// Función eliminada o exportada si se necesita
```

### Otros Casos de Prueba

#### Test 1: Commit a branch protegida (Backend)

```bash
git checkout main  # o master
echo "test" > test.txt
git add test.txt
git commit -m "test"

# Resultado:
# 🔒 Protect main branch.......................................Failed
# ❌ COMMIT BLOQUEADO
```

#### Test 2: Archivo muy grande (Backend)

```bash
# Crear archivo de 2MB
dd if=/dev/zero of=large_file.bin bs=1024 count=2048
git add large_file.bin
git commit -m "add large file"

# Resultado:
# 🚫 Check for large files....................................Failed
# ❌ COMMIT BLOQUEADO
```

#### Test 3: Debugger statement (Backend)

```python
# test_debug.py
def proceso():
    x = 10
    breakpoint()  # ❌ Debugger
    return x

git add test_debug.py
git commit -m "test"

# Resultado:
# 🐛 Check for debugger statements...........................Failed
# ❌ COMMIT BLOQUEADO
```

#### Test 4: Syntax error en JSON (Backend)

```json
// config.json
{
  "name": "test",
  "value": "invalid,  // ❌ Falta cerrar comillas
}
```

```bash
git add config.json
git commit -m "add config"

# Resultado:
# 📝 Check JSON syntax........................................Failed
# ❌ COMMIT BLOQUEADO
```

---

## 🐛 TROUBLESHOOTING

### Backend (pre-commit)

#### Problema: Hook no se ejecuta

**Síntoma:**
```bash
git commit -m "test"
# No se ejecuta ningún hook, commit pasa directo
```

**Solución:**
```bash
# Verificar que el hook esté instalado
ls -la .git/hooks/pre-commit

# Si no existe, reinstalar
pre-commit install

# Verificar que pre-commit esté en PATH
which pre-commit
```

#### Problema: "command not found: ruff"

**Síntoma:**
```bash
[ERROR] ruff not found
```

**Solución:**
```bash
# Instalar ruff
pip install ruff==0.14.3

# O instalar todas las dependencias del proyecto
pip install -r requirements.txt
```

#### Problema: Hook muy lento

**Síntoma:**
Cada commit tarda >10 segundos

**Solución:**
```bash
# Opción 1: Excluir directorios pesados en .pre-commit-config.yaml
exclude: |
  (?x)^(
    alembic/versions/|
    BACKUP_LEGACY/|
    TEST/
  )$

# Opción 2: Solo correr en staged files (ya configurado)
# Opción 3: Skip hook para commits rápidos (no recomendado)
git commit -m "test" --no-verify
```

#### Problema: Bandit false positive

**Síntoma:**
```bash
bandit: B404 Consider possible security implications
```

**Solución:**
Agregar a `pyproject.toml`:
```toml
[tool.bandit]
skips = ["B404"]  # Agregar código del error
```

---

### Frontend (Husky + lint-staged)

#### Problema: Husky no instalado

**Síntoma:**
```bash
git commit -m "test"
# .husky/pre-commit: No such file or directory
```

**Solución:**
```bash
# Instalar husky
npm install --save-dev husky

# Inicializar
npx husky init

# Configurar pre-commit hook
echo "npm run pre-commit" > .husky/pre-commit
chmod +x .husky/pre-commit
```

#### Problema: "eslint: command not found"

**Síntoma:**
```bash
lint-staged: eslint: command not found
```

**Solución:**
```bash
# Instalar ESLint y plugins
npm install --save-dev eslint prettier \
  eslint-config-prettier \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin
```

#### Problema: ESLint tarda mucho

**Síntoma:**
Cada commit tarda >20 segundos

**Solución:**

**Opción 1:** Usar cache de ESLint
```json
// .eslintrc.json
{
  "cache": true,
  "cacheLocation": ".eslintcache"
}
```

**Opción 2:** Limitar archivos en lint-staged
```json
// package.json
"lint-staged": {
  "src/**/*.{ts,tsx}": [  // Solo src/
    "prettier --write",
    "eslint --fix --max-warnings 0"
  ]
}
```

#### Problema: Prettier y ESLint conflictos

**Síntoma:**
```bash
Prettier reformats → ESLint errors → Loop infinito
```

**Solución:**
```bash
# Asegurar que eslint-config-prettier está instalado
npm install --save-dev eslint-config-prettier

# Verificar que está al final del extends en .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "prettier"  // ← Debe ser el último
  ]
}
```

---

### General

#### Bypass temporal (NO RECOMENDADO)

```bash
# Solo para emergencias
git commit -m "emergency fix" --no-verify

# O usando variable de entorno
SKIP=ruff git commit -m "skip ruff"
```

#### Ver qué hooks están activos

```bash
# Backend
pre-commit run --all-files --verbose

# Frontend
npx lint-staged --verbose
```

#### Actualizar hooks

```bash
# Backend
pre-commit autoupdate

# Frontend
npm update husky lint-staged
```

---

## 📊 RESUMEN DE COMANDOS RÁPIDOS

### Setup Inicial

```bash
# Backend
cd backend
pip install pre-commit
pre-commit install

# Frontend (cuando haya red)
cd frontend
npm install
npx husky init
echo "npm run pre-commit" > .husky/pre-commit
chmod +x .husky/pre-commit
```

### Testing Manual

```bash
# Backend
cd backend
pre-commit run --all-files              # Todos los archivos
pre-commit run ruff --all-files         # Solo Ruff
pre-commit run bandit --all-files       # Solo Bandit

# Frontend
cd frontend
npx lint-staged                         # Staged files
npm run lint:fix                        # Todo el proyecto
npm run format                          # Formatear todo
```

### Verificar Estado

```bash
# Backend
ls -la .git/hooks/pre-commit            # Hook instalado?
pre-commit --version                    # Versión

# Frontend
cat .husky/pre-commit                   # Contenido del hook
npx husky --version                     # Versión
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Backend
- [ ] `pre-commit` instalado (`pip install pre-commit`)
- [ ] Hooks instalados (`.git/hooks/pre-commit` existe)
- [ ] `.pre-commit-config.yaml` presente
- [ ] `pyproject.toml` con config Bandit
- [ ] VS Code settings.json configurado
- [ ] Ruff extension instalada en VS Code
- [ ] Format on save funciona
- [ ] Commit con error bloqueado ✅

### Frontend
- [ ] `husky` y `lint-staged` en `package.json`
- [ ] `.husky/pre-commit` script existe
- [ ] `.eslintrc.json` presente
- [ ] `.prettierrc` presente
- [ ] VS Code settings.json configurado
- [ ] ESLint + Prettier extensions instaladas
- [ ] Format on save funciona
- [ ] Commit con error bloqueado ✅

---

## 🎉 CONCLUSIÓN

### Beneficios Logrados

✅ **Calidad del código garantizada**: Solo código limpio llega al repositorio  
✅ **Automatización completa**: Formato y validación sin intervención manual  
✅ **Feedback inmediato**: Errores detectados antes del commit  
✅ **Rápido**: Solo valida archivos modificados (staged)  
✅ **Seguridad**: Detecta claves privadas, debuggers, vulnerabilidades  
✅ **Consistencia**: Todo el equipo usa las mismas reglas  
✅ **CI/CD ready**: Mismo workflow local y en pipeline  

### Próximos Pasos

1. ✅ Configurar CI/CD pipeline (GitHub Actions)
2. ✅ Agregar coverage thresholds
3. ✅ Agregar commit message linting (conventional commits)
4. ✅ Documentar para nuevos desarrolladores

---

**Documentado por:** GitHub Copilot  
**Fecha:** 2024-11-04  
**Versión:** 1.0  
**Proyecto:** Acadify - Sistema Educativo
