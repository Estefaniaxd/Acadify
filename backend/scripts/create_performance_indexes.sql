-- =====================================================
-- ÍNDICES DE OPTIMIZACIÓN PARA ACADIFY
-- =====================================================
-- Fecha: 28 de octubre de 2025
-- Propósito: Optimizar queries más frecuentes
-- Impacto esperado: 50-90% mejora en performance
-- =====================================================

-- IMPORTANTE: Ejecutar en horario de bajo tráfico
-- Estimado: 2-5 minutos dependiendo del tamaño de BD

BEGIN;

-- =====================================================
-- 1. COMENTARIOS (Alto impacto)
-- =====================================================

-- Búsqueda de comentarios por curso (GET comentarios)
CREATE INDEX IF NOT EXISTS idx_comentarios_curso_id 
ON "Comentario"(curso_id)
WHERE comentario_padre_id IS NULL;

-- Búsqueda de respuestas a comentarios
CREATE INDEX IF NOT EXISTS idx_comentarios_padre_id 
ON "Comentario"(comentario_padre_id)
WHERE comentario_padre_id IS NOT NULL;

-- JOIN con Usuario (autor de comentarios)
CREATE INDEX IF NOT EXISTS idx_comentarios_autor_id 
ON "Comentario"(autor_id);

-- Ordenamiento por fecha
CREATE INDEX IF NOT EXISTS idx_comentarios_fecha_creacion 
ON "Comentario"(fecha_creacion DESC);

-- Índice compuesto para queries complejas
CREATE INDEX IF NOT EXISTS idx_comentarios_curso_tipo_fecha 
ON "Comentario"(curso_id, tipo, fecha_creacion DESC)
WHERE comentario_padre_id IS NULL;


-- =====================================================
-- 2. REACCIONES (Medio impacto)
-- =====================================================

-- Búsqueda de reacciones por comentario
CREATE INDEX IF NOT EXISTS idx_reacciones_comentario_id 
ON "Reacciones"(comentario_id);

-- Búsqueda de reacciones por usuario
CREATE INDEX IF NOT EXISTS idx_reacciones_usuario_id 
ON "Reacciones"(usuario_id);

-- Índice compuesto para verificar si usuario ya reaccionó
CREATE INDEX IF NOT EXISTS idx_reacciones_comentario_usuario 
ON "Reacciones"(comentario_id, usuario_id);


-- =====================================================
-- 3. CURSOS (Alto impacto)
-- =====================================================

-- Búsqueda de cursos por institución
CREATE INDEX IF NOT EXISTS idx_curso_institucion_id 
ON "Curso"(institucion_id);

-- Búsqueda de cursos por programa
CREATE INDEX IF NOT EXISTS idx_curso_programa_id 
ON "Curso"(programa_id);

-- Búsqueda de cursos por coordinador
CREATE INDEX IF NOT EXISTS idx_curso_coordinador_id 
ON "Curso"(coordinador_id)
WHERE coordinador_id IS NOT NULL;

-- Índice compuesto para listados
CREATE INDEX IF NOT EXISTS idx_curso_institucion_programa 
ON "Curso"(institucion_id, programa_id);


-- =====================================================
-- 4. GRUPOS Y MATRÍCULAS (Alto impacto)
-- =====================================================

-- Búsqueda de grupos por curso
CREATE INDEX IF NOT EXISTS idx_grupo_curso_curso_id 
ON "GrupoCurso"(curso_id);

-- Búsqueda de grupos por docente
CREATE INDEX IF NOT EXISTS idx_grupo_curso_docente_id 
ON "GrupoCurso"(docente_id);

-- Búsqueda de estudiantes por grupo
CREATE INDEX IF NOT EXISTS idx_estudiante_grupo_grupo_id 
ON "EstudianteGrupo"(grupo_id);

-- Búsqueda de grupos de un estudiante
CREATE INDEX IF NOT EXISTS idx_estudiante_grupo_estudiante_id 
ON "EstudianteGrupo"(estudiante_id);

-- Índice compuesto para verificar inscripción
CREATE INDEX IF NOT EXISTS idx_estudiante_grupo_estudiante_grupo 
ON "EstudianteGrupo"(estudiante_id, grupo_id);


-- =====================================================
-- 5. USUARIOS (Medio impacto)
-- =====================================================

-- Índice de búsqueda por rol
CREATE INDEX IF NOT EXISTS idx_usuario_rol 
ON "Usuario"(rol);

-- Índice de búsqueda por estado de cuenta
CREATE INDEX IF NOT EXISTS idx_usuario_estado_cuenta 
ON "Usuario"(estado_cuenta);

-- Índice compuesto para búsquedas combinadas
CREATE INDEX IF NOT EXISTS idx_usuario_rol_estado 
ON "Usuario"(rol, estado_cuenta);

-- Índice para búsqueda de texto en nombres
CREATE INDEX IF NOT EXISTS idx_usuario_nombres_busqueda 
ON "Usuario" USING gin(to_tsvector('spanish', nombres || ' ' || apellidos));


-- =====================================================
-- 6. TAREAS (Medio impacto)
-- =====================================================

-- Búsqueda de tareas por clase
CREATE INDEX IF NOT EXISTS idx_tareas_clase_id 
ON "Tarea"(clase_id);

-- Búsqueda de tareas por docente
CREATE INDEX IF NOT EXISTS idx_tareas_docente_id 
ON "Tarea"(docente_id)
WHERE docente_id IS NOT NULL;

-- Filtro por fecha límite
CREATE INDEX IF NOT EXISTS idx_tareas_fecha_limite 
ON "Tarea"(fecha_limite);

-- Búsqueda de entregas por tarea
CREATE INDEX IF NOT EXISTS idx_entregas_tarea_id 
ON "EntregarTarea"(tarea_id);

-- Búsqueda de entregas por estudiante
CREATE INDEX IF NOT EXISTS idx_entregas_estudiante_id 
ON "EntregarTarea"(estudiante_id);

-- Índice compuesto para verificar entrega
CREATE INDEX IF NOT EXISTS idx_entregas_tarea_estudiante 
ON "EntregarTarea"(tarea_id, estudiante_id);


-- =====================================================
-- 7. ARCHIVOS Y MATERIALES (Bajo impacto)
-- =====================================================

-- Búsqueda de materiales por curso
CREATE INDEX IF NOT EXISTS idx_material_curso_curso_id 
ON "MaterialCurso"(curso_id);

-- Búsqueda de materiales por clase
CREATE INDEX IF NOT EXISTS idx_material_clase_clase_id 
ON "MaterialClase"(clase_id);

-- Búsqueda de materiales educativos por tipo
CREATE INDEX IF NOT EXISTS idx_material_educativo_tipo 
ON "MaterialEducativo"(tipo)
WHERE tipo IS NOT NULL;


-- =====================================================
-- 8. INVITACIONES (Bajo impacto) - PENDIENTE VERIFICAR TABLA
-- =====================================================

-- NOTA: Verificar si existe tabla InvitationToken
-- Si no existe, comentar esta sección


-- =====================================================
-- 9. NOTIFICACIONES (Medio impacto)
-- =====================================================

-- Búsqueda de notificaciones por usuario
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_id 
ON notificaciones(usuario_id);

-- Filtro por leídas/no leídas
CREATE INDEX IF NOT EXISTS idx_notificaciones_leida 
ON notificaciones(leida);

-- Índice compuesto para listados
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_leida_fecha 
ON notificaciones(usuario_id, leida, fecha_creacion DESC);

-- Filtro por tipo de notificación
CREATE INDEX IF NOT EXISTS idx_notificaciones_tipo 
ON notificaciones(tipo_notificacion)
WHERE tipo_notificacion IS NOT NULL;


-- =====================================================
-- 10. GAMIFICACIÓN (Bajo impacto)
-- =====================================================

-- Puntos por usuario
CREATE INDEX IF NOT EXISTS idx_usuario_puntos_usuario_id 
ON "UsuarioPuntos"(usuario_id);

-- Insignias por usuario
CREATE INDEX IF NOT EXISTS idx_insignias_usuario_usuario_id 
ON "UsuarioInsignia"(usuario_id);

-- Índice para insignias por fecha obtenida
CREATE INDEX IF NOT EXISTS idx_insignias_usuario_fecha 
ON "UsuarioInsignia"(fecha_obtencion DESC)
WHERE fecha_obtencion IS NOT NULL;


-- =====================================================
-- ANÁLISIS Y ESTADÍSTICAS
-- =====================================================

-- Actualizar estadísticas de las tablas
ANALYZE "Comentario";
ANALYZE "Reacciones";
ANALYZE "Curso";
ANALYZE "GrupoCurso";
ANALYZE "EstudianteGrupo";
ANALYZE "Usuario";
ANALYZE "Tarea";
ANALYZE "EntregarTarea";
ANALYZE "MaterialCurso";
ANALYZE notificaciones;
ANALYZE "UsuarioPuntos";
ANALYZE "UsuarioInsignia";

COMMIT;

-- =====================================================
-- VERIFICACIÓN
-- =====================================================

-- Query para ver todos los índices creados
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Query para ver tamaño de índices
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =====================================================
-- NOTAS DE MANTENIMIENTO
-- =====================================================

-- 1. REINDEXAR periódicamente (cada 3 meses):
--    REINDEX TABLE "Comentario";
--    REINDEX TABLE "Curso";

-- 2. VACUUM ANALYZE después de grandes cambios:
--    VACUUM ANALYZE "Comentario";
--    VACUUM ANALYZE "Curso";

-- 3. MONITOREAR uso de índices:
--    SELECT * FROM pg_stat_user_indexes 
--    WHERE idx_scan = 0 
--    ORDER BY relname;

-- 4. ELIMINAR índices no usados:
--    DROP INDEX IF EXISTS idx_nombre_indice;

-- =====================================================
-- IMPACTO ESPERADO
-- =====================================================

-- Comentarios: 70-90% mejora en listados
-- Cursos: 60-80% mejora en búsquedas
-- Inscripciones: 50-70% mejora en validaciones
-- Tareas: 60-85% mejora en consultas
-- Usuarios: 40-60% mejora en autenticación

-- Performance global estimada: +70% en promedio

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
