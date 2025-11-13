-- =====================================================
-- Tabla: respuestas_estudiante
-- =====================================================

CREATE TABLE IF NOT EXISTS respuestas_estudiante (
    respuesta_id character varying NOT NULL,
    intento_id character varying NOT NULL,
    pregunta_id character varying NOT NULL,
    respuesta_estudiante json,
    texto_respuesta text,
    puntuacion_obtenida double precision DEFAULT '0'::double precision,
    puntuacion_maxima double precision NOT NULL,
    es_correcta boolean,
    calificada_automaticamente boolean DEFAULT false,
    fecha_respuesta timestamp with time zone DEFAULT now(),
    tiempo_empleado_segundos integer,
    fecha_ultima_modificacion timestamp with time zone,
    historial_respuestas json,
    numero_modificaciones integer DEFAULT 0,
    feedback_automatico text,
    feedback_profesor text,
    mostrar_respuesta_correcta boolean DEFAULT false,
    palabras_clave_encontradas json,
    similitud_respuesta_correcta double precision,
    version_pregunta character varying(50),
    metadata_respuesta json
,
    PRIMARY KEY (respuesta_id)
);

-- Foreign Keys de respuestas_estudiante
ALTER TABLE respuestas_estudiante ADD CONSTRAINT respuestas_estudiante_intento_id_fkey FOREIGN KEY (intento_id) REFERENCES intentos_examen(intento_id);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT respuestas_estudiante_pregunta_id_fkey FOREIGN KEY (pregunta_id) REFERENCES preguntas_examen(pregunta_id);

-- Check Constraints de respuestas_estudiante
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_1_not_null CHECK (respuesta_id IS NOT NULL);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_2_not_null CHECK (intento_id IS NOT NULL);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_3_not_null CHECK (pregunta_id IS NOT NULL);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_7_not_null CHECK (puntuacion_maxima IS NOT NULL);
