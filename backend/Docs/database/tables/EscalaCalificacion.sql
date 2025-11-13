-- =====================================================
-- Tabla: EscalaCalificacion
-- =====================================================

CREATE TABLE IF NOT EXISTS EscalaCalificacion (
    escala_id uuid NOT NULL DEFAULT gen_random_uuid(),
    institucion_id uuid NOT NULL,
    nombre character varying(50) NOT NULL,
    tipo USER-DEFINED NOT NULL,
    min_valor numeric,
    max_valor numeric
,
    PRIMARY KEY (escala_id)
);

-- Foreign Keys de EscalaCalificacion
ALTER TABLE EscalaCalificacion ADD CONSTRAINT EscalaCalificacion_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);

-- Check Constraints de EscalaCalificacion
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_1_not_null CHECK (escala_id IS NOT NULL);
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_2_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_3_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_4_not_null CHECK (tipo IS NOT NULL);
