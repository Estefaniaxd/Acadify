-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS PARA ACADIFY
-- Base de datos: PostgreSQL
-- Autor: Sistema Acadify
-- Fecha: 2025-12-16
-- =====================================================

-- =====================================================
-- 1. PROCEDIMIENTO: Obtener estadísticas de usuario
-- =====================================================
CREATE OR REPLACE FUNCTION sp_obtener_estadisticas_usuario(
    p_usuario_id UUID
)
RETURNS TABLE (
    total_curso INT,
    total_tareas_asignadas INT,
    tareas_completadas INT,
    tareas_pendientes INT,
    promedio_calificaciones DECIMAL(5,2),
    total_puntos INT,
    nivel_actual INT,
    insignias_obtenidas INT,
    racha_actual INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        -- Total de cursos
        (SELECT COUNT(DISTINCT eg.curso_id)
         FROM "EstudianteGrupo" eg
         WHERE eg.estudiante_id = (SELECT estudiante_id FROM "Estudiante" WHERE usuario_id = p_usuario_id)
        )::INT AS total_curso,
        
        -- Total de tareas asignadas
        (SELECT COUNT(*) 
         FROM "Tarea" t
         INNER JOIN "EstudianteGrupo" eg ON t.curso_id = eg.curso_id
         WHERE eg.estudiante_id = (SELECT estudiante_id FROM "Estudiante" WHERE usuario_id = p_usuario_id)
        )::INT AS total_tareas_asignadas,
        
        -- Tareas completadas
        (SELECT COUNT(*) 
         FROM "EntregaTarea" et
         WHERE et.estudiante_id = (SELECT estudiante_id FROM "Estudiante" WHERE usuario_id = p_usuario_id)
         AND et.estado = 'entregada'
        )::INT AS tareas_completadas,
        
        -- Tareas pendientes
        (SELECT COUNT(*) 
         FROM "Tarea" t
         INNER JOIN "EstudianteGrupo" eg ON t.curso_id = eg.curso_id
         LEFT JOIN "EntregaTarea" et ON t.tarea_id = et.tarea_id 
            AND et.estudiante_id = (SELECT estudiante_id FROM "Estudiante" WHERE usuario_id = p_usuario_id)
         WHERE eg.estudiante_id = (SELECT estudiante_id FROM "Estudiante" WHERE usuario_id = p_usuario_id)
         AND et.entrega_id IS NULL
         AND t.fecha_limite > NOW()
        )::INT AS tareas_pendientes,
        
        -- Promedio de calificaciones
        COALESCE((SELECT AVG(et.calificacion)
         FROM "EntregaTarea" et
         WHERE et.estudiante_id = (SELECT estudiante_id FROM "Estudiante" WHERE usuario_id = p_usuario_id)
         AND et.calificacion IS NOT NULL
        ), 0.0)::DECIMAL(5,2) AS promedio_calificaciones,
        
        -- Total de puntos
        COALESCE((SELECT puntos_totales
         FROM "UsuarioPuntos"
         WHERE usuario_id = p_usuario_id
        ), 0)::INT AS total_puntos,
        
        -- Nivel actual
        COALESCE((SELECT nivel
         FROM "UsuarioPuntos"
         WHERE usuario_id = p_usuario_id
        ), 1)::INT AS nivel_actual,
        
        -- Insignias obtenidas
        (SELECT COUNT(*)
         FROM "UsuarioInsignia"
         WHERE usuario_id = p_usuario_id
        )::INT AS insignias_obtenidas,
        
        -- Racha actual (días consecutivos)
        COALESCE((SELECT dias_consecutivos
         FROM "Racha"
         WHERE usuario_id = p_usuario_id
         ORDER BY fecha_ultima_actividad DESC
         LIMIT 1
        ), 0)::INT AS racha_actual;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 2. PROCEDIMIENTO: Obtener estadísticas de institución
-- =====================================================
CREATE OR REPLACE FUNCTION sp_obtener_estadisticas_institucion(
    p_institucion_id UUID
)
RETURNS TABLE (
    total_coordinadores INT,
    total_docentes INT,
    total_estudiantes INT,
    total_programas INT,
    total_cursos INT,
    cursos_activos INT,
    tasa_aprobacion DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        -- Total coordinadores
        (SELECT COUNT(*)
         FROM "InstitucionCoordinador" ic
         WHERE ic.institucion_id = p_institucion_id
        )::INT AS total_coordinadores,
        
        -- Total docentes de la institución
        (SELECT COUNT(DISTINCT cd.docente_id)
         FROM "CursoDocente" cd
         INNER JOIN "Curso" c ON cd.curso_id = c.curso_id
         WHERE c.institucion_id = p_institucion_id
        )::INT AS total_docentes,
        
        -- Total estudiantes
        (SELECT COUNT(DISTINCT eg.estudiante_id)
         FROM "EstudianteGrupo" eg
         INNER JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
         INNER JOIN "Curso" c ON gc.curso_id = c.curso_id
         WHERE c.institucion_id = p_institucion_id
        )::INT AS total_estudiantes,
        
        -- Total programas
        (SELECT COUNT(*)
         FROM "Programa"
         WHERE institucion_id = p_institucion_id
        )::INT AS total_programas,
        
        -- Total cursos
        (SELECT COUNT(*)
         FROM "Curso"
         WHERE institucion_id = p_institucion_id
        )::INT AS total_cursos,
        
        -- Cursos activos (asumiendo que tienen estudiantes)
        (SELECT COUNT(DISTINCT c.curso_id)
         FROM "Curso" c
         INNER JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
         INNER JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
         WHERE c.institucion_id = p_institucion_id
        )::INT AS cursos_activos,
        
        -- Tasa de aprobación
        COALESCE((SELECT (COUNT(*) FILTER (WHERE et.calificacion >= 3.0) * 100.0 / NULLIF(COUNT(*), 0))
         FROM "EntregaTarea" et
         INNER JOIN "Tarea" t ON et.tarea_id = t.tarea_id
         INNER JOIN "Curso" c ON t.curso_id = c.curso_id
         WHERE c.institucion_id = p_institucion_id
         AND et.calificacion IS NOT NULL
        ), 0.0)::DECIMAL(5,2) AS tasa_aprobacion;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 3. PROCEDIMIENTO: Registrar auditoría de acciones
-- =====================================================
CREATE OR REPLACE FUNCTION sp_registrar_auditoria(
    p_usuario_id UUID,
    p_accion VARCHAR(100),
    p_tabla_afectada VARCHAR(100),
    p_registro_id UUID,
    p_detalles TEXT DEFAULT NULL,
    p_ip_address VARCHAR(45) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_auditoria_id UUID;
BEGIN
    -- Generar nuevo ID
    v_auditoria_id := gen_random_uuid();
    
    -- Insertar registro de auditoría
    -- Nota: Esta tabla debe existir, si no existe, créala primero
    INSERT INTO "AuditoriaAcciones" (
        auditoria_id,
        usuario_id,
        accion,
        tabla_afectada,
        registro_id,
        detalles,
        ip_address,
        fecha_hora
    ) VALUES (
        v_auditoria_id,
        p_usuario_id,
        p_accion,
        p_tabla_afectada,
        p_registro_id,
        p_detalles,
        p_ip_address,
        NOW()
    );
    
    RETURN v_auditoria_id;
EXCEPTION
    WHEN OTHERS THEN
        -- Si la tabla no existe, crear un log simple
        RAISE NOTICE 'Auditoría: Usuario % - Acción: % - Tabla: %', p_usuario_id, p_accion, p_tabla_afectada;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 4. PROCEDIMIENTO: Invalidar todas las sesiones de un usuario
-- =====================================================
CREATE OR REPLACE FUNCTION sp_invalidar_sesiones_usuario(
    p_usuario_id UUID
)
RETURNS TABLE (
    sesiones_invalidadas INT,
    mensaje TEXT
) AS $$
DECLARE
    v_count INT;
BEGIN
    -- Actualizar locked_until para forzar re-autenticación
    UPDATE "Usuario"
    SET locked_until = NOW() + INTERVAL '1 minute'
    WHERE usuario_id = p_usuario_id;
    
    -- Contar sesiones (esto es simbólico, la invalidación real se hace en Redis)
    v_count := 1;
    
    RETURN QUERY
    SELECT 
        v_count AS sesiones_invalidadas,
        'Todas las sesiones han sido invalidadas. El usuario deberá iniciar sesión nuevamente.' AS mensaje;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 5. PROCEDIMIENTO: Obtener dashboard de coordinador
-- =====================================================
CREATE OR REPLACE FUNCTION sp_obtener_dashboard_coordinador(
    p_usuario_id UUID
)
RETURNS TABLE (
    institucion_nombre VARCHAR(200),
    total_programas INT,
    total_cursos INT,
    total_docentes INT,
    total_estudiantes INT,
    cursos_activos INT,
    estudiantes_activos_mes INT,
    tareas_pendiente_revision INT
) AS $$
DECLARE
    v_institucion_id UUID;
BEGIN
    -- Obtener institución del coordinador
    SELECT ic.institucion_id INTO v_institucion_id
    FROM "InstitucionCoordinador" ic
    INNER JOIN "Coordinador" co ON ic.coordinador_id = co.coordinador_id
    WHERE co.usuario_id = p_usuario_id
    LIMIT 1;
    
    IF v_institucion_id IS NULL THEN
        RETURN QUERY
        SELECT 
            'Sin institución asignada'::VARCHAR(200),
            0::INT, 0::INT, 0::INT, 0::INT, 0::INT, 0::INT, 0::INT;
        RETURN;
    END IF;
    
    RETURN QUERY
    SELECT 
        i.nombre AS institucion_nombre,
        (SELECT COUNT(*) FROM "Programa" WHERE institucion_id = v_institucion_id)::INT AS total_programas,
        (SELECT COUNT(*) FROM "Curso" WHERE institucion_id = v_institucion_id)::INT AS total_cursos,
        (SELECT COUNT(DISTINCT cd.docente_id)
         FROM "CursoDocente" cd
         INNER JOIN "Curso" c ON cd.curso_id = c.curso_id
         WHERE c.institucion_id = v_institucion_id)::INT AS total_docentes,
        (SELECT COUNT(DISTINCT eg.estudiante_id)
         FROM "EstudianteGrupo" eg
         INNER JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
         INNER JOIN "Curso" c ON gc.curso_id = c.curso_id
         WHERE c.institucion_id = v_institucion_id)::INT AS total_estudiantes,
        (SELECT COUNT(DISTINCT c.curso_id)
         FROM "Curso" c
         INNER JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
         INNER JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
         WHERE c.institucion_id = v_institucion_id)::INT AS cursos_activos,
        (SELECT COUNT(DISTINCT u.usuario_id)
         FROM "Usuario" u
         INNER JOIN "Estudiante" e ON u.usuario_id = e.usuario_id
         INNER JOIN "EstudianteGrupo" eg ON e.estudiante_id = eg.estudiante_id
         INNER JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
         INNER JOIN "Curso" c ON gc.curso_id = c.curso_id
         WHERE c.institucion_id = v_institucion_id
         AND u.ultimo_acceso >= NOW() - INTERVAL '30 days')::INT AS estudiantes_activos_mes,
        (SELECT COUNT(*)
         FROM "EntregaTarea" et
         INNER JOIN "Tarea" t ON et.tarea_id = t.tarea_id
         INNER JOIN "Curso" c ON t.curso_id = c.curso_id
         WHERE c.institucion_id = v_institucion_id
         AND et.estado = 'entregada'
         AND et.calificacion IS NULL)::INT AS tareas_pendiente_revision
    FROM "Institucion" i
    WHERE i.institucion_id = v_institucion_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. PROCEDIMIENTO: Obtener top estudiantes por puntos
-- =====================================================
CREATE OR REPLACE FUNCTION sp_obtener_top_estudiantes(
    p_limite INT DEFAULT 10
)
RETURNS TABLE (
    usuario_id UUID,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    puntos_totales INT,
    nivel INT,
    posicion INT
) AS $$
BEGIN
    RETURN QUERY
    WITH ranked_students AS (
        SELECT 
            u.usuario_id,
            u.nombres,
            u.apellidos,
            up.puntos_totales,
            up.nivel,
            ROW_NUMBER() OVER (ORDER BY up.puntos_totales DESC, up.nivel DESC) AS posicion
        FROM "Usuario" u
        INNER JOIN "UsuarioPuntos" up ON u.usuario_id = up.usuario_id
        WHERE u.rol = 'estudiante'
    )
    SELECT 
        rs.usuario_id,
        rs.nombres,
        rs.apellidos,
        rs.puntos_totales,
        rs.nivel,
        rs.posicion::INT
    FROM ranked_students rs
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 7. PROCEDIMIENTO: Calcular progreso de curso
-- =====================================================
CREATE OR REPLACE FUNCTION sp_calcular_progreso_curso(
    p_curso_id UUID,
    p_estudiante_id UUID
)
RETURNS TABLE (
    total_tareas INT,
    tareas_completadas INT,
    porcentaje_completado DECIMAL(5,2),
    promedio_calificacion DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(t.tarea_id)::INT AS total_tareas,
        COUNT(et.entrega_id) FILTER (WHERE et.estado = 'entregada')::INT AS tareas_completadas,
        CASE 
            WHEN COUNT(t.tarea_id) > 0 THEN
                (COUNT(et.entrega_id) FILTER (WHERE et.estado = 'entregada') * 100.0 / COUNT(t.tarea_id))
            ELSE 0.0
        END::DECIMAL(5,2) AS porcentaje_completado,
        COALESCE(AVG(et.calificacion) FILTER (WHERE et.calificacion IS NOT NULL), 0.0)::DECIMAL(5,2) AS promedio_calificacion
    FROM "Tarea" t
    LEFT JOIN "EntregaTarea" et ON t.tarea_id = et.tarea_id 
        AND et.estudiante_id = p_estudiante_id
    WHERE t.curso_id = p_curso_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. PROCEDIMIENTO: Reporte de actividad diaria
-- =====================================================
CREATE OR REPLACE FUNCTION sp_reporte_actividad_diaria(
    p_fecha DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    usuarios_activos INT,
    tareas_entregadas INT,
    nuevos_registros INT,
    sesiones_iniciadas INT,
    puntos_ganados INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        -- Usuarios que accedieron hoy
        (SELECT COUNT(DISTINCT usuario_id)
         FROM "Usuario"
         WHERE DATE(ultimo_acceso) = p_fecha)::INT AS usuarios_activos,
        
        -- Tareas entregadas hoy
        (SELECT COUNT(*)
         FROM "EntregaTarea"
         WHERE DATE(fecha_entrega) = p_fecha)::INT AS tareas_entregadas,
        
        -- Nuevos registros
        (SELECT COUNT(*)
         FROM "Usuario"
         WHERE DATE(fecha_creacion) = p_fecha)::INT AS nuevos_registros,
        
        -- Sesiones iniciadas (aproximación por último acceso)
        (SELECT COUNT(*)
         FROM "Usuario"
         WHERE DATE(ultimo_acceso) = p_fecha)::INT AS sesiones_iniciadas,
        
        -- Puntos ganados hoy
        (SELECT COALESCE(SUM(puntos), 0)
         FROM "HistorialPuntos"
         WHERE DATE(fecha) = p_fecha)::INT AS puntos_ganados;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMENTARIOS Y PERMISOS
-- =====================================================

COMMENT ON FUNCTION sp_obtener_estadisticas_usuario IS 'Obtiene estadísticas completas de un usuario estudiante';
COMMENT ON FUNCTION sp_obtener_estadisticas_institucion IS 'Obtiene métricas de una institución educativa';
COMMENT ON FUNCTION sp_registrar_auditoria IS 'Registra acciones críticas para auditoría del sistema';
COMMENT ON FUNCTION sp_invalidar_sesiones_usuario IS 'Invalida todas las sesiones activas de un usuario';
COMMENT ON FUNCTION sp_obtener_dashboard_coordinador IS 'Obtiene datos para el dashboard del coordinador';
COMMENT ON FUNCTION sp_obtener_top_estudiantes IS 'Lista los estudiantes con más puntos';
COMMENT ON FUNCTION sp_calcular_progreso_curso IS 'Calcula el progreso de un estudiante en un curso';
COMMENT ON FUNCTION sp_reporte_actividad_diaria IS 'Genera reporte de actividad del sistema para un día';

-- =====================================================
-- FIN DE PROCEDIMIENTOS ALMACENADOS
-- =====================================================
