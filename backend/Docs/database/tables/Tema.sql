-- =====================================================
-- Tabla: Tema
-- =====================================================

CREATE TABLE IF NOT EXISTS Tema (
    tema_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    emoji character varying(8) NOT NULL
,
    PRIMARY KEY (tema_id)
);

-- Check Constraints de Tema
ALTER TABLE Tema ADD CONSTRAINT 39558_39677_1_not_null CHECK (tema_id IS NOT NULL);
ALTER TABLE Tema ADD CONSTRAINT 39558_39677_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Tema ADD CONSTRAINT 39558_39677_3_not_null CHECK (emoji IS NOT NULL);
