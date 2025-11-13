-- =====================================================
-- Tabla: preguntas_examen
-- =====================================================

CREATE TABLE IF NOT EXISTS preguntas_examen (
    pregunta_id character varying NOT NULL,
    examen_id character varying NOT NULL,
    titulo text NOT NULL,
    descripcion text,
    tipo_pregunta character varying(50) NOT NULL,
    orden integer NOT NULL,
    puntuacion double precision NOT NULL DEFAULT '1'::double precision,
    es_obligatoria boolean DEFAULT true,
    tiempo_limite_segundos integer,
    opciones_respuesta json,
    respuesta_correcta json,
    explicacion text,
    puntos_respuesta_parcial boolean DEFAULT false,
    dificultad character varying(50) DEFAULT 'medio'::character varying,
    imagen_url character varying(500),
    audio_url character varying(500),
    video_url character varying(500),
    archivos_adjuntos json,
    banco_pregunta_id character varying,
    tags json,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    veces_utilizada integer DEFAULT 0,
    promedio_aciertos double precision,
    tiempo_promedio_respuesta double precision
,
    PRIMARY KEY (pregunta_id)
);

-- Foreign Keys de preguntas_examen
ALTER TABLE preguntas_examen ADD CONSTRAINT preguntas_examen_examen_id_fkey FOREIGN KEY (examen_id) REFERENCES examenes(examen_id);
ALTER TABLE preguntas_examen ADD CONSTRAINT fk_preguntas_examen_banco_pregunta_id FOREIGN KEY (banco_pregunta_id) REFERENCES banco_preguntas(pregunta_id);

-- Check Constraints de preguntas_examen
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_1_not_null CHECK (pregunta_id IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_2_not_null CHECK (examen_id IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_3_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_5_not_null CHECK (tipo_pregunta IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_6_not_null CHECK (orden IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_7_not_null CHECK (puntuacion IS NOT NULL);
