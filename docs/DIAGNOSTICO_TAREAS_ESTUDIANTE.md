# 🔍 DIAGNÓSTICO: Tareas no visibles para estudiantes

## 📋 Resumen del Problema

**Síntoma**: Cuando un estudiante ingresa a un curso, el frontend muestra **cero tareas**, aunque el docente haya creado tareas en ese curso.

**Root Cause**: Bug crítico en SQL JOIN con nombre de tabla incorrecto en `tarea_service.py`.

---

## 🐛 BUG ENCONTRADO

### Ubicación
**Archivo**: `backend/src/services/academic/tarea_service.py`
**Método**: `obtener_tareas_curso()` línea ~206
**Tabla afectada**: `EstudianteGrupo` (incorrectamente escrita como `GrupoEstudiante`)

### Código Incorrecto (ANTES)
```python
grupo_query_estudiante = text("""
    SELECT gc.grupo_id FROM "GrupoCurso" gc
    JOIN GrupoEstudiante ge ON gc.grupo_id = ge.grupo_id  # ❌ TABLA NO EXISTE
    WHERE gc.curso_id = :curso_id AND ge.estudiante_id = :usuario_id
    LIMIT 1
""")
```

### Código Corregido (DESPUÉS)
```python
grupo_query_estudiante = text("""
    SELECT gc.grupo_id FROM "GrupoCurso" gc
    JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id  # ✅ TABLA CORRECTA
    WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
    LIMIT 1
""")
```

### Impacto
- **El JOIN falla silenciosamente** porque `GrupoEstudiante` no existe
- **No se encuentra el grupo_id** del estudiante
- **Se retorna HTTPException 403** "No tienes acceso a este curso"
- **El frontend muestra lista vacía** de tareas

---

## ✅ FIX APLICADO

✅ **Línea 206 actualizada**: `GrupoEstudiante` → `"EstudianteGrupo"`

### Verificación de Bug
```bash
# Buscar otros usos del nombre incorrecto
grep -r "GrupoEstudiante" backend/src/

# Resultado: NO ENCONTRADO (solo había en tarea_service.py)
```

---

## 🔬 DIAGNÓSTICO TÉCNICO COMPLETO

### Estructura de Datos

```
Usuario (estudiante)
    ↓ (estudiante_id)
EstudianteGrupo
    ↓ (grupo_id)
Grupo
    ↓ (grupo_id)
GrupoCurso
    ↓ (curso_id)
Curso
    
tareas
    ↓ (grupo_id)
Grupo
```

### SQL Query Correcta
```sql
-- Para obtener tareas de un estudiante:
SELECT t.* FROM tareas t
WHERE t.grupo_id IN (
    SELECT gc.grupo_id
    FROM "GrupoCurso" gc
    JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
    WHERE gc.curso_id = :curso_id 
      AND eg.estudiante_id = :usuario_id
)
```

### Datos de Test
```
Estudiante: seed_a99e64_0a4daabb@test.unan.local
Usuario ID: 3961a106-4c5c-45a3-b326-116ac9753187
Grupo: 99ab10f3-db80-4f91-8600-cfbc8442fb20 (Grupo java)
Curso: a99e64e5-e6d5-4d0d-8a9d-56be34b5fb8c (java)

✅ Inscripción: EstudianteGrupo → grupo_id = 99ab10f3-db80-4f91-8600-cfbc8442fb20
✅ Grupo en Curso: GrupoCurso → grupo_id a curso_id mapeado
✅ Tareas en Grupo: 1 tarea "JVM" con grupo_id = 99ab10f3-db80-4f91-8600-cfbc8442fb20
```

---

## 🧪 Test para Verificar Fix

```python
# Test: Login estudiante → Obtener tareas del curso
import httpx

client = httpx.Client()

# 1. Login
resp = client.post("http://localhost:8000/api/auth/login", json={
    "correo_institucional": "seed_a99e64_0a4daabb@test.unan.local",
    "password": "Juanito243019@"
})
token = resp.json()["access_token"]

# 2. Obtener tareas
resp = client.get(
    "http://localhost:8000/api/cursos/tareas/a99e64e5-e6d5-4d0d-8a9d-56be34b5fb8c/tareas",
    headers={"Authorization": f"Bearer {token}"}
)

# ANTES DEL FIX: Status 403 "No tienes acceso a este curso"
# DESPUÉS DEL FIX: Status 200 + JSON con 1 tarea (JVM)
print(resp.status_code, resp.json())
```

---

## 🎯 Pasos Siguientes (Prioridad)

### 1. ✅ **CRÍTICO: Reiniciar Backend**
```bash
cd backend
# Matar proceso anterior
pkill -f "uvicorn src.main"
# Reiniciar con cambios
uvicorn src.main:app --reload --port 8000
```

### 2. ✅ **VERIFICAR: Test en Frontend**
```
1. Ir a http://localhost:5173
2. Logout + Login como estudiante (seed_a99e64_0a4daabb@test.unan.local / Juanito243019@)
3. Ir al curso Java
4. Verificar que aparece la tarea "JVM" (ANTES: vacío, DESPUÉS: 1 tarea)
```

### 3. ⏳ **PRÓXIMOS BUGS A REVISAR**

#### a) Edición de Tareas (Probablemente no funciona)
- **Síntoma**: El frontend probablemente no tiene botón de editar o no llamar a endpoint PUT
- **Verificar**: `backend/src/api/routes/academic/tareas.py` línea ~149 (PUT handler)

#### b) Entrega de Tareas (Probablemente no funciona)
- **Síntoma**: Estudiante no puede subir solución
- **Verificar**: Endpoint POST `/entregas` en backend
- **Revisar**: ¿Frontend tiene formulario para subir archivo?

#### c) Calificación de Entregas
- **Síntoma**: Docente no puede calificar entregas
- **Verificar**: Endpoint PATCH `/calificar` 
- **Revisar**: ¿Se crean game_points al calificar?

#### d) Game Points
- **Síntoma**: Al calificar no se otorgan puntos
- **Verificar**: Si `gamification_service` se llama en `tarea_service.calificar_entrega()`

#### e) IA Feedback
- **Síntoma**: Botón no funciona o genera error
- **Verificar**: Endpoint POST `/ia-feedback` en `ia_tareas.py`
- **OPTIMIZAR**: Cambiar JSON a JSONL para ahorrar tokens

---

## 📊 Verificación en BD

```bash
# Confirmar estructura correcta
PGPASSWORD=243019 psql -U postgres -d acadify_db << 'SQL'
-- Verificar que tablas existen
SELECT tablename FROM pg_tables WHERE tablename LIKE '%Grupo%' OR tablename LIKE '%Estudiante%';

-- Verificar relaciones del estudiante de test
SELECT eg.estudiante_id, eg.grupo_id, gc.curso_id, c.nombre
FROM "EstudianteGrupo" eg
JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
JOIN "Curso" c ON gc.curso_id = c.curso_id
WHERE eg.estudiante_id = '3961a106-4c5c-45a3-b326-116ac9753187';

-- Verificar tareas en el grupo
SELECT * FROM tareas WHERE grupo_id = '99ab10f3-db80-4f91-8600-cfbc8442fb20';
SQL
```

---

## 🔄 RESUMEN CAMBIOS

| Archivo | Línea | Cambio | Razón |
|---------|-------|--------|-------|
| `tarea_service.py` | ~206 | `GrupoEstudiante` → `"EstudianteGrupo"` | Nombre de tabla incorrecto |
| `tarea_service.py` | ~207 | `ge.estudiante_id` → `eg.estudiante_id` | Actualizar alias de tabla |

---

## 📝 Notas Importantes

1. **Este bug solo afecta a estudiantes** - Docentes ven tareas porque usan diferente query (docente_id en GrupoCurso)
2. **El error era silencioso** - No lanzaba excepción, simplemente no retornaba grupo_id
3. **No había otros usos del nombre incorrecto** - Solo era este uno
4. **El fix es simple pero crítico** - Solo 2 caracteres de diferencia

---

**Status**: ✅ FIX APLICADO - Pendiente: Reiniciar backend y verificar en frontend

**Tiempo de fix**: < 5 minutos  
**Impacto**: Crítico - Bloquea a todos los estudiantes  
**Riesgo**: Bajo - Simple corrección de nombre de tabla
