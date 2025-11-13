-- Script para crear la tabla eventos_audio directamente en PostgreSQL
-- Ejecutar con: psql -U tu_usuario -d acadify < create_eventos_audio_table.sql

-- Crear tabla eventos_audio para almacenar eventos de audio del sistema de proctoring
CREATE TABLE IF NOT EXISTS eventos_audio (
    evento_audio_id SERIAL PRIMARY KEY,
    intento_id VARCHAR NOT NULL,
    nivel_audio FLOAT NOT NULL CHECK (nivel_audio >= 0 AND nivel_audio <= 100),
    frecuencias_detectadas JSONB DEFAULT '[]'::jsonb,
    duracion_ms INTEGER NOT NULL CHECK (duracion_ms > 0),
    es_sospechoso BOOLEAN DEFAULT false,
    descripcion TEXT,
    datos_adicionales JSONB DEFAULT '{}'::jsonb,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key hacia intentos_evaluacion
    CONSTRAINT fk_eventos_audio_intento 
        FOREIGN KEY (intento_id) 
        REFERENCES intentos_evaluacion(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Crear índices para optimizar las consultas
CREATE INDEX IF NOT EXISTS idx_eventos_audio_intento_id 
    ON eventos_audio(intento_id);

CREATE INDEX IF NOT EXISTS idx_eventos_audio_fecha_creacion 
    ON eventos_audio(fecha_creacion DESC);

CREATE INDEX IF NOT EXISTS idx_eventos_audio_sospechoso 
    ON eventos_audio(es_sospechoso) 
    WHERE es_sospechoso = true;

-- Índice para búsquedas por nivel de audio alto
CREATE INDEX IF NOT EXISTS idx_eventos_audio_nivel_alto 
    ON eventos_audio(nivel_audio) 
    WHERE nivel_audio > 70;

-- Comentarios descriptivos
COMMENT ON TABLE eventos_audio IS 'Registra eventos de audio capturados durante el sistema de proctoring';
COMMENT ON COLUMN eventos_audio.evento_audio_id IS 'ID único del evento de audio';
COMMENT ON COLUMN eventos_audio.intento_id IS 'Referencia al intento de examen';
COMMENT ON COLUMN eventos_audio.nivel_audio IS 'Nivel de audio detectado (0-100)';
COMMENT ON COLUMN eventos_audio.frecuencias_detectadas IS 'Array JSON con frecuencias dominantes detectadas';
COMMENT ON COLUMN eventos_audio.duracion_ms IS 'Duración del evento en milisegundos';
COMMENT ON COLUMN eventos_audio.es_sospechoso IS 'Indica si el evento es considerado sospechoso';
COMMENT ON COLUMN eventos_audio.datos_adicionales IS 'Datos adicionales en formato JSON';

-- Verificar que la tabla se creó correctamente
SELECT 
    'Tabla eventos_audio creada exitosamente' AS resultado,
    COUNT(*) AS total_registros
FROM eventos_audio;

-- Mostrar estructura de la tabla
\d eventos_audio
