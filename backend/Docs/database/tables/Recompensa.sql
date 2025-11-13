-- =====================================================
-- Tabla: Recompensa
-- =====================================================

CREATE TABLE IF NOT EXISTS Recompensa (
    recompensa_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    descripcion text,
    costo_puntos integer NOT NULL,
    tipo USER-DEFINED NOT NULL DEFAULT 'otro'::tipo_recompensa_enum
,
    PRIMARY KEY (recompensa_id)
);

-- Check Constraints de Recompensa
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_1_not_null CHECK (recompensa_id IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_4_not_null CHECK (costo_puntos IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_5_not_null CHECK (tipo IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT check_costo_puntos_positivo CHECK ((costo_puntos >= 0));
