-- =====================================================
-- FUNCIONES ALMACENADAS
-- Sistema Acadify - Funciones de utilidad y cálculos
-- Fecha: 4 noviembre 2025
-- =====================================================

-- =====================================================
-- 1. FUNCIÓN: Actualizar timestamp de modificación
-- =====================================================
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION actualizar_fecha_modificacion() IS 
'Actualiza automáticamente el campo fecha_actualizacion al momento de UPDATE';


-- =====================================================
-- 2. FUNCIÓN: Calcular promedio de estudiante
-- =====================================================
CREATE OR REPLACE FUNCTION calcular_promedio_estudiante(
    p_estudiante_id UUID
)
RETURNS NUMERIC(4,2) AS $$
DECLARE
    v_promedio NUMERIC(4,2);
BEGIN
    -- Calcular promedio de entregas calificadas
    SELECT COALESCE(AVG(calificacion), 0.0)
    INTO v_promedio
    FROM entregas_tareas
    WHERE estudiante_id = p_estudiante_id
    AND calificacion IS NOT NULL
    AND estado = 'calificada';
    
    RETURN ROUND(v_promedio, 2);
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calcular_promedio_estudiante(UUID) IS 
'Calcula el promedio de calificaciones de un estudiante en todas sus entregas';


-- =====================================================
-- 3. FUNCIÓN: Calcular promedio en curso específico
-- =====================================================
CREATE OR REPLACE FUNCTION calcular_promedio_estudiante_curso(
    p_estudiante_id UUID,
    p_curso_id UUID
)
RETURNS NUMERIC(4,2) AS $$
DECLARE
    v_promedio NUMERIC(4,2);
BEGIN
    -- Calcular promedio de entregas calificadas en un curso específico
    SELECT COALESCE(AVG(et.calificacion), 0.0)
    INTO v_promedio
    FROM entregas_tareas et
    INNER JOIN tareas t ON et.tarea_id = t.tarea_id
    WHERE et.estudiante_id = p_estudiante_id
    AND t.curso_id = p_curso_id
    AND et.calificacion IS NOT NULL
    AND et.estado = 'calificada';
    
    RETURN ROUND(v_promedio, 2);
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calcular_promedio_estudiante_curso(UUID, UUID) IS 
'Calcula el promedio de calificaciones de un estudiante en un curso específico';


-- =====================================================
-- 4. FUNCIÓN: Contar entregas pendientes por estudiante
-- =====================================================
CREATE OR REPLACE FUNCTION contar_entregas_pendientes(
    p_estudiante_id UUID
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM entregas_tareas
    WHERE estudiante_id = p_estudiante_id
    AND estado IN ('entregada', 'en_revision')
    AND calificacion IS NULL;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION contar_entregas_pendientes(UUID) IS 
'Cuenta las entregas pendientes de calificación de un estudiante';


-- =====================================================
-- 5. FUNCIÓN: Calcular estadísticas de curso
-- =====================================================
CREATE OR REPLACE FUNCTION calcular_estadisticas_curso(
    p_curso_id UUID
)
RETURNS TABLE(
    total_estudiantes INTEGER,
    total_entregas INTEGER,
    entregas_calificadas INTEGER,
    entregas_pendientes INTEGER,
    promedio_general NUMERIC(4,2),
    tasa_aprobacion NUMERIC(5,2)
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT 
            COUNT(DISTINCT et.estudiante_id) as tot_estudiantes,
            COUNT(et.entrega_id) as tot_entregas,
            COUNT(CASE WHEN et.calificacion IS NOT NULL THEN 1 END) as cal_entregas,
            COUNT(CASE WHEN et.calificacion IS NULL AND et.estado != 'borrador' THEN 1 END) as pend_entregas,
            COALESCE(AVG(et.calificacion), 0.0) as prom,
            COALESCE(
                COUNT(CASE WHEN et.calificacion >= 3.0 THEN 1 END)::NUMERIC / 
                NULLIF(COUNT(CASE WHEN et.calificacion IS NOT NULL THEN 1 END), 0) * 100,
                0.0
            ) as tasa_aprob
        FROM entregas_tareas et
        INNER JOIN tareas t ON et.tarea_id = t.tarea_id
        WHERE t.curso_id = p_curso_id
    )
    SELECT 
        tot_estudiantes::INTEGER,
        tot_entregas::INTEGER,
        cal_entregas::INTEGER,
        pend_entregas::INTEGER,
        ROUND(prom, 2),
        ROUND(tasa_aprob, 2)
    FROM stats;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calcular_estadisticas_curso(UUID) IS 
'Calcula estadísticas completas de un curso: estudiantes, entregas, promedios, etc.';


-- =====================================================
-- 6. FUNCIÓN: Obtener estudiantes en riesgo
-- =====================================================
CREATE OR REPLACE FUNCTION obtener_estudiantes_riesgo(
    p_curso_id UUID DEFAULT NULL,
    p_umbral_promedio NUMERIC DEFAULT 3.0
)
RETURNS TABLE(
    estudiante_id UUID,
    nombre_completo VARCHAR,
    promedio NUMERIC(4,2),
    entregas_pendientes INTEGER,
    ultima_entrega TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    WITH promedios AS (
        SELECT 
            et.estudiante_id,
            AVG(et.calificacion) as promedio,
            COUNT(CASE WHEN et.calificacion IS NULL AND et.estado != 'borrador' THEN 1 END) as pendientes,
            MAX(et.fecha_entrega) as ultima_fecha
        FROM entregas_tareas et
        INNER JOIN tareas t ON et.tarea_id = t.tarea_id
        WHERE (p_curso_id IS NULL OR t.curso_id = p_curso_id)
        AND et.calificacion IS NOT NULL
        GROUP BY et.estudiante_id
    )
    SELECT 
        p.estudiante_id,
        CONCAT(e.nombres, ' ', e.apellidos)::VARCHAR,
        ROUND(p.promedio, 2),
        p.pendientes::INTEGER,
        p.ultima_fecha
    FROM promedios p
    INNER JOIN "Estudiante" e ON p.estudiante_id = e.estudiante_id
    WHERE p.promedio < p_umbral_promedio
    OR p.pendientes > 3
    ORDER BY p.promedio ASC, p.pendientes DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION obtener_estudiantes_riesgo(UUID, NUMERIC) IS 
'Identifica estudiantes con bajo rendimiento o muchas entregas pendientes';


-- =====================================================
-- 7. FUNCIÓN: Validar rango de calificación
-- =====================================================
CREATE OR REPLACE FUNCTION validar_calificacion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.calificacion IS NOT NULL THEN
        IF NEW.calificacion < 0.0 OR NEW.calificacion > 5.0 THEN
            RAISE EXCEPTION 'Calificación debe estar entre 0.0 y 5.0. Valor recibido: %', NEW.calificacion;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validar_calificacion() IS 
'Valida que las calificaciones estén en el rango permitido (0.0 - 5.0)';


-- =====================================================
-- 8. FUNCIÓN: Calcular duración de intento evaluación
-- =====================================================
CREATE OR REPLACE FUNCTION calcular_duracion_intento()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fecha_fin IS NOT NULL AND NEW.fecha_inicio IS NOT NULL THEN
        NEW.duracion_segundos = EXTRACT(EPOCH FROM (NEW.fecha_fin - NEW.fecha_inicio))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calcular_duracion_intento() IS 
'Calcula automáticamente la duración en segundos de un intento de evaluación';


-- =====================================================
-- 9. FUNCIÓN: Registrar auditoría de cambios
-- =====================================================
CREATE OR REPLACE FUNCTION registrar_auditoria()
RETURNS TRIGGER AS $$
DECLARE
    v_cambios JSONB;
BEGIN
    -- Construir JSON con cambios
    v_cambios = jsonb_build_object(
        'tabla', TG_TABLE_NAME,
        'operacion', TG_OP,
        'usuario', current_user,
        'fecha', CURRENT_TIMESTAMP,
        'datos_anteriores', CASE WHEN TG_OP = 'UPDATE' THEN row_to_json(OLD) ELSE NULL END,
        'datos_nuevos', CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END
    );
    
    -- Aquí se podría insertar en una tabla de auditoría
    -- Por ahora solo logueamos
    RAISE NOTICE 'AUDITORÍA: %', v_cambios;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION registrar_auditoria() IS 
'Registra cambios en tablas críticas para auditoría y trazabilidad';


-- =====================================================
-- 10. FUNCIÓN: Validar integridad de evaluación
-- =====================================================
CREATE OR REPLACE FUNCTION validar_integridad_evaluacion(
    p_evaluacion_id UUID
)
RETURNS TABLE(
    es_valida BOOLEAN,
    errores TEXT[]
) AS $$
DECLARE
    v_errores TEXT[] := ARRAY[]::TEXT[];
    v_tiene_preguntas BOOLEAN;
    v_suma_puntajes NUMERIC;
    v_puntaje_maximo NUMERIC;
BEGIN
    -- Verificar que tiene preguntas
    SELECT EXISTS(
        SELECT 1 FROM preguntas_evaluacion 
        WHERE evaluacion_id = p_evaluacion_id
    ) INTO v_tiene_preguntas;
    
    IF NOT v_tiene_preguntas THEN
        v_errores := array_append(v_errores, 'La evaluación no tiene preguntas');
    END IF;
    
    -- Verificar que suma de puntajes coincide con puntaje máximo
    SELECT 
        SUM(puntos),
        e.puntaje_total
    INTO v_suma_puntajes, v_puntaje_maximo
    FROM preguntas_evaluacion p
    INNER JOIN evaluaciones e ON p.evaluacion_id = e.id
    WHERE p.evaluacion_id = p_evaluacion_id
    GROUP BY e.puntaje_total;
    
    IF v_suma_puntajes IS NOT NULL AND v_puntaje_maximo IS NOT NULL THEN
        IF v_suma_puntajes != v_puntaje_maximo THEN
            v_errores := array_append(
                v_errores, 
                format('Suma de puntos de preguntas (%s) no coincide con puntaje total (%s)', 
                    v_suma_puntajes, v_puntaje_maximo)
            );
        END IF;
    END IF;
    
    -- Retornar resultado
    RETURN QUERY SELECT 
        array_length(v_errores, 1) IS NULL,
        v_errores;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION validar_integridad_evaluacion(UUID) IS 
'Valida la integridad de una evaluación: preguntas, puntajes, etc.';


-- =====================================================
-- 11. FUNCIÓN: Obtener ranking de estudiantes por curso
-- =====================================================
CREATE OR REPLACE FUNCTION obtener_ranking_curso(
    p_curso_id UUID,
    p_limite INTEGER DEFAULT 10
)
RETURNS TABLE(
    posicion INTEGER,
    estudiante_id UUID,
    nombre_completo VARCHAR,
    promedio NUMERIC(4,2),
    total_entregas INTEGER,
    entregas_calificadas INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH ranking AS (
        SELECT 
            et.estudiante_id,
            AVG(et.calificacion) as promedio,
            COUNT(*) as total,
            COUNT(CASE WHEN et.calificacion IS NOT NULL THEN 1 END) as calificadas,
            ROW_NUMBER() OVER (ORDER BY AVG(et.calificacion) DESC, COUNT(et.calificacion) DESC) as pos
        FROM entregas_tareas et
        INNER JOIN tareas t ON et.tarea_id = t.tarea_id
        WHERE t.curso_id = p_curso_id
        AND et.calificacion IS NOT NULL
        GROUP BY et.estudiante_id
    )
    SELECT 
        r.pos::INTEGER,
        r.estudiante_id,
        CONCAT(e.nombres, ' ', e.apellidos)::VARCHAR,
        ROUND(r.promedio, 2),
        r.total::INTEGER,
        r.calificadas::INTEGER
    FROM ranking r
    INNER JOIN "Estudiante" e ON r.estudiante_id = e.estudiante_id
    ORDER BY r.pos
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION obtener_ranking_curso(UUID, INTEGER) IS 
'Obtiene el ranking de estudiantes por promedio en un curso';


-- =====================================================
-- FIN DE FUNCIONES
-- =====================================================
