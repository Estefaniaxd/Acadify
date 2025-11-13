-- =====================================================
-- Tabla: eventos_anti_trampa
-- =====================================================

CREATE TABLE IF NOT EXISTS eventos_anti_trampa (
    evento_id character varying NOT NULL,
    intento_id character varying NOT NULL,
    tipo_evento character varying(50) NOT NULL,
    descripcion text,
    datos_evento json,
    ip_address character varying(45),
    user_agent text,
    timestamp timestamp with time zone DEFAULT now(),
    es_sospechoso boolean DEFAULT false,
    nivel_riesgo character varying(20) DEFAULT 'bajo'::character varying,
    requiere_revision boolean DEFAULT false
,
    PRIMARY KEY (evento_id)
);

-- Foreign Keys de eventos_anti_trampa
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT eventos_anti_trampa_intento_id_fkey FOREIGN KEY (intento_id) REFERENCES intentos_examen(intento_id);

-- Check Constraints de eventos_anti_trampa
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT 39558_40921_1_not_null CHECK (evento_id IS NOT NULL);
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT 39558_40921_2_not_null CHECK (intento_id IS NOT NULL);
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT 39558_40921_3_not_null CHECK (tipo_evento IS NOT NULL);
