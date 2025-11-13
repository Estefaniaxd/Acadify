-- =====================================================
-- Tabla: examenes
-- =====================================================

CREATE TABLE IF NOT EXISTS examenes (
    examen_id character varying NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text,
    tipo_examen character varying(50) NOT NULL DEFAULT 'evaluacion'::character varying,
    estado_examen character varying(50) NOT NULL DEFAULT 'borrador'::character varying,
    tiempo_limite integer NOT NULL DEFAULT 60,
    fecha_inicio timestamp with time zone,
    fecha_limite timestamp with time zone,
    intentos_permitidos integer DEFAULT 1,
    requiere_contraseña boolean DEFAULT false,
    contraseña_acceso character varying(100),
    randomizar_preguntas boolean DEFAULT false,
    mostrar_resultados_inmediatos boolean DEFAULT true,
    permitir_revision boolean DEFAULT true,
    mostrar_respuestas_correctas boolean DEFAULT true,
    modo_pantalla_completa boolean DEFAULT false,
    bloquear_navegacion boolean DEFAULT false,
    detectar_cambio_pestana boolean DEFAULT false,
    tiempo_maximo_inactividad integer DEFAULT 300,
    puntuacion_total double precision NOT NULL DEFAULT '100'::double precision,
    puntuacion_minima_aprobacion double precision DEFAULT '60'::double precision,
    calificacion_automatica boolean DEFAULT true,
    curso_id character varying,
    grupo_id character varying,
    creado_por character varying NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    configuracion_avanzada json,
    instrucciones text,
    total_preguntas integer DEFAULT 0,
    total_intentos integer DEFAULT 0,
    promedio_calificacion double precision
,
    PRIMARY KEY (examen_id)
);

-- Check Constraints de examenes
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_1_not_null CHECK (examen_id IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_20_not_null CHECK (puntuacion_total IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_25_not_null CHECK (creado_por IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_2_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_4_not_null CHECK (tipo_examen IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_5_not_null CHECK (estado_examen IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_6_not_null CHECK (tiempo_limite IS NOT NULL);
