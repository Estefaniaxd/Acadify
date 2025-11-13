# 🎯 Plan Maestro de Sincronización - Modelos vs BD

**Fecha:** 4 de noviembre de 2025  
**Objetivo:** Sincronizar modelos y BD sin romper funcionalidades  
**Principios:** SOLID, Clean Code, Zero Breaking Changes

---

## 📊 1. DIAGNÓSTICO COMPLETO

### ✅ Estado Actual de Sincronización

| Modelo | Campos BD | Campos Modelo | Match | Estado |
|--------|-----------|---------------|-------|--------|
| **Evaluacion** | 82 | 82 | ✅ | PERFECTO |
| **PreguntaEvaluacion** | 42 | 42 | ✅ | PERFECTO |
| **IntentoEvaluacion** | 68 | 68 | ✅ | PERFECTO |
| **RespuestaEstudiante** | 47 | 47 | ✅ | PERFECTO |
| **BancoPregunta** | 33 | 33 | ✅ | PERFECTO |
| **Tarea** | 45 | 44 | ⚠️ | 1 campo diferencia |
| **EntregarTarea** | - | - | ❌ | Tablename incorrecto |
| **Clase** | 21 | 21 | ✅ | PERFECTO |
| **Curso** | 64 | 64 | ✅ | PERFECTO |
| **Grupo** | 56 | 56 | ✅ | PERFECTO |
| **PeriodoAcademico** | 49 | 49 | ✅ | PERFECTO |
| **Inscripcion** | 94 | 94 | ✅ | PERFECTO |
| **Mensaje** | 29 | 29 | ✅ | PERFECTO |
| **Videollamada** | 16 | 16 | ✅ | PERFECTO |
| **RachaUsuario** | 22 | 22 | ✅ | PERFECTO |
| **TiendaItem** | 33 | 33 | ✅ | PERFECTO |

**Métricas:**
- ✅ **15/17 modelos PERFECTOS** (88.2%)
- ⚠️ **1 modelo con 1 campo diferencia** (5.9%)
- ❌ **1 modelo con tablename incorrecto** (5.9%)

---

## 🚨 2. PROBLEMAS IDENTIFICADOS

### 🔴 CRÍTICO 1: CRUDs de Evaluaciones ROTOS (5/5)

**Estado Actual:**
```
❌ crud_banco_pregunta    → ImportError: cannot import 'Examen'
❌ crud_examen            → ImportError: cannot import 'Examen'
❌ crud_intento           → ImportError: cannot import 'Examen'
❌ crud_pregunta          → ImportError: cannot import 'Examen'
❌ crud_respuesta         → ImportError: cannot import 'Examen'
```

**Causa Raíz:**
```python
# Los CRUDs buscan:
from src.models.evaluaciones import Examen  # ❌ NO EXPORTADO

# Solo existe:
from src.models.evaluaciones import ExamenDeprecated  # ⚠️
from src.models.evaluaciones import Evaluacion  # ✅
```

**Impacto:**
- 🚨 **Sistema de evaluaciones 100% NO FUNCIONAL**
- 🚨 **5 CRUDs no se pueden importar**
- 🚨 **Endpoints de evaluaciones caídos**
- 🚨 **Servicios pueden funcionar pero CRUDs no**

---

### 🔴 CRÍTICO 2: EntregarTarea con tablename incorrecto

**Problema:**
```python
# Archivo: src/models/classes/entregar_tarea.py
class EntregarTarea(Base):
    __tablename__ = 'EntregarTarea'  # ❌
    
# BD real:
'entregas_tareas'  # ✅
```

**Impacto:**
- 🚨 **Sistema de entregas de tareas NO FUNCIONA**
- 🚨 **Cualquier operación CRUD falla**
- 🚨 **Datos no accesibles**

---

### ⚠️ IMPORTANTE 3: Tarea tiene 1 campo de diferencia

**Estado:**
- BD: 45 campos
- Modelo: 44 campos
- Diferencia: 1 campo

**Acción:** Investigar qué campo falta o sobra

---

### ⚠️ MENOR 4: ChatGrupo no se puede importar

**Error:**
```
module 'src.models.communication.chat' has no attribute 'ChatGrupo'
```

**Posibles causas:**
1. Modelo con nombre diferente en el archivo
2. No exportado en `__init__.py`
3. Archivo incorrecto

---

## ✅ 3. SISTEMAS QUE FUNCIONAN BIEN

### 🎓 Academic CRUDs (13/13) - 100%
```
✅ crud_clase
✅ crud_curso
✅ crud_curso_docente
✅ crud_estudiante_grupo
✅ crud_grupo
✅ crud_grupo_curso
✅ crud_inscripcion
✅ crud_institucion
✅ crud_material_clase
✅ crud_material_curso
✅ crud_material_educativo
✅ crud_periodo_academico
✅ crud_programa
```

### 🎮 Servicios de Gamificación
```
✅ puntos_service.py
✅ racha_service.py
✅ tienda_service.py
✅ etiquetas_service.py
```

### 💬 Servicios de Comunicación
```
✅ videollamada_service.py
```

### ✅ Otros Servicios
```
✅ avatar_service.py
✅ invitation_service.py
✅ tarea_service.py
✅ inscripcion_service.py
```

---

## 🎯 4. PLAN DE SINCRONIZACIÓN (7 FASES)

### 📋 FASE 0: Investigación Pre-Cambios (30 min)

#### 0.1 Investigar campo faltante en Tarea
```python
# Script de análisis
python -c "
from sqlalchemy import create_engine, inspect
from src.core.config import settings
from src.models.academic.tarea import Tarea

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

bd_cols = {c['name'] for c in inspector.get_columns('tareas')}
model_cols = {c.name for c in Tarea.__table__.columns}

print('Campos solo en BD:', bd_cols - model_cols)
print('Campos solo en Modelo:', model_cols - bd_cols)
"
```

#### 0.2 Investigar ChatGrupo
```bash
# Buscar dónde está definido
grep -r "class ChatGrupo" src/models/communication/
```

#### 0.3 Verificar dependencias de CRUDs evaluaciones
```bash
# Buscar qué servicios usan estos CRUDs
grep -r "from src.crud.evaluaciones" src/services/
grep -r "from src.crud.evaluaciones" src/api/routes/
```

---

### 🔧 FASE 1: Fixes Críticos Inmediatos (15 min)

#### 1.1 Fix EntregarTarea (5 min) ⚠️ CRÍTICO
```python
# Archivo: src/models/classes/entregar_tarea.py
# Línea: ~20-25

# ANTES:
class EntregarTarea(Base):
    __tablename__ = 'EntregarTarea'

# DESPUÉS:
class EntregarTarea(Base):
    __tablename__ = 'entregas_tareas'
```

**Testing:**
```python
python -c "
from src.models.classes.entregar_tarea import EntregarTarea
from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

assert EntregarTarea.__tablename__ == 'entregas_tareas'
assert 'entregas_tareas' in inspector.get_table_names()
print('✅ EntregarTarea fix verificado')
"
```

#### 1.2 Fix Tarea si es necesario (10 min)
Basado en resultados de Fase 0.1

---

### 🔄 FASE 2: Actualizar CRUDs de Evaluaciones (3 horas)

**Estrategia:** Actualizar imports uno por uno, con testing incremental.

#### 2.1 crud_banco_pregunta.py (30 min)

**Análisis de imports actuales:**
```python
# Línea 11
from src.models.evaluaciones import BancoPregunta, TipoPregunta, DificultadPregunta
```

**Estado:** ✅ BancoPregunta es SHARED, no deprecated

**Acción:** Solo verificar que no haya imports internos de `Examen`

**Pasos:**
1. Leer archivo completo
2. Buscar cualquier mención de `Examen` (sin Deprecated)
3. Si encuentra, cambiar a `Evaluacion`
4. Testing

---

#### 2.2 crud_pregunta.py (45 min)

**Análisis de imports:**
```python
# Línea 11
from src.models.evaluaciones import PreguntaExamen, TipoPregunta, DificultadPregunta

# Línea 300 (interno)
from src.models.evaluaciones import RespuestaEstudiante, IntentoExamen, EstadoIntento
```

**Cambios necesarios:**
```python
# Línea 11 - CAMBIO
from src.models.evaluaciones import PreguntaEvaluacion, TipoPregunta, DificultadPregunta

# Línea 300 - CAMBIO
from src.models.evaluaciones import RespuestaEstudiante, IntentoEvaluacion, EstadoIntento
```

**Búsqueda y reemplazo en todo el archivo:**
- `PreguntaExamen` → `PreguntaEvaluacion`
- `IntentoExamen` → `IntentoEvaluacion`

**Testing:**
```python
# Test 1: Import
from src.crud.evaluaciones.crud_pregunta import crud_pregunta
print('✅ CRUD importa correctamente')

# Test 2: Métodos básicos
# (crear script de testing específico)
```

---

#### 2.3 crud_intento.py (45 min)

**Análisis de imports:**
```python
# Línea 12
from src.models.evaluaciones import (
    IntentoExamen,
    RespuestaEstudiante,
    ...
)

# Línea 340 (interno)
from src.models.evaluaciones import PreguntaExamen
```

**Cambios necesarios:**
```python
# Línea 12 - CAMBIO
from src.models.evaluaciones import (
    IntentoEvaluacion,
    RespuestaEstudiante,
    ...
)

# Línea 340 - CAMBIO
from src.models.evaluaciones import PreguntaEvaluacion
```

**Búsqueda y reemplazo:**
- `IntentoExamen` → `IntentoEvaluacion`
- `PreguntaExamen` → `PreguntaEvaluacion`

---

#### 2.4 crud_respuesta.py (45 min)

**Análisis de imports:**
```python
# Línea 13
from src.models.evaluaciones import (
    RespuestaEstudiante,
    IntentoExamen,
    ...
)

# Línea 574 (interno)
from src.models.evaluaciones import Examen
```

**Cambios necesarios:**
```python
# Línea 13 - CAMBIO
from src.models.evaluaciones import (
    RespuestaEstudiante,
    IntentoEvaluacion,
    ...
)

# Línea 574 - CAMBIO
from src.models.evaluaciones import Evaluacion
```

**Búsqueda y reemplazo:**
- `IntentoExamen` → `IntentoEvaluacion`
- `Examen` → `Evaluacion` (con cuidado en nombres de métodos)

---

#### 2.5 crud_examen.py → crud_evaluacion.py (60 min)

**Este es el más complejo:** Incluye renombrar archivo + clase

**Paso 1: Cambios de imports (15 min)**
```python
# Línea 11 - ANTES
from src.models.evaluaciones import Examen, EstadoExamen, TipoExamen

# Línea 11 - DESPUÉS
from src.models.evaluaciones import Evaluacion, EstadoExamen, TipoExamen

# Línea 295 - ANTES
from src.models.evaluaciones import PreguntaExamen

# Línea 295 - DESPUÉS
from src.models.evaluaciones import PreguntaEvaluacion

# Línea 301 - ANTES
from src.models.evaluaciones import IntentoExamen, EstadoIntento

# Línea 301 - DESPUÉS  
from src.models.evaluaciones import IntentoEvaluacion, EstadoIntento

# Línea 355 - ANTES
from src.models.evaluaciones import IntentoExamen

# Línea 355 - DESPUÉS
from src.models.evaluaciones import IntentoEvaluacion
```

**Paso 2: Renombrar clase (10 min)**
```python
# Línea ~14 - ANTES
class CRUDExamen(CRUDBase[Examen, ExamenCreate, ExamenUpdate]):

# Línea ~14 - DESPUÉS
class CRUDEvaluacion(CRUDBase[Evaluacion, EvaluacionCreate, EvaluacionUpdate]):
```

**Paso 3: Búsqueda y reemplazo en TODO el archivo (20 min)**
- `Examen` → `Evaluacion` (excepto en docstrings donde tenga sentido)
- `examen` (variable) → `evaluacion`
- `PreguntaExamen` → `PreguntaEvaluacion`
- `IntentoExamen` → `IntentoEvaluacion`

**Paso 4: Actualizar docstrings (10 min)**
```python
"""CRUD operations para el modelo Evaluacion"""
```

**Paso 5: Renombrar archivo (5 min)**
```bash
mv src/crud/evaluaciones/crud_examen.py src/crud/evaluaciones/crud_evaluacion.py
```

---

### 📝 FASE 3: Actualizar __init__.py de CRUDs (20 min)

```python
# Archivo: src/crud/evaluaciones/__init__.py

# ANTES
from .crud_examen import crud_examen
from .crud_pregunta import crud_pregunta
from .crud_intento import crud_intento
from .crud_respuesta import crud_respuesta
from .crud_banco_pregunta import crud_banco_pregunta

__all__ = [
    "crud_examen",
    "crud_pregunta",
    # ...
]

# DESPUÉS
from .crud_evaluacion import crud_evaluacion
from .crud_pregunta import crud_pregunta_evaluacion  # O mantener nombre
from .crud_intento import crud_intento_evaluacion    # O mantener nombre
from .crud_respuesta import crud_respuesta
from .crud_banco_pregunta import crud_banco_pregunta

__all__ = [
    "crud_evaluacion",
    "crud_pregunta_evaluacion",
    # ...
]
```

**Decisión de nombrado:**
- Opción A: `crud_evaluacion` (consistente con modelo)
- Opción B: `crud_examen` (compatibilidad backward)

**Recomendación:** Opción A (mejor a largo plazo)

---

### 🌐 FASE 4: Actualizar Endpoints (2 horas)

#### 4.1 Identificar endpoints afectados
```bash
grep -r "from src.crud.evaluaciones" src/api/routes/evaluaciones/
```

#### 4.2 Actualizar imports en endpoints
```python
# Antes
from src.crud.evaluaciones import examen, pregunta_examen

# Después
from src.crud.evaluaciones import evaluacion, pregunta_evaluacion
```

#### 4.3 Actualizar referencias en funciones
```python
# Antes
examen.get(db, examen_id)

# Después
evaluacion.get(db, evaluacion_id)
```

---

### 📦 FASE 5: Actualizar Schemas (1 hora)

#### 5.1 Verificar que existen schemas para NEW models
```bash
ls src/schemas/evaluaciones/
```

#### 5.2 Crear/actualizar schemas necesarios
```python
# ExamenCreate → EvaluacionCreate
# ExamenUpdate → EvaluacionUpdate
# ExamenResponse → EvaluacionResponse
```

#### 5.3 Actualizar imports en endpoints

---

### 🧪 FASE 6: Testing Completo (2 horas)

#### 6.1 Test de importación (10 min)
```python
# test_imports.py
from src.crud.evaluaciones import (
    crud_evaluacion,
    crud_pregunta_evaluacion,
    crud_intento_evaluacion,
    crud_respuesta,
    crud_banco_pregunta
)
print('✅ Todos los CRUDs se importan correctamente')
```

#### 6.2 Test de operaciones CRUD básicas (30 min)
```python
# test_crud_evaluacion.py
def test_create_evaluacion():
    # Test crear evaluación
    pass

def test_get_evaluacion():
    # Test obtener evaluación
    pass

def test_update_evaluacion():
    # Test actualizar evaluación
    pass
```

#### 6.3 Test de endpoints (1 hora)
```python
# test_evaluaciones_endpoints.py
def test_create_evaluacion_endpoint():
    # Test POST /evaluaciones
    pass

def test_list_evaluaciones_endpoint():
    # Test GET /evaluaciones
    pass
```

#### 6.4 Test de integración (20 min)
```python
# Test flujo completo:
# 1. Crear evaluación
# 2. Agregar preguntas
# 3. Crear intento
# 4. Enviar respuestas
# 5. Calificar
```

---

### 🧹 FASE 7: Limpieza y Documentación (1 hora)

#### 7.1 Eliminar modelos deprecated (30 min)
```python
# Archivo: src/models/evaluaciones/examen.py
# Eliminar:
# - class Examen
# - class PreguntaExamen  
# - class IntentoExamen
```

#### 7.2 Actualizar __init__.py de modelos (10 min)
```python
# Eliminar exports deprecated
# Mantener solo NEW models
```

#### 7.3 Audit final (10 min)
```bash
python scripts/audit_all_models_comprehensive.py
```

#### 7.4 Documentación (10 min)
- Actualizar README si es necesario
- Documentar cambios en CHANGELOG
- Actualizar diagramas de arquitectura

---

## 🎯 5. ORDEN DE EJECUCIÓN RECOMENDADO

### DÍA 1 (4 horas)
```
09:00 - 09:30  ✅ Fase 0: Investigación
09:30 - 09:45  ✅ Fase 1: Fixes críticos
09:45 - 12:45  ✅ Fase 2: CRUDs (3 horas)
```

### DÍA 2 (5 horas)
```
09:00 - 09:20  ✅ Fase 3: __init__.py
09:20 - 11:20  ✅ Fase 4: Endpoints (2h)
11:20 - 12:20  ✅ Fase 5: Schemas (1h)
14:00 - 16:00  ✅ Fase 6: Testing (2h)
```

### DÍA 3 (1 hora)
```
09:00 - 10:00  ✅ Fase 7: Limpieza y docs
```

**TOTAL:** ~10 horas distribuidas en 3 días

---

## 🛡️ 6. ESTRATEGIA DE ZERO BREAKING CHANGES

### Principios:
1. ✅ **Testing antes y después de cada cambio**
2. ✅ **Commits atómicos** (1 cambio = 1 commit)
3. ✅ **Branches para cada fase**
4. ✅ **Rollback plan** preparado
5. ✅ **Documentación de cada cambio**

### Git Strategy:
```bash
# Crear branch para sincronización
git checkout -b feature/sync-models-bd

# Crear sub-branches para cada fase
git checkout -b feature/sync-models-bd-fase1
# ... hacer cambios fase 1 ...
git commit -m "feat(models): fix EntregarTarea tablename"
git checkout feature/sync-models-bd
git merge feature/sync-models-bd-fase1

# Repetir para cada fase
```

### Rollback Plan:
```bash
# Si algo falla, revertir commit específico
git revert <commit-hash>

# O descartar cambios no commiteados
git checkout -- <file>

# O volver a branch anterior
git checkout develop
```

---

## 📊 7. MÉTRICAS DE ÉXITO

### Antes de Sincronización:
- ❌ CRUDs evaluaciones: 0/5 funcionales (0%)
- ⚠️ Modelos sincronizados: 15/17 (88%)
- ⚠️ Problemas críticos: 2

### Después de Sincronización:
- ✅ CRUDs evaluaciones: 5/5 funcionales (100%)
- ✅ Modelos sincronizados: 17/17 (100%)
- ✅ Problemas críticos: 0
- ✅ Testing: 100% cobertura en CRUDs críticos
- ✅ Documentación: Actualizada

---

## 🎯 8. CHECKLIST DE VALIDACIÓN

### Pre-Sincronización:
- [ ] Backup de BD realizado
- [ ] Branch de trabajo creado
- [ ] Investigación Fase 0 completada
- [ ] Plan revisado y aprobado

### Durante Sincronización:
- [ ] Fase 1: Fixes críticos ✓
- [ ] Fase 2: CRUDs actualizados ✓
- [ ] Fase 3: __init__.py actualizado ✓
- [ ] Fase 4: Endpoints actualizados ✓
- [ ] Fase 5: Schemas actualizados ✓
- [ ] Fase 6: Testing completo ✓
- [ ] Fase 7: Limpieza realizada ✓

### Post-Sincronización:
- [ ] Audit final < 10 problemas
- [ ] Todos los tests pasan
- [ ] Documentación actualizada
- [ ] Code review realizado
- [ ] Merge a develop
- [ ] Deploy a staging
- [ ] Testing en staging OK

---

## ✅ CONCLUSIÓN

Este plan garantiza:
- ✅ **Zero Breaking Changes** - Cambios incrementales y testeados
- ✅ **SOLID & Clean Code** - Arquitectura profesional
- ✅ **100% Sincronización** - Modelos = BD
- ✅ **Funcionalidad preservada** - Nada se rompe
- ✅ **Trazabilidad completa** - Cada cambio documentado

**Resultado final:** Sistema profesional, mantenible y 100% funcional 🚀
