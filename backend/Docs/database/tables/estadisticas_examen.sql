-- =====================================================
-- Tabla: estadisticas_examen
-- =====================================================

CREATE TABLE IF NOT EXISTS estadisticas_examen (
    estadistica_id character varying NOT NULL,
    examen_id character varying NOT NULL,
    total_estudiantes_asignados integer DEFAULT 0,
    total_intentos_realizados integer DEFAULT 0,
    total_intentos_finalizados integer DEFAULT 0,
    total_aprobados integer DEFAULT 0,
    total_reprobados integer DEFAULT 0,
    puntuacion_promedio double precision DEFAULT '0'::double precision,
    puntuacion_mediana double precision DEFAULT '0'::double precision,
    puntuacion_maxima_obtenida double precision DEFAULT '0'::double precision,
    puntuacion_minima_obtenida double precision DEFAULT '0'::double precision,
    desviacion_estandar double precision DEFAULT '0'::double precision,
    tiempo_promedio_minutos double precision DEFAULT '0'::double precision,
    tiempo_maximo_empleado integer DEFAULT 0,
    tiempo_minimo_empleado integer DEFAULT 0,
    estadisticas_preguntas json,
    preguntas_mas_dificiles json,
    preguntas_mas_faciles json,
    patrones_abandono json,
    tiempo_por_pregunta json,
    fecha_calculo timestamp with time zone DEFAULT now(),
    fecha_ultima_actualizacion timestamp with time zone,
    incluir_intentos_incompletos boolean DEFAULT false,
    periodo_calculo character varying(50) DEFAULT 'completo'::character varying
,
    PRIMARY KEY (estadistica_id)
);

-- Foreign Keys de estadisticas_examen
ALTER TABLE estadisticas_examen ADD CONSTRAINT estadisticas_examen_examen_id_fkey FOREIGN KEY (examen_id) REFERENCES examenes(examen_id);

-- Check Constraints de estadisticas_examen
ALTER TABLE estadisticas_examen ADD CONSTRAINT 39558_40893_1_not_null CHECK (estadistica_id IS NOT NULL);
ALTER TABLE estadisticas_examen ADD CONSTRAINT 39558_40893_2_not_null CHECK (examen_id IS NOT NULL);
