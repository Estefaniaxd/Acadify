-- ============================================================================
-- Migración: Sistema de Misiones para Acadify
-- Fecha: 2025-11-09
-- Descripción: Crea las tablas misiones y misiones_usuario con todos los ENUMs
-- ============================================================================

-- ============================================================================
-- PASO 1: Crear ENUMs
-- ============================================================================

-- ENUM: Tipo de Misión
DO $$ BEGIN
    CREATE TYPE tipo_mision AS ENUM (
        'participacion',
        'entrega',
        'evaluacion',
        'racha',
        'social',
        'logro',
        'puntos'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ENUM: Estado de Misión de Usuario
DO $$ BEGIN
    CREATE TYPE estado_mision AS ENUM (
        'disponible',
        'en_progreso',
        'completada',
        'reclamada',
        'expirada',
        'bloqueada'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ENUM: Frecuencia de Misión
DO $$ BEGIN
    CREATE TYPE frecuencia_mision AS ENUM (
        'diaria',
        'semanal',
        'mensual',
        'unica'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ENUM: Dificultad de Misión
DO $$ BEGIN
    CREATE TYPE dificultad_mision AS ENUM (
        'facil',
        'normal',
        'dificil',
        'epica'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================================================
-- PASO 2: Crear tabla MISIONES
-- ============================================================================

CREATE TABLE IF NOT EXISTS misiones (
    -- Identificador único
    mision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Información básica
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    icono VARCHAR(50),
    
    -- Clasificación
    tipo tipo_mision NOT NULL,
    frecuencia frecuencia_mision NOT NULL,
    dificultad dificultad_mision NOT NULL DEFAULT 'normal',
    
    -- Objetivo
    objetivo INTEGER NOT NULL CHECK (objetivo > 0),
    unidad VARCHAR(50) NOT NULL DEFAULT 'veces',
    
    -- Recompensas
    puntos_recompensa INTEGER NOT NULL DEFAULT 0 CHECK (puntos_recompensa >= 0),
    experiencia_recompensa INTEGER NOT NULL DEFAULT 0 CHECK (experiencia_recompensa >= 0),
    recompensas_extra JSONB DEFAULT '{}',
    
    -- Configuración
    es_activa BOOLEAN NOT NULL DEFAULT true,
    requisitos JSONB DEFAULT '{}',
    orden_visualizacion INTEGER DEFAULT 0,
    
    -- Timestamps
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para tabla misiones
CREATE INDEX IF NOT EXISTS idx_misiones_tipo ON misiones(tipo);
CREATE INDEX IF NOT EXISTS idx_misiones_frecuencia ON misiones(frecuencia);
CREATE INDEX IF NOT EXISTS idx_misiones_dificultad ON misiones(dificultad);
CREATE INDEX IF NOT EXISTS idx_misiones_activa ON misiones(es_activa);
CREATE INDEX IF NOT EXISTS idx_misiones_orden ON misiones(orden_visualizacion);

-- Comentarios para documentación
COMMENT ON TABLE misiones IS 'Tabla de misiones disponibles en el sistema de gamificación';
COMMENT ON COLUMN misiones.mision_id IS 'Identificador único de la misión';
COMMENT ON COLUMN misiones.nombre IS 'Nombre descriptivo de la misión';
COMMENT ON COLUMN misiones.tipo IS 'Tipo de misión: participacion, entrega, evaluacion, racha, social, logro, puntos';
COMMENT ON COLUMN misiones.frecuencia IS 'Frecuencia de la misión: diaria, semanal, mensual, unica';
COMMENT ON COLUMN misiones.dificultad IS 'Nivel de dificultad: facil, normal, dificil, epica';
COMMENT ON COLUMN misiones.objetivo IS 'Cantidad necesaria para completar la misión';
COMMENT ON COLUMN misiones.unidad IS 'Unidad de medida del objetivo (veces, puntos, días, etc.)';
COMMENT ON COLUMN misiones.recompensas_extra IS 'Recompensas adicionales en formato JSON (insignias, avatars, etc.)';

-- ============================================================================
-- PASO 3: Crear tabla MISIONES_USUARIO
-- ============================================================================

CREATE TABLE IF NOT EXISTS misiones_usuario (
    -- Identificador único
    mision_usuario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Referencias
    usuario_id UUID NOT NULL,
    mision_id UUID NOT NULL REFERENCES misiones(mision_id) ON DELETE CASCADE,
    
    -- Estado y progreso
    estado estado_mision NOT NULL DEFAULT 'disponible',
    progreso_actual INTEGER NOT NULL DEFAULT 0 CHECK (progreso_actual >= 0),
    
    -- Fechas de seguimiento
    fecha_asignacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_inicio TIMESTAMP WITH TIME ZONE,
    fecha_completada TIMESTAMP WITH TIME ZONE,
    fecha_reclamada TIMESTAMP WITH TIME ZONE,
    fecha_expiracion TIMESTAMP WITH TIME ZONE,
    
    -- Metadata adicional
    metadata_progreso JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT uq_usuario_mision UNIQUE (usuario_id, mision_id)
);

-- Índices para tabla misiones_usuario
CREATE INDEX IF NOT EXISTS idx_misiones_usuario_usuario ON misiones_usuario(usuario_id);
CREATE INDEX IF NOT EXISTS idx_misiones_usuario_mision ON misiones_usuario(mision_id);
CREATE INDEX IF NOT EXISTS idx_misiones_usuario_estado ON misiones_usuario(estado);
CREATE INDEX IF NOT EXISTS idx_misiones_usuario_fechas ON misiones_usuario(fecha_asignacion, fecha_expiracion);
CREATE INDEX IF NOT EXISTS idx_misiones_usuario_completadas ON misiones_usuario(fecha_completada) WHERE fecha_completada IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_misiones_usuario_activas ON misiones_usuario(usuario_id, estado) WHERE estado IN ('disponible', 'en_progreso');

-- Comentarios para documentación
COMMENT ON TABLE misiones_usuario IS 'Relación entre usuarios y misiones con seguimiento de progreso';
COMMENT ON COLUMN misiones_usuario.mision_usuario_id IS 'Identificador único de la asignación';
COMMENT ON COLUMN misiones_usuario.usuario_id IS 'Referencia al usuario (FK a usuarios.usuario_id)';
COMMENT ON COLUMN misiones_usuario.estado IS 'Estado actual: disponible, en_progreso, completada, reclamada, expirada, bloqueada';
COMMENT ON COLUMN misiones_usuario.progreso_actual IS 'Progreso actual del usuario en la misión';
COMMENT ON COLUMN misiones_usuario.metadata_progreso IS 'Información adicional sobre el progreso en formato JSON';

-- ============================================================================
-- PASO 4: Trigger para actualizar fecha_actualizacion
-- ============================================================================

-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para tabla misiones
DROP TRIGGER IF EXISTS trigger_actualizar_misiones ON misiones;
CREATE TRIGGER trigger_actualizar_misiones
    BEFORE UPDATE ON misiones
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- ============================================================================
-- PASO 5: Datos iniciales - Misiones de ejemplo
-- ============================================================================

-- Misiones diarias
INSERT INTO misiones (nombre, descripcion, icono, tipo, frecuencia, dificultad, objetivo, unidad, puntos_recompensa, experiencia_recompensa, orden_visualizacion)
VALUES 
    ('Asistencia Diaria', 'Inicia sesión en la plataforma', '📅', 'participacion', 'diaria', 'facil', 1, 'veces', 10, 5, 1),
    ('Completar una Tarea', 'Entrega al menos una tarea del día', '✅', 'entrega', 'diaria', 'normal', 1, 'tareas', 25, 15, 2),
    ('Participar en Clase', 'Comenta o reacciona en al menos 3 publicaciones', '💬', 'participacion', 'diaria', 'normal', 3, 'participaciones', 20, 10, 3),
    ('Racha de Estudio', 'Mantén tu racha de días consecutivos', '🔥', 'racha', 'diaria', 'facil', 1, 'días', 15, 8, 4)
ON CONFLICT DO NOTHING;

-- Misiones semanales
INSERT INTO misiones (nombre, descripcion, icono, tipo, frecuencia, dificultad, objetivo, unidad, puntos_recompensa, experiencia_recompensa, orden_visualizacion)
VALUES 
    ('Estudiante Dedicado', 'Completa 5 tareas durante la semana', '📚', 'entrega', 'semanal', 'normal', 5, 'tareas', 100, 50, 1),
    ('Evaluación Semanal', 'Completa al menos 1 evaluación', '📊', 'evaluacion', 'semanal', 'dificil', 1, 'evaluaciones', 150, 75, 2),
    ('Interacción Social', 'Interactúa con 10 compañeros diferentes', '👥', 'social', 'semanal', 'normal', 10, 'interacciones', 80, 40, 3),
    ('Acumulador de Puntos', 'Gana 200 puntos durante la semana', '⭐', 'puntos', 'semanal', 'dificil', 200, 'puntos', 120, 60, 4)
ON CONFLICT DO NOTHING;

-- Misiones mensuales
INSERT INTO misiones (nombre, descripcion, icono, tipo, frecuencia, dificultad, objetivo, unidad, puntos_recompensa, experiencia_recompensa, orden_visualizacion)
VALUES 
    ('Maestro del Mes', 'Completa 20 tareas durante el mes', '🏆', 'entrega', 'mensual', 'epica', 20, 'tareas', 500, 250, 1),
    ('Racha Legendaria', 'Mantén una racha de 30 días consecutivos', '🔥', 'racha', 'mensual', 'epica', 30, 'días', 600, 300, 2),
    ('Evaluador Experto', 'Completa 5 evaluaciones con calificación superior a 80%', '📈', 'evaluacion', 'mensual', 'dificil', 5, 'evaluaciones', 400, 200, 3)
ON CONFLICT DO NOTHING;

-- Misiones únicas (logros especiales)
INSERT INTO misiones (nombre, descripcion, icono, tipo, frecuencia, dificultad, objetivo, unidad, puntos_recompensa, experiencia_recompensa, orden_visualizacion)
VALUES 
    ('Primera Tarea', 'Completa tu primera tarea en la plataforma', '🎯', 'logro', 'unica', 'facil', 1, 'tareas', 50, 25, 1),
    ('Primera Evaluación', 'Completa tu primera evaluación', '📝', 'logro', 'unica', 'normal', 1, 'evaluaciones', 75, 35, 2),
    ('Colaborador Activo', 'Realiza 50 interacciones con compañeros', '🤝', 'logro', 'unica', 'dificil', 50, 'interacciones', 200, 100, 3),
    ('Leyenda de Puntos', 'Acumula 10,000 puntos en total', '💎', 'logro', 'unica', 'epica', 10000, 'puntos', 1000, 500, 4)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 6: Función para auto-asignar misiones diarias
-- ============================================================================

CREATE OR REPLACE FUNCTION asignar_misiones_diarias_usuario(p_usuario_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_mision RECORD;
    v_hoy_inicio TIMESTAMP WITH TIME ZONE;
    v_hoy_fin TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Calcular inicio y fin del día actual
    v_hoy_inicio := DATE_TRUNC('day', CURRENT_TIMESTAMP);
    v_hoy_fin := v_hoy_inicio + INTERVAL '1 day';
    
    -- Recorrer misiones diarias activas
    FOR v_mision IN 
        SELECT mision_id, fecha_creacion + INTERVAL '1 day' as expiracion
        FROM misiones 
        WHERE es_activa = true 
        AND frecuencia = 'diaria'
    LOOP
        -- Verificar si ya tiene esta misión asignada hoy
        IF NOT EXISTS (
            SELECT 1 FROM misiones_usuario 
            WHERE usuario_id = p_usuario_id 
            AND mision_id = v_mision.mision_id
            AND fecha_asignacion >= v_hoy_inicio
        ) THEN
            -- Asignar misión
            INSERT INTO misiones_usuario (
                usuario_id, 
                mision_id, 
                estado, 
                fecha_asignacion,
                fecha_expiracion
            ) VALUES (
                p_usuario_id,
                v_mision.mision_id,
                'disponible',
                CURRENT_TIMESTAMP,
                v_hoy_fin
            )
            ON CONFLICT (usuario_id, mision_id) DO NOTHING;
            
            v_count := v_count + 1;
        END IF;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION asignar_misiones_diarias_usuario IS 'Asigna automáticamente misiones diarias a un usuario específico';

-- ============================================================================
-- PASO 7: Función para expirar misiones vencidas
-- ============================================================================

CREATE OR REPLACE FUNCTION expirar_misiones_vencidas()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE misiones_usuario
    SET estado = 'expirada'
    WHERE estado IN ('disponible', 'en_progreso')
    AND fecha_expiracion IS NOT NULL
    AND fecha_expiracion < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION expirar_misiones_vencidas IS 'Marca como expiradas todas las misiones que han pasado su fecha límite';

-- ============================================================================
-- PASO 8: Vista para estadísticas rápidas
-- ============================================================================

CREATE OR REPLACE VIEW vista_estadisticas_misiones_usuario AS
SELECT 
    mu.usuario_id,
    COUNT(*) as total_misiones,
    COUNT(*) FILTER (WHERE mu.estado = 'completada') as completadas,
    COUNT(*) FILTER (WHERE mu.estado = 'reclamada') as reclamadas,
    COUNT(*) FILTER (WHERE mu.estado = 'en_progreso') as en_progreso,
    COUNT(*) FILTER (WHERE mu.estado = 'expirada') as expiradas,
    SUM(m.puntos_recompensa) FILTER (WHERE mu.estado = 'reclamada') as puntos_ganados_total,
    SUM(m.experiencia_recompensa) FILTER (WHERE mu.estado = 'reclamada') as experiencia_ganada_total,
    MAX(mu.fecha_completada) as ultima_mision_completada
FROM misiones_usuario mu
INNER JOIN misiones m ON mu.mision_id = m.mision_id
GROUP BY mu.usuario_id;

COMMENT ON VIEW vista_estadisticas_misiones_usuario IS 'Vista con estadísticas agregadas de misiones por usuario';

-- ============================================================================
-- FINALIZACIÓN
-- ============================================================================

-- Verificar que todo se creó correctamente
DO $$
DECLARE
    v_enums INTEGER;
    v_tables INTEGER;
    v_indices INTEGER;
    v_misiones INTEGER;
BEGIN
    -- Contar ENUMs
    SELECT COUNT(*) INTO v_enums
    FROM pg_type 
    WHERE typname IN ('tipo_mision', 'estado_mision', 'frecuencia_mision', 'dificultad_mision');
    
    -- Contar tablas
    SELECT COUNT(*) INTO v_tables
    FROM information_schema.tables 
    WHERE table_name IN ('misiones', 'misiones_usuario');
    
    -- Contar índices
    SELECT COUNT(*) INTO v_indices
    FROM pg_indexes 
    WHERE tablename IN ('misiones', 'misiones_usuario');
    
    -- Contar misiones de ejemplo
    SELECT COUNT(*) INTO v_misiones FROM misiones;
    
    RAISE NOTICE '============================================';
    RAISE NOTICE 'MIGRACIÓN COMPLETADA EXITOSAMENTE';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'ENUMs creados: %', v_enums;
    RAISE NOTICE 'Tablas creadas: %', v_tables;
    RAISE NOTICE 'Índices creados: %', v_indices;
    RAISE NOTICE 'Misiones de ejemplo: %', v_misiones;
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Puedes ejecutar: SELECT * FROM misiones;';
    RAISE NOTICE '============================================';
END $$;
