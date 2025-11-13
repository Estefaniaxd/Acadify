-- =====================================================
-- VISTAS
-- Sistema Acadify - Vistas para reportes y dashboards
-- Fecha: 4 noviembre 2025
-- =====================================================

-- =====================================================
-- 1. VISTA: Desempeño de estudiantes
-- =====================================================

CREATE OR REPLACE VIEW vista_estudiantes_desempeno AS
SELECT 
    e.estudiante_id,
    u.nombres || ' ' || u.apellidos AS nombre_completo,
    u.correo_institucional,
    
    -- Promedios
    calcular_promedio_estudiante(e.estudiante_id) AS promedio_general,
    
    -- Contadores de entregas
    COUNT(DISTINCT et.entrega_id) AS total_entregas,
    COUNT(DISTINCT CASE WHEN et.calificacion IS NOT NULL THEN et.entrega_id END) AS entregas_calificadas,
    COUNT(DISTINCT CASE WHEN et.calificacion IS NULL THEN et.entrega_id END) AS entregas_pendientes,
    
    -- Estadísticas de calificaciones
    AVG(et.calificacion) AS promedio_entregas,
    MIN(et.calificacion) AS calificacion_minima,
    MAX(et.calificacion) AS calificacion_maxima,
    
    -- Contadores de evaluaciones
    COUNT(DISTINCT ie.id) AS total_intentos_evaluaciones,
    AVG(ie.puntuacion_obtenida) AS promedio_evaluaciones,
    
    -- Estado general
    CASE 
        WHEN calcular_promedio_estudiante(e.estudiante_id) >= 4.0 THEN 'Excelente'
        WHEN calcular_promedio_estudiante(e.estudiante_id) >= 3.5 THEN 'Bueno'
        WHEN calcular_promedio_estudiante(e.estudiante_id) >= 3.0 THEN 'Regular'
        ELSE 'En Riesgo'
    END AS estado_desempeno,
    
    -- Fechas
    MAX(et.fecha_entrega) AS ultima_entrega,
    MAX(ie.fecha_inicio) AS ultimo_intento_evaluacion

FROM "Estudiante" e
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
LEFT JOIN entregas_tareas et ON e.estudiante_id = et.estudiante_id
LEFT JOIN intentos_evaluacion ie ON e.estudiante_id::text = ie.estudiante_id

GROUP BY e.estudiante_id, u.nombres, u.apellidos, u.correo_institucional

ORDER BY promedio_general DESC NULLS LAST;

COMMENT ON VIEW vista_estudiantes_desempeno IS 
'Vista consolidada del desempeño de todos los estudiantes con métricas clave';


-- =====================================================
-- 2. VISTA: Estadísticas de cursos
-- =====================================================

CREATE OR REPLACE VIEW vista_cursos_estadisticas AS
SELECT 
    c.curso_id,
    c.nombre,
    c.codigo_curso,
    c.activo,
    c.estado,
    
    -- Información del coordinador
    u.nombres || ' ' || u.apellidos AS coordinador,
    
    -- Contadores básicos
    (SELECT COUNT(DISTINCT eg.estudiante_id) 
     FROM "EstudianteGrupo" eg 
     INNER JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id 
     WHERE gc.curso_id = c.curso_id) AS total_estudiantes,
     
    (SELECT COUNT(DISTINCT gc.grupo_id) FROM "GrupoCurso" gc WHERE gc.curso_id = c.curso_id) AS total_grupos,
    (SELECT COUNT(*) 
     FROM tareas t 
     INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id 
     WHERE gc.curso_id = c.curso_id) AS total_tareas,
    (SELECT COUNT(*) FROM evaluaciones WHERE curso_id::uuid = c.curso_id) AS total_evaluaciones,
    
    -- Estadísticas de entregas
    (SELECT COUNT(*) 
     FROM entregas_tareas et 
     INNER JOIN tareas t ON et.tarea_id = t.tarea_id 
     INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id
     WHERE gc.curso_id = c.curso_id) AS total_entregas,
     
    (SELECT COUNT(*) 
     FROM entregas_tareas et 
     INNER JOIN tareas t ON et.tarea_id = t.tarea_id 
     INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id
     WHERE gc.curso_id = c.curso_id 
     AND et.calificacion IS NULL) AS entregas_pendientes_calificacion,
     
    -- Promedios
    (SELECT AVG(et.calificacion) 
     FROM entregas_tareas et 
     INNER JOIN tareas t ON et.tarea_id = t.tarea_id 
     INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id
     WHERE gc.curso_id = c.curso_id 
     AND et.calificacion IS NOT NULL) AS promedio_entregas,
     
    (SELECT AVG(ie.puntuacion_obtenida) 
     FROM intentos_evaluacion ie 
     INNER JOIN evaluaciones ev ON ie.evaluacion_id = ev.id 
     WHERE ev.curso_id::uuid = c.curso_id 
     AND ie.puntuacion_obtenida IS NOT NULL) AS promedio_evaluaciones,
    
    -- Tasa de aprobación (>= 3.0)
    CASE 
        WHEN (SELECT COUNT(*) 
              FROM entregas_tareas et 
              INNER JOIN tareas t ON et.tarea_id = t.tarea_id 
              INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id
              WHERE gc.curso_id = c.curso_id 
              AND et.calificacion IS NOT NULL) > 0
        THEN (SELECT COUNT(*) * 100.0 / NULLIF(COUNT(*), 0)
              FROM entregas_tareas et 
              INNER JOIN tareas t ON et.tarea_id = t.tarea_id 
              INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id
              WHERE gc.curso_id = c.curso_id 
              AND et.calificacion >= 3.0)
        ELSE 0
    END AS tasa_aprobacion,
    
    -- Fechas
    c.fecha_creacion,
    c.fecha_actualizacion

FROM "Curso" c
LEFT JOIN "Usuario" u ON c.coordinador_id = u.usuario_id

ORDER BY c.nombre;

COMMENT ON VIEW vista_cursos_estadisticas IS 
'Vista consolidada de estadísticas de todos los cursos';


-- =====================================================
-- 3. VISTA: Resumen de evaluaciones
-- =====================================================

CREATE OR REPLACE VIEW vista_evaluaciones_resumen AS
SELECT 
    ev.id AS evaluacion_id,
    ev.titulo,
    ev.descripcion,
    ev.tipo_evaluacion,
    ev.estado_examen,
    ev.fecha_apertura,
    ev.fecha_cierre,
    ev.tiempo_limite_minutos,
    ev.intentos_permitidos,
    ev.puntuacion_minima_aprobacion,
    
    -- Información del curso
    c.nombre,
    c.codigo_curso,
    
    -- Estadísticas de intentos
    COUNT(DISTINCT ie.id) AS total_intentos,
    COUNT(DISTINCT ie.estudiante_id) AS estudiantes_participantes,
    COUNT(DISTINCT CASE WHEN ie.fecha_fin IS NOT NULL THEN ie.id END) AS intentos_completados,
    COUNT(DISTINCT CASE WHEN ie.fecha_fin IS NULL THEN ie.id END) AS intentos_en_progreso,
    
    -- Estadísticas de calificaciones
    AVG(ie.puntuacion_obtenida) AS promedio_calificacion,
    MIN(ie.puntuacion_obtenida) AS calificacion_minima,
    MAX(ie.puntuacion_obtenida) AS calificacion_maxima,
    STDDEV(ie.puntuacion_obtenida) AS desviacion_estandar,
    
    -- Tasa de aprobación
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN ie.puntuacion_obtenida IS NOT NULL THEN ie.id END) > 0
        THEN (COUNT(DISTINCT CASE WHEN ie.puntuacion_obtenida >= ev.puntuacion_minima_aprobacion THEN ie.id END) * 100.0 
              / NULLIF(COUNT(DISTINCT CASE WHEN ie.puntuacion_obtenida IS NOT NULL THEN ie.id END), 0))
        ELSE 0
    END AS tasa_aprobacion,
    
    -- Tasa de completitud
    CASE 
        WHEN COUNT(DISTINCT ie.id) > 0
        THEN (COUNT(DISTINCT CASE WHEN ie.fecha_fin IS NOT NULL THEN ie.id END) * 100.0 
              / NULLIF(COUNT(DISTINCT ie.id), 0))
        ELSE 0
    END AS tasa_completitud,
    
    -- Estadísticas de tiempo
    AVG(EXTRACT(EPOCH FROM (ie.fecha_fin - ie.fecha_inicio))/60) AS duracion_promedio_minutos,
    
    -- Estado de la evaluación
    CASE 
        WHEN ev.fecha_apertura > NOW() THEN 'Próxima'
        WHEN ev.fecha_cierre < NOW() THEN 'Cerrada'
        ELSE 'Activa'
    END AS estado_actual,
    
    -- Contadores de preguntas
    (SELECT COUNT(*) FROM preguntas_evaluacion pe WHERE evaluacion_id = ev.id) AS total_preguntas,
    (SELECT SUM(puntuacion) FROM preguntas_evaluacion pe WHERE evaluacion_id = ev.id) AS puntos_totales

FROM evaluaciones ev
LEFT JOIN "Curso" c ON ev.curso_id::uuid = c.curso_id
LEFT JOIN intentos_evaluacion ie ON ev.id = ie.evaluacion_id

GROUP BY 
    ev.id, ev.titulo, ev.descripcion, ev.tipo_evaluacion, ev.estado_examen,
    ev.fecha_apertura, ev.fecha_cierre, ev.tiempo_limite_minutos, 
    ev.intentos_permitidos, ev.puntuacion_minima_aprobacion,
    c.nombre, c.codigo_curso

ORDER BY ev.fecha_apertura DESC;

COMMENT ON VIEW vista_evaluaciones_resumen IS 
'Vista consolidada de estadísticas de evaluaciones con métricas de desempeño';


-- =====================================================
-- 4. VISTA: Entregas pendientes de calificación
-- =====================================================

CREATE OR REPLACE VIEW vista_entregas_pendientes AS
SELECT 
    et.entrega_id,
    et.fecha_entrega,
    EXTRACT(DAY FROM NOW() - et.fecha_entrega)::INTEGER AS dias_pendiente,
    
    -- Información del estudiante
    e.estudiante_id,
    u.nombres || ' ' || u.apellidos AS estudiante_nombre,
    u.correo_institucional AS estudiante_correo,
    
    -- Información de la tarea
    t.tarea_id,
    t.titulo,
    t.descripcion AS tarea_descripcion,
    t.fecha_limite,
    
    -- Información del curso
    c.curso_id,
    c.nombre AS curso_nombre,
    c.codigo_curso,
    
    -- Información del grupo
    g.grupo_id,
    g.nombre AS grupo_nombre,
    
    -- Detalles de la entrega
    et.comentarios_estudiante,
    et.archivo_url,
    et.intentos,
    et.estado,
    
    -- Prioridad basada en días pendientes
    CASE 
        WHEN EXTRACT(DAY FROM NOW() - et.fecha_entrega) > 7 THEN 'Alta'
        WHEN EXTRACT(DAY FROM NOW() - et.fecha_entrega) > 3 THEN 'Media'
        ELSE 'Normal'
    END AS prioridad_revision,
    
    -- Indicador de entrega tardía
    CASE 
        WHEN t.fecha_limite IS NOT NULL 
         AND et.fecha_entrega > t.fecha_limite 
        THEN TRUE
        ELSE FALSE
    END AS entrega_tardia

FROM entregas_tareas et
INNER JOIN "Estudiante" e ON et.estudiante_id = e.estudiante_id
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
INNER JOIN tareas t ON et.tarea_id = t.tarea_id
INNER JOIN "Grupo" g ON t.grupo_id = g.grupo_id
INNER JOIN "GrupoCurso" gc ON g.grupo_id = gc.grupo_id
INNER JOIN "Curso" c ON gc.curso_id = c.curso_id

WHERE et.calificacion IS NULL
  AND et.estado IN ('entregada', 'en_revision')

ORDER BY dias_pendiente DESC, et.fecha_entrega ASC;

COMMENT ON VIEW vista_entregas_pendientes IS 
'Vista de entregas pendientes de calificación ordenadas por prioridad';


-- =====================================================
-- 5. VISTA: Estudiantes en riesgo académico
-- =====================================================

CREATE OR REPLACE VIEW vista_estudiantes_riesgo AS
SELECT 
    e.estudiante_id,
    u.nombres || ' ' || u.apellidos AS nombre_completo,
    u.correo_institucional,
    
    -- Promedio y estado
    calcular_promedio_estudiante(e.estudiante_id) AS promedio_general,
    
    -- Contadores críticos
    contar_entregas_pendientes(e.estudiante_id) AS entregas_pendientes,
    
    -- Métricas de alerta
    (SELECT COUNT(*) 
     FROM entregas_tareas et 
     WHERE et.estudiante_id = e.estudiante_id 
     AND et.calificacion < 3.0) AS entregas_reprobadas,
     
    (SELECT COUNT(*) 
     FROM intentos_evaluacion ie 
     WHERE ie.estudiante_id::uuid = e.estudiante_id 
     AND ie.puntuacion_obtenida < 3.0) AS evaluaciones_reprobadas,
    
    -- Última actividad
    GREATEST(
        (SELECT MAX(fecha_entrega) FROM entregas_tareas WHERE estudiante_id::uuid = e.estudiante_id),
        (SELECT MAX(fecha_inicio) FROM intentos_evaluacion WHERE estudiante_id::uuid = e.estudiante_id)
    ) AS ultima_actividad,
    
    -- Días sin actividad
    EXTRACT(DAY FROM NOW() - GREATEST(
        COALESCE((SELECT MAX(fecha_entrega) FROM entregas_tareas WHERE estudiante_id::uuid = e.estudiante_id), NOW()),
        COALESCE((SELECT MAX(fecha_inicio) FROM intentos_evaluacion WHERE estudiante_id::uuid = e.estudiante_id), NOW())
    ))::INTEGER AS dias_sin_actividad,
    
    -- Razones de riesgo
    ARRAY_REMOVE(ARRAY[
        CASE WHEN calcular_promedio_estudiante(e.estudiante_id) < 3.0 
             THEN 'Promedio bajo' END,
        CASE WHEN contar_entregas_pendientes(e.estudiante_id) >= 3 
             THEN 'Múltiples entregas pendientes' END,
        CASE WHEN EXTRACT(DAY FROM NOW() - GREATEST(
                    COALESCE((SELECT MAX(fecha_entrega) FROM entregas_tareas WHERE estudiante_id::uuid = e.estudiante_id), NOW()),
                    COALESCE((SELECT MAX(fecha_inicio) FROM intentos_evaluacion WHERE estudiante_id::uuid = e.estudiante_id), NOW())
                )) > 14 
             THEN 'Inactividad prolongada' END
    ], NULL) AS razones_riesgo,
    
    -- Nivel de riesgo
    CASE 
        WHEN calcular_promedio_estudiante(e.estudiante_id) < 2.5 
          OR contar_entregas_pendientes(e.estudiante_id) >= 5 
        THEN 'Crítico'
        WHEN calcular_promedio_estudiante(e.estudiante_id) < 3.0 
          OR contar_entregas_pendientes(e.estudiante_id) >= 3 
        THEN 'Alto'
        ELSE 'Medio'
    END AS nivel_riesgo

FROM "Estudiante" e
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id

WHERE calcular_promedio_estudiante(e.estudiante_id) < 3.5
   OR contar_entregas_pendientes(e.estudiante_id) >= 2

ORDER BY 
    CASE 
        WHEN calcular_promedio_estudiante(e.estudiante_id) < 2.5 THEN 1
        WHEN calcular_promedio_estudiante(e.estudiante_id) < 3.0 THEN 2
        ELSE 3
    END,
    calcular_promedio_estudiante(e.estudiante_id) ASC NULLS LAST;

COMMENT ON VIEW vista_estudiantes_riesgo IS 
'Vista de estudiantes en riesgo académico con indicadores de alerta';


-- =====================================================
-- 6. VISTA: Ranking de estudiantes por curso
-- =====================================================

CREATE OR REPLACE VIEW vista_ranking_cursos AS
SELECT 
    c.curso_id,
    c.nombre,
    c.codigo_curso,
    
    e.estudiante_id,
    u.nombres || ' ' || u.apellidos AS nombre_completo,
    
    calcular_promedio_estudiante_curso(e.estudiante_id, c.curso_id) AS promedio_curso,
    
    ROW_NUMBER() OVER (
        PARTITION BY c.curso_id 
        ORDER BY calcular_promedio_estudiante_curso(e.estudiante_id, c.curso_id) DESC NULLS LAST
    ) AS posicion,
    
    COUNT(*) OVER (PARTITION BY c.curso_id) AS total_estudiantes,
    
    -- Percentil
    PERCENT_RANK() OVER (
        PARTITION BY c.curso_id 
        ORDER BY calcular_promedio_estudiante_curso(e.estudiante_id, c.curso_id)
    ) * 100 AS percentil,
    
    -- Contadores específicos del curso
    (SELECT COUNT(*) 
     FROM entregas_tareas et 
     INNER JOIN tareas t ON et.tarea_id = t.tarea_id 
     INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id
     WHERE et.estudiante_id = e.estudiante_id 
     AND gc.curso_id = c.curso_id) AS total_entregas_curso,
     
    (SELECT COUNT(*) 
     FROM intentos_evaluacion ie 
     INNER JOIN evaluaciones ev ON ie.evaluacion_id = ev.id 
     WHERE ie.estudiante_id::uuid = e.estudiante_id 
     AND ev.curso_id::uuid = c.curso_id) AS total_intentos_curso

FROM "Curso" c
CROSS JOIN "Estudiante" e
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
INNER JOIN "EstudianteGrupo" eg ON e.estudiante_id = eg.estudiante_id
INNER JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id

WHERE gc.curso_id = c.curso_id

ORDER BY c.nombre, posicion;

COMMENT ON VIEW vista_ranking_cursos IS 
'Vista de ranking de estudiantes por curso con posición y percentil';


-- =====================================================
-- 7. VISTA: Actividad reciente del sistema
-- =====================================================

CREATE OR REPLACE VIEW vista_actividad_reciente AS
SELECT 
    'Entrega' AS tipo_actividad,
    et.entrega_id::TEXT AS actividad_id,
    et.fecha_entrega AS fecha_actividad,
    
    u.nombres || ' ' || u.apellidos AS estudiante,
    t.titulo AS titulo,
    c.nombre AS curso,
    
    CASE 
        WHEN et.calificacion IS NULL THEN 'Pendiente'
        WHEN et.calificacion >= 3.0 THEN 'Aprobada'
        ELSE 'Reprobada'
    END AS estado,
    
    et.calificacion

FROM entregas_tareas et
INNER JOIN "Estudiante" e ON et.estudiante_id = e.estudiante_id
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
INNER JOIN tareas t ON et.tarea_id = t.tarea_id
INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id
INNER JOIN "Curso" c ON gc.curso_id = c.curso_id

WHERE et.fecha_entrega >= NOW() - INTERVAL '7 days'

UNION ALL

SELECT 
    'Intento Evaluación' AS tipo_actividad,
    ie.id::TEXT AS actividad_id,
    ie.fecha_inicio AS fecha_actividad,
    
    u.nombres || ' ' || u.apellidos AS estudiante,
    ev.titulo AS titulo,
    c.nombre AS curso,
    
    CASE 
        WHEN ie.fecha_fin IS NULL THEN 'En Progreso'
        WHEN ie.puntuacion_obtenida IS NULL THEN 'Pendiente'
        WHEN ie.puntuacion_obtenida >= ev.puntuacion_minima_aprobacion THEN 'Aprobado'
        ELSE 'Reprobado'
    END AS estado,
    
    ie.puntuacion_obtenida AS calificacion

FROM intentos_evaluacion ie
INNER JOIN "Estudiante" e ON ie.estudiante_id::uuid = e.estudiante_id
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
INNER JOIN evaluaciones ev ON ie.evaluacion_id = ev.id
INNER JOIN "Curso" c ON ev.curso_id::uuid = c.curso_id

WHERE ie.fecha_inicio >= NOW() - INTERVAL '7 days'

ORDER BY fecha_actividad DESC

LIMIT 100;

COMMENT ON VIEW vista_actividad_reciente IS 
'Vista de actividad reciente del sistema (últimos 7 días, límite 100 registros)';


-- =====================================================
-- FIN DE VISTAS
-- =====================================================
