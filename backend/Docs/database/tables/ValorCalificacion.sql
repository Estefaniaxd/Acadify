-- =====================================================
-- Tabla: ValorCalificacion
-- =====================================================

CREATE TABLE IF NOT EXISTS ValorCalificacion (
    valor_id uuid NOT NULL DEFAULT gen_random_uuid(),
    escala_id uuid NOT NULL,
    valor character varying(10) NOT NULL,
    descripcion character varying(100),
    orden smallint
,
    PRIMARY KEY (valor_id)
);

-- Foreign Keys de ValorCalificacion
ALTER TABLE ValorCalificacion ADD CONSTRAINT ValorCalificacion_escala_id_fkey FOREIGN KEY (escala_id) REFERENCES EscalaCalificacion(escala_id);

-- Check Constraints de ValorCalificacion
ALTER TABLE ValorCalificacion ADD CONSTRAINT 39558_40148_1_not_null CHECK (valor_id IS NOT NULL);
ALTER TABLE ValorCalificacion ADD CONSTRAINT 39558_40148_2_not_null CHECK (escala_id IS NOT NULL);
ALTER TABLE ValorCalificacion ADD CONSTRAINT 39558_40148_3_not_null CHECK (valor IS NOT NULL);
