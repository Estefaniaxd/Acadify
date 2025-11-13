-- =====================================================
-- ÍNDICES DE OPTIMIZACIÓN - VERSIÓN SIMPLIFICADA
-- =====================================================
-- Sin transacción para aplicar índices individuales
-- =====================================================

-- ===== COMENTARIOS Y REACCIONES =====

CREATE INDEX IF NOT EXISTS idx_comentarios_curso_id 
ON "Comentario"(curso_id) WHERE comentario_padre_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_comentarios_padre_id 
ON "Comentario"(comentario_padre_id) WHERE comentario_padre_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_comentarios_autor_id 
ON "Comentario"(autor_id);

CREATE INDEX IF NOT EXISTS idx_comentarios_fecha_creacion 
ON "Comentario"(fecha_creacion DESC);

CREATE INDEX IF NOT EXISTS idx_comentarios_curso_tipo_fecha 
ON "Comentario"(curso_id, tipo, fecha_creacion DESC) WHERE comentario_padre_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_reacciones_comentario_id 
ON "Reacciones"(comentario_id);

CREATE INDEX IF NOT EXISTS idx_reacciones_usuario_id 
ON "Reacciones"(usuario_id);

CREATE INDEX IF NOT EXISTS idx_reacciones_comentario_usuario 
ON "Reacciones"(comentario_id, usuario_id);

-- ===== CURSOS =====

CREATE INDEX IF NOT EXISTS idx_curso_institucion_id 
ON "Curso"(institucion_id);

CREATE INDEX IF NOT EXISTS idx_curso_programa_id 
ON "Curso"(programa_id);

CREATE INDEX IF NOT EXISTS idx_curso_coordinador_id 
ON "Curso"(coordinador_id) WHERE coordinador_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_curso_institucion_programa 
ON "Curso"(institucion_id, programa_id);

-- ===== GRUPOS Y ESTUDIANTES =====

CREATE INDEX IF NOT EXISTS idx_grupo_curso_curso_id 
ON "GrupoCurso"(curso_id);

CREATE INDEX IF NOT EXISTS idx_grupo_curso_docente_id 
ON "GrupoCurso"(docente_id);

CREATE INDEX IF NOT EXISTS idx_estudiante_grupo_grupo_id 
ON "EstudianteGrupo"(grupo_id);

CREATE INDEX IF NOT EXISTS idx_estudiante_grupo_estudiante_id 
ON "EstudianteGrupo"(estudiante_id);

CREATE INDEX IF NOT EXISTS idx_estudiante_grupo_estudiante_grupo 
ON "EstudianteGrupo"(estudiante_id, grupo_id);

-- ===== USUARIOS =====

CREATE INDEX IF NOT EXISTS idx_usuario_rol 
ON "Usuario"(rol);

CREATE INDEX IF NOT EXISTS idx_usuario_estado_cuenta 
ON "Usuario"(estado_cuenta);

CREATE INDEX IF NOT EXISTS idx_usuario_rol_estado 
ON "Usuario"(rol, estado_cuenta);

CREATE INDEX IF NOT EXISTS idx_usuario_nombres_busqueda 
ON "Usuario" USING gin(to_tsvector('spanish', nombres || ' ' || apellidos));

-- ===== TAREAS Y ENTREGAS =====

CREATE INDEX IF NOT EXISTS idx_tareas_clase_id 
ON "Tarea"(clase_id);

CREATE INDEX IF NOT EXISTS idx_tareas_docente_id 
ON "Tarea"(docente_id) WHERE docente_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tareas_fecha_limite 
ON "Tarea"(fecha_limite);

CREATE INDEX IF NOT EXISTS idx_entregas_tarea_id 
ON "EntregarTarea"(tarea_id);

CREATE INDEX IF NOT EXISTS idx_entregas_estudiante_id 
ON "EntregarTarea"(estudiante_id);

CREATE INDEX IF NOT EXISTS idx_entregas_tarea_estudiante 
ON "EntregarTarea"(tarea_id, estudiante_id);

-- ===== MATERIALES =====

CREATE INDEX IF NOT EXISTS idx_material_curso_curso_id 
ON "MaterialCurso"(curso_id);

CREATE INDEX IF NOT EXISTS idx_material_clase_clase_id 
ON "MaterialClase"(clase_id);

-- ===== NOTIFICACIONES =====

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_id 
ON notificaciones(usuario_id);

CREATE INDEX IF NOT EXISTS idx_notificaciones_leida 
ON notificaciones(leida);

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_leida_fecha 
ON notificaciones(usuario_id, leida, fecha_creacion DESC);

CREATE INDEX IF NOT EXISTS idx_notificaciones_tipo 
ON notificaciones(tipo_notificacion) WHERE tipo_notificacion IS NOT NULL;

-- ===== GAMIFICACIÓN =====

CREATE INDEX IF NOT EXISTS idx_usuario_puntos_usuario_id 
ON "UsuarioPuntos"(usuario_id);

CREATE INDEX IF NOT EXISTS idx_insignias_usuario_usuario_id 
ON "UsuarioInsignia"(usuario_id);

CREATE INDEX IF NOT EXISTS idx_insignias_usuario_fecha 
ON "UsuarioInsignia"(fecha_obtencion DESC) WHERE fecha_obtencion IS NOT NULL;

-- ===== ACTUALIZAR ESTADÍSTICAS =====

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

-- ===== VERIFICACIÓN =====

SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
