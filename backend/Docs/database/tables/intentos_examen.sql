-- =====================================================
-- Tabla: intentos_examen
-- =====================================================

CREATE TABLE IF NOT EXISTS intentos_examen (
    intento_id character varying NOT NULL,
    examen_id character varying NOT NULL,
    estudiante_id character varying NOT NULL,
    numero_intento integer NOT NULL,
    estado_intento character varying(50) NOT NULL DEFAULT 'en_progreso'::character varying,
    fecha_inicio timestamp with time zone DEFAULT now(),
    fecha_fin timestamp with time zone,
    tiempo_total_segundos integer,
    tiempo_limite_vencido boolean DEFAULT false,
    puntuacion_obtenida double precision DEFAULT '0'::double precision,
    puntuacion_maxima double precision NOT NULL,
    porcentaje double precision,
    aprobado boolean,
    preguntas_respondidas integer DEFAULT 0,
    total_preguntas integer NOT NULL,
    pregunta_actual integer DEFAULT 1,
    cambios_pestana_detectados integer DEFAULT 0,
    tiempo_inactividad_total integer DEFAULT 0,
    ip_address character varying(45),
    user_agent text,
    eventos_sospechosos json,
    orden_preguntas json,
    configuracion_intento json,
    finalizado_por character varying(50) DEFAULT 'estudiante'::character varying,
    comentarios_finalizacion text,
    fecha_revision timestamp with time zone,
    revisado_por character varying,
    comentarios_profesor text
,
    PRIMARY KEY (intento_id)
);

-- Foreign Keys de intentos_examen
ALTER TABLE intentos_examen ADD CONSTRAINT intentos_examen_examen_id_fkey FOREIGN KEY (examen_id) REFERENCES examenes(examen_id);

-- Check Constraints de intentos_examen
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_11_not_null CHECK (puntuacion_maxima IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_15_not_null CHECK (total_preguntas IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_1_not_null CHECK (intento_id IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_2_not_null CHECK (examen_id IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_3_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_4_not_null CHECK (numero_intento IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_5_not_null CHECK (estado_intento IS NOT NULL);
