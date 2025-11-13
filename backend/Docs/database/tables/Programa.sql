-- =====================================================
-- Tabla: Programa
-- =====================================================

CREATE TABLE IF NOT EXISTS Programa (
    programa_id uuid NOT NULL DEFAULT gen_random_uuid(),
    institucion_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    nivel USER-DEFINED NOT NULL,
    tipo USER-DEFINED NOT NULL
,
    PRIMARY KEY (programa_id)
);

-- Foreign Keys de Programa
ALTER TABLE Programa ADD CONSTRAINT Programa_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);

-- Unique Constraints de Programa
ALTER TABLE Programa ADD CONSTRAINT uq_programa_nombre UNIQUE (institucion_id, nombre);

-- Check Constraints de Programa
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_1_not_null CHECK (programa_id IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_2_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_3_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_5_not_null CHECK (nivel IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_6_not_null CHECK (tipo IS NOT NULL);

-- Índices de Programa
CREATE UNIQUE INDEX uq_programa_nombre ON public."Programa" USING btree (institucion_id, nombre);
