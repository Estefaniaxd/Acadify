-- =====================================================
-- Tabla: EstudianteGrupo
-- =====================================================

CREATE TABLE IF NOT EXISTS EstudianteGrupo (
    grupo_id uuid NOT NULL,
    estudiante_id uuid NOT NULL,
    fecha_vinculacion date NOT NULL
,
    PRIMARY KEY (grupo_id, estudiante_id)
);

-- Foreign Keys de EstudianteGrupo
ALTER TABLE EstudianteGrupo ADD CONSTRAINT EstudianteGrupo_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Estudiante(estudiante_id);
ALTER TABLE EstudianteGrupo ADD CONSTRAINT EstudianteGrupo_grupo_id_fkey FOREIGN KEY (grupo_id) REFERENCES Grupo(grupo_id);

-- Check Constraints de EstudianteGrupo
ALTER TABLE EstudianteGrupo ADD CONSTRAINT 39558_40199_1_not_null CHECK (grupo_id IS NOT NULL);
ALTER TABLE EstudianteGrupo ADD CONSTRAINT 39558_40199_2_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE EstudianteGrupo ADD CONSTRAINT 39558_40199_3_not_null CHECK (fecha_vinculacion IS NOT NULL);

-- Índices de EstudianteGrupo
CREATE INDEX idx_estudiante_grupo_grupo_id ON public."EstudianteGrupo" USING btree (grupo_id);
CREATE INDEX idx_estudiante_grupo_estudiante_id ON public."EstudianteGrupo" USING btree (estudiante_id);
CREATE INDEX idx_estudiante_grupo_estudiante_grupo ON public."EstudianteGrupo" USING btree (estudiante_id, grupo_id);
