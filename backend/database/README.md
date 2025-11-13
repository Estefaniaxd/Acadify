# Objetos de Base de Datos - Sistema Acadify

Este directorio contiene todos los objetos avanzados de PostgreSQL para el sistema Acadify: funciones, triggers y vistas que mejoran la calidad, integridad y funcionalidad del sistema.

## 📁 Estructura de Archivos

```
database/
├── 01_funciones.sql           # 11 funciones de negocio
├── 02_triggers.sql            # 10 triggers automáticos
├── 03_vistas.sql              # 7 vistas para reportes
├── apply_database_objects.py  # Script de aplicación
└── README.md                  # Esta documentación
```

## 🚀 Instalación Rápida

```bash
cd backend/database
python apply_database_objects.py
```

El script:
1. ✅ Verifica que todos los archivos SQL existan
2. ✅ Se conecta a la base de datos
3. ✅ Ejecuta en orden: funciones → triggers → vistas
4. ✅ Verifica que todo se haya creado correctamente
5. ✅ Ejecuta pruebas básicas
6. ✅ Muestra un resumen detallado

## 📦 Funciones (01_funciones.sql)

### Funciones de Auditoría

#### `actualizar_fecha_modificacion()`
**Tipo:** Función de trigger  
**Uso:** Actualiza automáticamente `fecha_actualizacion` en tablas con campos de auditoría  
**Ejemplo:**
```sql
-- No se llama directamente, se usa en triggers
CREATE TRIGGER trigger_curso_fecha_actualizacion
    BEFORE UPDATE ON "Curso"
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();
```

### Funciones de Cálculo

#### `calcular_promedio_estudiante(estudiante_id UUID)`
**Retorna:** `NUMERIC(4,2)`  
**Descripción:** Calcula el promedio general del estudiante considerando entregas calificadas e intentos de evaluación  
**Ejemplo:**
```sql
SELECT calcular_promedio_estudiante('123e4567-e89b-12d3-a456-426614174000');
-- Retorna: 4.25
```

#### `calcular_promedio_estudiante_curso(estudiante_id UUID, curso_id UUID)`
**Retorna:** `NUMERIC(4,2)`  
**Descripción:** Calcula el promedio del estudiante en un curso específico  
**Ejemplo:**
```sql
SELECT calcular_promedio_estudiante_curso(
    '123e4567-e89b-12d3-a456-426614174000',
    '987fcdeb-51a2-43d7-8f9e-123456789abc'
);
-- Retorna: 4.50
```

#### `contar_entregas_pendientes(estudiante_id UUID)`
**Retorna:** `INTEGER`  
**Descripción:** Cuenta las entregas del estudiante que aún no han sido calificadas  
**Ejemplo:**
```sql
SELECT contar_entregas_pendientes('123e4567-e89b-12d3-a456-426614174000');
-- Retorna: 3
```

#### `calcular_estadisticas_curso(curso_id UUID)`
**Retorna:** `TABLE`  
**Descripción:** Calcula estadísticas completas de un curso  
**Retorna:**
- `total_estudiantes` - Número de estudiantes inscritos
- `total_entregas` - Total de entregas realizadas
- `entregas_calificadas` - Entregas con calificación
- `entregas_pendientes` - Entregas sin calificar
- `promedio_curso` - Promedio general del curso
- `tasa_aprobacion` - Porcentaje de aprobación (>= 3.0)

**Ejemplo:**
```sql
SELECT * FROM calcular_estadisticas_curso('987fcdeb-51a2-43d7-8f9e-123456789abc');

-- Resultado:
-- total_estudiantes | total_entregas | entregas_calificadas | entregas_pendientes | promedio_curso | tasa_aprobacion
-- -------------------|----------------|----------------------|---------------------|----------------|----------------
--        25          |      150       |         120          |          30         |      3.85      |      78.50
```

### Funciones de Análisis

#### `obtener_estudiantes_riesgo(curso_id UUID, umbral_promedio NUMERIC DEFAULT 3.0)`
**Retorna:** `TABLE`  
**Descripción:** Identifica estudiantes en riesgo académico  
**Criterios de riesgo:**
- Promedio < umbral_promedio (default 3.0)
- 3 o más entregas pendientes

**Retorna:**
- `estudiante_id` - ID del estudiante
- `nombre_completo` - Nombre y apellido
- `promedio` - Promedio en el curso
- `entregas_pendientes` - Número de entregas sin calificar
- `razon` - Razón del riesgo

**Ejemplo:**
```sql
SELECT * FROM obtener_estudiantes_riesgo(
    '987fcdeb-51a2-43d7-8f9e-123456789abc',
    3.5  -- Umbral más estricto
);
```

#### `obtener_ranking_curso(curso_id UUID, limite INTEGER DEFAULT 10)`
**Retorna:** `TABLE`  
**Descripción:** Obtiene el ranking de estudiantes por promedio en un curso  
**Retorna:**
- `posicion` - Posición en el ranking
- `estudiante_id` - ID del estudiante
- `nombre_completo` - Nombre y apellido
- `promedio` - Promedio en el curso
- `total_entregas` - Total de entregas
- `entregas_calificadas` - Entregas calificadas

**Ejemplo:**
```sql
-- Top 5 estudiantes del curso
SELECT * FROM obtener_ranking_curso(
    '987fcdeb-51a2-43d7-8f9e-123456789abc',
    5
);
```

### Funciones de Validación

#### `validar_calificacion()`
**Tipo:** Función de trigger  
**Descripción:** Valida que las calificaciones estén en el rango 0.0 - 5.0  
**Uso:** Se aplica automáticamente en INSERT/UPDATE de calificaciones

#### `calcular_duracion_intento()`
**Tipo:** Función de trigger  
**Descripción:** Calcula automáticamente la duración de un intento de evaluación  
**Uso:** Se aplica automáticamente cuando se establece fecha_fin

#### `registrar_auditoria()`
**Tipo:** Función de trigger  
**Descripción:** Registra cambios en tablas críticas para auditoría  
**Uso:** Se aplica automáticamente en INSERT/UPDATE/DELETE

#### `validar_integridad_evaluacion(evaluacion_id UUID)`
**Retorna:** `TABLE(valida BOOLEAN, errores TEXT[])`  
**Descripción:** Valida la integridad de una evaluación  
**Validaciones:**
- Tiene al menos una pregunta
- La suma de puntos de preguntas coincide con calificacion_maxima
- Todas las preguntas tienen respuestas válidas

**Ejemplo:**
```sql
SELECT * FROM validar_integridad_evaluacion('abc123-...');

-- Resultado:
-- valida | errores
-- -------|--------
-- false  | {"La evaluación no tiene preguntas", "La suma de puntos no coincide"}
```

## ⚡ Triggers (02_triggers.sql)

### Triggers de Auditoría (Auto-actualización de fecha_actualizacion)

1. **trigger_curso_fecha_actualizacion** - Tabla: Curso
2. **trigger_grupo_fecha_actualizacion** - Tabla: Grupo
3. **trigger_entrega_fecha_actualizacion** - Tabla: entregas_tareas
4. **trigger_comentario_fecha_actualizacion** - Tabla: Comentario

**Comportamiento:** Actualiza automáticamente el campo `fecha_actualizacion` con `NOW()` cada vez que se modifica un registro.

### Triggers de Validación

#### **trigger_validar_calificacion_entrega**
**Tabla:** entregas_tareas  
**Evento:** BEFORE INSERT OR UPDATE OF calificacion  
**Función:** Valida que la calificación esté entre 0.0 y 5.0

#### **trigger_validar_calificacion_intento**
**Tabla:** intentos_evaluacion  
**Evento:** BEFORE INSERT OR UPDATE OF calificacion_obtenida  
**Función:** Valida que la calificación esté en el rango permitido

#### **trigger_validar_cambio_estado_entrega**
**Tabla:** entregas_tareas  
**Evento:** BEFORE UPDATE OF estado  
**Función:** Valida transiciones de estado permitidas
- No se puede cambiar el estado de una entrega calificada
- No se puede marcar como calificada sin asignar calificación

#### **trigger_validar_limite_intentos**
**Tabla:** intentos_evaluacion  
**Evento:** BEFORE INSERT  
**Función:** Valida que el estudiante no exceda el límite de intentos

### Triggers de Cálculo Automático

#### **trigger_calcular_duracion_intento**
**Tabla:** intentos_evaluacion  
**Evento:** BEFORE INSERT OR UPDATE OF fecha_inicio, fecha_fin  
**Función:** Calcula automáticamente la duración en segundos

#### **trigger_actualizar_contadores_curso**
**Tabla:** entregas_tareas  
**Evento:** AFTER INSERT OR UPDATE OR DELETE  
**Función:** Actualiza contadores y estadísticas del curso

### Triggers de Protección de Datos

#### **trigger_prevenir_eliminacion_calificada**
**Tabla:** entregas_tareas  
**Evento:** BEFORE DELETE  
**Función:** Previene la eliminación de entregas que ya han sido calificadas

#### **trigger_prevenir_modificacion_intento**
**Tabla:** intentos_evaluacion  
**Evento:** BEFORE UPDATE  
**Función:** Previene la modificación de intentos finalizados

### Triggers de Auditoría de Cambios

#### **trigger_auditoria_entregas**
**Tabla:** entregas_tareas  
**Evento:** AFTER INSERT OR UPDATE OR DELETE  
**Función:** Registra todos los cambios para auditoría

#### **trigger_auditoria_evaluaciones**
**Tabla:** evaluaciones  
**Evento:** AFTER INSERT OR UPDATE OR DELETE  
**Función:** Registra todos los cambios para auditoría

## 👁️ Vistas (03_vistas.sql)

### Vista: vista_estudiantes_desempeno
**Descripción:** Vista consolidada del desempeño de todos los estudiantes  
**Casos de uso:**
- Dashboard de administradores
- Reportes de rendimiento académico
- Identificación de estudiantes destacados

**Columnas principales:**
- `estudiante_id`, `nombre_completo`, `correo_electronico`
- `promedio_general` - Promedio calculado de todas las actividades
- `total_entregas`, `entregas_calificadas`, `entregas_pendientes`
- `promedio_entregas`, `calificacion_minima`, `calificacion_maxima`
- `total_intentos_evaluaciones`, `promedio_evaluaciones`
- `estado_desempeno` - Categorización: Excelente/Bueno/Regular/En Riesgo
- `ultima_entrega`, `ultimo_intento_evaluacion`

**Ejemplo de uso:**
```sql
-- Estudiantes con mejor desempeño
SELECT nombre_completo, promedio_general, estado_desempeno
FROM vista_estudiantes_desempeno
WHERE promedio_general >= 4.0
ORDER BY promedio_general DESC
LIMIT 10;

-- Estudiantes en riesgo
SELECT nombre_completo, promedio_general, entregas_pendientes
FROM vista_estudiantes_desempeno
WHERE estado_desempeno = 'En Riesgo'
ORDER BY promedio_general ASC;
```

### Vista: vista_cursos_estadisticas
**Descripción:** Estadísticas consolidadas de todos los cursos  
**Casos de uso:**
- Dashboard institucional
- Comparación de cursos
- Análisis de rendimiento por curso

**Columnas principales:**
- `curso_id`, `nombre_curso`, `codigo_curso`, `activo`, `estado`
- `coordinador` - Nombre del coordinador
- `total_estudiantes`, `total_grupos`, `total_tareas`, `total_evaluaciones`
- `total_entregas`, `entregas_pendientes_calificacion`
- `promedio_entregas`, `promedio_evaluaciones`
- `tasa_aprobacion` - Porcentaje de calificaciones >= 3.0
- `fecha_creacion`, `fecha_actualizacion`

**Ejemplo de uso:**
```sql
-- Cursos con mejor rendimiento
SELECT nombre_curso, total_estudiantes, promedio_entregas, tasa_aprobacion
FROM vista_cursos_estadisticas
WHERE activo = TRUE
ORDER BY tasa_aprobacion DESC, promedio_entregas DESC;

-- Cursos que requieren atención
SELECT nombre_curso, entregas_pendientes_calificacion, promedio_entregas
FROM vista_cursos_estadisticas
WHERE entregas_pendientes_calificacion > 20
   OR promedio_entregas < 3.0;
```

### Vista: vista_evaluaciones_resumen
**Descripción:** Resumen estadístico de todas las evaluaciones  
**Casos de uso:**
- Análisis de efectividad de evaluaciones
- Identificación de evaluaciones problemáticas
- Reportes de desempeño en evaluaciones

**Columnas principales:**
- `evaluacion_id`, `titulo`, `descripcion`, `tipo_evaluacion`
- `estado_examen`, `fecha_disponible`, `fecha_cierre`
- `duracion_minutos`, `intentos_maximos`, `calificacion_aprobacion`
- `nombre_curso`, `codigo_curso`
- `total_intentos`, `estudiantes_participantes`
- `intentos_completados`, `intentos_en_progreso`
- `promedio_calificacion`, `calificacion_minima`, `calificacion_maxima`
- `desviacion_estandar`
- `tasa_aprobacion`, `tasa_completitud`
- `duracion_promedio_minutos`
- `estado_actual` - Próxima/Activa/Cerrada
- `total_preguntas`, `puntos_totales`

**Ejemplo de uso:**
```sql
-- Evaluaciones activas con baja tasa de aprobación
SELECT titulo, nombre_curso, tasa_aprobacion, promedio_calificacion
FROM vista_evaluaciones_resumen
WHERE estado_actual = 'Activa'
  AND tasa_aprobacion < 60.0
ORDER BY tasa_aprobacion ASC;

-- Evaluaciones completadas con estadísticas
SELECT 
    titulo,
    estudiantes_participantes,
    tasa_completitud,
    promedio_calificacion,
    duracion_promedio_minutos
FROM vista_evaluaciones_resumen
WHERE estado_actual = 'Cerrada'
  AND intentos_completados > 0
ORDER BY fecha_cierre DESC;
```

### Vista: vista_entregas_pendientes
**Descripción:** Entregas pendientes de calificación con priorización  
**Casos de uso:**
- Dashboard de docentes
- Gestión de calificaciones pendientes
- Alertas de entregas sin revisar

**Columnas principales:**
- `entrega_id`, `fecha_entrega`, `dias_pendiente`
- `estudiante_id`, `estudiante_nombre`, `estudiante_correo`
- `tarea_id`, `nombre_tarea`, `tarea_descripcion`, `fecha_limite_entrega`
- `curso_id`, `nombre_curso`, `codigo_curso`
- `grupo_id`, `nombre_grupo`
- `comentario_entrega`, `archivo_url`, `intentos`, `estado`
- `prioridad_revision` - Alta/Media/Normal (basada en días pendientes)
- `entrega_tardia` - Boolean, indica si se entregó después de la fecha límite

**Ejemplo de uso:**
```sql
-- Entregas urgentes (más de 7 días pendientes)
SELECT 
    estudiante_nombre,
    nombre_tarea,
    nombre_curso,
    dias_pendiente,
    prioridad_revision
FROM vista_entregas_pendientes
WHERE prioridad_revision = 'Alta'
ORDER BY dias_pendiente DESC;

-- Entregas pendientes por curso
SELECT 
    nombre_curso,
    COUNT(*) as total_pendientes,
    AVG(dias_pendiente) as promedio_dias_pendientes
FROM vista_entregas_pendientes
GROUP BY nombre_curso
ORDER BY total_pendientes DESC;
```

### Vista: vista_estudiantes_riesgo
**Descripción:** Estudiantes en riesgo académico con indicadores de alerta  
**Casos de uso:**
- Sistema de alertas tempranas
- Intervención pedagógica
- Seguimiento académico

**Criterios de inclusión:**
- Promedio general < 3.5
- O 2 o más entregas pendientes

**Columnas principales:**
- `estudiante_id`, `nombre_completo`, `correo_electronico`
- `promedio_general`
- `entregas_pendientes`
- `entregas_reprobadas` - Entregas con calificación < 3.0
- `evaluaciones_reprobadas` - Intentos con calificación < 3.0
- `ultima_actividad`, `dias_sin_actividad`
- `razones_riesgo` - Array de textos explicando por qué está en riesgo
- `nivel_riesgo` - Crítico/Alto/Medio

**Niveles de riesgo:**
- **Crítico:** Promedio < 2.5 O 5+ entregas pendientes
- **Alto:** Promedio < 3.0 O 3+ entregas pendientes
- **Medio:** Promedio < 3.5 O 2+ entregas pendientes

**Ejemplo de uso:**
```sql
-- Estudiantes en riesgo crítico
SELECT 
    nombre_completo,
    promedio_general,
    entregas_pendientes,
    razones_riesgo,
    dias_sin_actividad
FROM vista_estudiantes_riesgo
WHERE nivel_riesgo = 'Crítico'
ORDER BY promedio_general ASC;

-- Estadísticas de riesgo por nivel
SELECT 
    nivel_riesgo,
    COUNT(*) as total_estudiantes,
    AVG(promedio_general) as promedio,
    AVG(entregas_pendientes) as promedio_pendientes
FROM vista_estudiantes_riesgo
GROUP BY nivel_riesgo
ORDER BY 
    CASE nivel_riesgo
        WHEN 'Crítico' THEN 1
        WHEN 'Alto' THEN 2
        WHEN 'Medio' THEN 3
    END;
```

### Vista: vista_ranking_cursos
**Descripción:** Ranking de estudiantes por curso con posición y percentil  
**Casos de uso:**
- Gamificación
- Leaderboards
- Análisis de distribución de rendimiento

**Columnas principales:**
- `curso_id`, `nombre_curso`, `codigo_curso`
- `estudiante_id`, `nombre_completo`
- `promedio_curso` - Promedio del estudiante en ese curso específico
- `posicion` - Ranking dentro del curso (1 = mejor)
- `total_estudiantes` - Total de estudiantes en el curso
- `percentil` - Percentil del estudiante (0-100)
- `total_entregas_curso`, `total_intentos_curso`

**Ejemplo de uso:**
```sql
-- Top 10 de un curso específico
SELECT 
    posicion,
    nombre_completo,
    promedio_curso,
    percentil
FROM vista_ranking_cursos
WHERE curso_id = '987fcdeb-51a2-43d7-8f9e-123456789abc'
  AND posicion <= 10
ORDER BY posicion;

-- Comparar posiciones de un estudiante en todos sus cursos
SELECT 
    nombre_curso,
    posicion,
    total_estudiantes,
    promedio_curso,
    ROUND(percentil, 2) as percentil
FROM vista_ranking_cursos
WHERE estudiante_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY promedio_curso DESC;
```

### Vista: vista_actividad_reciente
**Descripción:** Actividad reciente del sistema (últimos 7 días)  
**Casos de uso:**
- Dashboard de actividad
- Monitoreo del sistema
- Timeline de eventos

**Tipos de actividad:**
- Entregas de tareas
- Intentos de evaluación

**Columnas principales:**
- `tipo_actividad` - 'Entrega' o 'Intento Evaluación'
- `actividad_id` - ID del objeto
- `fecha_actividad`
- `estudiante` - Nombre del estudiante
- `titulo` - Nombre de la tarea/evaluación
- `curso` - Nombre del curso
- `estado` - Estado de la actividad
- `calificacion`

**Estados posibles:**
- Entregas: Pendiente/Aprobada/Reprobada
- Intentos: En Progreso/Pendiente/Aprobado/Reprobado

**Ejemplo de uso:**
```sql
-- Actividad reciente general
SELECT 
    tipo_actividad,
    fecha_actividad,
    estudiante,
    titulo,
    curso,
    estado
FROM vista_actividad_reciente
ORDER BY fecha_actividad DESC
LIMIT 20;

-- Actividad por tipo
SELECT 
    tipo_actividad,
    COUNT(*) as total,
    COUNT(CASE WHEN estado IN ('Aprobada', 'Aprobado') THEN 1 END) as aprobadas
FROM vista_actividad_reciente
GROUP BY tipo_actividad;
```

## 🧪 Testing

El script `apply_database_objects.py` incluye pruebas automáticas:

### Pruebas de Funciones
- Busca un estudiante de prueba
- Ejecuta `calcular_promedio_estudiante()`
- Ejecuta `contar_entregas_pendientes()`
- Busca un curso de prueba
- Ejecuta `calcular_estadisticas_curso()`

### Pruebas de Vistas
- Cuenta registros en cada vista
- Muestra un registro de ejemplo de cada vista

### Verificación de Objetos
- Cuenta funciones creadas en `pg_proc`
- Cuenta triggers creados en `information_schema.triggers`
- Cuenta vistas creadas en `pg_views`
- Lista todos los objetos con sus detalles

## 📊 Beneficios

### 1. **Integridad de Datos**
- ✅ Validación automática de calificaciones (0.0 - 5.0)
- ✅ Prevención de eliminación de datos calificados
- ✅ Validación de transiciones de estado
- ✅ Validación de límites de intentos

### 2. **Auditoría y Trazabilidad**
- ✅ Actualización automática de timestamps
- ✅ Registro de cambios en tablas críticas
- ✅ Historial de modificaciones

### 3. **Cálculos Consistentes**
- ✅ Funciones centralizadas para promedios
- ✅ Estadísticas estandarizadas
- ✅ Evita cálculos duplicados en el código

### 4. **Alertas Tempranas**
- ✅ Identificación automática de estudiantes en riesgo
- ✅ Priorización de entregas pendientes
- ✅ Métricas de desempeño en tiempo real

### 5. **Reportes Eficientes**
- ✅ Vistas pre-calculadas para dashboards
- ✅ Consultas optimizadas
- ✅ Datos agregados listos para usar

### 6. **Rendimiento**
- ✅ Triggers en lugar de lógica en aplicación
- ✅ Vistas materializables en el futuro
- ✅ Cálculos en base de datos (más rápido)

## 🔧 Mantenimiento

### Actualizar una función
```sql
-- Editar 01_funciones.sql
-- Luego ejecutar solo ese archivo:
psql -U postgres -d acadify_db -f 01_funciones.sql
```

### Recrear un trigger
```sql
-- Los triggers usan DROP TRIGGER IF EXISTS
-- Solo ejecutar la sección específica de 02_triggers.sql
```

### Actualizar una vista
```sql
-- Las vistas usan CREATE OR REPLACE VIEW
-- Solo ejecutar la sección específica de 03_vistas.sql
```

### Re-aplicar todo
```bash
python apply_database_objects.py
```

## 📝 Notas Importantes

1. **Orden de ejecución:** Siempre aplicar en orden: funciones → triggers → vistas
2. **Dependencias:** Los triggers dependen de las funciones, las vistas pueden usar funciones
3. **Performance:** Las vistas con muchos JOINs pueden ser lentas, considera materializarlas
4. **Backup:** Siempre haz backup antes de aplicar cambios a producción
5. **Testing:** Prueba en desarrollo antes de aplicar a producción

## 🎯 Próximos Pasos Sugeridos

1. **Vistas Materializadas:** Convertir vistas de uso frecuente a materializadas
2. **Índices Adicionales:** Agregar índices en columnas usadas en JOINs de vistas
3. **Políticas de Refresh:** Definir cuándo refrescar vistas materializadas
4. **Más Funciones:** Agregar funciones para otros cálculos comunes
5. **Notificaciones:** Usar NOTIFY/LISTEN para alertas en tiempo real
6. **Particionamiento:** Particionar tablas grandes (entregas_tareas, intentos_evaluacion)

## 📚 Referencias

- [PostgreSQL Functions](https://www.postgresql.org/docs/current/xfunc.html)
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/trigger-definition.html)
- [PostgreSQL Views](https://www.postgresql.org/docs/current/sql-createview.html)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

## ✨ Contribución

Al agregar nuevos objetos:
1. Documenta claramente el propósito
2. Incluye ejemplos de uso
3. Agrega pruebas en `apply_database_objects.py`
4. Actualiza este README
5. Prueba en desarrollo primero

---

**Fecha de creación:** 4 noviembre 2025  
**Última actualización:** 4 noviembre 2025  
**Versión:** 1.0.0  
**Estado:** ✅ Producción Ready
