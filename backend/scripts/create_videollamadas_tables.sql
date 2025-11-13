-- ============================================================================
-- Script SQL para crear tablas de Videollamadas con Jitsi Meet
-- ============================================================================
-- Fecha: 2025-11-09
-- Descripción: Crea las tablas necesarias para el sistema de videollamadas
--              usando Jitsi Meet como proveedor
-- ============================================================================

-- Crear ENUMs si no existen
DO $$ BEGIN
    CREATE TYPE tipo_llamada AS ENUM ('VIDEO', 'VOZ');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE estado_videollamada AS ENUM ('PROGRAMADA', 'ACTIVA', 'FINALIZADA', 'CANCELADA');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE calidad_conexion AS ENUM ('excelente', 'buena', 'regular', 'mala');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE formato_grabacion AS ENUM ('mp4', 'webm', 'mkv', 'avi');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE calidad_grabacion AS ENUM ('SD', 'HD', 'FHD', '4K');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE estado_procesamiento AS ENUM ('pendiente', 'procesando', 'completado', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================================================
-- Tabla: videollamadas
-- ============================================================================
CREATE TABLE IF NOT EXISTS videollamadas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jitsi_room_name VARCHAR(255) NOT NULL UNIQUE,
    tipo_llamada tipo_llamada NOT NULL DEFAULT 'VIDEO',
    iniciador_id UUID NOT NULL REFERENCES "Usuario"(usuario_id),
    sala_chat_id UUID REFERENCES salas_chat(id),
    
    -- Timestamps
    fecha_inicio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_fin TIMESTAMPTZ,
    duracion_segundos INTEGER,
    
    -- Estado y configuración
    estado estado_videollamada NOT NULL DEFAULT 'ACTIVA',
    configuracion JSON NOT NULL DEFAULT '{}',
    
    -- Procesamiento posterior
    grabacion_url VARCHAR(500),
    transcripcion TEXT,
    resumen_ia TEXT
);

-- Índices para videollamadas
CREATE INDEX IF NOT EXISTS ix_videollamadas_jitsi_room_name ON videollamadas(jitsi_room_name);
CREATE INDEX IF NOT EXISTS ix_videollamadas_iniciador_id ON videollamadas(iniciador_id);
CREATE INDEX IF NOT EXISTS ix_videollamadas_sala_chat_id ON videollamadas(sala_chat_id);
CREATE INDEX IF NOT EXISTS ix_videollamadas_estado ON videollamadas(estado);
CREATE INDEX IF NOT EXISTS ix_videollamadas_fecha_inicio ON videollamadas(fecha_inicio);

-- Comentarios
COMMENT ON TABLE videollamadas IS 'Tabla principal de videollamadas usando Jitsi Meet';
COMMENT ON COLUMN videollamadas.jitsi_room_name IS 'Nombre único de la sala en Jitsi Meet';
COMMENT ON COLUMN videollamadas.tipo_llamada IS 'Tipo: video (con cámara) o voz (solo audio)';
COMMENT ON COLUMN videollamadas.configuracion IS 'Configuración JSON de Jitsi (max_participantes, calidad, etc)';

-- ============================================================================
-- Tabla: videollamadas_participantes
-- ============================================================================
CREATE TABLE IF NOT EXISTS videollamadas_participantes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    videollamada_id UUID NOT NULL REFERENCES videollamadas(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES "Usuario"(usuario_id),
    
    -- Timestamps
    fecha_union TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_salida TIMESTAMPTZ,
    duracion_segundos INTEGER,
    
    -- Estado de participación
    es_moderador BOOLEAN NOT NULL DEFAULT FALSE,
    calidad_conexion calidad_conexion,
    estadisticas JSON
);

-- Índices para participantes
CREATE INDEX IF NOT EXISTS ix_videollamadas_participantes_videollamada_id ON videollamadas_participantes(videollamada_id);
CREATE INDEX IF NOT EXISTS ix_videollamadas_participantes_usuario_id ON videollamadas_participantes(usuario_id);
CREATE INDEX IF NOT EXISTS ix_videollamadas_participantes_fecha_union ON videollamadas_participantes(fecha_union);

-- Restricción única: un usuario no puede estar duplicado en la misma videollamada activa
CREATE UNIQUE INDEX IF NOT EXISTS uq_participante_videollamada_usuario 
    ON videollamadas_participantes(videollamada_id, usuario_id) 
    WHERE fecha_salida IS NULL;

-- Comentarios
COMMENT ON TABLE videollamadas_participantes IS 'Participantes en videollamadas Jitsi';
COMMENT ON COLUMN videollamadas_participantes.es_moderador IS 'Indica si tiene permisos de moderador en Jitsi';
COMMENT ON COLUMN videollamadas_participantes.calidad_conexion IS 'Calidad de conexión del participante';
COMMENT ON COLUMN videollamadas_participantes.estadisticas IS 'Métricas JSON: latencia, packet_loss, jitter, etc';

-- ============================================================================
-- Tabla: videollamadas_grabaciones
-- ============================================================================
CREATE TABLE IF NOT EXISTS videollamadas_grabaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    videollamada_id UUID NOT NULL REFERENCES videollamadas(id) ON DELETE CASCADE,
    
    -- Información de archivo
    titulo VARCHAR(255) NOT NULL,
    archivo_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    
    -- Especificaciones técnicas
    formato formato_grabacion NOT NULL,
    calidad calidad_grabacion NOT NULL,
    duracion_segundos INTEGER NOT NULL,
    tamano_bytes BIGINT NOT NULL,
    
    -- Procesamiento
    fecha_subida TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    estado_procesamiento estado_procesamiento NOT NULL DEFAULT 'pendiente',
    error_mensaje TEXT,
    metadatos JSON
);

-- Índices para grabaciones
CREATE INDEX IF NOT EXISTS ix_videollamadas_grabaciones_videollamada_id ON videollamadas_grabaciones(videollamada_id);
CREATE INDEX IF NOT EXISTS ix_videollamadas_grabaciones_estado_procesamiento ON videollamadas_grabaciones(estado_procesamiento);
CREATE INDEX IF NOT EXISTS ix_videollamadas_grabaciones_fecha_subida ON videollamadas_grabaciones(fecha_subida);

-- Comentarios
COMMENT ON TABLE videollamadas_grabaciones IS 'Grabaciones de videollamadas almacenadas';
COMMENT ON COLUMN videollamadas_grabaciones.formato IS 'Formato del archivo: mp4, webm, mkv, avi';
COMMENT ON COLUMN videollamadas_grabaciones.calidad IS 'Calidad de video: SD, HD, FHD, 4K';
COMMENT ON COLUMN videollamadas_grabaciones.estado_procesamiento IS 'Estado: pendiente, procesando, completado, error';

-- ============================================================================
-- Vista: videollamadas_activas
-- ============================================================================
CREATE OR REPLACE VIEW videollamadas_activas AS
SELECT 
    v.id,
    v.jitsi_room_name,
    v.tipo_llamada,
    v.fecha_inicio,
    v.estado,
    u.nombres AS iniciador_nombre,
    u.apellidos AS iniciador_apellido,
    COUNT(DISTINCT p.id) FILTER (WHERE p.fecha_salida IS NULL) AS participantes_conectados,
    COUNT(DISTINCT p.id) AS total_participantes
FROM videollamadas v
LEFT JOIN "Usuario" u ON v.iniciador_id = u.usuario_id
LEFT JOIN videollamadas_participantes p ON v.id = p.videollamada_id
WHERE v.estado = 'ACTIVA'
GROUP BY v.id, v.jitsi_room_name, v.tipo_llamada, v.fecha_inicio, v.estado, u.nombres, u.apellidos;

COMMENT ON VIEW videollamadas_activas IS 'Vista de videollamadas actualmente en curso con conteo de participantes';

-- ============================================================================
-- Función: finalizar_videollamada
-- ============================================================================
CREATE OR REPLACE FUNCTION finalizar_videollamada(p_videollamada_id UUID)
RETURNS TABLE (
    success BOOLEAN,
    mensaje TEXT
) AS $$
DECLARE
    v_fecha_inicio TIMESTAMPTZ;
    v_estado estado_videollamada;
BEGIN
    -- Verificar que existe y está activa
    SELECT fecha_inicio, estado INTO v_fecha_inicio, v_estado
    FROM videollamadas
    WHERE id = p_videollamada_id;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Videollamada no encontrada'::TEXT;
        RETURN;
    END IF;
    
    IF v_estado != 'ACTIVA' THEN
        RETURN QUERY SELECT FALSE, 'La videollamada no está activa'::TEXT;
        RETURN;
    END IF;
    
    -- Actualizar videollamada
    UPDATE videollamadas
    SET 
        fecha_fin = NOW(),
        duracion_segundos = EXTRACT(EPOCH FROM (NOW() - v_fecha_inicio))::INTEGER,
        estado = 'FINALIZADA'
    WHERE id = p_videollamada_id;
    
    -- Actualizar participantes que no salieron
    UPDATE videollamadas_participantes
    SET 
        fecha_salida = NOW(),
        duracion_segundos = EXTRACT(EPOCH FROM (NOW() - fecha_union))::INTEGER
    WHERE videollamada_id = p_videollamada_id
      AND fecha_salida IS NULL;
    
    RETURN QUERY SELECT TRUE, 'Videollamada finalizada correctamente'::TEXT;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION finalizar_videollamada IS 'Finaliza una videollamada y actualiza participantes';

-- ============================================================================
-- Función: get_estadisticas_videollamada
-- ============================================================================
CREATE OR REPLACE FUNCTION get_estadisticas_videollamada(p_videollamada_id UUID)
RETURNS JSON AS $$
DECLARE
    v_stats JSON;
BEGIN
    SELECT json_build_object(
        'videollamada_id', v.id,
        'jitsi_room_name', v.jitsi_room_name,
        'duracion_minutos', ROUND(v.duracion_segundos / 60.0, 2),
        'total_participantes', COUNT(DISTINCT p.usuario_id),
        'participantes_actuales', COUNT(DISTINCT p.id) FILTER (WHERE p.fecha_salida IS NULL),
        'duracion_promedio_participante', ROUND(AVG(p.duracion_segundos) / 60.0, 2),
        'tiene_grabacion', EXISTS(SELECT 1 FROM videollamadas_grabaciones WHERE videollamada_id = v.id),
        'total_grabaciones', COUNT(DISTINCT g.id)
    ) INTO v_stats
    FROM videollamadas v
    LEFT JOIN videollamadas_participantes p ON v.id = p.videollamada_id
    LEFT JOIN videollamadas_grabaciones g ON v.id = g.videollamada_id
    WHERE v.id = p_videollamada_id
    GROUP BY v.id, v.jitsi_room_name, v.duracion_segundos;
    
    RETURN v_stats;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_estadisticas_videollamada IS 'Retorna estadísticas completas de una videollamada';

-- ============================================================================
-- Trigger: actualizar_duracion_participante
-- ============================================================================
CREATE OR REPLACE FUNCTION actualizar_duracion_participante()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fecha_salida IS NOT NULL AND OLD.fecha_salida IS NULL THEN
        NEW.duracion_segundos = EXTRACT(EPOCH FROM (NEW.fecha_salida - NEW.fecha_union))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_duracion_participante ON videollamadas_participantes;
CREATE TRIGGER trigger_actualizar_duracion_participante
    BEFORE UPDATE ON videollamadas_participantes
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_duracion_participante();

COMMENT ON FUNCTION actualizar_duracion_participante IS 'Calcula automáticamente la duración cuando un participante sale';

-- ============================================================================
-- Permisos (ajustar según necesidades)
-- ============================================================================
-- GRANT SELECT, INSERT, UPDATE ON videollamadas TO backend_app;
-- GRANT SELECT, INSERT, UPDATE ON videollamadas_participantes TO backend_app;
-- GRANT SELECT, INSERT, UPDATE ON videollamadas_grabaciones TO backend_app;
-- GRANT SELECT ON videollamadas_activas TO backend_app;
-- GRANT EXECUTE ON FUNCTION finalizar_videollamada TO backend_app;
-- GRANT EXECUTE ON FUNCTION get_estadisticas_videollamada TO backend_app;

-- ============================================================================
-- Verificación
-- ============================================================================
SELECT 
    'Tablas creadas correctamente' AS status,
    COUNT(*) FILTER (WHERE table_name = 'videollamadas') AS tabla_videollamadas,
    COUNT(*) FILTER (WHERE table_name = 'videollamadas_participantes') AS tabla_participantes,
    COUNT(*) FILTER (WHERE table_name = 'videollamadas_grabaciones') AS tabla_grabaciones
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('videollamadas', 'videollamadas_participantes', 'videollamadas_grabaciones');

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
