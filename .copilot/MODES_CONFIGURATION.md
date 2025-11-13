# 🎭 Modes Configuration - Copilot Agent

> **Modos operativos especializados para diferentes escenarios de desarrollo**

---

## 🎯 ¿QUÉ SON LOS MODES?

Los **modes** son configuraciones pre-definidas que cambian el comportamiento del agente según el contexto de trabajo. Cada mode ajusta:
- **Herramientas habilitadas/deshabilitadas**
- **Nivel de agresividad** en ediciones
- **Prioridades** de acción
- **Output format**

---

## 📋 MODES DISPONIBLES

### **1. 🚀 DEVELOPMENT MODE** (Default)

**Propósito**: Desarrollo activo de features nuevas o modificación de existentes.

**Comportamiento**:
- ✅ Edita archivos libremente
- ✅ Crea nuevos archivos
- ✅ Ejecuta tests automáticamente
- ✅ Aplica fixes de errores
- ✅ Sugiere refactors oportunistas

**Herramientas Principales**:
- `read_file`, `replace_string_in_file`, `create_file`
- `get_errors`, `runTests`
- `run_in_terminal`
- `manage_todo_list`

**Workflow Típico**:
```
1. Recibe tarea → crea todo list
2. Lee contexto (archivos relacionados)
3. Implementa cambios incrementalmente
4. Valida con get_errors después de cada edit
5. Corre tests relevantes
6. Marca tareas completadas
```

**Activación**:
```
Modo activo por defecto. Úsalo para:
- Crear nuevas features
- Modificar código existente
- Agregar endpoints, componentes, servicios
- Implementar lógica de negocio
```

---

### **2. 🔍 REVIEW MODE** (Read-Only)

**Propósito**: Análisis de código, code review, detección de problemas sin modificar nada.

**Comportamiento**:
- ❌ NO edita archivos
- ❌ NO crea archivos nuevos
- ✅ Lee código exhaustivamente
- ✅ Analiza patrones y arquitectura
- ✅ Sugiere mejoras (sin aplicarlas)
- ✅ Detecta code smells, anti-patterns
- ✅ Verifica convenciones y best practices

**Herramientas Principales**:
- `read_file`, `grep_search`, `semantic_search`
- `get_errors`, `list_code_usages`
- `list_dir`, `file_search`

**Output**:
- Lista de problemas encontrados (por severidad)
- Sugerencias de mejora (con rationale)
- Archivos afectados y líneas exactas
- Ejemplos de código mejorado (sin aplicar)

**Activación**:
```
"Revisa el código en [ruta] y dame un reporte de calidad"
"Analiza la arquitectura del módulo de gamificación"
"Encuentra code smells en el servicio de autenticación"
```

**Reporte Típico**:
```markdown
## 🔴 CRITICAL
- [auth_service.py:45] Contraseñas sin hash en logs
- [curso.py:102] SQL injection vulnerable

## 🟡 WARNING
- [institucion_service.py:67] Código duplicado con programa_service.py:89
- [DashboardAdmin.tsx:120] useEffect sin cleanup

## 🟢 SUGGESTION
- [Button.tsx:34] Extraer variants a constante
- [crud_curso.py:78] Agregar type hints faltantes
```

---

### **3. 🔧 REFACTOR MODE**

**Propósito**: Reestructuración de código sin cambiar funcionalidad (refactoring seguro).

**Comportamiento**:
- ✅ Edita múltiples archivos relacionados
- ✅ Extrae código duplicado
- ✅ Aplica patrones (Repository, Service Layer)
- ✅ Renombra para claridad
- ✅ **Ejecuta tests después de CADA cambio** (mandatory)
- ❌ NO agrega funcionalidad nueva

**Herramientas Principales**:
- `list_code_usages` (antes de renombrar)
- `replace_string_in_file` (cambios coordinados)
- `runTests` (validación continua)
- `get_errors`

**Refactors Comunes**:
1. **Extract Function**
   ```python
   # Antes: código duplicado en 3 lugares
   result = data['items'].filter(lambda x: x['status'] == 'active')
   
   # Después: función reutilizable
   def get_active_items(data):
       return data['items'].filter(lambda x: x['status'] == 'active')
   ```

2. **Extract Component** (React)
   ```typescript
   // Antes: JSX repetido
   <div className="...">
     <img src={user.avatar} />
     <span>{user.name}</span>
   </div>
   
   // Después: componente reutilizable
   <UserCard user={user} />
   ```

3. **Apply Repository Pattern**
   ```python
   # Antes: queries directas en service
   def get_users(db):
       return db.query(Usuario).all()
   
   # Después: CRUD repository
   class CRUDUsuario:
       def get_multi(self, db, skip=0, limit=100):
           return db.query(Usuario).offset(skip).limit(limit).all()
   ```

**Activación**:
```
"Refactoriza el código duplicado en [archivos]"
"Extrae lógica común de [service A] y [service B]"
"Aplica Repository Pattern a [crud_xxx.py]"
"Mejora nomenclatura en [componente] sin cambiar funcionalidad"
```

**Safety Protocol**:
- Tests DEBEN pasar antes y después del refactor
- Si tests fallan → rollback inmediato
- Commits pequeños y atómicos

---

### **4. 🐛 DEBUG MODE**

**Propósito**: Investigar y resolver bugs, errores, comportamientos inesperados.

**Comportamiento**:
- ✅ Analiza stack traces
- ✅ Revisa logs (api_debug.log, console)
- ✅ Reproduce error en tests
- ✅ Aplica fix mínimo necesario
- ✅ Valida fix con tests
- ❌ NO refactoriza código no relacionado

**Herramientas Principales**:
- `get_errors`, `test_failure`
- `read_file` (archivos relacionados con error)
- `run_in_terminal` (reproducir error, ver logs)
- `grep_search` (buscar código relacionado)

**Workflow Debug**:
```
1. Leer error completo (stack trace, mensaje)
2. Identificar archivo y línea exacta
3. Leer contexto (función completa, imports)
4. Buscar código relacionado (grep_search)
5. Reproducir en test (si no existe)
6. Aplicar fix quirúrgico
7. Validar con get_errors + runTests
8. Verificar no se rompió nada más
```

**Activación**:
```
"Hay un error 500 en POST /api/cursos"
"El componente UserCard crashea cuando user.avatar es null"
"Tests de auth están fallando después del último commit"
"Analiza por qué el refresh token no funciona"
```

**Tipos de Errores Comunes**:
- **Runtime**: Null pointer, undefined, type errors
- **Lógica**: Cálculos incorrectos, condiciones invertidas
- **API**: Status codes inesperados, schemas incompatibles
- **DB**: Foreign key violations, unique constraints
- **Frontend**: Hooks mal usados, memory leaks

---

### **5. 📚 DOCUMENTATION MODE**

**Propósito**: Generar, actualizar y mejorar documentación técnica.

**Comportamiento**:
- ✅ Lee código para entender funcionalidad
- ✅ Genera/actualiza docstrings, JSDoc
- ✅ Crea/actualiza archivos README.md
- ✅ Documenta APIs (OpenAPI/Swagger)
- ✅ Genera diagramas (mermaid)
- ❌ NO modifica lógica de código

**Herramientas Principales**:
- `read_file` (código a documentar)
- `replace_string_in_file` (agregar docstrings)
- `create_file` (nuevos .md)
- `list_dir` (estructura de carpetas)

**Documentación Generada**:

1. **Docstrings Python (Google Style)**
   ```python
   def create_institucion(
       db: Session,
       data: InstitucionCreate,
       admin: Usuario
   ) -> Institucion:
       """Crea una nueva institución en el sistema.
       
       Args:
           db: Sesión de base de datos SQLAlchemy.
           data: Datos de la institución a crear.
           admin: Usuario administrador que crea la institución.
       
       Returns:
           Institucion: La institución creada con ID generado.
       
       Raises:
           HTTPException: Si el código ya existe (status 400).
           HTTPException: Si el usuario no es admin (status 403).
       
       Example:
           >>> inst = create_institucion(db, data, admin_user)
           >>> print(inst.nombre)
           'Universidad Nacional'
       """
   ```

2. **JSDoc TypeScript**
   ```typescript
   /**
    * Fetches all courses with optional filters.
    * 
    * @param filters - Optional filters (category, level, status)
    * @returns Promise resolving to array of courses
    * @throws {AxiosError} If request fails
    * 
    * @example
    * ```ts
    * const courses = await courseService.getCourses({ category: 'programming' });
    * ```
    */
   async getCourses(filters?: CourseFilters): Promise<Course[]> {
     // ...
   }
   ```

3. **README.md**
   ```markdown
   # Módulo de Gamificación
   
   ## Descripción
   Sistema de puntos, logros, rachas y recompensas.
   
   ## Componentes
   - `GamificacionService`: Lógica de negocio
   - `crud_puntos.py`: Operaciones de BD
   - `LogroCard.tsx`: Componente de logro
   
   ## Flujos
   ### Otorgar Puntos
   1. Usuario completa actividad
   2. Service calcula puntos
   3. Actualiza UsuarioPuntos
   4. Verifica logros desbloqueados
   
   ## API Endpoints
   - `GET /api/gamificacion/puntos` - Puntos del usuario
   - `POST /api/gamificacion/logros/{id}/claim` - Reclamar logro
   ```

**Activación**:
```
"Documenta el módulo de gamificación"
"Agrega docstrings a todos los servicios en auth/"
"Genera README.md para el componente de avatares"
"Actualiza la documentación de la API de cursos"
```

---

### **6. 🧪 TESTING MODE**

**Propósito**: Crear y mejorar tests unitarios, de integración y E2E.

**Comportamiento**:
- ✅ Crea tests para código sin tests
- ✅ Mejora coverage de tests existentes
- ✅ Refactoriza tests frágiles
- ✅ Ejecuta tests continuamente
- ❌ NO modifica código de producción (solo tests)

**Herramientas Principales**:
- `read_file` (código a testear)
- `create_file` (nuevos test files)
- `runTests` (modo run + coverage)
- `test_failure` (debugging tests fallidos)

**Tests Generados**:

1. **Unit Test (Backend - Pytest)**
   ```python
   # tests/test_auth_service.py
   import pytest
   from src.services.auth.auth_service import AuthService
   from src.schemas.auth import LoginRequest
   
   def test_login_success(db_session, test_user):
       """Test login con credenciales válidas."""
       service = AuthService(db_session, redis_client)
       
       result = service.login(
           identifier=test_user.email,
           password="TestPassword123!",
           ip_address="127.0.0.1"
       )
       
       assert result.access_token is not None
       assert result.token_type == "bearer"
       assert result.user.email == test_user.email
   
   def test_login_invalid_password(db_session, test_user):
       """Test login con contraseña incorrecta."""
       service = AuthService(db_session, redis_client)
       
       with pytest.raises(HTTPException) as exc_info:
           service.login(
               identifier=test_user.email,
               password="WrongPassword",
               ip_address="127.0.0.1"
           )
       
       assert exc_info.value.status_code == 401
       assert "Credenciales inválidas" in exc_info.value.detail
   ```

2. **Component Test (Frontend - Vitest)**
   ```typescript
   // src/components/ui/__tests__/Button.test.tsx
   import { render, screen, fireEvent } from '@testing-library/react';
   import { Button } from '../Button';
   
   describe('Button', () => {
     it('renders children correctly', () => {
       render(<Button>Click me</Button>);
       expect(screen.getByText('Click me')).toBeInTheDocument();
     });
     
     it('calls onClick handler', () => {
       const handleClick = vi.fn();
       render(<Button onClick={handleClick}>Click</Button>);
       
       fireEvent.click(screen.getByText('Click'));
       expect(handleClick).toHaveBeenCalledOnce();
     });
     
     it('disables button when loading', () => {
       render(<Button loading>Submit</Button>);
       expect(screen.getByRole('button')).toBeDisabled();
     });
   });
   ```

**Coverage Goals**:
- **Crítico** (auth, gamificación, cursos): >80%
- **Medio** (UI components, utils): >60%
- **Bajo** (layout, estático): >40%

**Activación**:
```
"Crea tests para AuthService"
"Mejora coverage de tests en institucion_service.py"
"Genera tests E2E para flujo de login"
"Refactoriza tests de UserCard (están frágiles)"
```

---

## 🔄 SWITCH ENTRE MODES

### **Comandos de Activación**

```
# Development Mode (default)
"Implementa [feature]"
"Crea endpoint para [funcionalidad]"
"Agrega componente [nombre]"

# Review Mode
"Revisa el código en [ruta]"
"Analiza arquitectura de [módulo]"
"Dame un code review de [archivo]"

# Refactor Mode
"Refactoriza [archivo/módulo]"
"Elimina código duplicado en [rutas]"
"Aplica [patrón] a [código]"

# Debug Mode
"Hay un error en [lugar]"
"Por qué falla [test/endpoint]"
"Investiga el bug de [funcionalidad]"

# Documentation Mode
"Documenta [módulo/archivo]"
"Genera README para [feature]"
"Agrega docstrings a [service]"

# Testing Mode
"Crea tests para [código]"
"Mejora coverage de [archivo]"
"Genera tests E2E para [flujo]"
```

### **Indicadores de Mode Activo**

El agente indicará mode activo en su respuesta:
```
🚀 [DEVELOPMENT MODE]
Implementando feature de invitaciones...

🔍 [REVIEW MODE]
Analizando código en src/services/auth/...

🔧 [REFACTOR MODE]
Extrayendo código duplicado de curso_service.py y programa_service.py...
```

---

## 🎯 MODE SELECTION MATRIX

| Escenario | Mode Recomendado |
|-----------|------------------|
| Crear feature nuevo | DEVELOPMENT |
| Modificar código existente | DEVELOPMENT |
| Agregar endpoint/componente | DEVELOPMENT |
| Revisar PR antes de merge | REVIEW |
| Auditoría de código | REVIEW |
| Encontrar code smells | REVIEW |
| Eliminar duplicación | REFACTOR |
| Renombrar para claridad | REFACTOR |
| Aplicar patrón arquitectónico | REFACTOR |
| Error 500 en endpoint | DEBUG |
| Test fallando | DEBUG |
| Comportamiento inesperado | DEBUG |
| Generar docstrings | DOCUMENTATION |
| Crear/actualizar README | DOCUMENTATION |
| Documentar API | DOCUMENTATION |
| Crear tests unitarios | TESTING |
| Mejorar coverage | TESTING |
| Tests E2E | TESTING |

---

## 📊 MÉTRICAS DE ÉXITO POR MODE

### **Development Mode**
- ✅ Feature funcional sin errores
- ✅ Tests passing
- ✅ Code linted y formateado
- ✅ Type safety completo

### **Review Mode**
- ✅ Reporte completo de problemas
- ✅ Severidad correctamente asignada
- ✅ Sugerencias accionables
- ✅ Ejemplos de código mejorado

### **Refactor Mode**
- ✅ Funcionalidad idéntica (tests passing)
- ✅ Código más limpio/legible
- ✅ Duplicación eliminada
- ✅ Patrones aplicados correctamente

### **Debug Mode**
- ✅ Bug reproducido y entendido
- ✅ Fix mínimo aplicado
- ✅ Tests validando fix
- ✅ No side effects

### **Documentation Mode**
- ✅ Docstrings/JSDoc completos
- ✅ README claro y útil
- ✅ Ejemplos funcionales
- ✅ Diagramas actualizados

### **Testing Mode**
- ✅ Coverage aumentado
- ✅ Tests passing
- ✅ Edge cases cubiertos
- ✅ Tests mantenibles

---

**Versión**: 1.0.0  
**Última actualización**: Noviembre 2025
