-- =====================================================
-- Tabla: Coordinador
-- =====================================================

CREATE TABLE IF NOT EXISTS Coordinador (
    coordinador_id uuid NOT NULL,
    horario_atencion character varying(50),
    fecha_inicio_carrera date NOT NULL
,
    PRIMARY KEY (coordinador_id)
);

-- Foreign Keys de Coordinador
ALTER TABLE Coordinador ADD CONSTRAINT Coordinador_coordinador_id_fkey FOREIGN KEY (coordinador_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de Coordinador
ALTER TABLE Coordinador ADD CONSTRAINT 39558_39740_1_not_null CHECK (coordinador_id IS NOT NULL);
ALTER TABLE Coordinador ADD CONSTRAINT 39558_39740_3_not_null CHECK (fecha_inicio_carrera IS NOT NULL);
