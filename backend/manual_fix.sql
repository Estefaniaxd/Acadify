-- Drop views that depend on Curso.nombre
DROP VIEW IF EXISTS vista_actividad_reciente CASCADE;
DROP VIEW IF EXISTS vista_ranking_cursos CASCADE;
DROP VIEW IF EXISTS vista_entregas_pendientes CASCADE;
DROP VIEW IF EXISTS vista_evaluaciones_resumen CASCADE;
DROP VIEW IF EXISTS vista_cursos_estadisticas CASCADE;

-- Alter Curso.nombre
ALTER TABLE "Curso" ALTER COLUMN nombre TYPE VARCHAR(100);

-- Create ENUM types if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_clase') THEN
        CREATE TYPE tipo_clase AS ENUM ('teorica', 'practica', 'laboratorio', 'taller', 'seminario', 'conferencia', 'examen', 'otro');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_clase') THEN
        CREATE TYPE estado_clase AS ENUM ('programada', 'en_progreso', 'finalizada', 'cancelada');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_codigo_acceso') THEN
        CREATE TYPE estado_codigo_acceso AS ENUM ('activo', 'vencido', 'deshabilitado');
    END IF;
END$$;

-- Alter Clase columns
-- Handle tipo_clase
ALTER TABLE "Clase" 
    ALTER COLUMN tipo_clase TYPE tipo_clase USING tipo_clase::tipo_clase;

-- Handle estado (map 'activo' to 'programada')
ALTER TABLE "Clase" 
    ALTER COLUMN estado DROP DEFAULT,
    ALTER COLUMN estado TYPE estado_clase USING (CASE WHEN estado = 'activo' THEN 'programada'::estado_clase ELSE estado::estado_clase END),
    ALTER COLUMN estado SET DEFAULT 'programada';

-- Handle duracion
ALTER TABLE "Clase" 
    ALTER COLUMN duracion TYPE INTEGER USING (EXTRACT(EPOCH FROM duracion)::integer / 60);

-- Handle estado_codigo
ALTER TABLE "Clase" 
    ALTER COLUMN estado_codigo TYPE estado_codigo_acceso USING estado_codigo::estado_codigo_acceso;

-- Recreate Views
CREATE OR REPLACE VIEW vista_cursos_estadisticas AS
SELECT 
    c.curso_id,
    c.nombre,
    c.codigo_curso,
    c.activo,
    c.estado,
    u.nombres || ' ' || u.apellidos AS coordinador,
    (SELECT COUNT(DISTINCT eg.estudiante_id) FROM "EstudianteGrupo" eg INNER JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id WHERE gc.curso_id = c.curso_id) AS total_estudiantes,
    (SELECT COUNT(DISTINCT gc.grupo_id) FROM "GrupoCurso" gc WHERE gc.curso_id = c.curso_id) AS total_grupos,
    (SELECT COUNT(*) FROM tareas t INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id WHERE gc.curso_id = c.curso_id) AS total_tareas,
    (SELECT COUNT(*) FROM evaluaciones WHERE curso_id::uuid = c.curso_id) AS total_evaluaciones,
    (SELECT COUNT(*) FROM entregas_tareas et INNER JOIN tareas t ON et.tarea_id = t.tarea_id INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id WHERE gc.curso_id = c.curso_id) AS total_entregas,
    (SELECT COUNT(*) FROM entregas_tareas et INNER JOIN tareas t ON et.tarea_id = t.tarea_id INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id WHERE gc.curso_id = c.curso_id AND et.calificacion IS NULL) AS entregas_pendientes_calificacion,
    (SELECT AVG(et.calificacion) FROM entregas_tareas et INNER JOIN tareas t ON et.tarea_id = t.tarea_id INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id WHERE gc.curso_id = c.curso_id AND et.calificacion IS NOT NULL) AS promedio_entregas,
    (SELECT AVG(ie.puntuacion_obtenida) FROM intentos_evaluacion ie INNER JOIN evaluaciones ev ON ie.evaluacion_id = ev.id WHERE ev.curso_id::uuid = c.curso_id AND ie.puntuacion_obtenida IS NOT NULL) AS promedio_evaluaciones,
    CASE WHEN (SELECT COUNT(*) FROM entregas_tareas et INNER JOIN tareas t ON et.tarea_id = t.tarea_id INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id WHERE gc.curso_id = c.curso_id AND et.calificacion IS NOT NULL) > 0 THEN (SELECT COUNT(*) * 100.0 / NULLIF(COUNT(*), 0) FROM entregas_tareas et INNER JOIN tareas t ON et.tarea_id = t.tarea_id INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id WHERE gc.curso_id = c.curso_id AND et.calificacion >= 3.0) ELSE 0 END AS tasa_aprobacion,
    c.fecha_creacion,
    c.fecha_actualizacion
FROM "Curso" c
LEFT JOIN "Usuario" u ON c.coordinador_id = u.usuario_id
ORDER BY c.nombre;

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
    c.nombre,
    c.codigo_curso,
    COUNT(DISTINCT ie.id) AS total_intentos,
    COUNT(DISTINCT ie.estudiante_id) AS estudiantes_participantes,
    COUNT(DISTINCT CASE WHEN ie.fecha_fin IS NOT NULL THEN ie.id END) AS intentos_completados,
    COUNT(DISTINCT CASE WHEN ie.fecha_fin IS NULL THEN ie.id END) AS intentos_en_progreso,
    AVG(ie.puntuacion_obtenida) AS promedio_calificacion,
    MIN(ie.puntuacion_obtenida) AS calificacion_minima,
    MAX(ie.puntuacion_obtenida) AS calificacion_maxima,
    STDDEV(ie.puntuacion_obtenida) AS desviacion_estandar,
    CASE WHEN COUNT(DISTINCT CASE WHEN ie.puntuacion_obtenida IS NOT NULL THEN ie.id END) > 0 THEN (COUNT(DISTINCT CASE WHEN ie.puntuacion_obtenida >= ev.puntuacion_minima_aprobacion THEN ie.id END) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN ie.puntuacion_obtenida IS NOT NULL THEN ie.id END), 0)) ELSE 0 END AS tasa_aprobacion,
    CASE WHEN COUNT(DISTINCT ie.id) > 0 THEN (COUNT(DISTINCT CASE WHEN ie.fecha_fin IS NOT NULL THEN ie.id END) * 100.0 / NULLIF(COUNT(DISTINCT ie.id), 0)) ELSE 0 END AS tasa_completitud,
    AVG(EXTRACT(EPOCH FROM (ie.fecha_fin - ie.fecha_inicio))/60) AS duracion_promedio_minutos,
    CASE WHEN ev.fecha_apertura > NOW() THEN 'Próxima' WHEN ev.fecha_cierre < NOW() THEN 'Cerrada' ELSE 'Activa' END AS estado_actual,
    (SELECT COUNT(*) FROM preguntas_evaluacion pe WHERE evaluacion_id = ev.id) AS total_preguntas,
    (SELECT SUM(puntuacion) FROM preguntas_evaluacion pe WHERE evaluacion_id = ev.id) AS puntos_totales
FROM evaluaciones ev
LEFT JOIN "Curso" c ON ev.curso_id::uuid = c.curso_id
LEFT JOIN intentos_evaluacion ie ON ev.id = ie.evaluacion_id
GROUP BY ev.id, ev.titulo, ev.descripcion, ev.tipo_evaluacion, ev.estado_examen, ev.fecha_apertura, ev.fecha_cierre, ev.tiempo_limite_minutos, ev.intentos_permitidos, ev.puntuacion_minima_aprobacion, c.nombre, c.codigo_curso
ORDER BY ev.fecha_apertura DESC;

CREATE OR REPLACE VIEW vista_entregas_pendientes AS
SELECT 
    et.entrega_id,
    et.fecha_entrega,
    EXTRACT(DAY FROM NOW() - et.fecha_entrega)::INTEGER AS dias_pendiente,
    e.estudiante_id,
    u.nombres || ' ' || u.apellidos AS estudiante_nombre,
    u.correo_institucional AS estudiante_correo,
    t.tarea_id,
    t.titulo,
    t.descripcion AS tarea_descripcion,
    t.fecha_limite,
    c.curso_id,
    c.nombre AS curso_nombre,
    c.codigo_curso,
    g.grupo_id,
    g.nombre AS grupo_nombre,
    et.comentarios_estudiante,
    et.archivo_url,
    et.intentos,
    et.estado,
    CASE WHEN EXTRACT(DAY FROM NOW() - et.fecha_entrega) > 7 THEN 'Alta' WHEN EXTRACT(DAY FROM NOW() - et.fecha_entrega) > 3 THEN 'Media' ELSE 'Normal' END AS prioridad_revision,
    CASE WHEN t.fecha_limite IS NOT NULL AND et.fecha_entrega > t.fecha_limite THEN TRUE ELSE FALSE END AS entrega_tardia
FROM entregas_tareas et
INNER JOIN "Estudiante" e ON et.estudiante_id = e.estudiante_id
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
INNER JOIN tareas t ON et.tarea_id = t.tarea_id
INNER JOIN "Grupo" g ON t.grupo_id = g.grupo_id
INNER JOIN "GrupoCurso" gc ON g.grupo_id = gc.grupo_id
INNER JOIN "Curso" c ON gc.curso_id = c.curso_id
WHERE et.calificacion IS NULL AND et.estado IN ('entregada', 'en_revision')
ORDER BY dias_pendiente DESC, et.fecha_entrega ASC;

CREATE OR REPLACE VIEW vista_ranking_cursos AS
SELECT 
    c.curso_id,
    c.nombre,
    c.codigo_curso,
    e.estudiante_id,
    u.nombres || ' ' || u.apellidos AS nombre_completo,
    calcular_promedio_estudiante_curso(e.estudiante_id, c.curso_id) AS promedio_curso,
    ROW_NUMBER() OVER (PARTITION BY c.curso_id ORDER BY calcular_promedio_estudiante_curso(e.estudiante_id, c.curso_id) DESC NULLS LAST) AS posicion,
    COUNT(*) OVER (PARTITION BY c.curso_id) AS total_estudiantes,
    PERCENT_RANK() OVER (PARTITION BY c.curso_id ORDER BY calcular_promedio_estudiante_curso(e.estudiante_id, c.curso_id)) * 100 AS percentil,
    (SELECT COUNT(*) FROM entregas_tareas et INNER JOIN tareas t ON et.tarea_id = t.tarea_id INNER JOIN "GrupoCurso" gc ON t.grupo_id = gc.grupo_id WHERE et.estudiante_id = e.estudiante_id AND gc.curso_id = c.curso_id) AS total_entregas_curso,
    (SELECT COUNT(*) FROM intentos_evaluacion ie INNER JOIN evaluaciones ev ON ie.evaluacion_id = ev.id WHERE ie.estudiante_id::uuid = e.estudiante_id AND ev.curso_id::uuid = c.curso_id) AS total_intentos_curso
FROM "Curso" c
CROSS JOIN "Estudiante" e
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
INNER JOIN "EstudianteGrupo" eg ON e.estudiante_id = eg.estudiante_id
INNER JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
WHERE gc.curso_id = c.curso_id
ORDER BY c.nombre, posicion;

CREATE OR REPLACE VIEW vista_actividad_reciente AS
SELECT 
    'Entrega' AS tipo_actividad,
    et.entrega_id::TEXT AS actividad_id,
    et.fecha_entrega AS fecha_actividad,
    u.nombres || ' ' || u.apellidos AS estudiante,
    t.titulo AS titulo,
    c.nombre AS curso,
    CASE WHEN et.calificacion IS NULL THEN 'Pendiente' WHEN et.calificacion >= 3.0 THEN 'Aprobada' ELSE 'Reprobada' END AS estado,
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
    CASE WHEN ie.fecha_fin IS NULL THEN 'En Progreso' WHEN ie.puntuacion_obtenida IS NULL THEN 'Pendiente' WHEN ie.puntuacion_obtenida >= ev.puntuacion_minima_aprobacion THEN 'Aprobado' ELSE 'Reprobado' END AS estado,
    ie.puntuacion_obtenida AS calificacion
FROM intentos_evaluacion ie
INNER JOIN "Estudiante" e ON ie.estudiante_id::uuid = e.estudiante_id
INNER JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
INNER JOIN evaluaciones ev ON ie.evaluacion_id = ev.id
INNER JOIN "Curso" c ON ev.curso_id::uuid = c.curso_id
WHERE ie.fecha_inicio >= NOW() - INTERVAL '7 days'
ORDER BY fecha_actividad DESC
LIMIT 100;
