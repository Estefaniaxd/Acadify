-- =====================================================
-- Tabla: GrupoCurso
-- =====================================================

CREATE TABLE IF NOT EXISTS GrupoCurso (
    grupo_curso_id uuid NOT NULL DEFAULT gen_random_uuid(),
    grupo_id uuid NOT NULL,
    curso_id uuid NOT NULL,
    docente_id uuid NOT NULL,
    fecha_asignacion date
,
    PRIMARY KEY (grupo_curso_id)
);

-- Foreign Keys de GrupoCurso
ALTER TABLE GrupoCurso ADD CONSTRAINT GrupoCurso_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES Curso(curso_id);
ALTER TABLE GrupoCurso ADD CONSTRAINT GrupoCurso_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Docente(docente_id);
ALTER TABLE GrupoCurso ADD CONSTRAINT GrupoCurso_grupo_id_fkey FOREIGN KEY (grupo_id) REFERENCES Grupo(grupo_id);

-- Unique Constraints de GrupoCurso
ALTER TABLE GrupoCurso ADD CONSTRAINT uq_grupo_curso UNIQUE (curso_id, grupo_id);

-- Check Constraints de GrupoCurso
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_1_not_null CHECK (grupo_curso_id IS NOT NULL);
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_2_not_null CHECK (grupo_id IS NOT NULL);
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_3_not_null CHECK (curso_id IS NOT NULL);
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_4_not_null CHECK (docente_id IS NOT NULL);

-- Índices de GrupoCurso
CREATE INDEX idx_grupo_curso_curso_id ON public."GrupoCurso" USING btree (curso_id);
CREATE INDEX idx_grupo_curso_docente_id ON public."GrupoCurso" USING btree (docente_id);
CREATE UNIQUE INDEX uq_grupo_curso ON public."GrupoCurso" USING btree (curso_id, grupo_id);
