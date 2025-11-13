-- =====================================================
-- Tabla: CursoDocente
-- =====================================================

CREATE TABLE IF NOT EXISTS CursoDocente (
    curso_id uuid NOT NULL,
    docente_id uuid NOT NULL,
    fecha_asignacion date
,
    PRIMARY KEY (curso_id, docente_id)
);

-- Foreign Keys de CursoDocente
ALTER TABLE CursoDocente ADD CONSTRAINT CursoDocente_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES Curso(curso_id);
ALTER TABLE CursoDocente ADD CONSTRAINT CursoDocente_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Docente(docente_id);

-- Check Constraints de CursoDocente
ALTER TABLE CursoDocente ADD CONSTRAINT 39558_40184_1_not_null CHECK (curso_id IS NOT NULL);
ALTER TABLE CursoDocente ADD CONSTRAINT 39558_40184_2_not_null CHECK (docente_id IS NOT NULL);
