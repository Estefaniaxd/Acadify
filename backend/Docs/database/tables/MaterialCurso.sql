-- =====================================================
-- Tabla: MaterialCurso
-- =====================================================

CREATE TABLE IF NOT EXISTS MaterialCurso (
    material_curso_id uuid NOT NULL,
    curso_id uuid NOT NULL
,
    PRIMARY KEY (material_curso_id, curso_id)
);

-- Foreign Keys de MaterialCurso
ALTER TABLE MaterialCurso ADD CONSTRAINT MaterialCurso_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES Curso(curso_id);
ALTER TABLE MaterialCurso ADD CONSTRAINT MaterialCurso_material_curso_id_fkey FOREIGN KEY (material_curso_id) REFERENCES MaterialEducativo(material_id);

-- Check Constraints de MaterialCurso
ALTER TABLE MaterialCurso ADD CONSTRAINT 39558_40237_1_not_null CHECK (material_curso_id IS NOT NULL);
ALTER TABLE MaterialCurso ADD CONSTRAINT 39558_40237_2_not_null CHECK (curso_id IS NOT NULL);

-- Índices de MaterialCurso
CREATE INDEX idx_material_curso_curso_id ON public."MaterialCurso" USING btree (curso_id);
