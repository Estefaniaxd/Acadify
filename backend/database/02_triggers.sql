-- =====================================================
-- TRIGGERS
-- Sistema Acadify - Triggers automáticos
-- Fecha: 4 noviembre 2025
-- =====================================================

-- =====================================================
-- 1. TRIGGER: Auto-actualizar fecha_actualizacion
-- =====================================================

-- Trigger para tabla Curso
DROP TRIGGER IF EXISTS trigger_curso_fecha_actualizacion ON "Curso";
CREATE TRIGGER trigger_curso_fecha_actualizacion
    BEFORE UPDATE ON "Curso"
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

COMMENT ON TRIGGER trigger_curso_fecha_actualizacion ON "Curso" IS 
'Actualiza automáticamente fecha_actualizacion al modificar un curso';


-- Trigger para tabla Grupo
DROP TRIGGER IF EXISTS trigger_grupo_fecha_actualizacion ON "Grupo";
CREATE TRIGGER trigger_grupo_fecha_actualizacion
    BEFORE UPDATE ON "Grupo"
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

COMMENT ON TRIGGER trigger_grupo_fecha_actualizacion ON "Grupo" IS 
'Actualiza automáticamente fecha_actualizacion al modificar un grupo';


-- Trigger para tabla entregas_tareas
DROP TRIGGER IF EXISTS trigger_entrega_fecha_actualizacion ON entregas_tareas;
CREATE TRIGGER trigger_entrega_fecha_actualizacion
    BEFORE UPDATE ON entregas_tareas
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

COMMENT ON TRIGGER trigger_entrega_fecha_actualizacion ON entregas_tareas IS 
'Actualiza automáticamente fecha_actualizacion al modificar una entrega';


-- Trigger para tabla Comentario
DROP TRIGGER IF EXISTS trigger_comentario_fecha_actualizacion ON "Comentario";
CREATE TRIGGER trigger_comentario_fecha_actualizacion
    BEFORE UPDATE ON "Comentario"
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

COMMENT ON TRIGGER trigger_comentario_fecha_actualizacion ON "Comentario" IS 
'Actualiza automáticamente fecha_actualizacion al modificar un comentario';


-- =====================================================
-- 2. TRIGGER: Validar calificaciones
-- =====================================================

-- Trigger para entregas_tareas
DROP TRIGGER IF EXISTS trigger_validar_calificacion_entrega ON entregas_tareas;
CREATE TRIGGER trigger_validar_calificacion_entrega
    BEFORE INSERT OR UPDATE OF calificacion ON entregas_tareas
    FOR EACH ROW
    EXECUTE FUNCTION validar_calificacion();

COMMENT ON TRIGGER trigger_validar_calificacion_entrega ON entregas_tareas IS 
'Valida que las calificaciones estén en el rango 0.0 - 5.0';


-- Trigger para intentos_evaluacion
-- NOTA: intentos_evaluacion usa puntuacion_obtenida (DOUBLE PRECISION) en lugar de calificacion
-- Por eso comentamos este trigger ya que las puntuaciones son diferentes
-- DROP TRIGGER IF EXISTS trigger_validar_calificacion_intento ON intentos_evaluacion;
-- CREATE TRIGGER trigger_validar_calificacion_intento
--     BEFORE INSERT OR UPDATE OF puntuacion_obtenida ON intentos_evaluacion
--     FOR EACH ROW
--     WHEN (NEW.puntuacion_obtenida IS NOT NULL)
--     EXECUTE FUNCTION validar_calificacion();

-- COMMENT ON TRIGGER trigger_validar_calificacion_intento ON intentos_evaluacion IS 
-- 'Valida que las calificaciones de intentos estén en el rango permitido';


-- =====================================================
-- 3. TRIGGER: Calcular duración de intentos
-- =====================================================

DROP TRIGGER IF EXISTS trigger_calcular_duracion_intento ON intentos_evaluacion;
CREATE TRIGGER trigger_calcular_duracion_intento
    BEFORE INSERT OR UPDATE OF fecha_inicio, fecha_fin ON intentos_evaluacion
    FOR EACH ROW
    EXECUTE FUNCTION calcular_duracion_intento();

COMMENT ON TRIGGER trigger_calcular_duracion_intento ON intentos_evaluacion IS 
'Calcula automáticamente la duración del intento en segundos';


-- =====================================================
-- 4. TRIGGER: Auditoría de cambios en entregas
-- =====================================================

DROP TRIGGER IF EXISTS trigger_auditoria_entregas ON entregas_tareas;
CREATE TRIGGER trigger_auditoria_entregas
    AFTER INSERT OR UPDATE OR DELETE ON entregas_tareas
    FOR EACH ROW
    WHEN (pg_trigger_depth() = 0)  -- Evitar recursión
    EXECUTE FUNCTION registrar_auditoria();

COMMENT ON TRIGGER trigger_auditoria_entregas ON entregas_tareas IS 
'Registra todos los cambios en entregas para auditoría';


-- =====================================================
-- 5. TRIGGER: Auditoría de cambios en evaluaciones
-- =====================================================

DROP TRIGGER IF EXISTS trigger_auditoria_evaluaciones ON evaluaciones;
CREATE TRIGGER trigger_auditoria_evaluaciones
    AFTER INSERT OR UPDATE OR DELETE ON evaluaciones
    FOR EACH ROW
    WHEN (pg_trigger_depth() = 0)
    EXECUTE FUNCTION registrar_auditoria();

COMMENT ON TRIGGER trigger_auditoria_evaluaciones ON evaluaciones IS 
'Registra todos los cambios en evaluaciones para auditoría';


-- =====================================================
-- 6. TRIGGER: Prevenir eliminación de entregas calificadas
-- =====================================================

CREATE OR REPLACE FUNCTION prevenir_eliminacion_calificada()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.calificacion IS NOT NULL THEN
        RAISE EXCEPTION 'No se puede eliminar una entrega que ya ha sido calificada. Entrega ID: %', OLD.entrega_id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_prevenir_eliminacion_calificada ON entregas_tareas;
CREATE TRIGGER trigger_prevenir_eliminacion_calificada
    BEFORE DELETE ON entregas_tareas
    FOR EACH ROW
    EXECUTE FUNCTION prevenir_eliminacion_calificada();

COMMENT ON TRIGGER trigger_prevenir_eliminacion_calificada ON entregas_tareas IS 
'Previene la eliminación de entregas que ya han sido calificadas';


-- =====================================================
-- 7. TRIGGER: Validar cambio de estado de entrega
-- =====================================================

CREATE OR REPLACE FUNCTION validar_cambio_estado_entrega()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar transición de estados
    IF OLD.estado = 'calificada' AND NEW.estado != 'calificada' THEN
        RAISE EXCEPTION 'No se puede cambiar el estado de una entrega calificada';
    END IF;
    
    -- Si se está calificando, debe tener calificación
    IF NEW.estado = 'calificada' AND NEW.calificacion IS NULL THEN
        RAISE EXCEPTION 'No se puede marcar como calificada sin asignar una calificación';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_validar_cambio_estado_entrega ON entregas_tareas;
CREATE TRIGGER trigger_validar_cambio_estado_entrega
    BEFORE UPDATE OF estado ON entregas_tareas
    FOR EACH ROW
    WHEN (OLD.estado IS DISTINCT FROM NEW.estado)
    EXECUTE FUNCTION validar_cambio_estado_entrega();

COMMENT ON TRIGGER trigger_validar_cambio_estado_entrega ON entregas_tareas IS 
'Valida las transiciones de estado permitidas en entregas';


-- =====================================================
-- 8. TRIGGER: Actualizar contadores de curso
-- =====================================================

CREATE OR REPLACE FUNCTION actualizar_contadores_curso()
RETURNS TRIGGER AS $$
DECLARE
    v_curso_id UUID;
BEGIN
    -- Obtener curso_id desde la tarea
    IF TG_OP = 'DELETE' THEN
        SELECT t.curso_id INTO v_curso_id
        FROM tareas t
        WHERE t.tarea_id = OLD.tarea_id;
    ELSE
        SELECT t.curso_id INTO v_curso_id
        FROM tareas t
        WHERE t.tarea_id = NEW.tarea_id;
    END IF;
    
    -- Aquí se podría actualizar una tabla de estadísticas
    -- Por ahora solo notificamos
    RAISE NOTICE 'Actualizando contadores del curso %', v_curso_id;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_contadores_curso ON entregas_tareas;
CREATE TRIGGER trigger_actualizar_contadores_curso
    AFTER INSERT OR UPDATE OR DELETE ON entregas_tareas
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_contadores_curso();

COMMENT ON TRIGGER trigger_actualizar_contadores_curso ON entregas_tareas IS 
'Actualiza contadores y estadísticas del curso cuando cambian las entregas';


-- =====================================================
-- 9. TRIGGER: Validar límite de intentos en evaluación
-- =====================================================

CREATE OR REPLACE FUNCTION validar_limite_intentos()
RETURNS TRIGGER AS $$
DECLARE
    v_intentos_actuales INTEGER;
    v_intentos_maximos INTEGER;
BEGIN
    -- Obtener intentos máximos de la evaluación
    SELECT intentos_maximos INTO v_intentos_maximos
    FROM evaluaciones
    WHERE id = NEW.evaluacion_id;
    
    -- Si no hay límite, permitir
    IF v_intentos_maximos IS NULL OR v_intentos_maximos = 0 THEN
        RETURN NEW;
    END IF;
    
    -- Contar intentos del estudiante
    SELECT COUNT(*) INTO v_intentos_actuales
    FROM intentos_evaluacion
    WHERE evaluacion_id = NEW.evaluacion_id
    AND estudiante_id = NEW.estudiante_id;
    
    -- Validar límite
    IF v_intentos_actuales >= v_intentos_maximos THEN
        RAISE EXCEPTION 'El estudiante ha alcanzado el límite de intentos (%) para esta evaluación', v_intentos_maximos;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_validar_limite_intentos ON intentos_evaluacion;
CREATE TRIGGER trigger_validar_limite_intentos
    BEFORE INSERT ON intentos_evaluacion
    FOR EACH ROW
    EXECUTE FUNCTION validar_limite_intentos();

COMMENT ON TRIGGER trigger_validar_limite_intentos ON intentos_evaluacion IS 
'Valida que el estudiante no exceda el límite de intentos permitidos';


-- =====================================================
-- 10. TRIGGER: Prevenir modificación de intentos finalizados
-- =====================================================

CREATE OR REPLACE FUNCTION prevenir_modificacion_intento_finalizado()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.fecha_fin IS NOT NULL AND OLD.estado_intento = 'completado' THEN
        RAISE EXCEPTION 'No se puede modificar un intento que ya ha sido finalizado';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_prevenir_modificacion_intento ON intentos_evaluacion;
CREATE TRIGGER trigger_prevenir_modificacion_intento
    BEFORE UPDATE ON intentos_evaluacion
    FOR EACH ROW
    WHEN (OLD.fecha_fin IS NOT NULL AND OLD.estado_intento = 'completado')
    EXECUTE FUNCTION prevenir_modificacion_intento_finalizado();

COMMENT ON TRIGGER trigger_prevenir_modificacion_intento ON intentos_evaluacion IS 
'Previene la modificación de intentos que ya han sido finalizados';


-- =====================================================
-- FIN DE TRIGGERS
-- =====================================================
