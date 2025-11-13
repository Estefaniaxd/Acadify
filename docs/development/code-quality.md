# Configuración de Linting y Formateo - Acadify

## 📋 Resumen

Este proyecto utiliza herramientas profesionales de linting y formateo tanto para el backend (Python) como para el frontend (TypeScript/React).

---

## 🐍 Backend (Python)

### Herramientas
- **Ruff**: Linter y formatter ultra-rápido (reemplaza pylint, black, isort, flake8)
- Versión instalada: `0.14.3`

### Archivos de Configuración
- `pyproject.toml`: Configuración principal (150+ líneas, 50+ reglas)
- `.editorconfig`: Consistencia entre editores
- `.ruffignore`: Exclusiones de archivos
- `.vscode/settings.json`: Integración con VS Code

### Uso

#### Opción 1: Script Automatizado (Recomendado)
```bash
cd backend
python scripts/lint_and_format.py
# o directamente:
./scripts/lint_and_format.py
```

Este script ejecuta en orden:
1. ✨ Formateo de código
2. 📦 Organización de imports
3. 🔧 Aplicación de fixes automáticos
4. ✅ Verificación final

#### Opción 2: Comandos Manuales
```bash
cd backend

# Formatear código
ruff format src/ scripts/

# Organizar imports
ruff check --select I --fix

# Aplicar fixes
ruff check --fix

# Solo verificar (sin cambios)
ruff check

# Ver solo errores específicos
ruff check --select E,F,W
```

### Reglas Principales
- **Line length**: 100 caracteres
- **Indentación**: 4 espacios
- **Quotes**: Dobles (`"`)
- **Docstrings**: Estilo Google
- **Imports**: Organizados automáticamente (isort)
- **Complejidad**: Max 10 (McCabe)
- **Type hints**: Requeridos (con excepciones FastAPI)

### Ignores Estratégicos
- `D100`, `D104`: Docstrings opcionales en módulos/paquetes
- `ANN101`, `ANN102`: No requerir type hints en `self`/`cls`
- `B008`: Permitir `Depends()` en defaults de FastAPI
- `FBT001`, `FBT002`: Permitir boolean args (común en FastAPI)
- `S101`: Permitir `assert` en tests

---

## ⚛️ Frontend (TypeScript/React)

### Herramientas
- **ESLint**: Linter para TypeScript y React
- **Prettier**: Formatter de código

### Instalación

**⚠️ IMPORTANTE**: Actualmente hay problemas de red. Ejecuta cuando tengas conexión:

```bash
cd frontend
npm install --save-dev \
  eslint \
  prettier \
  eslint-config-prettier \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin \
  eslint-plugin-import \
  eslint-plugin-jsx-a11y
```

### Archivos de Configuración
- `.eslintrc.json`: Configuración de ESLint (TypeScript strict)
- `.prettierrc`: Configuración de Prettier
- `.prettierignore`: Exclusiones de formateo
- `.editorconfig`: Consistencia entre editores
- `.vscode/settings.json`: Integración con VS Code
- `package.json`: Scripts de linting/formateo

### Uso

#### Scripts NPM
```bash
cd frontend

# Linting
npm run lint              # Ver errores
npm run lint:fix          # Corregir automáticamente

# Formateo
npm run format            # Formatear todo
npm run format:check      # Solo verificar

# Type checking
npm run type-check        # Verificar tipos TypeScript
```

### Reglas Principales
- **Print width**: 100 caracteres
- **Indentación**: 2 espacios
- **Quotes**: Dobles (`"`)
- **Semi**: Requerido (`;`)
- **Trailing comma**: ES5
- **Import order**: Automático (react primero)
- **React**: Sin prop-types (usando TypeScript)
- **Hooks**: Rules of hooks estrictas
- **Accessibility**: jsx-a11y recomendado

### Configuración ESLint
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/typescript",
    "plugin:jsx-a11y/recommended",
    "prettier"  // Debe ser el último
  ]
}
```

---

## 🔧 VS Code Integration

### Backend
- **Format on save**: ✅ Activado
- **Formatter**: Ruff
- **Organize imports on save**: ✅ Activado
- **Fix all on save**: ✅ Activado

### Frontend
- **Format on save**: ✅ Activado
- **Formatter**: Prettier
- **ESLint fix on save**: ✅ Activado
- **Organize imports on save**: ✅ Activado

### Extensiones Recomendadas
1. **Backend**:
   - Ruff (charliermarsh.ruff)
   - Python (ms-python.python)
   - EditorConfig (editorconfig.editorconfig)

2. **Frontend**:
   - ESLint (dbaeumer.vscode-eslint)
   - Prettier (esbenp.prettier-vscode)
   - EditorConfig (editorconfig.editorconfig)

---

## 📁 Estructura de Configuraciones

```
backend/
  ├── pyproject.toml          # Configuración Ruff (principal)
  ├── .editorconfig           # Consistencia editores
  ├── .ruffignore             # Exclusiones
  ├── .vscode/
  │   └── settings.json       # VS Code backend
  └── scripts/
      └── lint_and_format.py  # Script automatizado

frontend/
  ├── .eslintrc.json          # Configuración ESLint
  ├── .prettierrc             # Configuración Prettier
  ├── .prettierignore         # Exclusiones
  ├── .editorconfig           # Consistencia editores
  ├── .vscode/
  │   └── settings.json       # VS Code frontend
  └── package.json            # Scripts NPM
```

---

## 🚀 Workflow Recomendado

### Antes de commit
```bash
# Backend
cd backend
./scripts/lint_and_format.py

# Frontend (después de instalar)
cd frontend
npm run lint:fix
npm run format
npm run type-check
```

### Durante desarrollo
- **VS Code**: Guardar archivo = auto-format + auto-fix
- **Pre-commit hook** (futuro): Configurar husky + lint-staged

### CI/CD (futuro)
```yaml
# Backend
- ruff check --output-format=github
- ruff format --check

# Frontend
- npm run lint
- npm run format:check
- npm run type-check
```

---

## 🎯 Beneficios

### Consistencia
- ✅ Mismo estilo en todo el código
- ✅ Configuración compartida entre desarrolladores
- ✅ Funciona en cualquier editor (VS Code, PyCharm, Vim, etc.)

### Calidad
- ✅ 50+ reglas de linting en backend
- ✅ TypeScript strict en frontend
- ✅ Security checks (bandit en backend)
- ✅ Accessibility checks (jsx-a11y en frontend)

### Productividad
- ✅ Auto-format on save
- ✅ Auto-fix de errores simples
- ✅ Scripts one-command
- ✅ Fast: Ruff es 10-100x más rápido que pylint/black

### Mantenibilidad
- ✅ Menos bugs (type checking, linting)
- ✅ Código más legible
- ✅ Imports organizados
- ✅ Complejidad controlada (max 10)

---

## 📚 Referencias

### Backend
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### Frontend
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)
- [TypeScript ESLint](https://typescript-eslint.io/)
- [React Hooks Rules](https://react.dev/reference/rules/rules-of-hooks)

---

## ❓ Troubleshooting

### Backend
**Problema**: Ruff not found
```bash
pip install ruff==0.14.3
```

**Problema**: VS Code no detecta Ruff
- Instalar extensión: `charliermarsh.ruff`
- Reload window

### Frontend
**Problema**: ESLint/Prettier not found
```bash
cd frontend
npm install  # Instala todas las dependencias
```

**Problema**: VS Code no detecta ESLint
- Instalar extensión: `dbaeumer.vscode-eslint`
- Instalar extensión: `esbenp.prettier-vscode`
- Reload window

**Problema**: Conflictos ESLint-Prettier
- ✅ Ya configurado: `eslint-config-prettier` desactiva reglas conflictivas

---

## 📝 Notas

1. **Backend completo**: ✅ Ruff 100% configurado y listo
2. **Frontend pendiente**: ⏳ Instalar dependencias cuando haya red
3. **Próximo paso**: 🎮 Sistema Avatar después de verificar linters

---

**Creado**: 2024-11-04  
**Autor**: GitHub Copilot  
**Proyecto**: Acadify - Sistema de Gestión Educativa
