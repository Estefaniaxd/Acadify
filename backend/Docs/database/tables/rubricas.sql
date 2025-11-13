-- =====================================================
-- Tabla: rubricas
-- =====================================================

CREATE TABLE IF NOT EXISTS rubricas (
    rubrica_id character varying NOT NULL,
    nombre character varying(200) NOT NULL,
    descripcion text,
    criterios json NOT NULL,
    puntuacion_total double precision NOT NULL,
    es_publica boolean,
    es_plantilla boolean,
    activa boolean,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    creado_por character varying NOT NULL
,
    PRIMARY KEY (rubrica_id)
);

-- Check Constraints de rubricas
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_11_not_null CHECK (creado_por IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_1_not_null CHECK (rubrica_id IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_4_not_null CHECK (criterios IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_5_not_null CHECK (puntuacion_total IS NOT NULL);
