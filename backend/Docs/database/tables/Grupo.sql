-- =====================================================
-- Tabla: Grupo
-- =====================================================

CREATE TABLE IF NOT EXISTS Grupo (
    grupo_id uuid NOT NULL DEFAULT gen_random_uuid(),
    programa_id uuid NOT NULL,
    docente_tutor_id uuid,
    nombre character varying(50) NOT NULL,
    jornada USER-DEFINED NOT NULL DEFAULT 'manana'::jornada_grupo
,
    PRIMARY KEY (grupo_id)
);

-- Foreign Keys de Grupo
ALTER TABLE Grupo ADD CONSTRAINT Grupo_docente_tutor_id_fkey FOREIGN KEY (docente_tutor_id) REFERENCES Docente(docente_id);
ALTER TABLE Grupo ADD CONSTRAINT Grupo_programa_id_fkey FOREIGN KEY (programa_id) REFERENCES Programa(programa_id);

-- Unique Constraints de Grupo
ALTER TABLE Grupo ADD CONSTRAINT Grupo_docente_tutor_id_key UNIQUE (docente_tutor_id);

-- Check Constraints de Grupo
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_1_not_null CHECK (grupo_id IS NOT NULL);
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_2_not_null CHECK (programa_id IS NOT NULL);
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_4_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_5_not_null CHECK (jornada IS NOT NULL);

-- Índices de Grupo
CREATE UNIQUE INDEX "Grupo_docente_tutor_id_key" ON public."Grupo" USING btree (docente_tutor_id);
