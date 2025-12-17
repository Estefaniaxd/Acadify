# 📦 Procedimientos Almacenados - Acadify

## 🚀 Instalación Rápida

```bash
cd backend/database
./install_procedures.sh
```

El script detectará automáticamente la configuración de `.env` o te pedirá las credenciales.

## 📋 Procedimientos Disponibles

### 1. `sp_obtener_estadisticas_usuario`
**Propósito**: Obtiene estadísticas completas de un estudiante

```sql
SELECT * FROM sp_obtener_estadisticas_usuario('uuid-del-usuario');
```

**Retorna**:
- `total_curso`: Cantidad de cursos inscritos
- `total_tareas_asignadas`: Tareas asignadas
- `tareas_completadas`: Tareas entregadas
- `tareas_pendientes`: Tareas por entregar
- `promedio_calificaciones`: Promedio de notas
- `total_puntos`: Puntos de gamificación
- `nivel_actual`: Nivel actual
- `insignias_obtenidas`: Cantidad de insignias
- `racha_actual`: Días consecutivos de actividad

---

### 2. `sp_obtener_estadisticas_institucion`
**Propósito**: Métricas generales de una institución

```sql
SELECT * FROM sp_obtener_estadisticas_institucion('uuid-institucion');
```

**Retorna**:
- `total_coordinadores`: Cantidad de coordinadores
- `total_docentes`: Cantidad de docentes
- `total_estudiantes`: Cantidad de estudiantes
- `total_programas`: Programas académicos
- `total_cursos`: Cursos totales
- `cursos_activos`: Cursos con estudiantes
- `tasa_aprobacion`: Porcentaje de aprobación

---

### 3. `sp_registrar_auditoria`
**Propósito**: Registrar acciones críticas del sistema

```sql
SELECT sp_registrar_auditoria(
    'uuid-usuario'::UUID,
    'DELETE'::VARCHAR,
    'Usuario'::VARCHAR,
    'uuid-registro-eliminado'::UUID,
    'Eliminó cuenta de estudiante'::TEXT,
    '192.168.1.100'::VARCHAR
);
```

**Parámetros**:
- `p_usuario_id`: Usuario que realiza la acción
- `p_accion`: Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, etc.)
- `p_tabla_afectada`: Tabla o módulo afectado
- `p_registro_id`: ID del registro afectado
- `p_detalles`: Descripción adicional (opcional)
- `p_ip_address`: IP del usuario (opcional)

---

### 4. `sp_invalidar_sesiones_usuario`
**Propósito**: Cerrar todas las sesiones de un usuario

```sql
SELECT * FROM sp_invalidar_sesiones_usuario('uuid-usuario');
```

**Uso típico**: Cuando un usuario cambia su contraseña o se detecta actividad sospechosa.

---

### 5. `sp_obtener_dashboard_coordinador`
**Propósito**: Datos para el dashboard del coordinador

```sql
SELECT * FROM sp_obtener_dashboard_coordinador('uuid-coordinador');
```

**Retorna**:
- `institucion_nombre`: Nombre de la institución
- `total_programas`: Programas académicos
- `total_cursos`: Cursos totales
- `total_docentes`: Docentes activos
- `total_estudiantes`: Estudiantes inscritos
- `cursos_activos`: Cursos con actividad
- `estudiantes_activos_mes`: Estudiantes que accedieron en 30 días
- `tareas_pendiente_revision`: Tareas sin calificar

---

### 6. `sp_obtener_top_estudiantes`
**Propósito**: Ranking de estudiantes por puntos

```sql
-- Top 10 (default)
SELECT * FROM sp_obtener_top_estudiantes();

-- Top 50
SELECT * FROM sp_obtener_top_estudiantes(50);
```

**Retorna**:
- `usuario_id`: ID del usuario
- `nombres`: Nombres del estudiante
- `apellidos`: Apellidos
- `puntos_totales`: Puntos acumulados
- `nivel`: Nivel actual
- `posicion`: Posición en el ranking

---

### 7. `sp_calcular_progreso_curso`
**Propósito**: Progreso de un estudiante en un curso específico

```sql
SELECT * FROM sp_calcular_progreso_curso(
    'uuid-curso'::UUID,
    'uuid-estudiante'::UUID
);
```

**Retorna**:
- `total_tareas`: Tareas del curso
- `tareas_completadas`: Tareas entregadas
- `porcentaje_completado`: Porcentaje de avance
- `promedio_calificacion`: Promedio de notas

---

### 8. `sp_reporte_actividad_diaria`
**Propósito**: Métricas diarias del sistema

```sql
-- Actividad de hoy
SELECT * FROM sp_reporte_actividad_diaria();

-- Actividad de una fecha específica
SELECT * FROM sp_reporte_actividad_diaria('2025-12-15');
```

**Retorna**:
- `usuarios_activos`: Usuarios que accedieron
- `tareas_entregadas`: Tareas entregadas
- `nuevos_registros`: Usuarios registrados
- `sesiones_iniciadas`: Sesiones de login
- `puntos_ganados`: Puntos totales ganados

---

## 🔧 Integración con FastAPI

Ejemplo de uso en un endpoint:

```python
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.api.deps import get_db

router = APIRouter()

@router.get("/stats/student/{usuario_id}")
async def get_student_stats(
    usuario_id: str,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT * FROM sp_obtener_estadisticas_usuario(:usuario_id)
    """)
    result = db.execute(query, {"usuario_id": usuario_id}).fetchone()
    
    return {
        "total_cursos": result.total_curso,
        "tareas_completadas": result.tareas_completadas,
        "promedio": float(result.promedio_calificaciones),
        # ... resto de campos
    }
```

---

## 📊 Ejemplos de Uso Completos

### Dashboard de Administrador

```sql
-- Obtener actividad de hoy
SELECT * FROM sp_reporte_actividad_diaria(CURRENT_DATE);

-- Top 10 estudiantes
SELECT * FROM sp_obtener_top_estudiantes(10);
```

### Dashboard de Coordinador

```sql
-- Obtener datos completos del dashboard
SELECT * FROM sp_obtener_dashboard_coordinador('uuid-coordinador');

-- Ver estadísticas de la institución
SELECT * FROM sp_obtener_estadisticas_institucion(
    (SELECT institucion_id 
     FROM "InstitucionCoordinador" ic
     INNER JOIN "Coordinador" c ON ic.coordinador_id = c.coordinador_id
     WHERE c.usuario_id = 'uuid-coordinador'
     LIMIT 1)
);
```

### Dashboard de Estudiante

```sql
-- Ver mis estadísticas
SELECT * FROM sp_obtener_estadisticas_usuario('mi-uuid');

-- Ver mi progreso en un curso
SELECT * FROM sp_calcular_progreso_curso(
    'uuid-del-curso'::UUID,
    (SELECT estudiante_id FROM "Estudiante" WHERE usuario_id = 'mi-uuid')::UUID
);
```

---

## 🛡️ Auditoría

Ejemplo de registro de auditoría en acciones críticas:

```sql
-- Al eliminar un usuario
SELECT sp_registrar_auditoria(
    current_user_id,
    'DELETE',
    'Usuario',
    deleted_user_id,
    'Eliminación de cuenta solicitada por el usuario',
    request_ip
);

-- Al cambiar contraseña
SELECT sp_registrar_auditoria(
    user_id,
    'CAMBIO_PASSWORD',
    'Usuario',
    user_id,
    'Contraseña actualizada exitosamente',
    request_ip
);
```

---

## 📝 Mantenimiento

### Eliminar procedimientos

```sql
DROP FUNCTION IF EXISTS sp_obtener_estadisticas_usuario CASCADE;
DROP FUNCTION IF EXISTS sp_obtener_estadisticas_institucion CASCADE;
-- ... etc
```

### Reinstalar
```bash
./install_procedures.sh
```

---

## ✅ Verificación

Verificar que los procedimientos fueron instalados:

```sql
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name LIKE 'sp_%'
ORDER BY routine_name;
```
