-- =====================================================
-- Tabla: Curso
-- =====================================================

CREATE TABLE IF NOT EXISTS Curso (
    curso_id uuid NOT NULL DEFAULT gen_random_uuid(),
    institucion_id uuid NOT NULL,
    coordinador_id uuid,
    programa_id uuid NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion text,
    modalidad USER-DEFINED NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    objetivos text,
    codigo_curso character varying(20),
    codigo_acceso character varying(10),
    creditos integer DEFAULT 0,
    horas_academicas integer DEFAULT 0,
    activo boolean NOT NULL DEFAULT true,
    permite_inscripcion boolean NOT NULL DEFAULT true,
    maximo_estudiantes integer,
    minimo_estudiantes integer DEFAULT 1,
    permite_material_estudiantes boolean NOT NULL DEFAULT false,
    requiere_aprobacion_material boolean NOT NULL DEFAULT true
,
    PRIMARY KEY (curso_id)
);

-- Foreign Keys de Curso
ALTER TABLE Curso ADD CONSTRAINT Curso_coordinador_id_fkey FOREIGN KEY (coordinador_id) REFERENCES Coordinador(coordinador_id);
ALTER TABLE Curso ADD CONSTRAINT Curso_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);
ALTER TABLE Curso ADD CONSTRAINT Curso_programa_id_fkey FOREIGN KEY (programa_id) REFERENCES Programa(programa_id);

-- Unique Constraints de Curso
ALTER TABLE Curso ADD CONSTRAINT Curso_codigo_acceso_key UNIQUE (codigo_acceso);
ALTER TABLE Curso ADD CONSTRAINT uq_curso_nombre UNIQUE (institucion_id, nombre);

-- Check Constraints de Curso
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_15_not_null CHECK (activo IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_16_not_null CHECK (permite_inscripcion IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_19_not_null CHECK (permite_material_estudiantes IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_1_not_null CHECK (curso_id IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_20_not_null CHECK (requiere_aprobacion_material IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_2_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_4_not_null CHECK (programa_id IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_5_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_7_not_null CHECK (modalidad IS NOT NULL);

-- Índices de Curso
CREATE UNIQUE INDEX "Curso_codigo_acceso_key" ON public."Curso" USING btree (codigo_acceso);
CREATE UNIQUE INDEX idx_curso_codigo_acceso ON public."Curso" USING btree (codigo_acceso);
CREATE INDEX idx_curso_institucion_id ON public."Curso" USING btree (institucion_id);
CREATE INDEX idx_curso_programa_id ON public."Curso" USING btree (programa_id);
CREATE INDEX idx_curso_coordinador_id ON public."Curso" USING btree (coordinador_id) WHERE (coordinador_id IS NOT NULL);
CREATE INDEX idx_curso_institucion_programa ON public."Curso" USING btree (institucion_id, programa_id);
CREATE UNIQUE INDEX uq_curso_nombre ON public."Curso" USING btree (institucion_id, nombre);
