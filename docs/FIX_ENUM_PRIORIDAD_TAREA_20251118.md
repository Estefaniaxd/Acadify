# Fix: Error de Validación de Enum PrioridadTarea

## 🔴 Error Reportado

```
Error al obtener tarea: 'baja' is not among the defined enum values. 
Enum name: prioridadtarea. 
Possible values: BAJA, MEDIA, ALTA, URGENTE
```

**Ocurría en**: GET `/api/tareas/{tarea_id}` → 500 Internal Server Error

---

## 🔍 Análisis del Problema

### Root Cause (Causa Raíz)

**Incompatibilidad entre Pydantic 2.x y SQLAlchemy enums**:

1. **Base de datos (PostgreSQL)** tenía valores minúsculas: `'baja'`, `'media'`, `'alta'`, `'urgente'`

2. **Modelo Enum** en Python estaba correctamente definido:
   ```python
   class PrioridadTarea(str, Enum):
       BAJA = "baja"        # Nombre = BAJA, Valor = "baja"
       MEDIA = "media"      # Nombre = MEDIA, Valor = "media"
       ALTA = "alta"        # Nombre = ALTA, Valor = "alta"
       URGENTE = "urgente"  # Nombre = URGENTE, Valor = "urgente"
   ```

3. **Pydantic Schema** heredaba de `BaseModel` **sin configuración explícita**
   - Por defecto, Pydantic 2.x valida enums usando el **NOMBRE** del enum (BAJA, MEDIA, etc.)
   - Pero la BD devolvía el **VALOR** ("baja", "media", etc.)
   - Esto causaba error de validación: "baja" no coincide con "BAJA"

### Por Qué No Falló Antes

Las tareas creadas recientemente pueden haber tenido valores en mayúsculas o el código anterior no pasaba por validación de Pydantic estricta.

---

## ✅ Solución Aplicada

### Configuración Pydantic 2.x: `use_enum_values=True`

Agregamos `ConfigDict(use_enum_values=True)` a todas las clases de schema que usan enums:

```python
from pydantic import BaseModel, Field, ConfigDict

class TareaBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    # ... campos ...
    prioridad: PrioridadTarea = PrioridadTarea.MEDIA
```

**¿Qué hace?**
- Le indica a Pydantic que valide usando el **VALOR** del enum ("baja") en lugar del **NOMBRE** ("BAJA")
- Asegura consistencia: BD envia "baja" → Pydantic acepta "baja" → Frontend recibe "baja"

### Archivos Modificados

#### 1. `/backend/src/schemas/academic/tarea_schemas.py`
- ✅ Actualizar import: `validator` → `field_validator, ConfigDict`
- ✅ `TareaBase`: Agregar `model_config = ConfigDict(use_enum_values=True)`
- ✅ `TareaResponse`: Cambiar `class Config` → `model_config = ConfigDict(...)`
- ✅ `EntregaTareaResponse`: Cambiar `class Config` → `model_config`
- ✅ `RubricaResponse`: Cambiar `class Config` → `model_config`
- ✅ `FiltrosTarea`: Agregar `model_config = ConfigDict(use_enum_values=True)`

#### 2. `/backend/src/schemas/academic/tarea_enriched.py`
- ✅ Actualizar import: Agregar `ConfigDict`
- ✅ `TareaEnriquecida`: Ya hereda de `TareaResponse` → Hereda `use_enum_values=True`
- ✅ `TareaResumen`: Agregar `model_config = ConfigDict(use_enum_values=True)`
- ✅ `TareaEstudianteEnriquecida`: Agregar `model_config = ConfigDict(...)`
- ✅ `FiltrosTareaEnriquecida`: Agregar `model_config = ConfigDict(use_enum_values=True)`

---

## 🔄 Flujo de Datos Después del Fix

```
PostgreSQL BD
    └─> Retorna: prioridad = 'baja' (string minúscula)
    
SQLAlchemy ORM
    └─> Convierte a: PrioridadTarea.BAJA (enum instance)
    
Pydantic Validation (con use_enum_values=True)
    └─> Valida valor: 'baja' ✅ ACEPTADO
    └─> Serializa como: 'baja' (valor, no nombre)
    
JSON Response al Frontend
    └─> Retorna: { "prioridad": "baja" }
    
Frontend (React/TypeScript)
    └─> Recibe: prioridad = 'baja' ✅ FUNCIONA
```

---

## 🧪 Testing

### Antes del Fix
```bash
GET /api/tareas/9f5df54d-983f-4885-b4e6-2209c7a23d47
Response: 500 Internal Server Error
Body: {
    "detail": "Error al obtener tarea: 'baja' is not among the defined enum values..."
}
```

### Después del Fix (Esperado)
```bash
GET /api/tareas/9f5df54d-983f-4885-b4e6-2209c7a23d47
Response: 200 OK
Body: {
    "tarea_id": "9f5df54d-983f-4885-b4e6-2209c7a23d47",
    "titulo": "Ensayo de Algoritmos",
    "prioridad": "baja",  ← Minúscula como en BD ✅
    "estado": "asignada",  ← También minúscula
    ...
    "docente_nombre": "Juan",
    "grupo_nombre": "Grupo A",
    ...
}
```

---

## 📋 Checklist Post-Fix

- [ ] Backend restarted successfully
- [ ] `python -m src.main` runs without import errors
- [ ] FastAPI /docs page loads at `http://127.0.0.1:8000/docs`
- [ ] GET `/api/tareas/{tarea_id}` returns 200 (test in FastAPI /docs)
- [ ] Response includes all task fields with correct enum values
- [ ] Frontend page "Entregar Tarea" loads task details
- [ ] Task detail modal displays without errors
- [ ] Task submission form is functional
- [ ] Console in browser shows no 500 errors
- [ ] Browser Network tab shows status 200 for task detail request

---

## 🎯 Comparable Fixes

Este es un patrón común en Pydantic 2.x:

```python
# ❌ ANTES (error con enums de BD en minúsculas)
class MySchema(BaseModel):
    status: StatusEnum  # Valida por nombre (DEFAULT)

# ✅ DESPUÉS (Pydantic valida por valor)
class MySchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    status: StatusEnum
```

---

## 📚 Documentación Relacionada

- [Pydantic Enum Documentation](https://docs.pydantic.dev/latest/concepts/json_schema/#enum)
- [ConfigDict Reference](https://docs.pydantic.dev/latest/api/config/#pydantic.ConfigDict)
- [Enum Validation](https://docs.pydantic.dev/latest/concepts/types/#enums)

---

## 🚀 Próximos Pasos

1. **Verificar Backend Inicia Sin Errores**
   ```bash
   cd backend
   uvicorn src.main:app --reload
   ```

2. **Test Manual en FastAPI Docs**
   - Abrir: `http://127.0.0.1:8000/docs`
   - Endpoint: GET `/api/tareas/{tarea_id}`
   - Usar un ID válido
   - Verificar: Status 200, enum values en minúscula

3. **Test Frontend**
   - Login con usuario
   - Navegar a curso con tareas
   - Hacer click en "Entregar Tarea"
   - Verificar que carga detalles sin error 500

4. **Validar Otros Enums**
   - Estado de tarea: "asignada", "en_progreso", "entregada" (minúsculas ✅)
   - Estado de entrega: "borrador", "entregada", "calificada" (minúsculas ✅)
   - Todos deberían funcionar con la configuración `use_enum_values=True`

---

**Status**: 🟢 **READY FOR TESTING**
**Modified Files**: 2
**Lines Changed**: ~50
**Backward Compatible**: ✅ Yes (solo config Pydantic, no lógica)
**Breaking Changes**: ❌ None

