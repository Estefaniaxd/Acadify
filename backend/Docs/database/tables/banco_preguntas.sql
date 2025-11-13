-- =====================================================
-- Tabla: banco_preguntas
-- =====================================================

CREATE TABLE IF NOT EXISTS banco_preguntas (
    pregunta_id character varying NOT NULL,
    titulo text NOT NULL,
    descripcion text,
    tipo_pregunta character varying(50) NOT NULL,
    dificultad character varying(50) DEFAULT 'medio'::character varying,
    materia character varying(100),
    tema character varying(200),
    subtema character varying(200),
    opciones_respuesta json,
    respuesta_correcta json,
    explicacion text,
    imagen_url character varying(500),
    audio_url character varying(500),
    video_url character varying(500),
    archivos_adjuntos json,
    creado_por character varying NOT NULL,
    institucion_id character varying,
    es_publica boolean DEFAULT false,
    tags json,
    categoria character varying(100),
    nivel_educativo character varying(50),
    puntuacion_sugerida double precision DEFAULT '1'::double precision,
    tiempo_estimado_segundos integer,
    veces_utilizada integer DEFAULT 0,
    promedio_aciertos double precision,
    calificacion_dificultad double precision,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    ultima_vez_utilizada timestamp with time zone,
    revisado_por character varying,
    fecha_revision timestamp with time zone,
    estado_revision character varying(50) DEFAULT 'pendiente'::character varying,
    comentarios_revision text
,
    PRIMARY KEY (pregunta_id)
);

-- Check Constraints de banco_preguntas
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_16_not_null CHECK (creado_por IS NOT NULL);
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_1_not_null CHECK (pregunta_id IS NOT NULL);
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_2_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_4_not_null CHECK (tipo_pregunta IS NOT NULL);
